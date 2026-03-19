部署指南
========

环境准备
--------

依赖安装
^^^^^^^^

**后端依赖（需要 CUDA 环境）：**

.. code-block:: bash

   # 安装核心 ML 依赖
   cd used
   pip install -r requirements.txt

   # 安装 Web 后端依赖
   cd ../deepaw_integrated/backend
   pip install -r requirements.txt

**前端依赖：**

.. code-block:: bash

   cd deepaw_integrated/frontend
   npm install

必要文件
^^^^^^^^

- ASE 数据库文件（``.db``）：包含原子结构数据
- 模型权重文件（``.pth``）：默认路径 ``checkpoints_mpall/3-23.pth``
- 输出目录：用于存放生成的 CHGCAR 文件

环境变量
--------

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - 变量名
     - 说明
     - 默认值
   * - ``DEEPAW_DB_PATH``
     - ASE 数据库路径
     - ``data/HfO2_demo.db``
   * - ``DEEPAW_CHECKPOINT``
     - 模型权重路径
     - ``checkpoints_mpall/3-23.pth``
   * - ``DEEPAW_GPUS``
     - 可用 GPU 编号（逗号分隔）
     - ``1,2,3``
   * - ``DEEPAW_OUTPUT_DIR``
     - CHGCAR 输出目录
     - ``outputs/``
   * - ``DEEPAW_SECRET_KEY``
     - JWT 签名密钥
     - 内置默认值
   * - ``BACKEND_PORT``
     - 后端端口
     - ``8080``
   * - ``FRONTEND_PORT``
     - 前端端口
     - ``3000``
   * - ``CONDA_ENV_NAME``
     - Conda 环境名称
     - ``maceedl``

快速启动（生产环境）
--------------------

.. code-block:: bash

   cd deepaw_integrated
   ./start_deepaw.sh start

启动脚本支持以下命令：

.. code-block:: bash

   ./start_deepaw.sh start     # 启动前后端服务
   ./start_deepaw.sh stop      # 停止服务
   ./start_deepaw.sh restart   # 重启服务
   ./start_deepaw.sh status    # 查看运行状态
   ./start_deepaw.sh logs      # 查看日志

自定义启动示例：

.. code-block:: bash

   DEEPAW_GPUS="0,1" \
   DEEPAW_DB_PATH=/path/to/custom.db \
   BACKEND_PORT=9000 \
   ./start_deepaw.sh start

手动启动（开发环境）
--------------------

**终端 1 — 后端（支持热重载）：**

.. code-block:: bash

   cd deepaw_integrated/backend
   python -m uvicorn main_simple:app --host 0.0.0.0 --port 8080 --reload

**终端 2 — 前端开发服务器：**

.. code-block:: bash

   cd deepaw_integrated/frontend
   npm run dev -- --host 0.0.0.0 --port 3000

前端生产构建
^^^^^^^^^^^^

.. code-block:: bash

   cd deepaw_integrated/frontend
   npm run build   # 输出到 dist/

远程访问
--------

通过 SSH 隧道从本地访问远程服务器上的 DeePAW：

.. code-block:: bash

   # 基本隧道
   ssh -N -L 3000:localhost:3000 -L 8080:localhost:8080 user@server

   # 或使用项目提供的脚本
   ./scripts/connect_remote.sh              # 基本隧道
   ./scripts/connect_remote_persistent.sh   # 自动重连隧道

访问地址：

- 前端界面：http://localhost:3000
- API 文档：http://localhost:8080/api/docs

验证部署
--------

.. code-block:: bash

   # 健康检查
   curl http://localhost:8080/health

   # GPU 状态
   curl http://localhost:8080/api/tasks/system/status

   # 测试推理流程（需要 GPU）
   cd deepaw_integrated
   python test_model_inference.py
