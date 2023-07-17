# Atlantic Coastal Islands
Created by Anneke van der Laan for EPM GIS in March and April 2023. Edited by Leah Fulton in May 2023.

This project uses the CoastSat open-source software toolkit (version 2.1) to extract the coastline of input areas from Sentintel-2 satellite imagery.

There are two Python scripts for this process:

There are two Python scripts for this process:
1.	Prepare_GeoJSON.py - Extracts the coastline from Sentinel-2 imagery using the CoastSat toolkit resulting in a number of GeoJSON polyline files.*
2.	Process_GeoJSON.py - Processes the output GeoJSON files from Prepare_GeoJSON.py using ArcPy to create a single polyline Feature Class of the extracted coastline result.

* Prepare_GeoJSON.py was duplicated for each province and customized based on their polygon attributes and is renamed as follows:
•	Prepare_GeoJSON_NFLD.py
•	Prepare_GeoJSON_PEI.py
•	Prepare_GeoJSON_NB.py
•	Prepare_GeoJSON_QC.py

## 1 - SET UP
Before the scripts can be run, there are a number of set up steps that need to be performed.

### 1.1 - CLONE THIS REPO LOCALLY
The first step is to clone this repo locally! [How to clone a GitHub repository.](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository?tool=cli)

The first part of the project when the GeoJSON is prepared requires the CoastSat toolkit among other packages. The second half of the project when the GeoJSON is processed into Feature Classes requires the ArcPy package. If you will only be running on half of the project you only have to worry about the setup for that half. Note that I had difficulties with installing ArcPy in my Anaconda environment so I ran the `Prepare_GeoJSON.py` script in the Anaconda environment and ran the `Process_GeoJSON.py` script in my normal shell.

### 1.2 - SET UP AN ANACONDA ENVIRONMENT

An Anaconda environment is required to run `Prepare_GeoJSON.py`.

This part of the set-up is almost entirely copied (but simplified) from the CoastSat installation instructions. They include more details about the Anaconda, GitHub, Google Earth Engine (GEE), and CoastSat installation instructions. [Here is their installation guide.](https://github.com/kvos/CoastSat) 

#### If this is your first time using the program:
1. Download and install **Anaconda**. [Download Anaconda here.](https://www.anaconda.com/download/)
2. Open **Anaconda Navigator** and launch a **Powershell Prompt**.
3. Run `conda install gh --channel conda-forge` to download the Git CLI. Set up the CLI. [Here is a Git CLI quickstart.](https://docs.github.com/en/github-cli/github-cli/quickstart)
4. Download **Git for Windows**.
5. Clone the **CoastSat 2.1** repository locally using `gh repo clone kvos/CoastSat`.
6. Navigate to the cloned repository.
7. Create an Anaconda environment named `coastsat` with required packages installed by running the following commands:
      ```
      conda create -n coastsat python=3.8
      conda activate coastsat
      conda install -c conda-forge geopandas earthengine-api scikit-image matplotlib astropy notebook -y
      pip install pyqt5
      ```
8. Link environment to GEE server. `earthengine authenticate --auth_mode=notebook`

#### If you have been here before:
1. Open **Anaconda Navigator** and launch a **Powershell Prompt**.
2. Navigate to the cloned repository.
3. Activate the CoastSat profile. `conda activate coastsat` 
4. Ensure your GEE token is not expired. `earthengine authenticate --auth_mode=notebook`

### 1.3 - MAKE SURE YOU HAVE ARCPY SET UP

ArcPy is required to run `Process_GeoJSON.py`.

If you would like to install ArcPy in the same Anaconda environment, you can do if you are in an activated conda environment and run `conda install arcpy=3.1 -c esri` [Instructions to install ArcPy are here.](https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/installing-arcpy.htm)

As previously mentioned, I had troubles installing ArcPy in Anaconda, so I ran the Process_GeoJSON.py script in a regular shell outside of Anaconda. You can do this, or if you have ArcGIS Pro installed, it is likely already installed on your hardware – however, ArcGIS Pro environment will not allow to manipulate or modify the default environment, so you need to clone the default environment and activate a new environment. 

1.	Right click on Python Command Prompt, and open File location
2.	Run as Administer
3.	Paste into scratch and fill in the RED coloured items. `conda create --name myclone --clone myenv`
Ex: `conda create --name arcgispropy3_clone --clone arcgispro-py3`

### 1.4 - PREPARE POLYGON COORDINATES
The following example is for Newfoundland, but the preparation has also been completed for all of the Atlantic Canadian provinces, such as New Brunswick, P.E.I, and Quebec. 
The polygons in Newfoundland_Fishnet_Polygon_Points.csv are prepared for Newfoundland, but if you would like to run this program on another area, a similar file will need to be created for that area.
Create a fishnet over the area of interest where each square in the fishnet is no larger than 100 kilometres squared (10 kilometres by 10 kilometres). Newfoundland_Fishnet.png shows the fishnet in Newfoundland_Fishnet_Polygon_Points.csv.

### 1.5 - PREPARE THE SUBSET OF POLYGONS TO PROCESS
Within the area to be processed, there are different areas that have clear satellite imagery from different dates. I spent some time in GEE exploring Sentintel-2 imagery results for different regions around Newfoundland and came up with a polygon layer dividing the province. The date and an ID should be associated with each of the polygons in the layer, which still needs to be done.
This part of the process should be greatly improved. Right now, this triage of polygons into different areas is done manually. 

### 1.6 - EXPORT POLYGONS TO POINTS
Now that the fishnet is created, they will need to be organized by date of the satellite imagery dates polygons (Newfoundland Polygons by Date).
1.	Add a new field called "Date" as a Text field type. Highlight a Newfoundland Polygons by Date feature. Using Select by Location, the input feature: the fishnet polygons, intersect the selecting features: Newfoundland Polygons by Date. The result is the highlighted fishnet polygons that intersect with the highlighted polygon date. Open the attribute table and click on calculate field. In brackets, insert the date of said polygon that intersects. Example: "October 19, 2019". The result will only highlight the populated field. Repeat for all dates.
2.	In the geoprocessing pane, open the Feature Vertices to Point tool where the input feature is the fishnet that inlcudes the field with the associated polygon dates.
3.	In the new layer, add two fields: X and Y, with a Double field type. Save. Left click on the new field and Calculate geometry where the X and Y fields are the X and Y coordinates in Decimal Degrees.
4.	Export the polygons to a CSV where each row of the file is one point. Each row must consist of the shape ID of the point (which polygon it belongs to), the x coordinate, and the y coordinate of the point. See Newfoundland_Fishnet_Polygon_Points.csv for an example of what the CSV file should look like. The first shape ID must be 0.
