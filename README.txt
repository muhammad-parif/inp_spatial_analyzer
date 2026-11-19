================================================================================
INP VEGETATION ANALYSIS - QGIS PLUGIN
================================================================================

INP Vegetation Analysis is a Python-based QGIS plugin (QGIS 3.0+) designed to
automate the calculation of ecological vegetation parameters—Relative Density
(KR), Relative Frequency (FR), Relative Dominance (DR), and Importance Value
Index (INP)—and visualize their spatial distribution using Inverse Distance
Weighting (IDW) interpolation.

Built for forestry, ecology, and environmental researchers, this plugin enables
plot-based forest inventory processing directly within a GIS environment.

--------------------------------------------------------------------------------
RESOURCES & TEMPLATES
--------------------------------------------------------------------------------
- User Guidelines:
  https://drive.google.com/file/d/1SJFC4Vl5N0wtCwlgZxUccL4qvvAaOM4X/view?usp=drivesdk

- Data Naming Conventions Template (Stage-Level):
  https://docs.google.com/spreadsheets/d/1Pwo5Hs-0Z4UUl0CKj2GvnmGixT2cVVAWlecih10NOuw/edit?usp=drivesdk

--------------------------------------------------------------------------------
KEY FEATURES
--------------------------------------------------------------------------------
1. Automated Ecological Parameter Calculation
   Calculates Density (K, ind/ha), Relative Density (KR, %), Frequency (F),
   Relative Frequency (FR, %), Dominance (D, m2/ha), Relative Dominance (DR, %),
   and Importance Value Index (INP / IVI, %) from sample plot point data.

2. Multi-Growth Stage Support
   Supports automatic filtering for Trees (Pohon), Poles (Tiang),
   Stakes/Saplings (Pancang), Seedlings (Semai), Lianas, and Understory Plants
   (Tumbuhan Bawah). Automatically applies the 3-parameter formula for Trees
   and Poles, and the 2-parameter formula (without dominance) for other stages.

3. Dynamic Field Mapping
   Map attribute columns from your Shapefile or GeoPackage (plot_id, stadium,
   species, count, and dbh_cm) with automatic field name detection.

4. Area of Interest (AOI) Clipping
   Select an AOI polygon layer to filter sample points within the study
   boundary and automatically clip the resulting interpolated rasters.

5. CSV Summary Export
   Exports species-level ecological summaries into a .csv file ready for
   reporting or further statistical analysis.

6. Spatial Mapping (IDW Interpolation)
   Generates IDW interpolated raster layers for each selected metric (KR, FR,
   DR, INP) complete with automated pseudocolor symbology.

--------------------------------------------------------------------------------
METHODOLOGY & FORMULAS
--------------------------------------------------------------------------------
1. Density (K) & Relative Density (KR):
   K  = Number of Individuals of a Species / Total Sample Plot Area (ha)
   KR = (K of a Species / Sum of K of All Species) x 100%

2. Frequency (F) & Relative Frequency (FR):
   F  = Number of Plots Where a Species Occurs / Total Number of Sample Plots
   FR = (F of a Species / Sum of F of All Species) x 100%

3. Dominance (D) & Relative Dominance (DR) [Trees & Poles only]:
   Basal Area (LBDS) = 0.25 x pi x (DBH_cm / 100)^2
   D  = Sum of Basal Area of a Species (m2) / Total Sample Plot Area (ha)
   DR = (D of a Species / Sum of D of All Species) x 100%

4. Importance Value Index (INP / IVI):
   - Trees & Poles: INP = KR + FR + DR (range: 0% - 300%)
   - Stakes/Saplings, Seedlings, Lianas, & Understory: INP = KR + FR (0% - 200%)

--------------------------------------------------------------------------------
INSTALLATION
--------------------------------------------------------------------------------
Method 1: Install from QGIS Plugin Repository
  1. Open QGIS (version 3.0 or higher).
  2. Go to Plugins -> Manage and Install Plugins...
  3. Search for "INP Vegetation Analysis" and click Install Plugin.

Method 2: Install from ZIP
  1. Download this repository as a .zip file (Code -> Download ZIP).
  2. In QGIS, go to Plugins -> Manage and Install Plugins... -> Install from ZIP.
  3. Browse to the downloaded .zip file and click Install Plugin.

Method 3: Manual Installation to QGIS Plugin Directory
  1. Copy the "inp_spatial_analyzer" folder into your active QGIS user profile
     plugin directory:
     - Windows : C:\Users\<Username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
     - Linux   : ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
     - macOS   : ~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/
  2. Restart QGIS, then enable "INP Vegetation Analysis" under Installed plugins.

--------------------------------------------------------------------------------
USAGE
--------------------------------------------------------------------------------
1. Prepare Point Vector Data:
   Ensure your vegetation sample point layer follows the stage naming
   conventions and uses a Projected Coordinate System (e.g., UTM in meters)
   so pixel size calculations during interpolation are accurate.

2. Launch the Plugin:
   Click the "Analisis Spasial INP" icon on the toolbar or navigate to
   Vector / Plugins -> Analisis Vegetasi -> Analisis Spasial INP.

3. Configure Inputs:
   - Select the Vegetation Data Layer (Point) and AOI Boundary (Polygon, optional).
   - Verify or map the attribute fields (Plot ID, Growth Stage, Species,
     Individual Count, and DBH in cm).
   - Select the target Growth Stage, enter the Plot Area (m2), and specify the
     Raster Pixel Size (meters).

4. Select Outputs:
   - Check the spatial indicators to map (KR, FR, DR, INP).
   - Specify the output file path for the summary CSV table.

5. Run Analysis:
   Click Process. The CSV file will be saved, and the "Interpolasi IDW" raster
   layers will automatically be added to your QGIS map canvas.

--------------------------------------------------------------------------------
CHANGELOG
--------------------------------------------------------------------------------
Version 2.7.8
- Fixed a calculation bug: resolved duplicate metric accumulation (INP, KR, FR,
  DR) per unique species within each plot during IDW spatial interpolation so
  raster values remain within valid ecological bounds (0% - 300%).
- Updated output raster layer naming to "Interpolasi IDW" to accurately reflect
  the spatial interpolation method used.

Version 2.7.7
- Added dynamic attribute field mapping, polygon AOI boundary clipping,
  temporary GeoPackage processing, and stage-level data naming guidelines.

--------------------------------------------------------------------------------
AUTHOR & SUPPORT
--------------------------------------------------------------------------------
Author        : Muhammad Parif - IPB University
Email         : payip28muhammad@apps.ipb.ac.id
Repository    : https://github.com/muhammad-parif/inp_spatial_analyzer
Issue Tracker : https://github.com/muhammad-parif/inp_spatial_analyzer/issues
================================================================================