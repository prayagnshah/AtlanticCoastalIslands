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

1 - SET UP
Before the scripts can be run, there are a number of set up steps that need to be performed.

1.1 - CLONE THIS REPO LOCALLY
The first step is to clone this repo locally! How to clone a GitHub repository.

The first part of the project when the GeoJSON is prepared requires the CoastSat toolkit among other packages. The second half of the project when the GeoJSON is processed into Feature Classes requires the ArcPy package. If you will only be running on half of the project you only have to worry about the setup for that half. Note that I had difficulties with installing ArcPy in my Anaconda environment so I ran the Prepare_GeoJSON.py script in the Anaconda environment and ran the Process_GeoJSON.py script in my normal shell.

1.2 - SET UP AN ANACONDA ENVIRONMENT
An Anaconda environment is required to run Prepare_GeoJSON.py.

This part of the set-up is almost entirely copied (but simplified) from the CoastSat installation instructions. They include more details about the Anaconda, GitHub, Google Earth Engine (GEE), and CoastSat installation instructions. Here is their installation guide.

If this is your first time using the program:
Download and install Anaconda. Download Anaconda here.
Open Anaconda Navigator and launch a Powershell Prompt.
Run conda install gh --channel conda-forge to download the Git CLI. Set up the CLI. Here is a Git CLI quickstart.
Download Git for Windows.
Clone the CoastSat 2.1 repository locally using gh repo clone kvos/CoastSat.
Navigate to the cloned repository.
Create an Anaconda environment named coastsat with required packages installed by running the following commands:
conda create -n coastsat python=3.8
conda activate coastsat
conda install -c conda-forge geopandas earthengine-api scikit-image matplotlib astropy notebook -y
pip install pyqt5
Link environment to GEE server. earthengine authenticate --auth_mode=notebook
If you have been here before:
Open Anaconda Navigator and launch a Powershell Prompt.
Navigate to the cloned repository.
Activate the CoastSat profile. conda activate coastsat
Ensure your GEE token is not expired. earthengine authenticate --auth_mode=notebook
