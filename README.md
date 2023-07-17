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
