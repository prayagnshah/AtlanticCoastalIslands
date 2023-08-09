#=======================================================================================
#=======================================================================================
#
# Program:      Coastal Extraction from Sentinel-2 Satellite Imagery to GeoJSON using
#               the CoastSat Toolkit
# File Name:    Prepare_GeoJSON_PEI.py
# Author:       Anneke van der Laan & updated by Leah Fulton & Lisa Chamney
# Version:      1.6
# Date:         August 08, 2023
# Purpose:      EPM GIS Contract
#
# Description:  This program uses the CoastSat 2.1 open-source software toolkit
#               to extract the coastline from Sentinel-2 satellite imagery of input
#               areas as GeoJSON polyline files. ##The coastline is extracted in
#               sections of 100 square kilometres. Each area from an input list
#               of polygon coordinates is processed resulting in a GeoJSON file
#               of the coastline as a polyline. The resulting GeoJSON files are
#               all stored in a local folder.
#
#               Please note this program is not complete. See the README for
#               more details about the next steps in post-processing work,
#               issues in the current solution, and other improvements to be
#               made.
#
# Credit:       The example Jupyter notebook provided by CoastSat was used as the
#               foundation for this program.
#
#               Source - github.com/kvos/CoastSat/blob/master/example_jupyter.ipynb
#
# Note:         This script was written using CoastSat version 2.0
#
#=======================================================================================
#=======================================================================================

#=======================================================================================
#
# VERSION UPDATES:
#   1.6     -   (IN PROGRESS) Re-organize code to avoid duplication of functions for different AOIs,
#               gather all parameters up-front, and explicitly send them to functions.
#           -   Extract-from-CSV bug fixes. Remove unused code.
#
#   1.4     -   Added count of polygons left to process in update message.
#           -   Renamed file from CoastSat_Coastal_Extraction.py to Prepare_GeoJSON.py
#           -   Reverted any processing geojson changes because it became its own script
#
#   1.3     -   Starting to explore GeoJSON processing with ArcPy.
#           -   Split inputs into global, GeoJSON prep, and GeoJSON processing.
#           -   Create a feature class with the same name as the folder.
#
#   1.2     -   The output GeoJSON folder is created if it doesn't exist.
#
#   1.1     -   Lowercase print messages.
#           -   User selection of satellite date.
#           -   Satellite Dates enum created to automatically set start date, end
#               date, and polygon list according to the user input date. (User no
#               longer inputs start date or end date.)
#           -   Split program into two functions: preparing the GeoJSON and processing
#               the GeoJSON. The processing of GeoJSON is currently empty, but the
#               skeleton of the split is there.
#
#=======================================================================================

print("\n=============================================================================")
print("=============================================================================")
print("============================== STARTING PROGRAM =============================")
print("=============================================================================")
print("=============================================================================\n")

#=======================================================================================
# IMPORT PACKAGES (Copied from Jupyter example with some additions as required)

print("Warming up and getting ready...")

import  sys
import  os
import csv

#import  pickle##could be used to pause and restart, ingesting output pkl files
import  warnings
warnings.filterwarnings("ignore")

from    datetime import datetime
from collections import OrderedDict
from    coastsat import SDS_download, SDS_preprocess, SDS_shoreline, SDS_tools
from    pyproj   import CRS
from    enum     import Enum

print("Good to go! Let's get started.\n")

def error(msg):
	raise SystemExit("\n*!*!*!* ERROR: "+str(msg)) #aka sys.exit("\n*!*!*!* ERROR: "+str(msg)) 

#=======================================================================================
# SET DEFAULT VALUES FOR USER INPUTS
# These allow the script to be run with example data

DEFAULT_POLYGONS_PATH = os.path.join(os.getcwd(),'data','Example_Fishnet_Points_1.csv')
DEFAULT_FOLDER_NAME = "EXAMPLE_TEST_1"

# Satellite Options: Any subset of ['L5','L7','L8','L9','S2'] as a list
DEFAULT_SAT_LIST = ['S2']

# Landsat Collection Options: 'C01' or 'C02'
DEFAULT_COLLECTION = 'C02'

#=======================================================================================
# DEFINE SATELLITE DATES ENUM AND SET THE POLYGON LIST FOR EACH DATE
# polygon lists are allowed input csv feature ids for the given SatelliteDates option

DEFAULT_STARTDATE = '2023-05-23'
DEFAULT_ENDDATE = '2023-05-24'

