更新日志
========

v2.2.0 (2026-03-19)
--------------------

Bug 修复
^^^^^^^^

- 修复 ``check_download_permission`` 中 ``uploaded_at`` 字符串与 ``datetime`` 直接相减导致 ``TypeError``
- 修复 ``/api/tasks/system/status`` 返回硬编码 0 的问题，现在返回真实的任务统计数据
- 修复批次状态在所有任务失败时仍显示 ``processing`` 的问题，新增 ``failed`` 状态
- 移除 ``execute_task`` 中每次推理都全表扫描数据库的 DEBUG 日志
- 修复 CHGCAR 写入时包含 Selective dynamics 导致 ASE 读取失败的问题

改进
^^^^

- ``/api/files/upload-structures`` 的 ``nx``、``ny``、``nz`` 参数改为必填，不再使用默认值 48
- 上传文件名增加时间戳，避免同名文件覆盖导致数据混淆
- ``gridDimensions`` 正确反映数据库中存储的 nx/ny/nz，不同结构可返回不同网格尺寸

新增功能
^^^^^^^^

- 密码重置功能（``/api/auth/send-reset-code``、``/api/auth/reset-password``）
- 用户文件管理端点（``/api/user/files``）
- 用户预测历史端点（``/api/user/predictions``）

v2.1.0 (2026-03-10)
--------------------

- 多格式文件上传功能，支持 15 种结构文件格式
- 自动格式识别和转换
- 压缩包自动解压
- 新增 ``/api/files/upload-structures`` 和 ``/api/files/supported-formats`` 端点

v2.0.0 (2026-03-07)
--------------------

- 批量电荷密度预测
- 多 GPU 并行调度
- JWT 认证系统
- RESTful API
- WebSocket 实时更新
