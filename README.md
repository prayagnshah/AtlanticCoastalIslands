# Atlantic Coastal Islands
Created by Anneke van der Laan for EPM GIS in March and April 2023, under https://github.com/annekecvdl/epm_contract/tree/main (V.1.5). 
Edited by Leah Fulton in May 2023 (V.1.6).

This project uses the CoastSat open-source software toolkit (version 2.1) to extract the coastline of input areas from Sentintel-2 satellite imagery.

There are two Python scripts for this process:

There are two Python scripts for this process:
1.	Prepare_GeoJSON.py - Extracts the coastline from Sentinel-2 imagery using the CoastSat toolkit resulting in a number of GeoJSON polyline files.*
2.	Process_GeoJSON.py - Processes the output GeoJSON files from Prepare_GeoJSON.py using ArcPy to create a single polyline Feature Class of the extracted coastline result.

Prepare_GeoJSON.py was duplicated for each province and customized based on their polygon attributes and is renamed as follows:
- `Prepare_GeoJSON_NFLD.py`
- `Prepare_GeoJSON_PEI.py`
- `Prepare_GeoJSON_NB.py`
- `Prepare_GeoJSON_QC.py`

### At this stage, `Prepare_GeoJSON_NFLD.py` and `Prepare_GeoJSON_PEI.py` require review. From step #1 to #4 outlines the methodology and associated direction, while Step #5 outlines further improvement and recommendations to be reviewed.

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

## 2 - RUNNING THE SCRIPT TO PREPARE THE GEOJSON
To run the script, make sure you have run the above set up steps in an Anaconda shell and that you are navigated to the cloned repo folder containing the `Prepare_GeoJSON.py` script and run `python .\Prepare_GeoJSON.py`. Make sure the `Prepare_GeoJSON.py` script in the coastsat folder. 

### 2.1 - USER INPUTS
The user will be asked for many inputs. If no input is provided, a default value for that input is used. The default value is displayed to the user for each input. The inputs are as follows:
1. `POLYGON LIST CSV PATH`: The path to `Newfoundland_Fishnet_Polygon_Points.csv` that you downloaded and moved to the CoastSat folder.
2. `SENTINTEL-2 IMAGE DATE`: The date that you would like to download images for.
3. `SATELLITE LIST`: The list of satellites used to filter the satellite imagery from GEE. The input can be any subset of the following list of satellites: `['L5','L7','L8','L9','S2']`
4. `COLLECTION`: Indication to use collection 1 `'C01'` or collection 2 `'C02'`. It is recommended to use collection 2. 
5. `FOLDER NAME`: The name of the folder to store the downloaded images. (A good name would describe the area being processed.)
6. `DOWNLOAD IMAGES FROM GEE`: If you are running the program for the input folder name from step 1.6 with the current inputs for the first time, input `YES` to download the images from GEE. If you have already run the program for that folder name and the current input settings, input `NO` to use the images that have already been downloaded.
7. `SAVE JPGS`: If you would like to save an additional JPG image during processing input `YES`. This is useful if you would like to go inspect the image results of the program when it is finished running. These JPGs are not necessary for the program to run. If you don't need them, input `NO` to skip saving JPGs.

### 2.2 - LOGGING
As the program runs, it will keep track of how many polygons have run successfully as well as a list of any polygons that encountered errors. At the end of the program, the list of polygon IDs that errored will be printed to the console as well as the total run time of the program, the total processing time of the polygons, and the number of successful polygons. There are also logging and update messages that are printed throughout the processing to indicate the status and progress of the program as it runs.

### 2.3 - OUTPUTS
The outputs of this program are a number of GeoJSON files stored in the folder that was indicated by the user when the program ran. There is one GeoJSON polyline file for each input polygon.

### 2.4 - NOTES ON ERRORS
This program is not perfect or robust enough in its error/exception handling. If you are trying to run the program and having probleams, here is a common list of things to check first:
- Is the `Prepare_GeoJSON.py` script saved in the top level CoastSat folder?
- Is the points CSV file that you are using storing the correct data in the correct order? Is the file stored in the right place?
- When running the program to download GEE images, is there already a folder in `CoastSat/data` with the folder name that you are using in this program run that already contains data that you are trying to download?
- When running the program to use local images that have already been downloaded, have the images already been downloaded? Are they already in a folder in `CoastSat/data` with a matching folder name?
- If you used any custom user input values, are they formatted correctly and valid?
- Is the `coastsat` profile enabled in the Anaconda shell terminal?
- Do you need to renew the GEE token?