# POLYGON LIST - MAY 23, 2023 (an example date that works with Example_Fishnet_Points_1.csv)
DEFAULT_POLYLIST = list(range(1,476)) #1 to 475 inclusive

class SatelliteDates(Enum):

    def __new__(cls, *args, **kwds):
          value = len(cls.__members__) + 1
          obj = object.__new__(cls)
          obj._value_ = value
          return obj

    def __init__(self, startDate, endDate, polyList):
        self.startDate = startDate
        self.endDate = endDate
        self.polyList = polyList

    MAY23_2023 = (DEFAULT_STARTDATE, DEFAULT_ENDDATE, DEFAULT_POLYLIST)

def getUserInput(desiredInput, defaultValue, validationFunction=None):
    ## TODO: IMPROVE THE USER INPUT CHECK TO BE MORE ROBUST
    """
    # Function:     GET USER INPUT
    #
    # Description:  This function will request input from the user and return the response.
    #
    # Parameters:   desiredInput        - The description of desired input.
    #               defaultValue        - The default value for that input.
    #               validationFunction  - A function which takes a single input parameter and returns True or False.
    #
    # Returns:      The value that was input by the user. If the user inputs nothing,
    #               the default value is returned.
    """
    print("Input {} or hit ENTER to accept the default value: [{}]".format(desiredInput,defaultValue))
    userInput = sys.stdin.readline().strip()

    if userInput == "":
        print("Using default value: [{}]\n".format(defaultValue))
        return defaultValue

    elif userInput in ("QUIT","Quit","quit","Q","q"):
        print("\nQuitting...")
        raise SystemExit

    elif validationFunction:
        if validationFunction(userInput):
            print("\nUsing input value: [{}]\n".format(userInput))
            return userInput
        else:
            error("Invalid input value: "+userInput)

    else:
        userInput = userInput.strip()
        print("\nUsing input value: [{}]\n".format(userInput))
        return userInput

def getUserYesOrNo(inputQuery,reTryOnError=False):
    ## TODO: IMPROVE THE USER INPUT CHECK TO BE MORE VERSATILE
    """#=======================================================================================
    # Function:     GET USER RESPONSE TO A YES OR NO QUESTION
    #
    # Description:  This function will ask the user a yes or no question and return the
    #               response.
    #
    # Parameters:   inputQuery    - The subject of the yes or no question.
    #
    # Returns:      True if the user input 'YES'. False if the user input 'NO'.
    """
    if reTryOnError: #doesn't work in PyScripter
        print("Would you like to {}? Enter 'YES' or 'NO' (or hit ENTER for 'NO').".format(inputQuery))

        for currInput in sys.stdin:
            currInput = currInput.strip()

            if currInput == "":
                print("Using default value: [NO]\n")
                return False

            elif currInput in ("QUIT","Quit","quit","Q","q"):
                print("\nQuitting...")
                raise SystemExit

            elif currInput in ('YES','Yes','yes','Y','y'):
                print("")
                return True

            elif currInput in ('NO','No','no','N','n'):
                print("")
                return False

            else:
                #If the user makes a mistake (ex: enters No) when using an inputs txt file (python .\Prepare_GeoJSON.py < "C:\Users\LChamney\Documents\GitHub_aux\AtlanticCoastalIslands\Prepare_GeoJSON_PEI_Inputs_TEST_1.txt"),
                #it will unintentionally read their next line as the response.
                print("\nTry again. Would you like to {}? Enter 'YES' or 'NO' (or hit ENTER for 'NO').".format(inputQuery))
    else: #safer with input txt files, works in PyScripter, and if txt file EOF is reached, doesn't use default for remainder of inputs
        currInput = input("Would you like to {}? Enter 'YES' or 'NO' (or hit ENTER for 'NO').".format(inputQuery))
        if currInput == "":
            print("Using default value: [NO]\n")
            return False

        elif currInput in ("QUIT","Quit","quit","Q","q"):
            print("Quitting...")
            raise SystemExit

        elif currInput in ('YES','Yes','yes','Y','y'):
            print("")
            return True

        elif currInput in ('NO','No','no','N','n'):
            print("")
            return False
        else:
            error("Invalid input value: "+currInput)

def validateSatelliteDateChoice(inputChoice,allowedInputs):
    """
    # Function:     VALIDATE SATELLITE DATE CHOICE
    #
    # Description:  This function validates the user input of satellite date choice.
    #
    # Parameters:   inputChoice     - The choice input by the user
    #               allowedInputs   - List of allowed integers
    #
    # Returns:      True if the user input a value in the allowedInputs list.
                    False if the user input anything else.
    """
    try:
        intInput = int(inputChoice)
        if intInput in allowedInputs:
            return True
        else:
            return False
    except:
        return False

