Prediction Performance
======================

Generalization Capability
--------------------------

Although trained exclusively on three-dimensional bulk crystals from the MP database, DeePAW demonstrates remarkable zero-shot generalization capability:

**3D Crystals**

- Good predictive performance on unseen three-dimensional perfect crystals outside the MP database
- Capable of handling crystal structures containing point defects (vacancies, interstitial atoms, and substitutional atoms)
- Successfully applied to large supercells containing 154 atoms per unit cell (e.g., V4C6B144)

**Low-Dimensional Materials**

- Two-dimensional materials: monolayer structures (e.g., CsF monolayer)
- One-dimensional materials: nanotube structures (e.g., carbon nanotubes)

**Application Scenarios**

- Catalysis research: analysis of surface oxygen evolution reaction (OER) pathways (e.g., Na-doped RuO2)
- Ferroelectric materials: polarization charge density analysis of orthorhombic-phase HfO2
- Interstitial site discovery: prediction of energetically favorable interstitial occupation sites based on charge density

Supported Material Types
------------------------

.. list-table::
   :header-rows: 1

   * - Material Type
     - Support Level
     - Notes
   * - Oxides
     - Full support
     - Abundantly represented in the training set
   * - Metals and Alloys
     - Full support
     - Covers a wide range of metallic elements
   * - Semiconductors
     - Full support
     - Includes Group IV, III-V, and related compounds
   * - 2D Materials
     - Zero-shot generalization
     - Not present in training set but predictable
   * - 1D Materials
     - Zero-shot generalization
     - Nanotube and related structures
   * - Defect Structures
     - Zero-shot generalization
     - Vacancy, interstitial, and substitutional defects
   * - Molecular Structures
     - Partial support
     - Requires periodic boundary conditions

Known Limitations
-----------------

- The coverage of training data is limited by the availability of KSDFT calculations in the MP database
- Predictive accuracy may degrade for elemental combinations that are underrepresented in the training set
- Molecular structures require the manual imposition of periodic boundary conditions
- For certain elements, inconsistent POTCAR usage within the dataset may cause errors in the total electron count during inference; fine-tuning on a case-by-case basis may be necessary