## 3.0 - EXPLORE THE GEOJSON RESULTS
The results of Prepare_GeoJSON.py can be explored before further processing.

### 3.1 - OPEN IN QGIS
The easiest way that I have found to explore the results in the GeoJSON files is by opening them in QGIS. Open QGIS and create a new project with a basemap. Walkthrough for adding a basemap to a QGIS project. Add the resulting GeoJSON files to the project to look at the results. The current GeoJSON results are a single polyline for each polygon processed. This means that any line segments in the results are connected with other lines, so there is more post-processing work to be done to remove these extra lines.

### 3.2 - GOOD RESULTS
Most of the results are very successful and outline the islands, shore, and lakes accurately at a 1:10,000 scale.

### 3.3 - BAD RESULTS - BUSY IMAGES
Some of the polygons have undesirable results. I found some cases of polygons that had another jpeg downloaded in the results that was a subset of the polygon area that had only cloud cover that created an area of the result full of points. These polygons should be investigated to remove these extra images by altering some combination of the CoastSat settings and the user inputs. 

### 3.4 - BAD RESULTS - MISSING RESULTS
There are other areas of the original polygon fishnet that are missing in the results completely. Although the input fishnet was a perfect grid of squares, the results seem to skew these perfect squares a bit and create diagonal lines, in one section particularly. This area with missing data needs to be investigated to see why there is data missing and how to fill the gap of missing data.

### 3.5 - BAD RESULTS - IMAGE BOUNDARIES
For some of the results, there is a straight line that is created that is unrelated to the coastline. I found that these lines are caused by lighter lines along the edges of the images downloaded from GEE. Because there is a lighter edge around some of the borders of some of the images, the coastline detection process sees these changes in colour as changes between water and land and identify the areas as coastline when they are not. This is an issue because these line segments are not part of the coastline and will cause issues when trying to merge all of the coastlines together. I'm not sure the correct approach to solve this problem. One option could be to address the lightness in the images during processing by changing some of the CoastSat code itslef to not process the image pixels around the border. This could cause some problems though by missing legitamite coastline data that is along the edges. However, this could be solved by overlapping the polygons of the fishnet a little bit to account for the edges that would not be considered. This solution would have to be explored more to verify that it would work. Another option would be to clean up the coastline extracted in post-processing. Investigation would need to be done to see if there is a tool that can detect straight points in order to isolate the areas that need to be removed. There could also be another aproach to find these line segments. Another option would be to remove these lines manually, but this would be the most time consuming approach.

## 4 - RUNNING THE SCRIPT TO PROCESS THE GEOJSON
To run the script, navigate to the cloned repo folder containing the `Process_GeoJSON.py` script and run `python .\Process_GeoJSON.py`. Note that I had problems setting up an environment in Anaconda that would allow me to use ArcPy, but to make it work in tandem in an Anaconda Shell, you need to clone the arcgispro-py3 environment. You cannot modify the default Pythonenvironmnent (`arcgispro-py3`), so you must clone and activiate a new environment.  
1. If ArcGIS Pro is installed on your computer, you have a python command promnpt. Right click on the python command prompt, and open file location. 
2. Run as Administrator
3. Run `conda create --name myclone --clone myenv` , but replace `myclone` with your environment clone name, and replace `myenv` with your enviroinment that you are cloning. 

### 4.1 - USER INPUTS
The user will be asked for many inputs. If no input is provided, a default value for that input is used. The default value is displayed to the user for each input. The inputs are as follows:
1. `FOLDER NAME`: The name to use for the output results. It is recommended to use the same name as the GeoJSON folder, but it is not required.
2. `GEOJSON FOLDER PATH`: The path of the folder containing the GeoJSON files to process.
3. `GEO DATABASE PATH`: The path of the geodatabase where the resulting Feature Classes will be created.

