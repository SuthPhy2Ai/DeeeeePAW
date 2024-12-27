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
from utils_res import DensityData, MyCollator

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
output_dir = './checkpoints'


# dict_test = {'atom_edges_displacement': torch.zeros(1 , 50, 3),
#              'num_atom_edges': torch.tensor(10).long().unsqueeze(0),
#              'num_nodes': torch.tensor(5).long().unsqueeze(0),
#              'atom_edges': torch.zeros(1, 50, 2).long(),
#              'atom_xyz': torch.zeros(1, 5, 3),
#              'nodes': torch.ones(5).long().unsqueeze(0),
#              'cell': torch.zeros(1, 3, 3),
#              'probe_xyz': torch.zeros(1, 500, 3),
#              'num_probes': torch.tensor(500).long().unsqueeze(0),
#              'probe_edges_displacement': torch.zeros(1, 500, 3),
#              'num_probe_edges': torch.tensor(500).long().unsqueeze(0),
#              'probe_edges': torch.zeros(1, 500, 2).long()
#              }

# out = model(dict_test)






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



# for epoch in range(start_epoch, num_train_epochs):
#     train_loss_sum = 0.0
#     start = time.time()
#     pbar = tqdm(enumerate(train_dataloader), total=len(train_dataloader), desc="batch")
    
#     # 训练阶段
#     for step, (big_batch, big_batch_invalid) in pbar:
#         for batch in tqdm(big_batch, total=len(big_batch)):
#             batch = {k: v.to(device) for k, v in batch.items()}
#             tru_batch = batch['probe_target']
            
#             # 前向传播
#             output_batch, node_rep = model(batch)
#             res_corr, res_far = res_model(batch, node_rep)
#             Fr = res_corr.view(-1) + output_batch.view(-1)

#             # 计算损失
#             loss = torch.nn.functional.mse_loss(tru_batch.view(-1), Fr)
#             loss = loss.mean()

#             print_loss.append(loss.item())
#             loss.backward()
#             train_loss_sum += loss.item()

#             # 梯度更新
#             optimizer.step()
#             lr_scheduler.step()
#             optimizer.zero_grad()

#         for batch in tqdm(big_batch_invalid, total=len(big_batch_invalid)):
#             batch = {k: v.to(device) for k, v in batch.items()}
#             tru_batch = batch['probe_target']

#             # 仅使用模型推理并计算损失
#             output_batch, node_rep = model(batch)
#             res_corr, res_far = res_model(batch, node_rep)
#             Fr = res_corr.view(-1) + output_batch.view(-1)
#             loss = torch.nn.functional.mse_loss(tru_batch.view(-1), Fr)
#             loss = loss.mean()
#             print_loss.append(loss.item())
#             loss.backward()
#             train_loss_sum += loss.item()

#         # 更新进度条
#         lr = optimizer.state_dict()["param_groups"][0]["lr"]
#         pbar.set_description(f"epoch {epoch + 1} iter {step}: train loss {loss.item():.5f}. lr {lr:e}")
    
#     # 验证阶段
#     test_loss = []
#     nmape_loss = []
#     with torch.no_grad():
#         for step, (big_batch, big_batch_invalid) in enumerate(val_dataloader):
#             for batch in big_batch:
#                 batch = {k: v.to(device) for k, v in batch.items()}
#                 tru_batch = batch['probe_target']
#                 output_batch, node_rep = model(batch)
#                 res_corr, res_far = res_model(batch, node_rep)
#                 Fr = res_corr.view(-1) + output_batch.view(-1)

#                 # 计算验证损失
#                 loss = torch.nn.functional.mse_loss(tru_batch.view(-1), Fr)
#                 test_loss.append(loss.item())
#                 nmape_ = nmape(tru_batch.view(-1), Fr)
#                 nmape_loss.append(nmape_)

#             for batch in big_batch_invalid:
#                 batch = {k: v.to(device) for k, v in batch.items()}
#                 tru_batch = batch['probe_target']
#                 output_batch, node_rep = model(batch)
#                 res_corr, res_far = res_model(batch, node_rep)
#                 Fr = res_corr.view(-1) + output_batch.view(-1)

#                 loss = torch.nn.functional.mse_loss(tru_batch.view(-1), Fr)
#                 test_loss.append(loss.item())
#                 nmape_ = nmape(tru_batch.view(-1), Fr)
#                 nmape_loss.append(nmape_)

#     # 计算平均验证损失
#     test_loss = float(np.mean(test_loss))
#     nmape_loss = float(np.mean(nmape_loss))
#     print(f"test loss: {test_loss}; nmape loss : {nmape_loss}")

#     # 保存最优模型
#     if test_loss < best_loss:
#         best_loss = test_loss
#         torch.save(res_model.module.state_dict(), os.path.join(output_dir, "paw_zno_poly_res.pt"))
#         torch.save(model.module.state_dict(), os.path.join(output_dir, "zno_ploy_based.pt"))






















for epoch in range(start_epoch, num_train_epochs):
    train_loss_sum = 0.0
    start = time.time()
    pbar = tqdm(enumerate(train_dataloader), total=len(train_dataloader), desc="batch")
    for step, batch in pbar:
        batch = {k: v.to(device) for k, v in batch.items()}
        tru_batch = batch['probe_target']
        #model.eval()
        output_batch, node_rep = model(batch)
        res_corr, res_far = res_model(batch, node_rep) # 
        #Fr = res_corr.view(-1) + output_batch.view(-1)  PAW
        Fr = res_corr.view(-1) + output_batch.view(-1)
        #Fr = output_batch.view(-1) + res_model.module.a_w * (res_corr.view(-1)-output_batch.view(-1))
        loss = torch.nn.functional.mse_loss((batch['probe_target']).view(-1), Fr)
        # loss = torch.nn.functional.huber_loss((batch['probe_target']).view(-1), Fr, delta=1.0)                                                        #res_corr.view(-1) + output_batch.view(-1))
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
            res_corr, res_far = res_model(batch, node_rep)


            # Fr = res_corr.view(-1)
            Fr = res_corr.view(-1) + output_batch.view(-1)

            #Fr = output_batch.view(-1) + res_model.module.a_w * (res_corr.view(-1)-output_batch.view(-1))
            #loss = torch.nn.functional.huber_loss((batch['probe_target']).view(-1), Fr, delta=1.0)
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
        torch.save(res_model.module.state_dict(), os.path.join(output_dir, "paw_zno_poly_res.pt"))
        torch.save(model.module.state_dict(), os.path.join(output_dir, "zno_ploy_based.pt"))

