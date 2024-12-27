import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from accelerate import Accelerator
from transformers import AdamW, get_scheduler


# 初始化 Accelerate 库
accelerator = Accelerator()

device = accelerator.device

# 自定义 Dataset 类
class CustomDataset(Dataset):
    def __init__(self, x, y):
        # 将传入的数据存储起来以供之后使用
        self.x = x
        self.y = y

    def __len__(self):
        # 返回数据集的大小
        return len(self.x)

    def __getitem__(self, index):
        # 返回给定索引的数据对
        return {'input':self.x[index],'target': self.y[index]}

# 准备数据
x = torch.randn(10000000, 500)
y = torch.randn(10000000, 1)

# 创建自定义数据集
dataset = CustomDataset(x, y)
dataloader = DataLoader(dataset, batch_size=1024000*2, shuffle=True)

# 定义简单的模型
class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc1 = nn.Linear(500, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 32)
        self.fc5 = nn.Linear(32, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = x['input']
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.relu(self.fc3(x))
        x = self.relu(self.fc4(x))
        x = self.fc5(x)
        return x


model = SimpleModel()
criterion = nn.MSELoss()
optimizer_grouped_parameters = [
    {'params': [p for n, p in model.named_parameters()], 'lr': 1e-4},
    # {'params': [p for n, p in model.named_parameters() if 'bert' in n], 'lr': 2e-5}
]
optimizer_kwargs = {
    'betas': (0.9, 0.999),
    'eps': 1e-8,
}
optimizer = AdamW(optimizer_grouped_parameters, **optimizer_kwargs)
# 使用 accelerate 函数来准备模型、优化器和数据加载器
model, optimizer, dataloader = accelerator.prepare(model, optimizer, dataloader)

# 训练模型
# epochs = 500000000000
while True:
    model.train()
    for batch in dataloader:
        # 将数据移动到加速器设备上（通常是 GPU）
        batch = {k: v.to(device) for k, v in batch.items()}
        
        # 前向传播
        outputs = model(batch)
        loss = criterion(outputs, batch['target'])
        
        # 反向传播和优化
        # optimizer.zero_grad()
        # accelerator.backward(loss)
        # optimizer.step()
    
    # if epoch % 1000 == 0:  # 每1000个epoch打印一次损失
    print(f"Epoch [Loss: {loss.item():.4f}")

print("Training complete.")