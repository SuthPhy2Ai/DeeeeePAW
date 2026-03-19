# DeePAW

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://suthphy2ai.github.io/DeeeeePAW/)
[![Zenodo](https://img.shields.io/badge/model%20weights-Zenodo-blue)](https://zenodo.org/records/18311602)
[![Platform](https://img.shields.io/badge/platform-Linux%20x86__64-lightgrey)]()
[![Python](https://img.shields.io/badge/python-3.12-blue)]()

> Neural network prediction of 3D electron charge density from crystal structures — VASP-compatible CHGCAR output, no SCF loop required.

DeePAW predicts three-dimensional electron charge density directly from atomic structure using E(3)-equivariant dual-graph message passing. Trained on Materials Project bulk crystals, it generalizes zero-shot to 2D materials, 1D nanotubes, and defect structures. Output is a VASP-compatible CHGCAR file, ready for post-processing with VESTA, Ovito, or standard DFT toolchains.

---

## Requirements

**Local CLI only** — the web interface has no local requirements.

- Linux x86_64
- NVIDIA GPU with CUDA support (**CPU inference is not supported**)
- Podman ≥ 4.0 or Docker ≥ 20.10
- Python 3.12 (bundled inside the container — no host installation needed)

---

## Quick Start

### Option 1 — Web (no installation)

1. Request access at **[deepaw.tech](https://deepaw.tech)** — send an email to **thsu0407@gmail.com** to obtain an invitation code
2. Upload your structure file (CIF, VASP POSCAR, XYZ, PDB, ZIP/TAR, and 10 more formats)
3. Set the charge density grid dimensions (e.g. `nx=40 ny=40 nz=40`)
4. Submit the job — monitor real-time GPU status
5. Download the resulting **CHGCAR** from *My Files* (available for 3 days)

### Option 2 — Local CLI (Podman/Docker)

```bash
# 1. Load the pre-built container image
podman load -i deepaw-cppv1.tar.gz

# 2. Run inference (auto-detects GPU driver, mounts devices)
./start.sh --db your_structure.db --id 1 --device cuda

# 3. Output appears in ./output/ on the host
```

Custom grid and output path:

```bash
./start.sh --db your_structure.db --id 1 --device cuda --grid 56 56 56 --output ./results/CHGCAR
```

<details>
<summary>Manual <code>podman run</code> (advanced)</summary>

If `start.sh` does not fit your environment, you can mount GPU devices manually. Replace `525.60.13` with your actual driver version (`cat /sys/module/nvidia/version`):

```bash
DRIVER_VER=$(cat /sys/module/nvidia/version)

podman run --rm -it \
    --security-opt=label=disable \
    --device /dev/nvidia0 --device /dev/nvidiactl \
    --device /dev/nvidia-uvm --device /dev/nvidia-uvm-tools --device /dev/nvidia-modeset \
    -v /usr/lib64/libnvidia-ml.so.${DRIVER_VER}:/usr/lib64/libnvidia-ml.so.${DRIVER_VER}:ro \
    -v /usr/lib64/libcuda.so.${DRIVER_VER}:/usr/lib64/libcuda.so.${DRIVER_VER}:ro \
    -v /usr/lib64/libnvidia-ptxjitcompiler.so.${DRIVER_VER}:/usr/lib64/libnvidia-ptxjitcompiler.so.${DRIVER_VER}:ro \
    -e PYTHONPATH=/app/deepaw \
    -e LD_LIBRARY_PATH=/app/deepaw:/usr/local/lib/python3.12/dist-packages/torch/lib:/usr/lib64 \
    -v $(pwd)/data:/data -v $(pwd)/output:/output \
    deepaw-cpp:v1 \
    python predict_chgcar.py --db /data/your_structure.db --id 1 --device cuda
```
</details>

---

## Features

- Predicts 3D electron charge density (CHGCAR) from 15+ structure file formats
- E(3)-equivariant dual-graph MPNN backbone with KAN residual correction
- Zero-shot generalization to 2D/1D materials and defect structures
- Multi-GPU parallel scheduling with real-time WebSocket task status
- Interactive 3D isosurface and 2D slice visualization in the browser
- RESTful API for integration into automated high-throughput workflows
- Self-contained container deployment — no environment configuration beyond Podman/Docker

---

## Method

DeePAW uses a **dual-graph message-passing** architecture:

- **Atomic Representation**: An E(3)-equivariant GNN (via [`e3nn`](https://e3nn.org)) builds atom-level embeddings encoding the local chemical environment, with rotational and translational equivariance enforced as a hard constraint.
- **Electronic Potential**: A second graph propagates atom embeddings to real-space probe grid points, from which an MLP head predicts the smooth electron density envelope.
- **KAN Correction**: A Kolmogorov-Arnold Network applies a local residual correction, recovering fine-grained charge features near nuclei that long-range message passing tends to smooth over.
- **Training**: Model weights are trained on VASP Kohn-Sham DFT charge densities from the [Materials Project](https://materialsproject.org/) database.

---

## Supported Materials

| Material Type | Support | Notes |
|---|---|---|
| Oxides | Full | Core training domain |
| Metals & Alloys | Full | Wide elemental coverage |
| Semiconductors | Full | Group IV, III-V, etc. |
| 2D Materials | Zero-shot | e.g. CsF monolayer |
| 1D Materials | Zero-shot | e.g. carbon nanotubes |
| Defect Structures | Zero-shot | Vacancies, interstitials, substitutions |
| Molecular | Partial | Periodic boundary conditions required |

**Known limitations:**
- Training data coverage is bounded by the Materials Project database; accuracy may decrease for underrepresented element combinations
- Some elements may show electron count discrepancies due to POTCAR inconsistencies in the training dataset — per-case adjustment may be needed
- Molecular structures require manually imposed periodic boundary conditions

---

## Performance

| System | Grid | Probe points | Time (RTX 4090) |
|---|---|---|---|
| HfO₂ (built-in test) | 40×40×40 | 64,000 | ~27 s |

The model handles supercells up to 154 atoms per unit cell.

---

## Grid Size Guide

Choose `nx/ny/nz` based on your k-point density from the DFT calculation (refer to the VASP documentation). As a general reference:

| Grid | Density | Recommended Use |
|---|---|---|
| 32³ | Low | Quick tests |
| 48³ | Medium | General use |
| 56³ | High | High-precision studies |
| 64³ | Very high | Publication-quality results |

Larger grids increase CHGCAR file size and GPU memory usage proportionally.

---

## Visualization

The output CHGCAR file is compatible with standard charge density tools:

| Tool | Notes |
|---|---|
| [VESTA](https://jp-minerals.org/vesta/en/) | Open CHGCAR directly for isosurface and slice rendering |
| [Ovito](https://www.ovito.org/) | Supports volumetric data import |
| [Device Studio](https://iresearch.net.cn/DeviceStudio.html) | Integrated materials modeling platform; supports CHGCAR visualization |
| Web frontend | Built-in 3D isosurface + 2D slice viewer at [deepaw.tech](https://deepaw.tech) |
| Python / ASE | Scriptable analysis with `ase.io.vasp.VaspChargeDensity` |

```python
from ase.io.vasp import VaspChargeDensity

chg = VaspChargeDensity('CHGCAR')
density = chg.chg[0]          # numpy array, shape (nx, ny, nz)
atoms = chg.atoms[0]          # ASE Atoms object
print(density.shape, atoms.get_chemical_formula())
```

---

## Documentation

Full documentation — API reference, input format guide, web frontend guide, and troubleshooting — is available at:

**[https://suthphy2ai.github.io/DeeeeePAW/](https://suthphy2ai.github.io/DeeeeePAW/)**

---

## Model Weights

Pre-trained model weights are publicly available on Zenodo:

**[https://zenodo.org/records/18311602](https://zenodo.org/records/18311602)**

---

## Citation

If you use DeePAW in your research, please cite the Zenodo record for the model weights:

```bibtex
@misc{deepaw2025weights,
  title     = {{DeePAW}: Pre-trained model weights for 3D electron density prediction},
  author    = {DeePAW Team},
  year      = {2025},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.18311602},
  url       = {https://zenodo.org/records/18311602}
}
```

> A manuscript describing the method is in preparation. The citation will be updated with a paper DOI when available.
> For citation inquiries or collaboration, contact: **thsu0407@gmail.com**

---

## Acknowledgements

We gratefully acknowledge the following resources and projects that made DeePAW possible:

- **[Materials Project](https://materialsproject.org/)** — training data source; charge density labels computed from DFT calculations in the MP database
- **[VASP](https://www.vasp.at/)** — electronic structure calculations used to generate the training labels via Kohn-Sham DFT
- **[e3nn](https://e3nn.org/)** — E(3)-equivariant neural network library forming the backbone of the GNN architecture
- **[PyTorch](https://pytorch.org/)** — deep learning framework
- **[ASE (Atomic Simulation Environment)](https://wiki.fysik.dtu.dk/ase/)** — crystal structure handling, graph construction, and CHGCAR I/O
- **[Zenodo](https://zenodo.org/)** — open-access hosting of pre-trained model weights
- **[Kolmogorov-Arnold Networks (KAN)](https://github.com/KindXiaoming/pykan)** — residual correction module

---

## License

This project is licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

You are free to use, share, and adapt this work for any purpose, provided appropriate credit is given and the source is cited.
