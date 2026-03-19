DeePAW 方法
===========

方法概述
--------

DeePAW (Deep Augmented Way) 是一种面向 OFDFT 电子密度泛函和形成能预测的通用机器学习方法。其命名灵感来源于投影缀加波 (Projector Augmented-Wave, PAW) 方法。DeePAW 采用基于 e3nn 库的 E(3) 等变图神经网络架构，通过端到端的自动化表征学习，同时实现电子密度和形成能的预测。

双图消息传递架构
----------------

DeePAW 采用双图消息传递神经网络 (Double Graph MPNN) 架构，包含两个协同工作的 MPNN 和一个输出头:

**原子表示**

原子表示负责学习原子级别的表征。初始边嵌入通过高斯基函数 (Gaussian Basis Function, GBF) 构建:

.. math::

   e_{ij} = \exp\left(-\frac{(d_{ij} - \mu)^2}{2\sigma^2}\right)

其中 :math:`d_{ij}` 为节点 i 和 j 之间的距离，:math:`\mu` 在 0 到 6 |angstrom| 之间均匀分布。

消息函数利用 Clebsch-Gordan 系数和球谐函数构建等变消息，每个原子聚合来自所有邻居的消息后更新节点嵌入。节点嵌入的更新过程中引入了动态旋转角机制，通过 e3nn 的门控机制动态调整等变特征的方向信息。

.. |angstrom| unicode:: U+00C5

**电子势能**

电子势能模块在网格点级别工作。原子表示的节点嵌入被馈入电子势能模块，网格点通过聚合来自邻近原子核的信息来更新自身嵌入。嵌入更新过程中使用共享权重向量和交互权重向量来控制节点自身特征与邻居消息的相对贡献。

**输出头**

输出头包含三个模块:

- **GAT 头**: 基于图注意力网络 (Graph Attention Network)，从原子表示所有层的节点嵌入中提取形成能或任何原子级的输出任务
- **MLP 头**: 从电子势能模块所有层的节点嵌入中生成平滑变化的电子密度轮廓
- **KAN 头**: 基于 Kolmogorov-Arnold 网络，从电子势能模块最后一层的节点嵌入中计算残差电子密度

电荷密度网格构建
----------------

DeePAW 采用 VASP 的粗-细网格方案 (coarse-fine grid scheme) 构建电子密度网格。网格密度的确定遵循 Nyquist-Shannon 采样定理，确保对电子密度场的充分采样。

用户在使用平台时需要指定网格维度 (nx, ny, nz)，这三个参数决定了:

- 三维空间中电荷密度的采样分辨率
- 预测的总探针点数 (nx * ny * nz)
- 输出 CHGCAR 文件的网格尺寸

网格点的笛卡尔坐标通过分数坐标与晶胞矩阵的变换获得:

.. math::

   \mathbf{r}_{ijk} = \frac{i}{n_x} \mathbf{a} + \frac{j}{n_y} \mathbf{b} + \frac{k}{n_z} \mathbf{c}

其中 :math:`\mathbf{a}, \mathbf{b}, \mathbf{c}` 为晶胞基矢。

训练策略
--------

DeePAW 的训练分为两个阶段，使用 L1 损失函数:

- **第一阶段**: 联合训练 MLP 头和 GAT 头，同时优化电子密度和形成能
- **第二阶段**: MLP 头使用极小的学习率，KAN 头使用较大的学习率，进行 PAW 的自适应实现，捕获残差电子密度的精细结构

训练数据来自 Materials Project (MP) 数据库。电子密度标签由基于 VASP 的 KSDFT 轨道波函数计算得到。
