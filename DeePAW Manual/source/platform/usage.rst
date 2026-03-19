Usage Guide
===========

Authentication
--------------

All API requests (except login, register, and health check) require a JWT token in the request header:

.. code-block:: text

   Authorization: Bearer <your_token>

Tokens are valid for 24 hours.

Register Account
^^^^^^^^^^^^^^^^

Register using an invitation code:

.. code-block:: bash

   curl -X POST http://localhost:8080/api/auth/register-with-code \
     -H 'Content-Type: application/json' \
     -d '{
       "username": "your_username",
       "password": "your_password",
       "email": "your@email.com",
       "invitation_code": "deepawdeepaw"
     }'

Login and Obtain Token
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   curl -X POST http://localhost:8080/api/auth/login \
     -H 'Content-Type: application/json' \
     -d '{"username":"your_username","password":"your_password"}'

``data.access_token`` in the response is the JWT token required for subsequent requests.

Complete Workflow
-----------------

The typical workflow is: upload structure file → submit prediction → poll status → download results.

Step 1: Upload Structure Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Supports CIF, VASP (POSCAR/CONTCAR), XYZ, PDB, MOL, SDF, JSON, TRAJ, DB formats,
as well as ZIP / TAR / TAR.GZ archives.

.. code-block:: bash

   curl -X POST http://localhost:8080/api/files/upload-structures \
     -H "Authorization: Bearer $TOKEN" \
     -F "file=@structure.cif" \
     -F "nx=56" -F "ny=56" -F "nz=80"

.. important::

   ``nx``, ``ny``, ``nz`` are required parameters that specify the three-dimensional grid dimensions
   for charge density prediction. Grid size directly affects prediction accuracy and computation time;
   choose appropriate values based on the actual structure.

Grid Size Reference:

.. list-table::
   :header-rows: 1

   * - Grid Size
     - Accuracy
     - Recommended Use
   * - 32\ :sup:`3`
     - Low
     - Quick test
   * - 48\ :sup:`3`
     - Medium
     - General use
   * - 56\ :sup:`3`
     - High
     - High precision
   * - 64\ :sup:`3`
     - Very High
     - Publication quality

Step 2: Submit Batch Prediction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   curl -X POST http://localhost:8080/api/predictions/batch \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"start_id":1,"end_id":5,"db_path":"db_path returned from upload"}'

Step 3: Check Progress
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   curl http://localhost:8080/api/predictions/batch/{batch_id} \
     -H "Authorization: Bearer $TOKEN"

Batch status values:

- ``processing``: Job in progress
- ``completed``: All tasks finished
- ``failed``: All tasks failed

Step 4: Download Results
^^^^^^^^^^^^^^^^^^^^^^^^

**Download CHGCAR file:**

.. code-block:: bash

   curl -o result.CHGCAR \
     http://localhost:8080/api/predictions/download/{task_id} \
     -H "Authorization: Bearer $TOKEN"

**Retrieve results in JSON format:**

.. code-block:: bash

   curl http://localhost:8080/api/predictions/result/{task_id} \
     -H "Authorization: Bearer $TOKEN"

The JSON response contains ``gridDimensions`` (grid dimensions) and ``densityArray`` (flattened 3D density array).

Python Client
-------------

.. code-block:: python

   import requests, time

   BASE = "http://localhost:8080"

   # Login
   r = requests.post(f"{BASE}/api/auth/login",
                     json={"username": "demo_user", "password": "Demo@2026"})
   token = r.json()["data"]["access_token"]
   headers = {"Authorization": f"Bearer {token}"}

   # Upload structure file (nx/ny/nz required)
   with open("structure.cif", "rb") as f:
       r = requests.post(f"{BASE}/api/files/upload-structures",
                         headers=headers,
                         files={"file": f},
                         data={"nx": 56, "ny": 56, "nz": 80})
   db_path = r.json()["db_path"]

   # Submit prediction
   r = requests.post(f"{BASE}/api/predictions/batch",
                     headers=headers,
                     json={"start_id": 1, "end_id": 1, "db_path": db_path})
   batch_id = r.json()["batch_id"]

   # Wait for completion
   while True:
       r = requests.get(f"{BASE}/api/predictions/batch/{batch_id}",
                        headers=headers)
       status = r.json()
       print(f"Progress: {status['progress']:.0f}%")
       if status["status"] in ("completed", "failed"):
           break
       time.sleep(2)

   # Download CHGCAR
   task_id = status["tasks"][0]["task_id"]
   r = requests.get(f"{BASE}/api/predictions/download/{task_id}",
                    headers=headers)
   with open("result.CHGCAR", "wb") as f:
       f.write(r.content)

Visualize Results
-----------------

**VESTA (recommended):**

.. code-block:: bash

   vesta result.CHGCAR

**Python + ASE verification:**

.. code-block:: python

   from ase.calculators.vasp import VaspChargeDensity
   import numpy as np

   chg = VaspChargeDensity("result.CHGCAR")
   density = chg.chg[0]
   atoms = chg.atoms[0]

   print(f"Grid shape: {density.shape}")
   print(f"Density range: {density.min():.3f} ~ {density.max():.3f}")
   print(f"Chemical formula: {atoms.get_chemical_formula()}")
