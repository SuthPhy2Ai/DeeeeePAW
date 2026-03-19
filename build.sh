#!/bin/bash
# Build DeePAW C++ Inference Engine Podman Image

set -e

echo "========================================"
echo "Building DeePAW C++ Inference Image"
echo "========================================"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if distribution package exists
if [ ! -d "deepaw_dist_v1_cpp" ]; then
    echo "Error: deepaw_dist_v1_cpp directory not found"
    echo "Copying from parent directory..."
    cp -r ../deepaw_dist_v1_cpp .
fi

# Build image
echo "Building image with Podman..."
podman build -t deepaw-cpp:v1 -f Containerfile .

echo ""
echo "✓ Build complete!"
echo ""
echo "Image: deepaw-cpp:v1"
echo ""
echo "To run the container:"
echo "  ./run.sh"
echo ""
echo "To run with custom parameters:"
echo "  podman run --rm --gpus all deepaw-cpp:v1 python predict_chgcar.py --db tests/hfo2.db --id 1"
