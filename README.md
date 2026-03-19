# DeePAW C++ Inference Engine - Containerized

Containerized DeePAW C++ inference engine with encrypted neural network models. This container resolves glibc/C library version dependencies and can run on different Linux hosts with NVIDIA GPUs.

## Quick Start

### 1. Load Container Image (First Time)

```bash
# Check if image exists
podman images | grep deepaw

# Load from tarball
podman load -i deepaw_dist_v1_cpp/deepaw-cppv1.tar.gz
```

### 2. Launch Container

```bash
# Run with default data directory
./start.sh

# Or specify custom data directory
./start.sh /path/to/your/data
```

The `start.sh` script automatically:
- Detects NVIDIA driver version
- Mounts GPU devices and libraries
- Sets required environment variables
- Mounts data and output directories

### 3. Run Inference

Inside the container:

```bash
# Built-in test data
python predict_chgcar.py --db tests/hfo2.db --id 1 --device cuda

# Custom data (mounted to /data)
python predict_chgcar.py --db /data/your_database.db --id 1 --device cuda

# Custom output path (/output maps to host output/ directory)
python predict_chgcar.py --db /data/your_database.db --id 1 --device cuda --output /output/CHGCAR_result

# Custom grid density
python predict_chgcar.py --db /data/your_database.db --id 1 --device cuda --grid 60 60 60
```

Output files are available in the `output/` directory on the host after exiting the container.

## Requirements

### Host System
- Linux x86_64
- NVIDIA GPU with CUDA support
- Podman or Docker
- NVIDIA driver (version auto-detected by start.sh)
- nvidia-container-toolkit (optional, for CDI mode)

### Container Specifications
- Base image: `nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04`
- Python: 3.12
- GLIBC: 2.35 (container), 2.34+ (host recommended)

## Important Notes

### CUDA Only
The encrypted models contain decryption logic compiled into the C++ engine that only initializes on CUDA devices. Using `--device cpu` will cause silent initialization failure.

### GPU Passthrough
On some systems (e.g., Rocky Linux 9.2), CDI mode (`--device nvidia.com/gpu=all`) may not work. The `start.sh` script handles this by manually mounting `/dev/nvidia*` devices and host NVIDIA libraries.

If driver upgrades cause issues, verify the version:
```bash
cat /sys/module/nvidia/version
# or
nvidia-smi | head -3
```

### Environment Variables
The following must be set inside the container:
```
PYTHONPATH=/app/deepaw
LD_LIBRARY_PATH=/app/deepaw:/usr/local/lib/python3.12/dist-packages/torch/lib:/usr/lib64
```
The `start.sh` script sets these automatically.

## Container Structure

```
/app/
├── predict_chgcar.py          # Main inference script
├── deepaw/
│   ├── __init__.py            # Python API (Model/SecureModel)
│   ├── deepaw_cpp.*.so        # pybind11 C++ bindings
│   ├── libdeepaw_core.so      # C++ core library (contains decryption key)
│   └── data/                  # Graph construction utilities
├── models/
│   ├── f_nonlocal.enc         # Encrypted GNN model (~20MB)
│   └── f_local.enc            # Encrypted KAN correction model (~300KB)
├── tests/hfo2.db              # Built-in test data
└── welcome.sh                 # Welcome screen
```

## Manual Execution (Without start.sh)

If `start.sh` is not suitable for your environment:

```bash
DRIVER_VER=$(cat /sys/module/nvidia/version)

podman run -it --rm \
    --security-opt=label=disable \
    --device /dev/nvidia0 \
    --device /dev/nvidiactl \
    --device /dev/nvidia-uvm \
    --device /dev/nvidia-uvm-tools \
    --device /dev/nvidia-modeset \
    -v /usr/lib64/libnvidia-ml.so.${DRIVER_VER}:/usr/lib64/libnvidia-ml.so.${DRIVER_VER}:ro \
    -v /usr/lib64/libcuda.so.${DRIVER_VER}:/usr/lib64/libcuda.so.${DRIVER_VER}:ro \
    -v /usr/lib64/libnvidia-ptxjitcompiler.so.${DRIVER_VER}:/usr/lib64/libnvidia-ptxjitcompiler.so.${DRIVER_VER}:ro \
    -e PYTHONPATH=/app/deepaw \
    -e LD_LIBRARY_PATH=/app/deepaw:/usr/local/lib/python3.12/dist-packages/torch/lib:/usr/lib64 \
    -v /path/to/your/data:/data \
    -v $(pwd)/output:/output \
    deepaw-cpp:v1 \
    bash
```

## Build Image (Development)

```bash
./build.sh
```

## Image Distribution

Export:
```bash
podman save deepaw-cpp:v1 | gzip > deepaw-cpp-v1.tar.gz
```

Import on another machine:
```bash
gunzip -c deepaw-cpp-v1.tar.gz | podman load
podman images | grep deepaw-cpp
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "Models not initialized" | Using `--device cpu` | Use `--device cuda` |
| "failed to stat CDI host device" | CDI mode unavailable | Use `start.sh` (handles manually) |
| `ModuleNotFoundError: deepaw_cpp` | Missing environment variables | Use `start.sh` (sets automatically) |
| `libtorch.so: cannot open` | LD_LIBRARY_PATH not set | Use `start.sh` (sets automatically) |
| nvidia-smi not available in container | NVIDIA libraries not mounted | Use `start.sh` (mounts automatically) |
| `.so` file not found | Driver version mismatch | `start.sh` auto-detects driver version |

## File Structure

```
.
├── start.sh               # One-click launch script (recommended)
├── build.sh               # Image build script
├── Containerfile          # GPU container definition
├── welcome.sh             # Container welcome screen
├── deepaw_dist_v1_cpp/    # Distribution package
│   └── deepaw-cppv1.tar.gz # Pre-built image tarball
├── output/                # Inference output directory
├── README.md              # This documentation
└── archive/               # Archived files (legacy scripts, logs)
```

## License

Please cite the source when using this code or model. C++ source code is available at https://zenodo.org/records/18311602