#=======================================================================================
# Function:     GET SATELLITE DATE CHOICE
#
# Description:  This function will ask the user to select a date to process satellite
#               images for. They must input the number of the selection.
#
# Parameters:   None.
#
# Returns:      The value of the enum at the index input by the user.

def getSatelliteDateChoice():
    print("For which Sentinel-2 image date would you like to process images?\n")
    print("[1] MAY 23, 2023")

    currInput = input("Enter your choice: ")

    if currInput == "":
        print("Using default value: [1]")
        return SatelliteDates.MAY23_2023

    elif validateSatelliteDateChoice(currInput,allowedInputs=[1]):
        print("\nUsing input value: [{}]".format(currInput))
        return SatelliteDates(int(currInput))

    else:
        print("\nInvalid choice. Defaulting to [1] MAY 23, 2023.")
        return SatelliteDates.MAY23_2023

def validate_ExistingPath(inPath):
	if os.path.exists(inPath):
		return True
	else:
		print("Path does not exist:"+inPath)
		return False
	
def getPolygonsFromCSV(polygonCSVPath=None):
    """
    # Function:     GET POLYGONS FROM CSV
    #
    # Description:  This function creates a list of polygons from a CSV file.
    #               Each polygon consists of its shape ID and coordinates.
    #
    # Parameters:   polygonCSVPath  - str. Path to CSV containing polygon vertices.
                        Shorelines will be mapped for each polygon area.
    #                   For more details about the formatting of the CSV, see the README.
    #
    # Returns:      polygonList  - list. [[shapeID, ptList],] where ptList is [[lon, lat],]
                        ```
                        polygonList = [['0', [['-62.59394899', '45.56531847'], ['-62.59394566', '46.02171974'], ['-62.51542156', '46.02169112'], ['-62.51550024', '45.56528993'], ['-62.59394899', '45.56531847']]],
                                       ['1', [['-62.51550024', '45.56528993'], ['-62.51542156', '46.02169112'], ['-62.44089783', '46.02160989'], ['-62.44105187', '45.56520895'], ['-62.51550024', '45.56528993']]]]
                        ```
    """
    if not polygonCSVPath: polygonCSVPath = getUserInput("POLYGON LIST CSV PATH", DEFAULT_POLYGONS_PATH, validate_ExistingPath)
    polygonCSVPath = polygonCSVPath.strip('"').strip("'") #else cannot copy-paste from Windows File Explorer Copy Path
    print("CREATING POLYGON LIST FROM CSV FILE...")

    polygonDict = OrderedDict() #{shapeID:[pt,pt],} #dict of all coordinates of all polygons. Could just use regualar dict; user likely doesn't care

    # The resulting list of polygons (list of lists)
    polygonList = []

    with open(polygonCSVPath,'r') as polygonCSVFile:
        csvreader = csv.reader(polygonCSVFile)

        # Skip the header row
        next(csvreader)

        for split in csvreader:
            if len(split) == 0: continue #handle blank row at end
            shapeID = split[0]
            currPt = [(split[1]),(split[2])]

            if shapeID not in polygonDict: polygonDict[shapeID] = [] #ptList
            polygonDict[shapeID].append(currPt)

        polygonList = [[shapeID, ptList] for shapeID,ptList in polygonDict.items()] #convert to list just because that is what existing functions require

        print("POLYGONS READY! CLOSING FILE.\n")

    #Summarize results so user knows they didn't use wrong csv / make mistake in their csv creation
    print("Num polygons extracted:",len(polygonList))
    print("First polygon ID: ",polygonList[0][0])
    print("Last polygon ID: ",polygonList[-1][0])

    return polygonList

