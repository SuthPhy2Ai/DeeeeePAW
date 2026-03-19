API Reference
=============

Authentication
--------------

.. list-table::
   :header-rows: 1
   :widths: 35 10 10 45

   * - Endpoint
     - Method
     - Auth
     - Description
   * - ``/api/auth/register-with-code``
     - POST
     - No
     - Register a new user (invitation code required)
   * - ``/api/auth/login``
     - POST
     - No
     - User login, returns JWT token
   * - ``/api/auth/profile``
     - GET
     - Yes
     - Retrieve current user information
   * - ``/api/auth/send-reset-code``
     - POST
     - No
     - Send password reset verification code
   * - ``/api/auth/reset-password``
     - POST
     - No
     - Reset password using verification code

POST /api/auth/register-with-code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Request body:

.. code-block:: json

   {
     "username": "your_username",
     "password": "your_password",
     "email": "your@email.com",
     "invitation_code": "deepawdeepaw"
   }

POST /api/auth/login
^^^^^^^^^^^^^^^^^^^^

Request body:

.. code-block:: json

   {"username": "demo_user", "password": "Demo@2026"}

Response:

.. code-block:: json

   {
     "success": true,
     "data": {
       "access_token": "eyJ...",
       "token_type": "bearer",
       "expires_in": 86400
     }
   }

POST /api/auth/send-reset-code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Request body:

.. code-block:: json

   {"email": "user@example.com"}

POST /api/auth/reset-password
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Request body:

.. code-block:: json

   {
     "email": "user@example.com",
     "code": "123456",
     "new_password": "new_secure_password"
   }

File Upload
-----------

.. list-table::
   :header-rows: 1
   :widths: 35 10 10 45

   * - Endpoint
     - Method
     - Auth
     - Description
   * - ``/api/files/supported-formats``
     - GET
     - No
     - Query supported file formats
   * - ``/api/files/upload-structures``
     - POST
     - Yes
     - Upload and convert structure files
   * - ``/api/files/upload``
     - POST
     - Yes
     - Upload a .db file (legacy interface)

POST /api/files/upload-structures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Upload a structure file and automatically convert it to an ASE database.

Parameters (multipart/form-data):

.. list-table::
   :header-rows: 1

   * - Parameter
     - Type
     - Required
     - Description
   * - ``file``
     - File
     - Yes
     - Structure file (CIF, VASP, XYZ, etc.)
   * - ``nx``
     - int
     - Yes
     - Number of grid points in the X direction
   * - ``ny``
     - int
     - Yes
     - Number of grid points in the Y direction
   * - ``nz``
     - int
     - Yes
     - Number of grid points in the Z direction

Supported single-file formats: CIF, VASP (.vasp/.poscar/.contcar), XYZ, PDB, MOL, SDF, JSON, TRAJ, DB

Supported archive formats: ZIP, TAR, TAR.GZ / TGZ

Example:

.. code-block:: bash

   curl -X POST http://localhost:8080/api/files/upload-structures \
     -H "Authorization: Bearer $TOKEN" \
     -F "file=@structure.cif" \
     -F "nx=56" -F "ny=56" -F "nz=80"

Response:

.. code-block:: json

   {
     "success": true,
     "message": "Successfully converted 1 structures",
     "db_path": "/path/to/user_hash_ts_structure.db",
     "filename": "user_hash_ts_structure.db",
     "statistics": {
       "total_structures": 1,
       "success_count": 1,
       "failed_count": 0,
       "grid_size": [56, 56, 80]
     }
   }

.. note::

   Each upload generates a unique database filename with a timestamp to prevent data conflicts caused by overwriting files with the same name.

Prediction Tasks
----------------

.. list-table::
   :header-rows: 1
   :widths: 40 10 10 40

   * - Endpoint
     - Method
     - Auth
     - Description
   * - ``/api/predictions/batch``
     - POST
     - Yes
     - Submit a batch prediction job
   * - ``/api/predictions/batch/{batch_id}``
     - GET
     - Yes
     - Query batch status
   * - ``/api/predictions/result/{task_id}``
     - GET
     - Yes
     - Retrieve results in JSON format
   * - ``/api/predictions/download/{task_id}``
     - GET
     - Yes
     - Download CHGCAR file
   * - ``/api/predictions/slice/{task_id}``
     - GET
     - Yes
     - Retrieve 2D slice data

