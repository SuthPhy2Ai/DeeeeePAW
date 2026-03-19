Web Frontend
============

DeePAW provides an online web application that allows users to perform charge density predictions and visualization directly in the browser, without writing any code.

Access URL: **https://deepaw.tech**

The locally deployed version is accessible via ``http://localhost:3000`` (local) or remotely through an SSH tunnel.

Login and Registration
----------------------

First-time users must register an account. An invitation code is required during registration.

.. figure:: /_static/20260319-180321.jpg
   :width: 100%
   :alt: DeePAW Login Page

   Login page: DeePAW branding on the left, login/registration form on the right

- Enter your username, password, and email address
- Enter the invitation code (default: ``deepawdeepaw``)
- After successful registration, you will be redirected to the main interface automatically

Existing users can log in by entering their username and password directly. If you forget your password, it can be reset via email verification code.

Main Interface Layout
---------------------

After logging in, the main interface is displayed. The top navigation bar contains two view-switching buttons:

- **Predictions**: Prediction workspace (default view)
- **My Files**: File and history management

The currently logged-in username and a disconnect button are shown in the upper-right corner.

Prediction Workspace (Predictions)
-----------------------------------

The prediction workspace uses a three-panel layout:

.. figure:: /_static/20260319-180331.jpg
   :width: 100%
   :alt: Prediction Workspace - File Upload and Parameter Configuration

   Prediction workspace interface: left panel shows GPU cluster status, center panel shows file upload and task configuration, right panel shows the visualization area

Left Panel: GPU Cluster Status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Displays the real-time operating status of each GPU:

- GPU name and index
- VRAM usage (used / total in MB)
- GPU utilization (%)
- Temperature
- Status indicator (idle/busy)

Data is refreshed automatically every 5 seconds via WebSocket.

Center Panel: Prediction Task Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Upload Structure Files**

Click the upload area to select files. Supported formats include CIF, VASP, XYZ, PDB, and 14 others (15 formats total), as well as ZIP/TAR archives. The grid dimensions nx, ny, and nz must be specified at upload time.

Alternatively, click "Load Demo" to quickly load the built-in demonstration database.

**Submit Prediction**

- Select the structure ID range (start_id ~ end_id)
- Click the submit button
- Tasks enter the GPU queue; each task card displays its status in real time:

  - Grey: pending
  - Blue: processing
  - Green: completed
  - Red: failed

Right Panel: Visualization
^^^^^^^^^^^^^^^^^^^^^^^^^^

Once a task is complete, click its task card to view the prediction results in the right panel. Two visualization modes are available:

**2D Slice (Slice)**

A two-dimensional charge density slice along a specified Miller index (hkl) plane:

.. figure:: /_static/20260319-180338.jpg
   :width: 100%
   :alt: 2D Charge Density Slice Visualization

   2D slice view: heatmap of charge density distribution along the (hkl) plane, with optional contour overlay and Gaussian blur

- Select the slice direction (h, k, l)
- Adjust the slice distance (distance)
- Gaussian blur smoothing supported
- Contour overlay display supported
- Viridis colormap

**3D Isosurface (Isosurface)**

Interactive three-dimensional isosurface rendering powered by Plotly.js:

.. figure:: /_static/20260319-180345.jpg
   :width: 100%
   :alt: 3D Charge Density Isosurface Visualization

   3D isosurface view: interactive three-dimensional charge density rendering showing the unit cell boundary and lattice parameters

- Click and drag to rotate the view
- Scroll to zoom
- Adjustable isosurface threshold (ISO MIN/MAX)
- Adjustable resolution and number of isosurface levels
- Displays the unit cell boundary (gold wireframe) and lattice parameters (a, b, c, alpha, beta, gamma)

File Management (My Files)
--------------------------

Switch to the "My Files" view to manage uploaded files and prediction history:

.. figure:: /_static/20260319-180351.jpg
   :width: 100%
   :alt: File Management and Result Storage Page

   My Files view: uploaded file list and prediction history, showing download status and expiration information

**Uploaded File List**

- File name and upload time
- Days since upload
- Download status (available / expired)
- Files are available for download for 3 days

**Prediction History**

- Task ID and creation time
- CHGCAR file path
- Download status and expiration

Performance Tips
----------------

**3D Visualization Optimization**

- For large CHGCAR files (grid > 48^3), it is recommended to preview at reduced resolution first
- Reducing the number of isosurface levels improves browser rendering performance
- Raising the ISO MIN threshold to display only high-density regions reduces the number of rendered polygons

**Browser Compatibility**

- Chrome / Edge (Chromium-based) is recommended
- WebGL support is required (for Plotly 3D rendering)
- A screen resolution of >= 1920x1080 is recommended