def setCoastSatConfig(inputs):
    ## TODO: GET SOME OF THESE SETTINGS AS USER INPUTS?
    """
    # Function:     SET COASTSAT CONFIG
    #
    # Description:  This function sets configuration settings for the
    #               CoastSat toolkit.
    #
    Parameters:
    -----------
    inputs: dict defined by coastsat with the following keys
        'sitename': str
            name of the site
        'polygon': list
            polygon containing the lon/lat coordinates to be extracted,
            longitudes in the first column and latitudes in the second column,
            there are 5 pairs of lat/lon with the fifth point equal to the first point:
            ```
            polygon = [[[151.3, -33.7],[151.4, -33.7],[151.4, -33.8],[151.3, -33.8],
            [151.3, -33.7]]]
            ```
        'dates': list of str
            list that contains 2 strings with the initial and final dates in
            format 'yyyy-mm-dd':
            ```
            dates = ['1987-01-01', '2018-01-01']
            ```
        'sat_list': list of str
            list that contains the names of the satellite missions to include:
            ```
            sat_list = ['L5', 'L7', 'L8', 'S2']
            ```
        'filepath_data': str
            filepath to the directory where the images are downloaded
        'landsat_collection': ##UNDOCUMENTED in coastsat
    
    Returns:
    -----------
    settings: dict defined by coastsat with the following keys
    
    #               GENERAL PARAMETERS
    #
    #                   cloud_thresh     - The threshold on maximum cloud cover.
    #
    #                   dist_clouds      - The distance around clouds where shoreline
    #                                      can't be mapped.
    #
    #                   output_epsg      - The EPSG code of spatial reference system
    #                                      desired for the output.
    #
    #               QUALITY CONTROL
    #
    #                   check_detection  - If True, shows each shoreline detection to the
    #                                      user for validation.
    #
    #                   adjust_detection - If True, allows user to adjust the postion of
    #                                      each shoreline by changing the threshold.
    #
    #                   save_figure      - If True, saves a figure showing the mapped
    #                                      shoreline for each image.
    #
    #               SHORELINE DETECTION PARAMETERS
    #
    #                   min_beach_area   - The inimum area (in metres squared) for an
    #                                      object to be labelled as a beach.
    #
    #                   min_length_sl    - The minimum length (in metres) of shoreline
    #                                      perimeter to be valid.
    #
    #                   cloud_mask_issue - If True, sand pixels are masked (in black) on
    #                                      many images.
    #
    #                   sand_color       - 'default', 'latest', 'dark' (for grey/black sand
    #                                      beaches) or 'bright' (for white sand beaches).
    #
    #                   pan_off          - True to switch pansharpening off for Landsat 7,
    #                                      8, and 9 imagery.
    #
    #                   inputs           - the dict that was input (see Parameters)
    """
    print("Configuring CoastSat...")
    settings = {

        # GENERAL PARAMETERS
        'cloud_thresh': 0.9,
        'dist_clouds': 300,
        'output_epsg': 3857,

        # QUALITY CONTROL
        'check_detection': False,
        'adjust_detection': False,
        'save_figure': False,

        # [***ONLY FOR ADVANCED USERS***]
        # SHORELINE DETECTION PARAMETERS
        'min_beach_area': 1000,
        'min_length_sl': 500,
        'cloud_mask_issue': False,
        'sand_color': 'default',
        'pan_off': False,

        # Add the global inputs
        'inputs': inputs, #referenced, so will update when inputs is updated
    }

    print("CoastSat configured!\n")

    return settings

#=======================================================================================
# Function:     SET GLOBAL INPUTS
#
# Description:  This function sets global configurations from global inputs. The inputs
#               are stored in the global 'inputs' variable.
#
# Parameters:   None. However, values are set using user inputs.
#
# Returns:      None.

def setGlobalInputs(inputs,foldername=None):
    print("Setting global configurations...\n")

    if not foldername: foldername = getUserInput("FOLDER NAME", DEFAULT_FOLDER_NAME)
    filepath = os.path.join(os.getcwd(), 'data', foldername)
    geofilepath = os.path.join(os.getcwd(), 'data', 'GEOJSON', foldername)

    # Set inputs
    globalInputs = {'foldername': foldername, ##NOT used by coastsat. Actually projectname/runname/outputname
                    'filepath': filepath, ##used by coastsat retrieve_images, save_jpg etc
                    'geofilepath': geofilepath} ##NOT used by coastsat. Output GeoJSON file

    inputs.update(globalInputs)

#=======================================================================================
# Function:     SET GEOJSON PREP INPUTS
#
# Description:  This function sets the configurations for the GeoJSON prep from user
#               inputs. The inputs are stored in the global 'inputs' variable.
#
# Parameters:   None. However, values are set using user inputs.
#
# Returns:      None.

