Frequently Asked Questions
==========================

How to choose grid dimensions nx/ny/nz?
---------------------------------------

The grid dimensions nx/ny/nz should be determined based on the k-point density used in your first-principles calculation. Refer to the relevant VASP documentation for guidance on selecting appropriate grid dimensions.

Larger grids produce larger CHGCAR files and consume more GPU VRAM.

Are nx/ny/nz required when uploading files?
--------------------------------------------

Yes. The ``/api/files/upload-structures`` endpoint requires ``nx``, ``ny``, and ``nz`` to be specified explicitly.
No default values are provided, in order to prevent users from inadvertently using an unsuitable grid size.

If you upload a ``.db`` file directly (``/api/files/upload``), the grid settings already stored in the database are used.

How to troubleshoot failed predictions?
----------------------------------------

1. Query the batch status to identify which tasks have failed
2. Inspect the backend log: ``tail -f /tmp/deepaw_backend.log``
3. Check GPU status: ``curl http://localhost:8080/api/tasks/system/status``

Are molecular structures supported?
-------------------------------------

Yes. When using the local CLI deployment, periodic boundary conditions must be disabled. When using the online version (deepaw.tech), setting periodic boundary conditions is not supported by default.

How to visualize CHGCAR files?
--------------------------------

- **VESTA** (free): open the CHGCAR file directly
- **Ovito**: supports isosurface rendering
- **Web Frontend**: built-in Plotly 3D isosurface visualization
- **Python**: plot manually using ASE + Plotly

What to do if GPU VRAM is insufficient?
-----------------------------------------

- Reduce the grid dimensions (e.g., from 64³ to 48³)
- Reduce the number of GPUs used simultaneously: ``export DEEPAW_GPUS="1,2"``
- Check whether other processes are consuming VRAM: ``nvidia-smi``

What is the difference between the two upload methods?
-------------------------------------------------------

.. list-table::
   :header-rows: 1

   * - Feature
     - upload-structures
     - upload
   * - Supported formats
     - 15 formats
     - .db only
   * - Format conversion
     - Automatic
     - Not required
   * - Grid dimensions
     - Required parameter
     - Uses existing database settings
   * - Archive
     - Supported
     - Not supported
