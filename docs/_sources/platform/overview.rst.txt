平台介绍
========

DeePAW 是 DeePAW 方法的在线推理服务平台，提供 Web 界面和 RESTful API 两种访问方式，面向材料科学研究人员提供高效的批量电荷密度计算服务。

核心功能
--------

- **批量电荷密度预测**: 从原子结构文件预测三维电荷密度分布
- **多格式文件支持**: 支持 CIF、VASP、XYZ、PDB 等 15 种结构文件格式
- **多 GPU 并行调度**: 内置优先级队列和 GPU 任务调度器，支持多任务并行
- **RESTful API**: 完整的程序化访问接口，便于集成到自动化工作流
- **CHGCAR 输出**: 兼容 VASP 格式，可直接用 VESTA、Ovito 等工具可视化
- **实时进度追踪**: WebSocket 实时推送任务状态
- **Web 前端**: React 交互界面，支持 3D 等值面可视化
- **模型热启动**: GPU 模型缓存机制，首次推理后模型常驻显存，后续任务无需重复加载

技术栈
------

- **前端**: React 19 + TypeScript + Vite + Plotly.js
- **后端**: FastAPI + Uvicorn (ASGI)
- **推理**: PyTorch + E3NN + ASE
- **数据格式**: 多种格式 -> ASE Database -> CHGCAR (VASP)

系统架构
--------

.. code-block:: text

   浏览器 / Python 客户端
     -> React 前端 (端口 3000)
     -> Vite 代理 /api/*
     -> FastAPI 后端 (端口 8080)
     -> GPU 任务队列 + 调度器
     -> DeePAW 推理引擎
     -> CHGCAR 文件输出
     -> 前端 3D 可视化 / 客户端下载

GPU 任务调度
^^^^^^^^^^^^

- 每个 GPU 一个工作线程，通过 ``threading.Lock`` 实现独占访问
- 任务按优先级队列 (PriorityQueue) 排序处理
- 模型缓存: 首次任务加载模型到 GPU 显存 (~5-10s)，后续任务直接复用 (<0.1s 开销)
- 每个 GPU 缓存一个模型实例，约占 2-4GB 显存

系统要求
--------

服务器端
^^^^^^^^

- Python 3.10+
- CUDA 11.8+ / 12.x
- GPU: 8GB+ 显存 (推荐 16GB+)
- 磁盘: 每个 CHGCAR 约 5-10MB
- 内存: 16GB+ (推荐 32GB+)

客户端
^^^^^^

- Python 3.7+ (仅需 ``requests`` 库)
- 或任何支持 HTTP 请求的编程语言
- 无 GPU 要求