def setGeoJSONPrepInputs(inputs,dates=None,poly_list=None,sat_list=None,landsat_collection=None,download_images=None,save_jpgs=None):
    print("Setting GeoJSON prep configurations...\n")

    # Get values from user input
    if not dates or not poly_list:
        dateSelection = getSatelliteDateChoice()
        dates = [dateSelection.startDate, dateSelection.endDate]
        poly_list = dateSelection.polyList
    print("Selected dates:",dates)
    print("Number of polygons to process: {}\n".format(len(poly_list))) ##incorrect; depends on CSV
    if not sat_list: sat_list = getUserInput("SATELLITE LIST", DEFAULT_SAT_LIST)
    if not landsat_collection: landsat_collection = getUserInput("COLLECTION", DEFAULT_COLLECTION) ##does it make sense to use both landsat and sentinel? how do these params interact?
    if download_images is None: download_images = getUserYesOrNo("DOWNLOAD IMAGES FROM GEE")
    if save_jpgs is None: save_jpgs = getUserYesOrNo("SAVE JPGS")

    # Set inputs
    geoJSONPrepInputs = { 'dates': dates, ##used by coastsat retrieve_images etc
                          'sat_list': sat_list, ##used by coastsat retrieve_images etc
                          'landsat_collection': landsat_collection, ##used by coastsat retrieve_images, extract_shorelines even though their doc doesn't say so
                          'save_jpgs': save_jpgs, ##NOT used by coastsat
                          'download_images': download_images, ##NOT used by coastsat
                          'poly_list': poly_list} ##NOT used by coastsat. Allowed Ids

    inputs.update(geoJSONPrepInputs)

    print("GeoJSON prep configurations ready to go!")

def setCurrPolyInputs(projectName, shapeId, polyCoords, inputs):
    """
    # Function:     SET CURRENT POLYGON INPUTS
    #
    # Description:  This function sets the coastsat inputs specific to the current polygon.
                    It updates the 'inputs' dict variable.
    #
    # Parameters:
        -----------
    projectName: str. Sitename will be [projectName]_[shapeId].
    shapeId: Polygon ID. Sitename will be [projectName]_[shapeId].
    polyCoords: list of pairs of coordinates defining a polygon. In clockwise order;
        first and last points must match
    inputs: dict

    # Returns:
    None: The input 'inputs' dict is updated with the following keys defined by coastsat
        'sitename': str. [projectName]_[shapeId].
        'polygon': list
            polygon containing the lon/lat coordinates to be extracted,
            longitudes in the first column and latitudes in the second column,
            there are 5 pairs of lat/lon with the fifth point equal to the first point:
            ```
            polygon = [[[151.3, -33.7],[151.4, -33.7],[151.4, -33.8],[151.3, -33.8],
            [151.3, -33.7]]]
            ```
    """
    # Put the polygon coordinates list in another list
    polyCoordsList = []
    polyCoordsList.append(polyCoords)

    # Recommended by CoastSat to run this method that makes sides parallel to
    # coordinate axes
    polygon = SDS_tools.smallest_rectangle(polyCoordsList)

    # Sitename is "projectName_shapeId"
    sitename = "{}_{}".format(projectName,shapeId)

    currConfig = {'polygon': polygon,
                  'sitename': sitename}

    # Update inputs with the config of the current polygon
    inputs.update(currConfig)

def retrieveImages(inputs,downloadImages=False):
    """
    # Function:     RETRIEVE IMAGES
    #
    # Description:  This function retrieves the images to be processed. The images are
    #               either downloaded from Google Earth Engine (GEE) or from local files.
    #
    # Parameters:
        -----------
    inputs: dict defined by coastsat with the following keys
        'sitename': str
            name of the site
        'polygon': list
            polygon containing the lon/lat coordinates to be extracted,
            longitudes in the first column and latitudes in the second column,
            there are 5 pairs of lat/lon with the fifth point equal to the first point:
            ```
            polygon = [[[151.3, -33.7],[151.4, -33.7],[151.4, -33.8],[151.3, -33.8],
            [151.3, -33.7]]]
            ```
        'dates': list of str
            list that contains 2 strings with the initial and final dates in
            format 'yyyy-mm-dd':
            ```
            dates = ['1987-01-01', '2018-01-01']
            ```
        'sat_list': list of str
            list that contains the names of the satellite missions to include:
            ```
            sat_list = ['L5', 'L7', 'L8', 'S2']
            ```
        'filepath_data': str
            filepath to the directory where the images are downloaded
		'landsat_collection': ##UNDOCUMENTED in coastsat

    Returns:
    -----------
    metadata: dict defined by coastsat
        contains the information about the satellite images that were downloaded:
        date, filename, georeferencing accuracy and image coordinate reference system
    """
    if downloadImages:
        print("Downloading images from GEE...")
        metadata = SDS_download.retrieve_images(inputs)

    else:
        print("Referencing local images...")
        metadata = SDS_download.get_metadata(inputs)

    print("Images acquired!\n")

    return metadata

