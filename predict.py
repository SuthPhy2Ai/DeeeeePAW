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

random_seed = 42
torch.manual_seed(random_seed)
torch.cuda.manual_seed(random_seed)


device = 'cuda:0'
# device = 'cpu'

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
print(len(dataset))
total_count = len(dataset)
train_count = int(0.8 * total_count)
valid_count = int(0.1 * total_count)
test_count = total_count - train_count - valid_count

train_dataset, valid_dataset, test_dataset = random_split(dataset, [train_count, valid_count, test_count])



train_dataloader = DataLoader(
    train_dataset,
    shuffle=True,
    batch_size=1,
    num_workers=8,
    collate_fn=MyCollator(mysql_url, cutoff=4.0, num_probes=350)
)
val_dataloader = DataLoader(
    valid_dataset,
    shuffle=True,
    batch_size=6,
    num_workers=32,
    collate_fn=MyCollator(mysql_url, cutoff=4.0, num_probes=350)
)
# device = torch.cuda.current_device()
# device = 'cpu'
# num_train_epochs = 15000
# output_dir = './checkpoints'

# # model = torch.nn.DataParallel(model).to(torch.cuda.current_device())

# optimizer_grouped_parameters = [
#     {'params': [p for n, p in model.named_parameters()], 'lr': 1e-4},
#     # {'params': [p for n, p in model.named_parameters() if 'bert' in n], 'lr': 2e-5}
# ]
# optimizer_kwargs = {
#     'betas': (0.9, 0.999),
#     'eps': 1e-8,
# }
# optimizer = AdamW(optimizer_grouped_parameters, **optimizer_kwargs)

# model.train()

# num_update_steps_per_epoch = math.ceil(
#     len(train_dataloader)
# )

# max_train_steps = num_train_epochs * num_update_steps_per_epoch
# # lr_scheduler = get_scheduler(
# #     name='linear',
# #     optimizer=optimizer,
# #     num_warmup_steps=0 * len(train_dataloader),
# #     num_training_steps=max_train_steps,
# # )
# lr_scheduler = get_scheduler(
#     name='cosine',
#     optimizer=optimizer,
#     num_warmup_steps=0 * len(train_dataloader),
#     num_training_steps=max_train_steps,
# )
# start_epoch = 0
# completed_steps = 0


# print_loss = []
# best_loss = float('inf')

# for epoch in range(start_epoch, num_train_epochs):
#     train_loss_sum = 0.0
#     start = time.time()
#     pbar = tqdm(enumerate(train_dataloader), total=len(train_dataloader))
#     for step, (batch) in pbar:

#         # batch = {k: v.to(device) for k, v in batch.items()}
#         output = model(batch)
#         loss = torch.nn.functional.l1_loss(batch['probe_target'], output)
#         loss = loss.mean()


#         print_loss.append(loss.item())
#         loss.backward()
#         train_loss_sum += loss.item()
#         if (
#                 step % 1 == 0
#                 or step == len(train_dataloader) - 1
#         ):
#             optimizer.step()
#             lr_scheduler.step()
#             optimizer.zero_grad()
#         lr = optimizer.state_dict()["param_groups"][0]["lr"]
#         pbar.set_description(f"epoch {epoch + 1} iter {step}: train loss {loss.item():.5f}. lr {lr:e}")

#     test_loss = []
#     for step, (batch) in enumerate(val_dataloader):
#         # batch = {k: v.to(device) for k, v in batch.items()}
#         output = model(batch)
#         loss = torch.nn.functional.l1_loss(batch['probe_target'], output)
#         loss = loss.mean()

#         test_loss.append(loss.item())

#     test_loss = float(np.mean(test_loss))
#     print("test loss: {}".format(test_loss))

#     if test_loss < best_loss:
#         best_loss = test_loss
#         torch.save(model.module.state_dict(), os.path.join(output_dir, "xrd_best.pt"))

# np.savetxt('./training_loss_ten.txt', np.array(print_loss))
# torch.save(model.module.state_dict(), os.path.join(output_dir, "final_{}_tan.pt".format(epoch)))




# checkpoint = torch.load('/data/chg/charge3net-main/models/charge3net_mp.pt', map_location='cpu')  # 加载 .pt 文件
# # print(checkpoint.keys())
# model.load_state_dict(checkpoint['model'])

checkpoint = torch.load('/data/chg/charge3net-main/checkpoints/xrd_best.pt', map_location='cpu')  # 加载 .pt 文件
# print(checkpoint.keys())
model.load_state_dict(checkpoint)

model = model.to(device)
pbar = tqdm(enumerate(val_dataloader), total=len(val_dataloader))

total_nmape, total_count_cal = 0.0, 0


all_true = []
all_pred = []
with torch.no_grad():
    for step, (batch) in pbar:
        # if step == 4:
        #     break
        batch = {k: v.to(device) for k, v in batch.items()}
        output = model(batch)
        tru = batch['probe_target']
        all_true.append(tru.view(-1).detach().cpu())
        all_pred.append(output.view(-1).detach().cpu())


from sklearn.metrics import r2_score, mean_absolute_error
all_true = torch.cat(all_true, dim=0).numpy()
all_pred = torch.cat(all_pred, dim=0).numpy()

import matplotlib.pyplot as plt
r2 = r2_score(all_true, all_pred)
mae = mean_absolute_error(all_true, all_pred)

print(f"R² (R-squared): {r2:.10f}")
print(f"MAE (Mean Absolute Error): {mae:.10f}")

plt.figure(figsize=(8, 8))
plt.scatter(all_true, all_pred, alpha=0.3, s=5, edgecolors='none')
plt.plot([all_true.min(), all_true.max()+1], [all_true.min(), all_true.max()+1], 'r--', lw=0.2)

# 显示R²和MAE
plt.text(0.05, 0.95, f"$R^2 = {r2:.10f}$\nMAE = {mae:.10f}", transform=plt.gca().transAxes, 
         fontsize=14, verticalalignment='top', bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

plt.xlabel('True Values', fontsize=14)
plt.ylabel('Predicted Values', fontsize=14)
plt.title('Scatter Plot of Predictions vs True Values', fontsize=16)
plt.grid(True)

# 保存图片
plt.savefig('scatter_plot_total.png', dpi=300, bbox_inches='tight')
plt.show()