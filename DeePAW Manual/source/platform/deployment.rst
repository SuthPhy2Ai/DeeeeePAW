Local CLI Deployment
====================

DeePAW provides a containerized local CLI deployment, running encrypted neural network model inference via Podman/Docker containers.

Requirements
------------

- Linux x86_64
- NVIDIA GPU (CUDA support)
- Podman or Docker
- NVIDIA driver

Quick Start
-----------

**1. Load the container image (first-time setup)**

.. code-block:: bash

   # Check whether the image is already loaded
   podman images | grep deepaw

   # Load from tarball
   podman load -i deepaw_dist_v1_cpp/deepaw-cppv1.tar.gz

**2. Start the container**

.. code-block:: bash

   # Use the default data directory
   ./start.sh

   # Specify a custom data directory
   ./start.sh /path/to/your/data

The ``start.sh`` script automatically performs the following:

- Detects the NVIDIA driver version
- Mounts GPU devices and libraries
- Sets the required environment variables
- Mounts data and output directories

**3. Run inference**

Execute inside the container:

.. code-block:: bash

   # Use built-in test data
   python predict_chgcar.py --db tests/hfo2.db --id 1 --device cuda

   # Use mounted custom data
   python predict_chgcar.py --db /data/your_database.db --id 1 --device cuda

   # Specify an output path
   python predict_chgcar.py --db /data/your_database.db --id 1 --device cuda --output /output/CHGCAR_result

   # Custom grid density
   python predict_chgcar.py --db /data/your_database.db --id 1 --device cuda --grid 60 60 60

After exiting the container, output files are located in the ``output/`` directory on the host.

Important Notes
---------------

**CUDA only**

The decryption logic for the encrypted models is compiled into the C++ engine and can only be initialized on a CUDA device. Using ``--device cpu`` will cause silent model initialization failure.

**GPU mounting**

On some systems (e.g., Rocky Linux 9.2), CDI mode (``--device nvidia.com/gpu=all``) may not work correctly. ``start.sh`` resolves this by manually mounting ``/dev/nvidia*`` devices and the host NVIDIA libraries.

Container Structure
-------------------

::

   /app/
   ├── predict_chgcar.py          # Main inference script
   ├── deepaw/
   │   ├── __init__.py            # Python API
   │   ├── deepaw_cpp.*.so        # pybind11 C++ bindings
   │   ├── libdeepaw_core.so      # C++ core library (contains decryption key)
   │   └── data/                  # Graph construction utilities
   ├── models/
   │   ├── f_nonlocal.enc         # Encrypted GNN model
   │   └── f_local.enc            # Encrypted KAN correction model
   └── tests/hfo2.db              # Built-in test data

Manual Run
----------

If ``start.sh`` does not suit your environment:

.. code-block:: bash

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

Troubleshooting
---------------

.. list-table::
   :header-rows: 1

   * - Issue
     - Cause
     - Solution
   * - "Models not initialized"
     - Using ``--device cpu``
     - Switch to ``--device cuda``
   * - "failed to stat CDI host device"
     - CDI mode unavailable
     - Use ``start.sh`` (handled manually)
   * - ``ModuleNotFoundError: deepaw_cpp``
     - Missing environment variables
     - Use ``start.sh`` (sets automatically)
   * - ``libtorch.so: cannot open``
     - LD_LIBRARY_PATH not set
     - Use ``start.sh`` (sets automatically)
   * - nvidia-smi unavailable inside container
     - NVIDIA libraries not mounted
     - Use ``start.sh`` (mounts automatically)
   * - ``.so`` file not found
     - Driver version mismatch
     - ``start.sh`` detects driver version automatically
