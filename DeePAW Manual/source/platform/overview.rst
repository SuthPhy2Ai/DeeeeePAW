Platform Overview
=================

DeePAW is an online inference service platform for the DeePAW method, offering both a web interface and a RESTful API. It is designed to provide materials science researchers with efficient, high-throughput charge density calculation services.

Core Features
-------------

- **Batch charge density prediction**: Predicts three-dimensional charge density distributions from atomic structure files
- **Multi-format file support**: Supports 15 structure file formats including CIF, VASP, XYZ, and PDB
- **Multi-GPU parallel scheduling**: Built-in priority queue and GPU task scheduler supporting concurrent multi-task execution
- **RESTful API**: Comprehensive programmatic access interface for seamless integration into automated workflows
- **CHGCAR output**: VASP-compatible format, directly visualizable with tools such as VESTA and Ovito
- **Real-time progress tracking**: Live task status updates delivered via WebSocket
- **Web frontend**: React-based interactive interface with 3D isosurface visualization
- **Model warm-start**: GPU model caching mechanism that keeps the model resident in VRAM after the first inference, eliminating repeated loading overhead for subsequent tasks

Technology Stack
----------------

- **Frontend**: React 19 + TypeScript + Vite + Plotly.js
- **Backend**: FastAPI + Uvicorn (ASGI)
- **Inference**: PyTorch + E3NN + ASE
- **Data format**: Multiple formats -> ASE Database -> CHGCAR (VASP)

System Architecture
-------------------

.. code-block:: text

   Browser / Python Client
     -> React Frontend (port 3000)
     -> Vite proxy /api/*
     -> FastAPI Backend (port 8080)
     -> GPU task queue + scheduler
     -> DeePAW inference engine
     -> CHGCAR file output
     -> Frontend 3D visualization / client download

GPU Task Scheduling
^^^^^^^^^^^^^^^^^^^^

- One worker thread per GPU, with exclusive access enforced via ``threading.Lock``
- Tasks are processed in order of a priority queue (PriorityQueue)
- Model caching: the first task loads the model into GPU VRAM (~5-10 s); subsequent tasks reuse the cached instance (<0.1 s overhead)
- One model instance cached per GPU, occupying approximately 2-4 GB of VRAM

System Requirements
-------------------

Server Side
^^^^^^^^^^^

- Python 3.10+
- CUDA 11.8+ / 12.x
- GPU: 8 GB+ VRAM (16 GB+ recommended)
- Disk: approximately 5-10 MB per CHGCAR file
- Memory: 16 GB+ (32 GB+ recommended)

Client Side
^^^^^^^^^^^

- Python 3.7+ (only the ``requests`` library required)
- Or any programming language with HTTP request support
- No GPU requirement
