Scientific Background
=====================

Electron Density and Density Functional Theory
----------------------------------------------

The electron density is one of the most fundamental physical quantities in condensed matter physics and materials science. According to the Hohenberg-Kohn theorem, the ground-state electron density uniquely determines all ground-state properties of a many-electron system, including the total energy, forces, stress tensor, and related observables.

Traditionally, obtaining an accurate electron density distribution requires self-consistent field iterations within Kohn-Sham density functional theory (KSDFT). KSDFT obtains orbital wavefunctions by solving the single-particle Kohn-Sham equations, from which the electron density is constructed:

.. math::

   n(\mathbf{r}) = \sum_i f_i |\psi_i(\mathbf{r})|^2

where :math:`\psi_i` are the Kohn-Sham orbitals and :math:`f_i` are the corresponding occupation numbers. The computational complexity of this procedure scales steeply with system size, limiting its applicability to large-scale materials screening.

Orbital-Free Density Functional Theory
--------------------------------------

Orbital-free density functional theory (Orbital-Free DFT, OFDFT) provides an alternative route that bypasses the Kohn-Sham equations entirely. Within the OFDFT framework, ground-state materials properties are expressed directly through the variational minimization of an energy functional of the electron density, without explicitly solving for orbital wavefunctions.

E(3) Equivariance
-----------------

The electron density of a physical system must satisfy the symmetry constraints of the three-dimensional Euclidean group E(3), remaining equivariant under rotations, translations, and inversion:

- **Translation equivariance**: A global translation of the atomic structure results in an identical translation of the electron density field.
- **Rotation equivariance**: A rotation of the atomic structure induces the same rotation in the electron density field.
- **Inversion equivariance**: Spatial inversion of the atomic structure produces a corresponding inversion of the electron density field.

Embedding E(3) equivariance as a hard constraint into the neural network architecture significantly improves data efficiency and generalization, ensuring that predicted electron densities are physically consistent by construction.

Message Passing Neural Networks
-------------------------------

Message passing neural networks (MPNNs), a class of graph neural networks (GNNs), are a natural framework for processing atomic structure data. Within the MPNN formalism:

- Atoms are represented as nodes of a graph, carrying features such as element type.
- Chemical bonds or nearest-neighbor relationships between atoms are represented as edges of the graph.
- Through multiple rounds of message passing, each atom aggregates information from its neighbors, progressively building a representation of its local chemical environment.

This mechanism is naturally suited to describing interatomic interactions in materials and can handle crystal structures of arbitrary size and composition.
