# DeeeeePAW

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://suthphy2ai.github.io/DeeeeePAW)
[![Zenodo](https://img.shields.io/badge/model%20weights-Zenodo-blue)](https://zenodo.org/records/18311602)
[![Platform](https://img.shields.io/badge/platform-Linux%20x86__64-lightgrey)]()
[![Python](https://img.shields.io/badge/python-3.12-blue)]()

> Neural network prediction of 3D electron charge density from crystal structures.

<p align="center">
  <img src="assets/gifs/deepaw-web-demo.gif" width="72%" alt="DeePAW web interface demo"/>
</p>

DeePAW predicts three-dimensional electron charge density directly from atomic structure using E(3)-equivariant dual-graph message passing. It is trained on PAW (Projector Augmented-Wave, plane-wave augmented-wave) charge density data from Materials Project bulk crystals, and generalizes zero-shot to 2D materials, 1D nanotubes, and defect structures. Output is a VASP-compatible CHGCAR file, ready for post-processing with VESTA, Ovito, Device Studio, or standard DFT toolchains.

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

<table>
<tr>
<td width="50%" align="center" valign="top">
<img src="https://raw.githubusercontent.com/SuthPhy2Ai/DeeeeePAW/main/DeePAW%20Manual/source/_static/20260319-180338.jpg" width="100%"/><br/>
<em>2D charge density slice along (hkl) plane</em>
</td>
<td width="50%" align="center" valign="top">
<img src="https://raw.githubusercontent.com/SuthPhy2Ai/DeeeeePAW/main/DeePAW%20Manual/source/_static/20260319-180345.jpg" width="100%"/><br/>
<em>Interactive 3D isosurface with unit cell boundary and lattice parameters</em>
</td>
</tr>
</table>

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

<img src="https://raw.githubusercontent.com/SuthPhy2Ai/DeeeeePAW/main/DeePAW%20Manual/source/_static/20260319-180247.png" width="100%"/>

*Launching the DeePAW C++ inference engine in the container*

#### Manual `podman run` (advanced)

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

---

## Method

DeePAW uses a **dual-graph message-passing** architecture:

- **Atomic Representation**: An E(3)-equivariant GNN (via [`e3nn`](https://e3nn.org)) builds atom-level embeddings encoding the local chemical environment, with rotational and translational equivariance enforced as a hard constraint.
- **Electronic Potential**: A second graph propagates atom embeddings to real-space probe grid points, from which an MLP head predicts the smooth electron density envelope.
- **KAN Correction**: A Kolmogorov-Arnold Network applies a local residual correction, recovering fine-grained charge features near nuclei that long-range message passing tends to smooth over.
- **Training**: Model weights are trained on VASP Kohn-Sham DFT charge densities from the [Materials Project](https://materialsproject.org/) database.

---

---

## Visualization

The output CHGCAR file is compatible with standard charge density tools:

| Tool | Notes |
|---|---|
| [VESTA](https://jp-minerals.org/vesta/en/) | Open CHGCAR directly for isosurface and slice rendering |
| [Ovito](https://www.ovito.org/) | Supports volumetric data import |
| [Device Studio](https://hzwtech.com/Help/index.html) | Integrated materials modeling platform; supports CHGCAR visualization |
| [Web frontend](https://deepaw.tech) | Built-in 3D isosurface + 2D slice viewer |
| [ASE](https://wiki.fysik.dtu.dk/ase/) | Scriptable analysis and CHGCAR I/O via Python |

---

## Documentation

Full documentation — API reference, input format guide, web frontend guide, and troubleshooting — is available at:

**[https://suthphy2ai.github.io/DeeeeePAW](https://suthphy2ai.github.io/DeeeeePAW)**

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
