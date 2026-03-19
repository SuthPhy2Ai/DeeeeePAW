本地 CLI 部署
==============

DeePAW 提供容器化的本地 CLI 部署版本，通过 Podman/Docker 容器运行加密的神经网络模型推理。

环境要求
--------

- Linux x86_64
- NVIDIA GPU (CUDA 支持)
- Podman 或 Docker
- NVIDIA 驱动

快速开始
--------

**1. 加载容器镜像（首次使用）**

.. code-block:: bash

   # 检查镜像是否已加载
   podman images | grep deepaw

   # 从 tar 包加载
   podman load -i deepaw_dist_v1_cpp/deepaw-cppv1.tar.gz

**2. 启动容器**

.. code-block:: bash

   # 使用默认数据目录
   ./start.sh

   # 指定自定义数据目录
   ./start.sh /path/to/your/data

``start.sh`` 脚本自动完成以下操作：

- 检测 NVIDIA 驱动版本
- 挂载 GPU 设备和库
- 设置所需的环境变量
- 挂载数据和输出目录

**3. 运行推理**

容器内执行：

.. code-block:: bash

   # 使用内置测试数据
   python predict_chgcar.py --db tests/hfo2.db --id 1 --device cuda

   # 使用挂载的自定义数据
   python predict_chgcar.py --db /data/your_database.db --id 1 --device cuda

   # 指定输出路径
   python predict_chgcar.py --db /data/your_database.db --id 1 --device cuda --output /output/CHGCAR_result

   # 自定义网格密度
   python predict_chgcar.py --db /data/your_database.db --id 1 --device cuda --grid 60 60 60

退出容器后，输出文件在宿主机的 ``output/`` 目录。

重要说明
--------

**CUDA only**

加密模型的解密逻辑编译在 C++ 引擎中，只能在 CUDA 设备上初始化。使用 ``--device cpu`` 会导致模型初始化静默失败。

**GPU 挂载**

在某些系统上（如 Rocky Linux 9.2），CDI 模式（``--device nvidia.com/gpu=all``）可能无法正常工作。``start.sh`` 通过手动挂载 ``/dev/nvidia*`` 设备和宿主机 NVIDIA 库来解决此问题。

容器结构
--------

::

   /app/
   ├── predict_chgcar.py          # 主推理脚本
   ├── deepaw/
   │   ├── __init__.py            # Python API
   │   ├── deepaw_cpp.*.so        # pybind11 C++ 绑定
   │   ├── libdeepaw_core.so      # C++ 核心库（含解密密钥）
   │   └── data/                  # 图构建工具
   ├── models/
   │   ├── f_nonlocal.enc         # 加密的 GNN 模型
   │   └── f_local.enc            # 加密的 KAN 校正模型
   └── tests/hfo2.db              # 内置测试数据

手动运行
--------

如果 ``start.sh`` 不适用于你的环境：

.. code-block:: bash

   DRIVER_VER=$(cat /sys/module/nvidia/version)

   podman run -it --rm \
       --security-opt=label=disable \
       --device /dev/nvidia0 \
       --device /dev/nvidiactl \
       --device /dev/nvidia-uvm \
       --device /dev/nvidia-uvm-tools \
       --device /dev/nvidia-modeset \
       -v /usr/lib64/libnvidia-ml.so.${DRIVER_VER}:/usr/lib64/libnvidia-ml.so.${DRIVER_VER}:ro \
       -v /usr/lib64/libcuda.so.${DRIVER_VER}:/usr/lib64/libcuda.so.${DRIVER_VER}:ro \
       -v /usr/lib64/libnvidia-ptxjitcompiler.so.${DRIVER_VER}:/usr/lib64/libnvidia-ptxjitcompiler.so.${DRIVER_VER}:ro \
       -e PYTHONPATH=/app/deepaw \
       -e LD_LIBRARY_PATH=/app/deepaw:/usr/local/lib/python3.12/dist-packages/torch/lib:/usr/lib64 \
       -v /path/to/your/data:/data \
       -v $(pwd)/output:/output \
       deepaw-cpp:v1 \
       bash

故障排除
--------

.. list-table::
   :header-rows: 1

   * - 问题
     - 原因
     - 解决方案
   * - "Models not initialized"
     - 使用了 ``--device cpu``
     - 改用 ``--device cuda``
   * - "failed to stat CDI host device"
     - CDI 模式不可用
     - 使用 ``start.sh``（已手动处理）
   * - ``ModuleNotFoundError: deepaw_cpp``
     - 缺少环境变量
     - 使用 ``start.sh``（自动设置）
   * - ``libtorch.so: cannot open``
     - LD_LIBRARY_PATH 未设置
     - 使用 ``start.sh``（自动设置）
   * - nvidia-smi 容器内不可用
     - NVIDIA 库未挂载
     - 使用 ``start.sh``（自动挂载）
   * - ``.so`` 文件找不到
     - 驱动版本不匹配
     - ``start.sh`` 自动检测驱动版本
