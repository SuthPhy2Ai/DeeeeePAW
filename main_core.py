import math
import logging
import time
from kan import *
from model import E3DensityModel, ResidualCorrectionModel

from torch.utils.data.dataloader import DataLoader

import torch

import glob
import os
import numpy as np
from tqdm import  tqdm
from torch.utils.data import DataLoader, random_split, Subset
# from torch.utils.data import DataLoader
from ase.db import connect
#from utils_see_chg import DensityData, MyCollator
from utils import DensityData, MyCollator

from transformers import AdamW, get_scheduler
from accelerate import Accelerator


from accelerate.utils import AutocastKwargs
from accelerate.utils import DistributedDataParallelKwargs

kwargs = DistributedDataParallelKwargs(find_unused_parameters=True)
#kwargs = AutocastKwargs(cache_enabled=True)
accelerator = Accelerator(kwargs_handlers=[kwargs])

random_seed = 42
torch.manual_seed(random_seed)
torch.cuda.manual_seed(random_seed)

#accelerator = Accelerator()

device = accelerator.device


model = E3DensityModel()
res_model = ResidualCorrectionModel(num_embeddings=300, embedding_dim=128)

num_train_epochs = 300
#mysql_url = 'mysql://root:@localhost:3306/temp_chg'
mysql_url = '/data/chg/quick.db'

dataset = DensityData(mysql_url)
total_count = len(dataset)
train_count = int(0.8 * total_count)
valid_count = int(0.1 * total_count)
test_count = total_count - train_count - valid_count

train_dataset, valid_dataset, test_dataset = random_split(dataset, [train_count, valid_count, test_count])
train_dataloader = DataLoader(
    train_dataset,
    shuffle=True,
    batch_size=4,
    num_workers=16,
    collate_fn=MyCollator(mysql_url, cutoff=4.0, num_probes=350)
)
val_dataloader = DataLoader(
    valid_dataset,
    shuffle=True,
    batch_size=6,
    num_workers=16,
    collate_fn=MyCollator(mysql_url, cutoff=4.0, num_probes=350)
)
# device = torch.cuda.current_device()
# device = 'cpu'
num_train_epochs = 15000
output_dir = './checkpoints_suth'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
# model = torch.nn.DataParallel(model).to(torch.cuda.current_device())

optimizer_grouped_parameters = [
    {'params': [p for n, p in res_model.named_parameters()], 'lr': 1e-3},
    {'params': [p for n, p in model.named_parameters()], 'lr': 2e-6}
]
optimizer_kwargs = {
    'betas': (0.9, 0.999),
    'eps': 1e-8,
}
optimizer = AdamW(optimizer_grouped_parameters, **optimizer_kwargs)

model.train()
res_model.train()

num_update_steps_per_epoch = math.ceil(
    len(train_dataloader)
)

max_train_steps = num_train_epochs * num_update_steps_per_epoch
lr_scheduler = get_scheduler(
    name='cosine',
    optimizer=optimizer,
    num_warmup_steps=0 * len(train_dataloader),
    num_training_steps=max_train_steps,
)
start_epoch = 0
completed_steps = 0

checkpoint = torch.load('/data/chg/charge3net-main/checkpoints_res/res_best_model.pt', map_location='cpu')  # 加载 .pt 文件
model.load_state_dict(checkpoint)
model = model.to(device)
res_model = res_model.to(device)
 


model, res_model, optimizer, train_dataloader, val_dataloader = accelerator.prepare(model, res_model, optimizer, train_dataloader, val_dataloader)

def nmape(y_true, y_pred):
    y_true = y_true.cpu().numpy()  
    y_pred = y_pred.cpu().numpy()  
    return np.mean(np.abs((y_true - y_pred) / y_true+0.00001)) * 100

def nmape_batch(y_true, y_pred):
    diff = torch.abs(y_true - y_pred)  
    target_sum = torch.abs(y_true).sum(dim=1)  
    nmape_per_batch = diff.sum(dim=1) / target_sum * 100  
    return nmape_per_batch.mean()  

print_loss = []
best_loss = float('inf')


for epoch in range(start_epoch, num_train_epochs):
    train_loss_sum = 0.0
    start = time.time()
    pbar = tqdm(enumerate(train_dataloader), total=len(train_dataloader), desc="batch")
    for step, batch in pbar:
        batch = {k: v.to(device) for k, v in batch.items()}
        tru_batch = batch['probe_target']
        #model.eval()
        output_batch, node_rep = model(batch)
        Fr = output_batch.view(-1)
        loss = torch.nn.functional.mse_loss((batch['probe_target']).view(-1), Fr)
        loss = loss.mean()
        print_loss.append(loss.item())
        torch.distributed.barrier()
        loss.backward()
        train_loss_sum += loss.item()
        if (
                step % 1 == 0
                or step == len(train_dataloader) - 1
        ):
            optimizer.step()
            lr_scheduler.step()
            optimizer.zero_grad()
        lr = optimizer.state_dict()["param_groups"][0]["lr"]
        pbar.set_description(f"epoch {epoch + 1} iter {step}: train loss {loss.item():.5f}. lr {lr:e}")

    test_loss  = []
    nmape_loss = []
    with torch.no_grad():
        for step, batch in enumerate(val_dataloader):
            batch = {k: v.to(device) for k, v in batch.items()}
            tru_batch = batch['probe_target']
            output_batch, node_rep = model(batch)
            Fr = output_batch.view(-1)
            loss = torch.nn.functional.mse_loss((batch['probe_target']).view(-1), Fr)
            loss = loss.mean()
            test_loss.append(loss.item())
            nmape_ = nmape((batch['probe_target']).view(-1), Fr)
            nmape_loss.append(nmape_)
    
    test_loss = float(np.mean(test_loss))
    nmape_loss = float(np.mean(nmape_loss))
    print(f"test loss: {test_loss}; nmape loss : {nmape_loss}")

    if test_loss < best_loss:
        best_loss = test_loss
        # torch.save(res_model.module.state_dict(), os.path.join(output_dir, "paw_zno_poly_res.pt"))
        torch.save(model.module.state_dict(), os.path.join(output_dir, "zno_ploy_pt.pt"))