def mapShorelines(metadata, settings, minAcceptAccuracy=10):
    """
    # Function:     MAP SHORELINES
    #
    # Description:  This function extracts the shoreline from the images according to the
    #               configured CoastSat settings. The shoreline output is processed to
    #               remove duplicates (images taken on the same date by the same satellite)
    #               and inaccurate georeferencing (set threshold to 10m).
    #
    Parameters:
    -----------
    metadata: dict defined by coastsat
        contains all the information about the satellite images that were downloaded
    settings: dict defined by coastsat with the following keys
        'inputs': dict
            input parameters (sitename, filepath, polygon, dates, sat_list, landsat_collection)
        'cloud_thresh': float
            value between 0 and 1 indicating the maximum cloud fraction in
            the cropped image that is accepted
        'cloud_mask_issue': boolean
            True if there is an issue with the cloud mask and sand pixels
            are erroneously being masked on the image
        'min_beach_area': int
            minimum allowable object area (in metres^2) for the class 'sand',
            the area is converted to number of connected pixels
        'min_length_sl': int
            minimum length (in metres) of shoreline contour to be valid
        'sand_color': str
            default', 'dark' (for grey/black sand beaches) or 'bright' (for white sand beaches)
        'output_epsg': int
            output spatial reference system as EPSG code
        'check_detection': bool
            if True, lets user manually accept/reject the mapped shorelines
        'save_figure': bool
            if True, saves a -jpg file for each mapped shoreline
        'adjust_detection': bool
            if True, allows user to manually adjust the detected shoreline
        'pan_off': bool
            if True, no pan-sharpening is performed on Landsat 7,8 and 9 imagery
    minAcceptAccuracy: int
        minimum horizontal georeferencing accuracy (metres) for a shoreline to be accepted

    Returns:
    -----------
    shorelineOutput: dict defined by coastsat
        contains the extracted shorelines and corresponding dates + metadata

    """
    shorelineOutput = SDS_shoreline.extract_shorelines(metadata, settings)
    shorelineOutput = SDS_tools.remove_duplicates(shorelineOutput)
    shorelineOutput = SDS_tools.remove_inaccurate_georef(shorelineOutput, minAcceptAccuracy)
    print("Shorelines mapped!\n")

    return shorelineOutput

def saveAsJPGs(metadata, settings):
    """
    # Function:     SAVE AS JPGS
    #
    # Description:  This function saves the extracted images as JPGs. The user inputs
    #               whether or not the JPGs images should be saved.
    #
    Parameters:
    -----------
    metadata: dict defined by coastsat
        contains all the information about the satellite images that were downloaded
    settings: dict defined by coastsat with the following keys
        'inputs': dict
            input parameters (sitename, filepath, polygon, dates, sat_list)
        'cloud_thresh': float
            value between 0 and 1 indicating the maximum cloud fraction in
            the cropped image that is accepted
        'cloud_mask_issue': boolean
            True if there is an issue with the cloud mask and sand pixels
            are erroneously being masked on the images

    Returns:
    -----------
    None: Stores the images as .jpg in a folder named /preprocessed
    """
    print("Saving JPGs...")
    SDS_preprocess.save_jpg(metadata, settings) #coastsat prints location saved
    print("JPGs saved!\n")

def exportGeoJson(shorelineOutput, settings, geomtype = 'lines'):
    ## TODO: SET GEOMETRY TYPE AS AS POINTS OR LINES FROM USER INPUT
    """
    # Function:     EXPORT GEOJSON
    #
    # Description:  This function exports the shoreline output as a GeoJSON file in the
    #               GeoJSON folder.
    #
    #               Note that the geometry type of the layer can be set to 'points' or
    #               'lines'.
    #
    # Parameters:   shorelineOutput: dict defined by coastsat
    #                   contains the extracted shorelines and corresponding dates + metadata
    #               geomtype: 'lines' for LineString or 'points' for Multipoint geometry.
    #                   The geometry type of the output layer
    #
    # Returns:      outputFile: str
                        Name of the output geoJSON file
    """
    print("Exporting GeoJSON...")

    gdf = SDS_tools.output_to_gdf(shorelineOutput, geomtype)

    if gdf is None:
        raise Exception("Output does not contain any mapped shorelines.")

    # Set layer projection
    gdf.crs = CRS(settings['output_epsg'])

    # Create GEOJSON folder if it doesn't exist
    geofilepath = settings['inputs']['geofilepath']
    if not os.path.isdir(geofilepath):
        os.makedirs(geofilepath)

    # Save GEOJSON layer to file
    outputFile = os.path.join(geofilepath,'%s_output_%s.geojson'%(settings['inputs']['sitename'],geomtype))
    print("Saving to "+outputFile)
    gdf.to_file(outputFile,
                driver='GeoJSON',
                encoding='utf-8')
    print("GeoJSON exported!\n")

    return outputFile