### 4.2 - GEOJSON PROCESSING
1. First, a Feature Class is created for every input GeoJSON file using the JSON to Features tool. The name of each Feature Class is <FOLDER_NAME>_<NUMBER> where the folder name is the name input by the user and the number is extracted from the processed GeoJSON file name which represents the polygon number. The resulting Feature Classes are then merged together using the Merge tool. The name of the merged Feature Class is <FOLDER_NAME>_MERGE.
2. The merged Feature Class is then split using the Split Line tool to create multiple line segments along the vertices. The name of the output line Feature Class is <FOLDER_NAME>_SPLIT.
The next step is to remove the long line segments that connect different pieces of the coastline but are not parts of the coastline result. This is done by using an Update Cursor on <FOLDER_NAME>_SPLIT to remove any lines that have a Shape Length of longer than 40. This is an arbitrary number and should probably be tweaked.
3. Now, the goal is to merge line segments together that are connected. To do this, a buffer is created around each line segment using the Buffer tool. A buffer of 2 metres is used, which is, again, an arbitrary number but works. It could be tweaked. The resulting buffer called <FOLDER_NAME>_BUFFER is then dissolved using the Dissolve tool according to any overlapping buffers, meaning buffers that are close to each other will be dissolved into one and given an ID. Using the Spatial Join tool, the line segments and the dissolved buffers are joined, resulting in the line segments each being associated with one of the dissolved buffers. The result is <FOLDER_NAME>_SPATIAL_JOIN. By dissolving this spatial join result using the Dissolve tool, we end up with the desired result in <FOLDER_NAME>_RESULT.

### 4.3 - OUTPUTS
The outputs of the script are multiple Feature Classes:
- <FOLDER_NAME>_<NUMBER> (one for each processed GeoJSON file)
- <FOLDER_NAME>_MERGE
- <FOLDER_NAME>_SPLIT
- <FOLDER_NAME>_BUFFER
- <FOLDER_NAME>_DISSOLVE
- <FOLDER_NAME>_SPATIAL_JOIN
- <FOLDER_NAME>_RESULT

## 5 - NEXT PHASE
This section outlines current issues, improvements to be made, exploration to be done, more code to write, as well as ideas that could be considered beyond the scope of the current project.

### 5.1 - ISSUES
- The fishnet should be tweaked to remove polygons that don't include coastline. (1.4)
- Some polygon results include extra images that interfere with the coastline results. (3.3)
- There are data gaps along diagonal lines/in a triangular area that need to be investigated. (3.4)
- Some image edges are detected as shorelines. (3.5)
- Lakes need to be removed from the results.

### 5.2 - IMPROVEMENTS - FOR REVIEW
#### `Prepare_GeoJSON_NFLD.py`
1. Improved error and exception messaging and segmentation:
- Identify critical sections of your code where exceptions might occur.
- Use try-except blocks to catch specific exceptions in those sections.
- Provide informative error messages that explain the issue and how to resolve it.
- Consider using custom exceptions to handle specific scenarios, making error handling more precise.
2. User input validation:
- Define the expected format and valid ranges for each user input.
- Use functions to validate user inputs against these criteria.
- Continuously prompt the user until valid input is provided.
- Handle potential edge cases or unexpected input to prevent program crashes.
3. Add a logger to allow for logging filters and writing output to a document instead of the console:
- Import the Python logging module to use for logging purposes.
- Set up a logger with desired log level and file handler (for writing logs to a file).
- Use logging statements throughout your code to record important events and information.
- Customize the log format to include relevant details such as timestamp and log level.
- Optionally, add logging filters to control which log records are emitted based on specific criteria.
4. Add more logging statements that create more of a dialog and explanation as the program runs:
- Insert logging statements before and after significant steps or functions.
- Use logging to display the state of variables or important calculations.
- Add explanatory log messages to guide users and developers through the program's execution.
5. Set some of the CoastSat settings with user inputs:
- Identify which CoastSat settings can be controlled by users.
- Ask users for input or provide command-line arguments to specify these settings.
- Update the relevant parts of your code to use the user-provided settings.
6. Add an option to delete files only needed in intermediate steps:
- Determine which intermediate files can be safely deleted.
- Implement a flag or input option that allows users to choose whether to perform file cleanup.
- Provide a warning before deleting any files to prevent accidental data loss.
- Implement the file cleanup functionality at the end of the program or after the user-specified steps.

#### `Prepare_GeoJSON_PEI.py`
- All above improvements including
- It is picking up the cooridnates and number of polygons to process in the csv., but not processing them with the satelitte imagery. 

`Process_GeoJSON.py`
- User input validation.
- Improve performance.

Other:
- Use tools to triage the fishnet polygons into subsets by date.
