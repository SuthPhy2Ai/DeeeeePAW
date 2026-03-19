API 参考
========

认证相关
--------

.. list-table::
   :header-rows: 1
   :widths: 35 10 10 45

   * - 端点
     - 方法
     - 认证
     - 描述
   * - ``/api/auth/register-with-code``
     - POST
     - 否
     - 注册新用户（需邀请码）
   * - ``/api/auth/login``
     - POST
     - 否
     - 用户登录，返回 JWT token
   * - ``/api/auth/profile``
     - GET
     - 是
     - 获取当前用户信息
   * - ``/api/auth/send-reset-code``
     - POST
     - 否
     - 发送密码重置验证码
   * - ``/api/auth/reset-password``
     - POST
     - 否
     - 使用验证码重置密码

POST /api/auth/register-with-code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

请求体：

.. code-block:: json

   {
     "username": "your_username",
     "password": "your_password",
     "email": "your@email.com",
     "invitation_code": "deepawdeepaw"
   }

POST /api/auth/login
^^^^^^^^^^^^^^^^^^^^

请求体：

.. code-block:: json

   {"username": "demo_user", "password": "Demo@2026"}

响应：

.. code-block:: json

   {
     "success": true,
     "data": {
       "access_token": "eyJ...",
       "token_type": "bearer",
       "expires_in": 86400
     }
   }

POST /api/auth/send-reset-code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

请求体：

.. code-block:: json

   {"email": "user@example.com"}

POST /api/auth/reset-password
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

请求体：

.. code-block:: json

   {
     "email": "user@example.com",
     "code": "123456",
     "new_password": "new_secure_password"
   }

文件上传
--------

.. list-table::
   :header-rows: 1
   :widths: 35 10 10 45

   * - 端点
     - 方法
     - 认证
     - 描述
   * - ``/api/files/supported-formats``
     - GET
     - 否
     - 查询支持的文件格式
   * - ``/api/files/upload-structures``
     - POST
     - 是
     - 上传并转换结构文件
   * - ``/api/files/upload``
     - POST
     - 是
     - 上传 .db 文件（兼容旧接口）

POST /api/files/upload-structures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

上传结构文件并自动转换为 ASE 数据库。

参数（multipart/form-data）：

.. list-table::
   :header-rows: 1

   * - 参数
     - 类型
     - 必填
     - 说明
   * - ``file``
     - File
     - 是
     - 结构文件（CIF、VASP、XYZ 等）
   * - ``nx``
     - int
     - 是
     - X 方向网格数
   * - ``ny``
     - int
     - 是
     - Y 方向网格数
   * - ``nz``
     - int
     - 是
     - Z 方向网格数

支持的单文件格式：CIF、VASP（.vasp/.poscar/.contcar）、XYZ、PDB、MOL、SDF、JSON、TRAJ、DB

支持的压缩包格式：ZIP、TAR、TAR.GZ / TGZ

示例：

.. code-block:: bash

   curl -X POST http://localhost:8080/api/files/upload-structures \
     -H "Authorization: Bearer $TOKEN" \
     -F "file=@structure.cif" \
     -F "nx=56" -F "ny=56" -F "nz=80"

响应：

.. code-block:: json

   {
     "success": true,
     "message": "Successfully converted 1 structures",
     "db_path": "/path/to/user_hash_ts_structure.db",
     "filename": "user_hash_ts_structure.db",
     "statistics": {
       "total_structures": 1,
       "success_count": 1,
       "failed_count": 0,
       "grid_size": [56, 56, 80]
     }
   }

.. note::

   每次上传会生成带时间戳的唯一数据库文件名，避免同名文件覆盖导致数据混淆。

预测相关
--------

.. list-table::
   :header-rows: 1
   :widths: 40 10 10 40

   * - 端点
     - 方法
     - 认证
     - 描述
   * - ``/api/predictions/batch``
     - POST
     - 是
     - 提交批量预测
   * - ``/api/predictions/batch/{batch_id}``
     - GET
     - 是
     - 查询批次状态
   * - ``/api/predictions/result/{task_id}``
     - GET
     - 是
     - 获取 JSON 格式结果
   * - ``/api/predictions/download/{task_id}``
     - GET
     - 是
     - 下载 CHGCAR 文件
   * - ``/api/predictions/slice/{task_id}``
     - GET
     - 是
     - 获取 2D 切片数据