def processPolygonCheck(shapeId, polyList):
    """
    # Function:     PROCESS POLYGON CHECK
    #
    # Description:  This function determines whether or not a polygon should be processed
    #               according to its shape ID.
    #
    # Parameters:   shapeId     - The shape ID of the polygon.
    #               polyList    - A list of allowed IDs.
    #
    # Returns:      True or false indicating if the polygon should be processed or not.
    """
    if shapeId in polyList:
        return True

    else:
        return False

def processPolygon(shapeId, coords, settings, inputs): ##no need for both settings and coastsat inputs
    """
    # Function:     PROCESS POLYGON
    #
    # Description:  This function processes a single polygon to produce a GeoJSON file.
    #
    # Parameters:   shapeId     - The shape ID of the polygon.
    #               coords      - The coordinates of the polygon
                    settings    - dict defined by coastsat
                    inputs      - dict. Catchall for various params ##TO BE MODIFIED
    #
    # Returns:      None.
    """
    print(">>>>>>>>>>>>>>>>>>>>>> PROCESSING POLYGON: [{}] >>>>>>>>>>>>>>>>>>>>>>\n".format(shapeId))
    setCurrPolyInputs(inputs['foldername'], shapeId, coords, inputs)
    metadata = retrieveImages(inputs, inputs['download_images'])
    shorelineOutput = mapShorelines(metadata, settings)
    if inputs['save_jpgs']:
        saveAsJPGs(metadata, settings)
    exportGeoJson(shorelineOutput, settings)

def displayUpdateMessage(polySuccessCount, polygonsRemaining, polyErrs, procStartTime):
    """#=======================================================================================
    # Function:     DISPLAY UPDATE MESSAGE
    #
    # Description:  This function prints an update message displaying the status of the
    #               program and the progress made.
    #
    # Parameters:   polySuccessCount    - # polygons processed successfully
    #               polygonsRemaining   - # polygons still-to-process
    #               polyErrs            - list of polygons which were not processed successfully
    #               procStartTime       - datetime of the start of processing
    #
    # Returns:      None.
    """
    print("|-------------------------------------------------------------------")
    print("|CURRENT STATS:")
    print("|   Successful polygons:         ",polySuccessCount)
    print("|   Remaining polygons:          ",polygonsRemaining)
    print("|   Polygons with errors:        ",len(polyErrs))
    print("|   Processing time:             ",datetime.now()-procStartTime)
    print("|-------------------------------------------------------------------\n")

def displayCompleteMessage(polySuccessCount, polygonsRemaining, polyErrs, procStartTime, startTime):
    """#=======================================================================================
    # Function:     DISPLAY COMPLETE MESSAGE
    #
    # Description:  This function prints statistics about the program's current run.
    #
    # Parameters:   polySuccessCount    - # polygons processed successfully
    #               polygonsRemaining   - # polygons still-to-process
    #               polyErrs            - list of polygons which were not processed successfully
    #               procStartTime       - datetime of the start of processing
    #               startTime           - datetime of the start of running
    #
    # Returns:      None.
    """
    print("|===================================================================")
    print("|FINAL STATS:")
    print("|   Total # successful polygons: ",polySuccessCount)
    print("|   Total # polygons with errors:",len(polyErrs))
    print("|   Polygons with errors:        ",polyErrs)
    print("|   Total processing time:       ",datetime.now()-procStartTime)
    print("|   Total run time:              ",datetime.now()-startTime)
    print("|===================================================================\n")

