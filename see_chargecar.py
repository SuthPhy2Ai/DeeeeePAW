import math
import logging
import time

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
from utils_see_chg import DensityData, MyCollator
from transformers import AdamW, get_scheduler

random_seed = 42
torch.manual_seed(random_seed)
torch.cuda.manual_seed(random_seed)


device = 'cuda:7'

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


mysql_url= 'mysql://root:@localhost:3306/temp_chg'
dataset = DensityData(mysql_url)
total_count = len(dataset)
print(f"Total count: {total_count}")
train_count = int(0.8 * total_count)
valid_count = int(0.1 * total_count)
test_count = total_count - train_count - valid_count
train_dataset, valid_dataset, test_dataset = random_split(dataset, [train_count, valid_count, test_count])

# Access the last item from the test dataset
last_index = test_dataset.indices[-4]
last_example = dataset[last_index]


checkpoint = torch.load('/data/chg/charge3net-main/checkpoints/xrd_best.pt', map_location='cpu')  # 加载 .pt 文件
model.load_state_dict(checkpoint)
model = model.to(device)

# checkpoint = torch.load('/data/chg/charge3net-main/models/charge3net_mp.pt', map_location='cpu')  # 加载 .pt 文件
# model.load_state_dict(checkpoint['model'])
# model = model.to(device)




checkpoint = torch.load('/data/chg/charge3net-main/checkpoints_res/res_best.pt', map_location='cpu')  # 加载 .pt 文件
# print(checkpoint.keys())
res_model.load_state_dict(checkpoint)

res_model = res_model.to(device)

val_dataloader = DataLoader(
        [valid_dataset[1]],
        batch_size=1,
        collate_fn=MyCollator(mysql_url, cutoff=4, num_probes=None))



all_true = []
all_pred = []
all_true_corr = []
all_pred_corr = []
countt = 0

with torch.no_grad():
    for step, (big_batch, big_batch_invalid) in enumerate(val_dataloader):
        for batch in tqdm(big_batch, total=len(big_batch)):
            batch = {k: v.to(device) for k, v in batch.items()}
            output, node_rep = model(batch)
            output = output.view(-1)
            res, _ = res_model(batch, node_rep)
            tru = batch['probe_target'].view(-1)
            all_true.append(tru.detach().cpu())
            all_pred.append(output.detach().cpu())
            all_pred_corr.append(output.detach().cpu() + 1.0 * res.view(-1).detach().cpu())

        for batch in tqdm(big_batch_invalid, total=len(big_batch_invalid)):
            batch = {k: v.to(device) for k, v in batch.items()}
            output, _ = model(batch)
            output = output.view(-1)
            tru = batch['probe_target'].view(-1)
            all_true.append(tru.detach().cpu())
            all_pred.append(output.detach().cpu())
            all_pred_corr.append(output.detach().cpu())

from sklearn.metrics import r2_score, mean_absolute_error
all_true = torch.cat(all_true, dim=0).numpy()
all_pred = torch.cat(all_pred, dim=0).numpy()
# all_true_corr = torch.cat(all_true_corr, dim=0).numpy()
all_pred_corr = torch.cat(all_pred_corr, dim=0).numpy()


import matplotlib.pyplot as plt
r2 = r2_score(all_true, all_pred)
mae = mean_absolute_error(all_true, all_pred)

r2_corr = r2_score(all_true, all_pred_corr)
mae_corr = mean_absolute_error(all_true, all_pred_corr)
# r2_corr = r2_score(all_true_corr, all_pred_corr)
# mae_corr = mean_absolute_error(all_true_corr, all_pred_corr)


print(f"R² (R-squared): {r2:.10f}, R²_corr (R-squared): {r2_corr:.10f}")
print(f"MAE (Mean Absolute Error): {mae:.10f}, MAE_corr (Mean Absolute Error): {mae_corr:.10f}")


# 绘制散点图
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
plt.savefig('scatter_plot.png', dpi=300, bbox_inches='tight')
plt.show()


plt.figure(figsize=(8, 8))
plt.scatter(all_true, all_pred_corr, alpha=0.3, s=5, edgecolors='none')
plt.plot([all_true.min(), all_true.max()+1], [all_true.min(), all_true.max()+1], 'r--', lw=0.2)

# 显示R²和MAE
plt.text(0.05, 0.95, f"$R^2 = {r2_corr:.10f}$\nMAE = {mae_corr:.10f}", transform=plt.gca().transAxes, 
         fontsize=14, verticalalignment='top', bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

plt.xlabel('True Values', fontsize=14)
plt.ylabel('Predicted Values', fontsize=14)
plt.title('Scatter Plot of Predictions vs True Values', fontsize=16)
plt.grid(True)

# 保存图片
plt.savefig('scatter_plot_corr.png', dpi=300, bbox_inches='tight')
plt.show()