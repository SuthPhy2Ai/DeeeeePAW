DeePAW Method
=============

Method Overview
---------------

DeePAW (Deep Augmented Way) is a machine learning method for predicting electron density functionals. Its name is inspired by the Projector Augmented-Wave (PAW) method. DeePAW employs an E(3)-equivariant graph neural network architecture based on the e3nn library, predicting electron densities through end-to-end automated representation learning.

Dual-Graph Message Passing Architecture
---------------------------------------

DeePAW adopts a Double Graph Message Passing Neural Network (Double Graph MPNN) architecture comprising two collaborating MPNNs and an output head:

**Atomic Representation**

The atomic representation module is responsible for learning atom-level representations. Initial edge embeddings are constructed using Gaussian basis functions (GBF):

.. math::

   e_{ij} = \exp\left(-\frac{(d_{ij} - \mu)^2}{2\sigma^2}\right)

where :math:`d_{ij}` is the distance between nodes i and j, and :math:`\mu` is uniformly distributed between 0 and 6 |angstrom|.

The message function constructs equivariant messages using Clebsch-Gordan coefficients and spherical harmonics; each atom aggregates messages from all neighbors before updating its node embedding. A dynamic rotation angle mechanism is introduced during node embedding updates, dynamically adjusting the directional information of equivariant features through the gating mechanism of e3nn.

.. |angstrom| unicode:: U+00C5

**Electronic Potential**

The electronic potential module operates at the level of grid points. Node embeddings from the atomic representation are fed into the electronic potential module, where grid points update their own embeddings by aggregating information from neighboring atomic nuclei. Shared weight vectors and interaction weight vectors are used during the embedding update to control the relative contributions of a node's own features and the incoming neighbor messages.

**Output Heads**

The output head comprises three modules:

- **GAT head**: Based on a Graph Attention Network (GAT), it extracts atom-level output quantities from the node embeddings of all layers of the atomic representation.
- **MLP head**: Generates a smoothly varying electron density profile from the node embeddings of all layers of the electronic potential module.
- **KAN head**: Based on a Kolmogorov-Arnold Network (KAN), it computes the residual electron density from the node embeddings of the final layer of the electronic potential module.

Charge Density Grid Construction
--------------------------------

DeePAW constructs the electron density grid following VASP's coarse-fine grid scheme. The grid density is determined according to the Nyquist-Shannon sampling theorem to ensure adequate sampling of the electron density field.

Users must specify the grid dimensions (nx, ny, nz) when using the platform. These three parameters determine:

- The sampling resolution of the charge density in three-dimensional space.
- The total number of probe points to be predicted (nx * ny * nz).
- The grid dimensions of the output CHGCAR file.

The Cartesian coordinates of grid points are obtained by transforming fractional coordinates with the unit cell matrix:

.. math::

   \mathbf{r}_{ijk} = \frac{i}{n_x} \mathbf{a} + \frac{j}{n_y} \mathbf{b} + \frac{k}{n_z} \mathbf{c}

where :math:`\mathbf{a}, \mathbf{b}, \mathbf{c}` are the unit cell basis vectors.

Training Strategy
-----------------

DeePAW training proceeds in two stages using the L1 loss function:

- **Stage 1**: The MLP head and GAT head are jointly trained, optimizing for electron density prediction.
- **Stage 2**: The MLP head is trained with a very small learning rate while the KAN head uses a larger learning rate, implementing an adaptive PAW scheme that captures the fine structure of the residual electron density.

Training data are sourced from the Materials Project (MP) database. Electron density labels are computed from KSDFT orbital wavefunctions using VASP.