POST /api/predictions/batch
^^^^^^^^^^^^^^^^^^^^^^^^^^^

请求体：

.. code-block:: json

   {
     "start_id": 1,
     "end_id": 10,
     "db_path": "/path/to/database.db"
   }

``db_path`` 可选，不传则使用系统默认数据库。

响应：

.. code-block:: json

   {
     "success": true,
     "batch_id": "batch_abc123",
     "task_ids": ["task_batch_abc123_1", "..."],
     "total_tasks": 10
   }

GET /api/predictions/batch/{batch_id}
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

响应：

.. code-block:: json

   {
     "batch_id": "batch_abc123",
     "total": 10,
     "completed": 7,
     "failed": 0,
     "processing": 2,
     "pending": 1,
     "progress": 70.0,
     "status": "processing",
     "tasks": [
       {"task_id": "task_batch_abc123_1", "structure_id": 1, "status": "completed"}
     ]
   }

GET /api/predictions/result/{task_id}
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

响应：

.. code-block:: json

   {
     "success": true,
     "id": "task_batch_abc123_1",
     "structureId": 1,
     "gridDimensions": [56, 56, 80],
     "densityArray": [0.123, 0.456, "..."],
     "minValue": 0.001,
     "maxValue": 2.5,
     "atomsInfo": {
       "formula": "Mg2O2",
       "natoms": 4,
       "cell": [["..."]],
       "positions": [["..."]],
       "numbers": [12, 12, 8, 8]
     }
   }

``gridDimensions`` 由数据库中存储的 nx/ny/nz 决定，不同结构可能返回不同网格尺寸。

GET /api/predictions/slice/{task_id}
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

查询参数：

- ``h`` / ``k`` / ``l`` (int): Miller 指数，默认 (1,0,0)
- ``distance`` (float): 沿法线方向的距离，默认 0.0

用户管理
--------

.. list-table::
   :header-rows: 1
   :widths: 35 10 10 45

   * - 端点
     - 方法
     - 认证
     - 描述
   * - ``/api/user/files``
     - GET
     - 是
     - 获取用户上传文件列表
   * - ``/api/user/predictions``
     - GET
     - 是
     - 获取用户预测历史
   * - ``/api/database/parse``
     - POST
     - 是
     - 解析上传的数据库文件
   * - ``/api/database/load-demo``
     - GET
     - 否
     - 加载演示数据库

系统相关
--------

.. list-table::
   :header-rows: 1
   :widths: 35 10 10 45

   * - 端点
     - 方法
     - 认证
     - 描述
   * - ``/api/tasks/system/status``
     - GET
     - 否
     - GPU 状态和任务统计
   * - ``/health``
     - GET
     - 否
     - 健康检查
   * - ``/api/docs``
     - GET
     - 否
     - Swagger 交互文档
   * - ``/api/redoc``
     - GET
     - 否
     - ReDoc 文档

GET /api/tasks/system/status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

响应：

.. code-block:: json

   {
     "success": true,
     "data": {
       "gpu_status": [
         {
           "id": 1,
           "name": "NVIDIA GeForce RTX 4090",
           "load": 0,
           "memoryUsed": 13605,
           "memoryTotal": 24564,
           "status": "idle",
           "temperature": 33
         }
       ],
       "active_tasks": 0,
       "completed_tasks": 2,
       "failed_tasks": 0,
       "queue_size": 0
     }
   }

HTTP 状态码
-----------

.. list-table::
   :header-rows: 1

   * - 状态码
     - 含义
     - 处理方式
   * - 200
     - 成功
     - 正常处理
   * - 400
     - 请求错误
     - 检查请求参数
   * - 401
     - 未认证
     - 检查 token 是否有效
   * - 404
     - 资源不存在
     - 检查 ID 是否正确
   * - 422
     - 参数验证失败
     - 检查参数格式（如缺少必填的 nx/ny/nz）
   * - 500
     - 服务器错误
     - 查看后端日志
   * - 503
     - 服务不可用
     - ML 组件未加载或转换器不可用
