import math
import logging
import time

from model import E3DensityModel

from torch.utils.data.dataloader import DataLoader

import torch

import glob
import os
import numpy as np
from tqdm import  tqdm
from torch.utils.data import DataLoader, random_split, Subset
# from torch.utils.data import DataLoader
from ase.db import connect
from utils import DensityData, MyCollator
from transformers import AdamW, get_scheduler
from accelerate import Accelerator

random_seed = 42
torch.manual_seed(random_seed)
torch.cuda.manual_seed(random_seed)


accelerator = Accelerator()

device = accelerator.device


model = E3DensityModel()


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






mysql_url = 'mysql://root:@localhost:3306/temp_chg'



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
output_dir = './checkpoints'

# model = torch.nn.DataParallel(model).to(torch.cuda.current_device())

optimizer_grouped_parameters = [
    {'params': [p for n, p in model.named_parameters()], 'lr': 5e-3},
    # {'params': [p for n, p in model.named_parameters() if 'bert' in n], 'lr': 2e-5}
]
optimizer_kwargs = {
    'betas': (0.9, 0.999),
    'eps': 1e-8,
}
optimizer = AdamW(optimizer_grouped_parameters, **optimizer_kwargs)

model.train()

num_update_steps_per_epoch = math.ceil(
    len(train_dataloader)
)

max_train_steps = num_train_epochs * num_update_steps_per_epoch
# lr_scheduler = get_scheduler(
#     name='linear',
#     optimizer=optimizer,
#     num_warmup_steps=0 * len(train_dataloader),
#     num_training_steps=max_train_steps,
# )
lr_scheduler = get_scheduler(
    name='cosine',
    optimizer=optimizer,
    num_warmup_steps=0 * len(train_dataloader),
    num_training_steps=max_train_steps,
)
start_epoch = 0
completed_steps = 0

# checkpoint = torch.load('/data/chg/charge3net-main/checkpoints/xrd_best.pt', map_location='cpu')  # 加载 .pt 文件
# model.load_state_dict(checkpoint)


model, optimizer, train_dataloader, val_dataloader = accelerator.prepare(model, optimizer, train_dataloader, val_dataloader)



print_loss = []
best_loss = float('inf')

for epoch in range(start_epoch, num_train_epochs):
    train_loss_sum = 0.0
    start = time.time()
    pbar = tqdm(enumerate(train_dataloader), total=len(train_dataloader))
    for step, (batch) in pbar:

        # batch = {k: v.to(device) for k, v in batch.items()}
        output = model(batch)
        loss = torch.nn.functional.l1_loss(batch['probe_target'], output)
        loss = loss.mean()


        print_loss.append(loss.item())
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

    test_loss = []
    with torch.no_grad():
        for step, (batch) in enumerate(val_dataloader):
            # batch = {k: v.to(device) for k, v in batch.items()}
            output = model(batch)
            loss = torch.nn.functional.l1_loss(batch['probe_target'], output)
            loss = loss.mean()

            test_loss.append(loss.item())

    test_loss = float(np.mean(test_loss))
    print("test loss: {}".format(test_loss))

    if test_loss < best_loss:
        best_loss = test_loss
        torch.save(model.module.state_dict(), os.path.join(output_dir, "xrd_best.pt"))

np.savetxt('./training_loss_ten.txt', np.array(print_loss))
torch.save(model.module.state_dict(), os.path.join(output_dir, "final_{}_tan.pt".format(epoch)))
