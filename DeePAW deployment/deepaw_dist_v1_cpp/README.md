# DeePAW 加密模型分发包 - C++推理引擎版本

## 版本信息

- **版本**: 1.0.0-cpp
- **推理引擎**: C++（LibTorch）
- **加密算法**: AES-256-GCM
- **批次大小**: 1000个探测点
- **Python版本**: 3.12（必需）

## 简介

这是DeePAW电荷密度预测模型的**C++推理引擎版本**，提供最强的模型保护：

✓ **解密密钥编译到C++库中**（不在Python源码中）
✓ **解密逻辑在C++层**（难以逆向）
✓ **模型权重AES-256-GCM加密**
✓ **保护级别**: ⭐⭐⭐⭐⭐

## 系统要求

- **Python**: 3.12（必需，不支持其他版本）
- **CUDA**: 11.8+ (GPU推理)
- **平台**: Linux x86_64

## 文件结构

```
deepaw_dist_v1_cpp/
├── models/                    # 加密模型
│   ├── f_nonlocal.enc        # TorchScript模型 (20MB)
│   └── f_local.enc           # PyTorch模型 (301KB)
├── deepaw/                    # 推理引擎
│   ├── __init__.py           # Python API
│   ├── libdeepaw_core.so     # C++核心库（密钥在此）
│   ├── deepaw_cpp.cpython-312-x86_64-linux-gnu.so  # Python绑定
│   └── data/                 # 图构建工具
├── tests/
│   └── hfo2.db               # 测试数据库
├── run.sh                     # 启动脚本（自动设置环境）
├── predict_chgcar.py          # CHGCAR预测脚本
└── README.md                  # 本文档
```

## 安装

1. 确保使用Python 3.12环境：
```bash
python --version  # 应显示 Python 3.12.x
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 方法1：使用启动脚本（推荐）

启动脚本会自动设置环境变量：

```bash
./run.sh predict_chgcar.py
```

### 方法2：手动设置环境

```bash
# 设置库路径
export LD_LIBRARY_PATH=$(pwd)/deepaw:$LD_LIBRARY_PATH

# 运行脚本
python predict_chgcar.py
```

### 预期输出

```
======================================================================
HfO2 Complete CHGCAR Prediction - Encrypted Model Version
======================================================================

1. Loading structure (ID=1)...
   Formula: Hf4O8
   Number of atoms: 12

2. Loading encrypted model (device: cuda)...
   GPU: NVIDIA ...

3. Predicting full charge density grid...
Processing in 64 batches of 1000...

4. Prediction results:
   Grid dimensions: 40x40x40
   Total points: 64000
   Density statistics:
     Min: ~0.028
     Max: ~8.116
     Mean: ~0.689
     Std: ~1.036

✓ CHGCAR saved to: CHGCAR_hfo2_id1
```

## 保护机制

### C++推理引擎的安全优势

| 组件 | 保护方式 | 保护级别 |
|------|---------|---------|
| **模型权重** | AES-256-GCM加密 | ⭐⭐⭐⭐⭐ |
| **解密密钥** | 编译到libdeepaw_core.so | ⭐⭐⭐⭐⭐ |
| **解密逻辑** | C++实现，编译到.so | ⭐⭐⭐⭐⭐ |
| **F_nonlocal结构** | TorchScript序列化 | ⭐⭐⭐⭐ |

### 与Python版本的对比

**Python版本（V0/V1）**：
- ✗ 解密密钥在crypto_utils.py中可见
- ✗ 解密逻辑在Python源码中
- ✓ 模型权重加密

**C++版本（V1_cpp）**：
- ✓ 解密密钥编译到.so中，难以提取
- ✓ 解密逻辑在C++中，难以逆向
- ✓ 模型权重加密
- ✓ **无需crypto_utils.py源码**

## 技术细节

- **推理引擎**: C++ + LibTorch
- **Python绑定**: pybind11
- **批次大小**: 1000个探测点
- **自动批处理**: 支持任意数量的探测点
- **设备支持**: CPU / CUDA

## 注意事项

1. **Python版本**: 必须使用Python 3.12，其他版本不兼容
2. **环境变量**: 需要设置LD_LIBRARY_PATH，建议使用run.sh脚本
3. **平台限制**: 仅支持Linux x86_64
4. **GPU推理**: 需要CUDA 11.8+和兼容的GPU

## 版本历史

- **V1_cpp**: C++推理引擎版本，最强保护
- **V1**: Python版本，1000探测点批次
- **V0**: Python版本，100探测点批次
