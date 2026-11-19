# 🌿 INP Vegetation Analysis — QGIS Plugin for Vegetation Analysis & Importance Value Index

**INP Vegetation Analysis** is a Python-based QGIS plugin (QGIS 3.0+) designed to automate the calculation of ecological vegetation parameters (**Relative Density**, **Relative Frequency**, **Relative Dominance**, and **Importance Value Index / INP**) and visualize their spatial distribution using **Inverse Distance Weighting (IDW)** interpolation.

Built for forestry, ecology, and environmental researchers, this plugin enables plot-based forest inventory processing directly within a GIS environment without having to manually switch back and forth between spreadsheets.

## 📚 Resources & Templates

* **User Guidelines:** [Download / View Plugin Guidelines (PDF/Doc)](https://drive.google.com/file/d/1SJFC4Vl5N0wtCwlgZxUccL4qvvAaOM4X/view?usp=drivesdk)
* **Data Naming Conventions Template:** [Customize Stage-Level Data Naming Conventions (Google Sheets)](https://docs.google.com/spreadsheets/d/1Pwo5Hs-0Z4UUl0CKj2GvnmGixT2cVVAWlecih10NOuw/edit?usp=drivesdk)

## ✨ Key Features

* **Automated Ecological Parameter Calculation:** Instantly calculates **Density ($K$)** ($\text{ind/ha}$), **Relative Density ($KR$)** ($\%$), **Frequency ($F$)**, **Relative Frequency ($FR$)** ($\%$), **Dominance ($D$)** ($\text{m}^2/\text{ha}$), **Relative Dominance ($DR$)** ($\%$), and **Importance Value Index ($INP$ / IVI)** ($\%$) from sample plot point data.
* **Multi-Growth Stage Support:** Supports automatic filtering for **Trees (*Pohon*)**, **Poles (*Tiang*)**, **Stakes/Saplings (*Pancang*)**, **Seedlings (*Semai*)**, **Lianas**, and **Understory Plants (*Tumbuhan Bawah*)** (automatically applying the 3-parameter formula for *Trees & Poles*, and the 2-parameter formula without dominance for other stages).
* **Dynamic Field Mapping:** Freely map attribute columns from your own Shapefile/GeoPackage (`plot_id`, `stadium`, `species`, `count`, and `dbh_cm`) with automatic field name detection.
* **Area of Interest (AOI) Clipping:** Supports selecting an *Area of Interest* (AOI) polygon layer to filter sample points within the study boundary and automatically clip the resulting interpolated rasters.
* **Comprehensive Table Export (CSV):** Exports species-level ecological summaries into a `.csv` file ready for reporting or further statistical analysis.
* **Automated Spatial Mapping (IDW Interpolation):** Generates IDW interpolated raster layers for each selected metric (`KR`, `FR`, `DR`, `INP`) complete with automated pseudocolor symbology.

## 📐 Methodology & Formulas

This plugin implements standard plot-based vegetation analysis equations:

1. **Density ($K$) & Relative Density ($KR$):**
   $$K = \frac{\text{Number of Individuals of a Species}}{\text{Total Sample Plot Area (ha)}}$$
   $$KR = \left(\frac{K \text{ of a Species}}{\sum K \text{ of All Species}}\right) \times 100\%$$

2. **Frequency ($F$) & Relative Frequency ($FR$):**
   $$F = \frac{\text{Number of Plots Where a Species Occurs}}{\text{Total Number of Sample Plots}}$$
   $$FR = \left(\frac{F \text{ of a Species}}{\sum F \text{ of All Species}}\right) \times 100\%$$

3. **Dominance ($D$) & Relative Dominance ($DR$)** *(for Trees & Poles only)*:
   $$\text{Basal Area (LBDS)} = \frac{1}{4} \pi \left(\frac{\text{DBH}_{\text{cm}}}{100}\right)^2$$
   $$D = \frac{\sum \text{Basal Area of a Species } (\text{m}^2)}{\text{Total Sample Plot Area (ha)}}$$
   $$DR = \left(\frac{D \text{ of a Species}}{\sum D \text{ of All Species}}\right) \times 100\%$$

4. **Importance Value Index ($INP$ / IVI):**
   * **Trees & Poles:** $INP = KR + FR + DR$ *(range: $0\% - 300\%$)*
   * **Stakes/Saplings, Seedlings, Lianas, & Understory:** $INP = KR + FR$ *(range: $0\% - 200\%$)*

## 🛠️ Installation

### Method 1: Install from QGIS Plugin Repository
1. Open **QGIS** (version 3.0 or higher).
2. Go to **Plugins** $\rightarrow$ **Manage and Install Plugins...**
3. Search for **INP Vegetation Analysis** and click **Install Plugin**.

### Method 2: Install from ZIP
1. Download this repository as a `.zip` file (**Code** $\rightarrow$ **Download ZIP**).
2. In QGIS, open **Plugins** $\rightarrow$ **Manage and Install Plugins...** $\rightarrow$ **Install from ZIP**.
3. Browse to the downloaded `.zip` file and click **Install Plugin**.

### Method 3: Manual Installation to QGIS Plugin Directory
1. Copy the `inp_spatial_analyzer` folder into your active QGIS user profile plugin directory:
   * **Windows:** `C:\Users\<Username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   * **Linux:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   * **macOS:** `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
2. Restart QGIS, then enable **INP Vegetation Analysis** under **Installed** plugins.

## 🚀 Usage

1. **Prepare Point Vector Data:** Ensure your vegetation sample point layer follows the stage naming conventions and uses a **Projected Coordinate System (e.g., UTM in meters)** so pixel size calculations during interpolation are accurate.
2. **Launch the Plugin:** Click the **Analisis Spasial INP** icon on the toolbar or navigate to **Vector** / **Plugins** $\rightarrow$ **Analisis Vegetasi** $\rightarrow$ **Analisis Spasial INP**.
3. **Configure Inputs:**
   * Select the **Vegetation Data Layer (Point)** and **AOI Boundary (Polygon)** *(optional)*.
   * Verify or map the corresponding attribute fields (**Plot ID**, **Growth Stage**, **Species**, **Individual Count**, and **DBH in cm**).
   * Select the target **Growth Stage**, enter the **Plot Area ($\text{m}^2$)**, and specify the **Raster Pixel Size (meters)**.
4. **Select Outputs:**
   * Check the spatial indicators you wish to map (`KR`, `FR`, `DR`, `INP`).
   * Specify the output file path for the summary **CSV** table.
5. **Run Analysis:** Click **Process**. The CSV file will be saved, and the **Interpolasi IDW** raster layers will automatically be added to your QGIS map canvas.

## 📋 Changelog

* **Version 2.7.8**
  * Fixed a calculation bug: resolved duplicate metric accumulation (`INP`, `KR`, `FR`, `DR`) per unique species within each plot during IDW spatial interpolation so raster values remain within valid ecological bounds ($0\% - 300\%$).
  * Updated output raster layer naming to `Interpolasi IDW` to accurately reflect the spatial interpolation method used.
* **Version 2.7.7**
  * Added dynamic attribute field mapping, polygon AOI boundary clipping, temporary GeoPackage processing, and stage-level data naming guidelines.

## 👤 Author & Support

* **Author:** Muhammad Parif — IPB University
* **Email:** [payip28muhammad@apps.ipb.ac.id](mailto:payip28muhammad@apps.ipb.ac.id)
* **Issue Tracker:** [GitHub Issues](https://github.com/muhammad-parif/inp_spatial_analyzer/issues)
* **Repository:** [github.com/muhammad-parif/inp_spatial_analyzer](https://github.com/muhammad-parif/inp_spatial_analyzer)