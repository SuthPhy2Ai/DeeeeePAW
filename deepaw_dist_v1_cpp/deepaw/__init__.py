"""
DeePAW C++ Inference Engine - Python API
使用C++推理引擎进行加密模型推理
"""
import os
import sys
from pathlib import Path

# 设置库路径
_current_dir = Path(__file__).parent
_lib_path = str(_current_dir)

# 添加到LD_LIBRARY_PATH（对于已启动的进程可能不生效）
if 'LD_LIBRARY_PATH' in os.environ:
    os.environ['LD_LIBRARY_PATH'] = f"{_lib_path}:{os.environ['LD_LIBRARY_PATH']}"
else:
    os.environ['LD_LIBRARY_PATH'] = _lib_path

# 导入C++模块
try:
    import deepaw_cpp
except ImportError as e:
    raise ImportError(
        f"无法导入C++推理引擎: {e}\n"
        f"请确保：\n"
        f"1. 使用Python 3.12环境\n"
        f"2. 在启动Python前设置: export LD_LIBRARY_PATH={_lib_path}:$LD_LIBRARY_PATH\n"
        f"3. 或使用提供的启动脚本"
    )

__version__ = "1.0.0-cpp"
__all__ = ['Model', 'SecureModel']


class Model:
    """
    DeePAW模型 - C++推理引擎版本

    使用C++推理引擎进行加密模型的加载和推理。
    解密密钥已编译到C++库中，无需Python源码中的密钥。

    Args:
        device: 设备类型 ('cpu' 或 'cuda')
        auto_init: 是否自动初始化并加载模型
    """

    def __init__(self, device='cpu', auto_init=True):
        self.device = device
        self._engine = deepaw_cpp.InferenceEngine(device)

        if auto_init:
            # 自动加载bundled模型
            models_dir = _current_dir.parent / 'models'
            f_nonlocal_path = str(models_dir / 'f_nonlocal.enc')
            f_local_path = str(models_dir / 'f_local.enc')

            if not Path(f_nonlocal_path).exists():
                raise FileNotFoundError(f"F_nonlocal模型不存在: {f_nonlocal_path}")
            if not Path(f_local_path).exists():
                raise FileNotFoundError(f"F_local模型不存在: {f_local_path}")

            self.initialize(f_nonlocal_path, f_local_path)

    def initialize(self, f_nonlocal_path, f_local_path):
        """
        加载加密模型

        Args:
            f_nonlocal_path: F_nonlocal加密模型路径
            f_local_path: F_local加密模型路径
        """
        self._engine.initialize(f_nonlocal_path, f_local_path)

    def is_initialized(self):
        """检查模型是否已初始化"""
        return self._engine.is_initialized()

    def __call__(self, batch):
        """
        运行推理（F_nonlocal + F_local）

        Args:
            batch: 输入数据字典

        Returns:
            (predictions, node_rep): 预测结果和节点表示
        """
        return self._engine.predict_dual(batch)


# 向后兼容别名
SecureModel = Model