POST /api/predictions/batch
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Request body:

.. code-block:: json

   {
     "start_id": 1,
     "end_id": 10,
     "db_path": "/path/to/database.db"
   }

``db_path`` is optional; if omitted, the system default database is used.

Response:

.. code-block:: json

   {
     "success": true,
     "batch_id": "batch_abc123",
     "task_ids": ["task_batch_abc123_1", "..."],
     "total_tasks": 10
   }

GET /api/predictions/batch/{batch_id}
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Response:

.. code-block:: json

   {
     "batch_id": "batch_abc123",
     "total": 10,
     "completed": 7,
     "failed": 0,
     "processing": 2,
     "pending": 1,
     "progress": 70.0,
     "status": "processing",
     "tasks": [
       {"task_id": "task_batch_abc123_1", "structure_id": 1, "status": "completed"}
     ]
   }

GET /api/predictions/result/{task_id}
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Response:

.. code-block:: json

   {
     "success": true,
     "id": "task_batch_abc123_1",
     "structureId": 1,
     "gridDimensions": [56, 56, 80],
     "densityArray": [0.123, 0.456, "..."],
     "minValue": 0.001,
     "maxValue": 2.5,
     "atomsInfo": {
       "formula": "Mg2O2",
       "natoms": 4,
       "cell": [["..."]],
       "positions": [["..."]],
       "numbers": [12, 12, 8, 8]
     }
   }

``gridDimensions`` is determined by the nx/ny/nz values stored in the database; different structures may return different grid sizes.

GET /api/predictions/slice/{task_id}
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Query parameters:

- ``h`` / ``k`` / ``l`` (int): Miller indices, default (1,0,0)
- ``distance`` (float): Distance along the normal direction, default 0.0

User Management
---------------

.. list-table::
   :header-rows: 1
   :widths: 35 10 10 45

   * - Endpoint
     - Method
     - Auth
     - Description
   * - ``/api/user/files``
     - GET
     - Yes
     - Retrieve the list of files uploaded by the user
   * - ``/api/user/predictions``
     - GET
     - Yes
     - Retrieve user prediction history
   * - ``/api/database/parse``
     - POST
     - Yes
     - Parse an uploaded database file
   * - ``/api/database/load-demo``
     - GET
     - No
     - Load the demo database

System Status
-------------

.. list-table::
   :header-rows: 1
   :widths: 35 10 10 45

   * - Endpoint
     - Method
     - Auth
     - Description
   * - ``/api/tasks/system/status``
     - GET
     - No
     - GPU status and task statistics
   * - ``/health``
     - GET
     - No
     - Health check
   * - ``/api/docs``
     - GET
     - No
     - Swagger interactive documentation
   * - ``/api/redoc``
     - GET
     - No
     - ReDoc documentation

GET /api/tasks/system/status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Response:

.. code-block:: json

   {
     "success": true,
     "data": {
       "gpu_status": [
         {
           "id": 1,
           "name": "NVIDIA GeForce RTX 4090",
           "load": 0,
           "memoryUsed": 13605,
           "memoryTotal": 24564,
           "status": "idle",
           "temperature": 33
         }
       ],
       "active_tasks": 0,
       "completed_tasks": 2,
       "failed_tasks": 0,
       "queue_size": 0
     }
   }

HTTP Status Codes
-----------------

.. list-table::
   :header-rows: 1

   * - Status Code
     - Meaning
     - Action
   * - 200
     - Success
     - Handle normally
   * - 400
     - Bad request
     - Check request parameters
   * - 401
     - Unauthorized
     - Check if token is valid
   * - 404
     - Not found
     - Check if ID is correct
   * - 422
     - Validation error
     - Check parameter format (e.g. missing required nx/ny/nz)
   * - 500
     - Server error
     - Check backend logs
   * - 503
     - Service unavailable
     - ML component not loaded or converter unavailable
