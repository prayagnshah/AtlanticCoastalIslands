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
3.	Paste into scratch and fill in the RED coloured items. conda create --name myclone --clone myenv
Ex: conda create `--name arcgispropy3_clone --clone arcgispro-py3`