def prepareGeoJSON(polygonCSVPath=None, foldername=None, sat_list=None, landsat_collection=None, dates=None, poly_list=None, download_images=None, save_jpgs=None):
    """
    # Function:     PREPARE GEOJSON
    #
    # Description:  This function prepares GeoJSON files of the coastline using the
    #               CoastSat toolkit. All of the resulting GeoJSON files will be stored
    #               in one folder.
    #
    Parameters:
    -----------
    polygonCSVPath: str
        Path to CSV containing polygon vertices. Shorelines will be mapped for each polygon area.
        For more details about the formatting of the CSV, see the README.
    foldername: str
        Name representing this run session. Will be used for ##TO FILL OUT
    sat_list: list of str. Any subset of ['L5','L7','L8','L9','S2'] as a list
        list that contains the names of the satellite missions to include:
        ```
        sat_list = ['L5', 'L7', 'L8', 'S2']
        ```
    landsat_collection: str. 'C01' or 'C02'
        ##UNDOCUMENTED in coastsat. How does it interact with S2?
    dates: list of str
        list that contains 2 strings with the initial and final dates in
        format 'yyyy-mm-dd':
        ```
        dates = ['1987-01-01', '2018-01-01']
        ```
    poly_list: list
        Allowed polygon ids. Lets you process a subset of CSV polygon IDs. 
        Will only process features from the CSV which are in this list.
    download_images: bool
        Whether to download images from GEE or look for already-downloaded local images.
    save_jpgs: bool
        Whether to use coastsat's sav_jpg function to 'Save a .jpg image for all the images contained in metadata.'
        
    Returns:
    -----------
    """
    startTime = datetime.now() #start when the main function you are timing is called, not when the script is imported (which is when globals are set)
    
    # Acquire and validate user inputs, including CSV polygons
    inputs = {}
    setGlobalInputs(inputs,foldername) #will ask for user input if necessary
    polygonList = getPolygonsFromCSV(polygonCSVPath) #will ask for user input if necessary
    ##CHANGE SO NOT ALL VARIABLES IN CATCHALL DICT 'inputs'
    setGeoJSONPrepInputs(inputs,dates,poly_list,sat_list,landsat_collection,download_images,save_jpgs) #will ask for user input if necessary
    settings = setCoastSatConfig(inputs) ##DO NOT hand this function non-coastsat variables in inputs!!
    
    # Variables to track progress
    polySuccessCount = 0
    polyErrs = []
    procStartTime = datetime.now()
    polygonsRemaining = len(inputs['poly_list']) ##not true; depends on CSV

    # Process each polygon
    print("Processing polygons...\n")
    unprocessedList = []
    for polygon in polygonList:

        # Get the shape ID of the current polygon
        shapeId = polygon[0]

        # Check if we want to process the current polygon with that shapeId
        if processPolygonCheck(int(shapeId), inputs['poly_list']): ##inputs['poly_list'] via setGeoJSONPrepInputs via getSatelliteDateChoice via SatelliteDates

            # Process a polygon
            try:
                processPolygon(shapeId, polygon[1], settings, inputs)
                polySuccessCount += 1
                polygonsRemaining -= 1

            except Exception as e:
                print("\n*!*!*!* ERROR *!*!*!* {} \n".format(str(e)))
                raise e ##for testing
                # Keep track of any errored polygons
                polyErrs.append(shapeId)

            # After each polygon is processed display an update message
            displayUpdateMessage(polySuccessCount, polygonsRemaining, polyErrs, procStartTime)
        else:
            unprocessedList.append(shapeId)

    # After all polygons are processed display a complete message
    print("The following polygon ids were not processed as they were not in the allowed list for the selected date:",unprocessedList)
    displayCompleteMessage(polySuccessCount, polygonsRemaining, polyErrs, procStartTime, startTime)

#=======================================================================================

if __name__ == '__main__': #necessary if anyone might want to import this script without running it (ex: to use help(Prepare_GeoJSON), for testing, to access/reuse functions in per-AOI wrapper scripts)
    # LET'S ACTUALLY RUN IT!
    # CHOOSE ONE OPTION for how to run the script
     
    # OPTION 1: enter input params from command line
    ##prepareGeoJSON()
    
    # OPTION 2: set params here. Run from within a code editor or on command line using these defaults
    prepareGeoJSONParams = {
        'polygonCSVPath': DEFAULT_POLYGONS_PATH,
        'foldername': DEFAULT_FOLDER_NAME, ##rename to something like projectname, runname?? Leaving for now for historical clarity
        'sat_list': DEFAULT_SAT_LIST,
        'landsat_collection': DEFAULT_COLLECTION,
        'dates': [DEFAULT_STARTDATE, DEFAULT_ENDDATE],
        'poly_list': DEFAULT_POLYLIST,
        'download_images': False,
        'save_jpgs': False
    }
    prepareGeoJSON(**prepareGeoJSONParams)
    ##do Enum per-AOI SatelliteDates options in wrapper; send simple params to prepareGeoJSON

    print("==================================================================================\n")
