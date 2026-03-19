使用指南
========

认证
----

所有 API 请求（除登录、注册、健康检查外）需要在 Header 中携带 JWT token：

.. code-block:: text

   Authorization: Bearer <your_token>

Token 有效期为 24 小时。

注册账户
^^^^^^^^

使用邀请码注册：

.. code-block:: bash

   curl -X POST http://localhost:8080/api/auth/register-with-code \
     -H 'Content-Type: application/json' \
     -d '{
       "username": "your_username",
       "password": "your_password",
       "email": "your@email.com",
       "invitation_code": "deepawdeepaw"
     }'

登录获取 Token
^^^^^^^^^^^^^^

.. code-block:: bash

   curl -X POST http://localhost:8080/api/auth/login \
     -H 'Content-Type: application/json' \
     -d '{"username":"your_username","password":"your_password"}'

响应中 ``data.access_token`` 即为后续请求所需的 JWT token。

完整工作流
----------

典型使用流程为：上传结构文件 → 提交预测 → 轮询状态 → 下载结果。

步骤 1：上传结构文件
^^^^^^^^^^^^^^^^^^^^

支持 CIF、VASP（POSCAR/CONTCAR）、XYZ、PDB、MOL、SDF、JSON、TRAJ、DB 等格式，
以及 ZIP / TAR / TAR.GZ 压缩包。

.. code-block:: bash

   curl -X POST http://localhost:8080/api/files/upload-structures \
     -H "Authorization: Bearer $TOKEN" \
     -F "file=@structure.cif" \
     -F "nx=56" -F "ny=56" -F "nz=80"

.. important::

   ``nx``、``ny``、``nz`` 为必填参数，用于指定电荷密度预测的三维网格维度。
   网格尺寸直接影响预测精度和计算时间，需根据实际结构合理选择。

网格尺寸参考：

.. list-table::
   :header-rows: 1

   * - 网格尺寸
     - 精度
     - 推荐用途
   * - 32³
     - 低
     - 快速测试
   * - 48³
     - 中
     - 一般使用
   * - 56³
     - 高
     - 高精度需求
   * - 64³
     - 很高
     - 发表级精度

步骤 2：提交批量预测
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   curl -X POST http://localhost:8080/api/predictions/batch \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"start_id":1,"end_id":5,"db_path":"上传返回的db_path"}'

步骤 3：查询进度
^^^^^^^^^^^^^^^^

.. code-block:: bash

   curl http://localhost:8080/api/predictions/batch/{batch_id} \
     -H "Authorization: Bearer $TOKEN"

批次状态值：

- ``processing``：任务进行中
- ``completed``：全部完成
- ``failed``：全部失败

步骤 4：下载结果
^^^^^^^^^^^^^^^^

**下载 CHGCAR 文件：**

.. code-block:: bash

   curl -o result.CHGCAR \
     http://localhost:8080/api/predictions/download/{task_id} \
     -H "Authorization: Bearer $TOKEN"

**获取 JSON 格式结果：**

.. code-block:: bash

   curl http://localhost:8080/api/predictions/result/{task_id} \
     -H "Authorization: Bearer $TOKEN"

JSON 响应包含 ``gridDimensions`` (网格维度) 和 ``densityArray`` (展平的三维密度数组)。

Python 客户端
-------------

.. code-block:: python

   import requests, time

   BASE = "http://localhost:8080"

   # 登录
   r = requests.post(f"{BASE}/api/auth/login",
                     json={"username": "demo_user", "password": "Demo@2026"})
   token = r.json()["data"]["access_token"]
   headers = {"Authorization": f"Bearer {token}"}

   # 上传结构文件（nx/ny/nz 必填）
   with open("structure.cif", "rb") as f:
       r = requests.post(f"{BASE}/api/files/upload-structures",
                         headers=headers,
                         files={"file": f},
                         data={"nx": 56, "ny": 56, "nz": 80})
   db_path = r.json()["db_path"]

   # 提交预测
   r = requests.post(f"{BASE}/api/predictions/batch",
                     headers=headers,
                     json={"start_id": 1, "end_id": 1, "db_path": db_path})
   batch_id = r.json()["batch_id"]

   # 等待完成
   while True:
       r = requests.get(f"{BASE}/api/predictions/batch/{batch_id}",
                        headers=headers)
       status = r.json()
       print(f"进度: {status['progress']:.0f}%")
       if status["status"] in ("completed", "failed"):
           break
       time.sleep(2)

   # 下载 CHGCAR
   task_id = status["tasks"][0]["task_id"]
   r = requests.get(f"{BASE}/api/predictions/download/{task_id}",
                    headers=headers)
   with open("result.CHGCAR", "wb") as f:
       f.write(r.content)

可视化结果
----------

**VESTA（推荐）：**

.. code-block:: bash

   vesta result.CHGCAR

**Python + ASE 验证：**

.. code-block:: python

   from ase.calculators.vasp import VaspChargeDensity
   import numpy as np

   chg = VaspChargeDensity("result.CHGCAR")
   density = chg.chg[0]
   atoms = chg.atoms[0]

   print(f"网格尺寸: {density.shape}")
   print(f"密度范围: {density.min():.3f} ~ {density.max():.3f}")
   print(f"化学式: {atoms.get_chemical_formula()}")
