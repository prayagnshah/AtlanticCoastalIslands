#=======================================================================================
#=======================================================================================
#
# Program:      Coastal Extraction from Sentinel-2 Satellite Imagery to GeoJSON using
#               the CoastSat Toolkit
# File Name:    Prepare_GeoJSON.py
# Author:       Anneke van der Laan & updated by Leah Fulton
# Version:      1.5
# Date:         June 08, 2023
# Purpose:      EPM GIS Contract
#
# Description:  This program uses the CoastSat 2.1 open-source software toolkit
#               to extract the coastline from Sentinel-2 satellite imagery of input
#               areas as GeoJSON polyline files. The coastline is extracted in
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
from    os import walk

import  numpy as np
import  pickle
import  warnings
warnings.filterwarnings("ignore")

import  matplotlib
matplotlib.use('Qt5Agg')

import  matplotlib.pyplot as plt
from    matplotlib import gridspec
plt.ion()

import  pandas as pd

from    datetime import datetime
from    coastsat import SDS_download, SDS_preprocess, SDS_shoreline, SDS_tools, SDS_transects
from    pyproj   import CRS
from    enum     import Enum

print("Good to go! Let's get started.\n")

#=======================================================================================
# SET DEFAULT VALUES FOR USER INPUTS

DEFAULT_POLYGONS_PATH = r"C:\Users\annek\Documents\CoastSat\data\PointsReady.csv"
DEFAULT_FOLDER_NAME = "FINAL_TEST_1"

# Satellite Options: Any subset of ['L5','L7','L8','L9','S2'] as a list
DEFAULT_SAT_LIST = ['S2']

# Landsat Collection Options: 'C01' or 'C02'
DEFAULT_COLLECTION = 'C02'

#=======================================================================================
# SET PROGRAM STATISTICS

global inputs
inputs = {}
global procStartTime
startTime = datetime.now()
polySuccessCount = 0
polyErrs = []

#=======================================================================================
# DEFINE SATELLITE DATES ENUM AND SET THE POLYGON LIST FOR EACH DATE

# POLYGON LIST - SEPT 19, 2019
polyList_sept_19_2019 = ['1','2','3','4',
                         '9','10','11','12','13','14',
                         '22','23','24','25','26','27','28','29',
                         '39','40','41','42','43','44',
                         '51','52','53','54','55','56','57',
                         '68','69','70','71','72','73',
                         '82','83','84','85','86','87',
                         '98','99','100','101','102','103','104',
                         '117','118','119','120','121',
                         '141','142','143','144','145','146','147',
                         '171','172','173','174','175','176','177','178','179','180',
                         '217','218','219','220','221','222','223','224','225','226','227','228',
                         '252','253','254','255','256','257','258','259','260','261','262','263',
                         '274','275','276','277','278','279','280','281','282','283',
                         '290','291','292','293','294','295','296','297','298','299',
                         '302','303','304','305','306','307',
                         '311','312','313','314','315','316','317','318',
                         '321','322','323','324','325','326','327','328',
                         '331','332','333','334','335','336','337','338',
                         '341','342','343','344','345',
                         '351','352','353','354','355','356','357','358','359','360',
                         '370','371','372','373','374','375','376','377','378',
                         '384','385','386','387','388','389','390','391']

# POLYGON LIST - OCT 10, 2019
polyList_oct_10_2019 = [
    '105', '122', '123', '124', '148', '149', '150', '151', '152', '153', '154',
    '181', '182', '183', '184', '185', '186', '187', '188', '189', '190', '191',
    '192', '193', '194', '195', '196', '197', '230', '231', '232', '233', '234',
    '235', '236', '237', '266', '267', '286', '330', '340', '348', '349', '350',
    '366', '367', '368', '369', '421', '422', '423', '424', '432', '433', '434',
    '435', '436', '442', '443', '444', '445', '446', '454', '455', '456', '457',
    '458', '466', '467', '468', '469', '470', '471', '481', '482', '483', '484',
    '485', '486', '487', '488', '489', '490', '491', '492', '513', '514', '515',
    '516', '533', '593', '635', '636', '644', '652', '658', '675', '676', '677',
    '678', '679', '680', '681', '682', '683', '684', '685', '686', '687', '688',
    '689', '690', '691', '692', '693', '694', '695', '696', '697', '698', '699',
    '670', '701', '702', '703', '704', '705', '706', '707', '708'
]

# POLYGON LIST - SEPT 06, 2020
polyList_sept_06_2020 = [
    '5', '6', '7', '8', '15', '16', '17', '18', '19', '20', '21', '30', '31', '32',
    '33', '34', '35', '36', '37', '38', '45', '46', '47', '48', '49', '50', '58',
    '59', '60', '61', '62', '63', '64', '65', '66', '67', '74', '75', '76', '77',
    '78', '79', '80', '81', '88', '89', '90', '91', '92', '93', '94', '95', '96',
    '106', '107', '108', '109', '110', '111', '112', '113', '114', '115', '116',
    '125', '126', '127', '128', '129', '130', '131', '132', '133', '134', '135',
    '136', '137', '138', '139', '140', '141', '155', '156'
]


# POLYGON LIST - SEPT 16, 2020
polyList_sept_16_2020 = [
    '157', '158', '159', '160', '161', '162', '163', '164', '165', '166', '167', '168',
    '169', '170', '171', '198', '199', '200', '201', '202', '203', '204', '205', '206',
    '207', '208', '209', '210', '211', '212', '213', '214', '215', '216', '217', '238',
    '239', '240', '241', '242', '243', '244', '245', '246', '247', '248', '249', '250',
    '251', '252', '268', '269', '270', '271', '272', '273', '274', '287', '288', '289',
    '290', '341', '351'
]


# POLYGON LIST - SEPT 21, 2020
polyList_sept_21_2020 = [
    '384', '385', '386', '387', '388', '389', '390', '391', '396', '397', '398', '399',
    '400', '400', '401', '402', '403', '404', '407', '408', '409', '410', '411', '412',
    '415', '416', '417', '418', '419', '425', '426', '427', '428', '437', '438', '439',
    '440', '447', '448', '449', '450', '451', '452', '459', '460', '461', '462', '463',
    '464', '472', '473', '474', '475', '476', '477', '478', '479', '493', '494', '495',
    '496', '497', '498', '499', '500', '501', '502', '517', '518', '519', '520', '521',
    '522', '523', '524', '534', '535', '536', '537', '538', '539', '540', '549', '550',
    '551', '552', '553', '554', '555', '565', '566', '567', '568', '579', '580'
]


# POLYGON LIST - MAY 20, 2022
polyList_may_20_2022 = [
    '0', '229', '264', '265', '284', '285', '300', '301', '308', '309', '310', '319',
    '320', '329', '339', '346', '347', '361', '362', '363', '364', '365', '379', '380',
    '381', '382', '383', '392', '393', '394', '395', '405', '406', '413', '414', '420',
    '429', '430', '431', '441', '453', '465', '480'
]


# POLYGON LIST - JUNE 16, 2022
polyList_june_16_2022 = [
    '503', '504', '505', '506', '507', '508', '509', '510', '511', '512', '525', '526',
    '527', '528', '529', '530', '531', '532', '541', '542', '543', '544', '545', '546',
    '548', '556', '557', '558', '559', '560', '561', '562', '563', '564', '569', '570',
    '571', '572', '573', '574', '575', '576', '577', '581', '583', '584', '585', '586',
    '587', '588', '589', '590', '591', '592', '594', '595', '596', '597', '598', '599',
    '600', '601', '602', '603', '604', '605', '606', '607', '608', '609', '610', '611',
    '612', '613', '614', '615', '616', '617', '618', '619', '620', '621', '622', '623',
    '624', '625', '626', '627', '628', '629', '630', '631', '632', '633', '634', '637',
    '638', '639', '640', '641', '642', '645', '646', '647', '648', '649', '650', '651',
    '653', '654', '655', '656', '657', '659', '660', '661', '662', '663', '664', '665',
    '666', '667', '668', '669', '670', '671', '672', '673', '674'
]


# For testing:
polyList_testing = ['1']

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

    SEPT_19_2019 = ('2019-09-18', '2019-09-20', polyList_sept_19_2019)
    OCT_10_2019  = ('2019-10-09', '2019-10-11', polyList_oct_10_2019)
    SEPT_06_2020 = ('2020-09-05', '2020-09-07', polyList_sept_06_2020)
    SEPT_16_2020 = ('2020-09-15', '2020-09-17', polyList_sept_16_2020)
    SEPT_21_2020 = ('2020-09-20', '2020-09-22', polyList_sept_21_2020)
    MAY_20_2022  = ('2022-05-19', '2022-05-21', polyList_may_20_2022)
    JUNE_16_2022 = ('2022-06-15', '2022-06-17', polyList_june_16_2022)
    TESTING      = ('2019-09-18', '2019-09-20', polyList_testing)

#=======================================================================================
# Function:     GET USER INPUT
#
# Description:  This function will request input from the user and return the response.
#
# Parameters:   desiredInput    - The kind of input desired.
#               defaultValue    - The default value for that input.
#
# Returns:      The value that was input by the user. If the user inputs nothing,
#               the default value is returned.

# TODO: IMPROVE THE USER INPUT CHECK TO BE MORE ROBUST

def getUserInput(desiredInput, defaultValue):
    print("Input {} or hit ENTER to accept the default value: [{}]".format(desiredInput,defaultValue))
    userInput = sys.stdin.readline().rstrip().lstrip()

    if userInput == "":
        print("Using default value: [{}]\n".format(defaultValue))
        return defaultValue

    elif userInput == "QUIT" or userInput == "quit" or userInput == "Q" or userInput == "q":
        print("Quitting...")
        raise SystemExit

    else:
        userInput = userInput.lstrip().rstrip()
        print("\nUsing input value: [{}]\n".format(userInput))
        return userInput

#=======================================================================================
# Function:     GET USER RESPONSE TO A YES OR NO QUESTION
#
# Description:  This function will ask the user a yes or no question and return the
#               response.
#
# Parameters:   inputQuery    - The subject of the yes or no question.
#
# Returns:      True if the user input 'YES'. False if the user input 'NO'.

# TODO: IMPROVE THE USER INPUT CHECK TO BE MORE VERSATILE

def getUserYesOrNo(inputQuery):
    print("Would you like to {}? Enter 'YES' or 'NO' (or hit ENTER for 'NO').".format(inputQuery))

    for currInput in sys.stdin:
        currInput = currInput.rstrip().lstrip()

        if currInput == "":
            print("Using default value: [NO]\n")
            return False

        elif currInput == "QUIT" or currInput == "quit" or currInput == "Q" or currInput == "q":
            print("Quitting...")
            raise SystemExit
        
        elif currInput == 'YES' or currInput == 'yes' or currInput == 'Y' or currInput == 'y':
            print("")
            return True

        elif currInput == 'NO' or currInput == 'no' or currInput == 'N' or currInput == 'n':
            print("")
            return False

        else:
            print("\nTry again. Would you like to {}? Enter 'YES' or 'NO' (or hit ENTER for 'NO').".format(inputQuery))

#=======================================================================================
# Function:     VALIDATE SATELLITE DATE CHOICE
#
# Description:  This function validates the user input of satellite date choice.
#
# Parameters:   inputChoice    - The choice input by the user
#
# Returns:      True if the user input 1, 2, 3, 4, 5, 6, 7 or 8. False if the user input anything else.

def validateSatelliteDateChoice(inputChoice):
    try:
        intInput = int(inputChoice)
        if intInput in [1, 2, 3, 4, 5, 6, 7, 8]:
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
    print("[1] September 19, 2019")
    print("[2] October 10, 2019")
    print("[3] September 6, 2020")
    print("[4] September 16, 2020")
    print("[5] September 21, 2020")
    print("[6] May 20, 2022")
    print("[7] June 16, 2022")
    print("[8] Testing")
    print("\nEnter 1 or 8 or hit ENTER to default to testing.")
    
    for currInput in sys.stdin:
        currInput = currInput.rstrip().lstrip()

        if currInput == "":
            print("Using default value: [8]")
            return SatelliteDates(8)
        
        elif validateSatelliteDateChoice(currInput):
            print("\nUsing input value: [{}]".format(currInput))
            return SatelliteDates(int(currInput))

        else:
            print("\nTry again. Hit ENTER to default to testing.")

#=======================================================================================
# Function:     GET POLYGONS FROM CSV
#
# Description:  This function creates a list of polygons from an CSV file.
#               Each polygon consists of its shape ID and coordinates.
#
# Parameters:   None. However, the path for the CSV file is one of the user inputs.
#               For more details about the formatting of the CSV, see the README.
#
# Returns:      None.

import csv

def getPolygonsFromCSV():
    polygonCSVPath = getUserInput("POLYGON LIST CSV PATH", DEFAULT_POLYGONS_PATH)
    print("CREATING POLYGON LIST FROM CSV FILE...")
    polygonCSVFile = open(polygonCSVPath, "r")

    # The shape ID of the current polygon
    # Initialize at ID zero
    currID = '0'

    # The list of all coordinates of the current polygon
    # Initialize empty
    currPoly = []

    # The resulting list of polygons (list of lists)
    global polygonList
    polygonList = []

    csvreader = csv.reader(polygonCSVFile)

    # Skip the header row
    next(csvreader)

    for split in csvreader:
        shapeID = split[0]
        currPt = [float(split[1]), float(split[2])]

        # If we're still on the same ID as the last point, add it to the current
        # polygon that is being processed.
        if shapeID == currID:
            currPoly.append(currPt)

        # If the ID changed, we are on a new polygon! Add the old one to the
        # results, empty the current list, and add the current coordinates to it!
        else:
            polygonList.append([currID, currPoly])
            currID = shapeID
            currPoly = []
            currPoly.append(currPt)

    print("POLYGONS READY! CLOSING FILE.\n")
    polygonCSVFile.close()

#=======================================================================================
# Function:     SET COASTSAT CONFIG
#
# Description:  This function sets the following configuration settings for the
#               CoastSat toolkit:
#
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
#               The settings are stored in the global 'settings' variable.
#
# Parameters:   None. 
#
# Returns:      None.

# TODO: GET SOME OF THESE SETTINGS AS USER INPUTS?

def setCoastSatConfig():
    print("Configuring CoastSat...")
    global settings
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
        'inputs': inputs,
    }

    print("CoastSat configured!\n")

#=======================================================================================
# Function:     SET GLOBAL INPUTS
#
# Description:  This function sets global configurations from global inputs. The inputs
#               are stored in the global 'inputs' variable.
#
# Parameters:   None. However, values are set using user inputs.
#
# Returns:      None.

def setGlobalInputs():
    print("Setting global configurations...\n")
    global inputs

    foldername = getUserInput("FOLDER NAME", DEFAULT_FOLDER_NAME)
    filepath = os.path.join(os.getcwd(), 'data', foldername)
    geofilepath = os.path.join(os.getcwd(), 'data', 'GEOJSON', foldername)

    # Set inputs
    globalInputs = {'foldername': foldername,
                    'filepath': filepath,
                    'geofilepath': geofilepath}

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

def setGeoJSONPrepInputs():
    print("Setting GeoJSON prep configurations...\n")
    global inputs

    # Get values from user input
    dateSelection = getSatelliteDateChoice()
    dates = [dateSelection.startDate, dateSelection.endDate]
    print("Selected dates:",dates)
    poly_list = dateSelection.polyList
    print("Number of polygons to process: {}\n".format(len(poly_list)))
    sat_list = getUserInput("SATELLITE LIST", DEFAULT_SAT_LIST)
    landsat_collection = getUserInput("COLLECTION", DEFAULT_COLLECTION)
    download_images = getUserYesOrNo("DOWNLOAD IMAGES FROM GEE")
    save_jpgs = getUserYesOrNo("SAVE JPGS")

    # Set inputs
    geoJSONPrepInputs = { 'dates': dates,
                          'sat_list': sat_list,
                          'landsat_collection': landsat_collection,
                          'save_jpgs': save_jpgs,
                          'download_images': download_images,
                          'poly_list': poly_list}

    inputs.update(geoJSONPrepInputs)

    print("GeoJSON prep configurations ready to go!")

#=======================================================================================
# Function:     SET GEOJSON PROCESSING INPUTS
#
# Description:  This function sets the configurations for the GeoJSON proc from user
#               inputs. The inputs are stored in the global 'inputs' variable.
#
# Parameters:   None. However, values are set using user inputs.
#
# Returns:      None.

def setGeoJSONProcInputs():
    print("Setting GeoJSON processing configurations...\n")
    global inputs

    # Get values from user input
    
    # TODO: Set the output feature class for the GeoJSON Lines
    output_fc = os.path.join("outgdb.gdb", inputs['foldername'])

    # Set inputs
    geoJSONProcInputs = { 'output_fc': output_fc}

    inputs.update(geoJSONProcInputs)

    print("GeoJSON processing configurations ready to go!\n")

#=======================================================================================
# Function:     SET CURRENT POLYGON INPUTS
#
# Description:  This function sets the inputs specific to the current polygon. The
#               inputs are stored in the global 'inputs' variable.
#
# Parameters:   None. 
#
# Returns:      None.

def setCurrPolyInputs(shapeId, polyCoords): 
    # Put the polygon coordinates list in another list
    polyCoordsList = []
    polyCoordsList.append(polyCoords)

    # Recommended by CoastSat to run this method that makes sides parallel to
    # coordinate axes     
    polygon = SDS_tools.smallest_rectangle(polyCoordsList)

    # Sitename is "foldername_shapeID"
    sitename = "{}_{}".format(inputs['foldername'],shapeId)

    currConfig = {'polygon': polygon,
                  'sitename': sitename}

    # Update inputs with the config of the current polygon
    inputs.update(currConfig)

#=======================================================================================
# Function:     RETRIEVE IMAGES
#
# Description:  This function retrieves the images to be processed. The images are
#               either downloaded from Google Earth Engine (GEE) or from local files.
#
# Parameters:   None. However, the download method is set earlier in the program from
#               a user input.
#
# Returns:      None.

def retrieveImages():
    global metadata

    if inputs['download_images']:
        print("Downloading images from GEE...")
        metadata = SDS_download.retrieve_images(inputs)

    else:
        print("Downloading local images...")
        metadata = SDS_download.get_metadata(inputs)

    print("Images downloaded!\n")

#=======================================================================================
# Function:     MAP SHORELINES
#
# Description:  This function extracts the shoreline from the images according to the
#               configured CoastSat settings. The shoreline output is processed to
#               remove duplicates (images taken on the same date by the same satellite)
#               and inaccurate georeferencing (set threshold to 10m). 
#
# Parameters:   None. However, the download method is set earlier in the program from
#               a user input.
#
# Returns:      None.

def mapShorelines():
    global shorelineOutput
    shorelineOutput = SDS_shoreline.extract_shorelines(metadata, settings)
    shorelineOutput = SDS_tools.remove_duplicates(shorelineOutput)
    shorelineOutput = SDS_tools.remove_inaccurate_georef(shorelineOutput, 10) 
    print("Shorelines mapped!\n")

#=======================================================================================
# Function:     SAVE AS JPGS
#
# Description:  This function saves the extracted images as JPGs. The user inputs
#               whether or not the JPGs images should be saved.
#
# Parameters:   None. However, the user inputs whether or not to save the images
#               as JPGs earlier in the program.
#
# Returns:      None.
    
def saveAsJPGs():
    if inputs['save_jpgs']:
        print("Saving JPGs...")
        SDS_preprocess.save_jpg(metadata, settings)
        print("JPGs saved!\n")
    
#=======================================================================================
# Function:     EXPORT GEOJSON
#
# Description:  This function exports the shoreline output as a GeoJSON file in the
#               GeoJSON folder.
#
#               Note that the geometry type of the layer can be set to 'points' or
#               'lines'.
#
# Parameters:   None.
#
# Returns:      None.

# TODO: SET GEOMETRY TYPE AS AS POINTS OR LINES FROM USER INPUT

def exportGeoJson():
    print("Exporting GeoJSON...")

    # Choose 'points' or 'lines' for the layer geometry
    geomtype = 'lines' 
    gdf = SDS_tools.output_to_gdf(shorelineOutput, geomtype)

    if gdf is None:
        raise Exception("Output does not contain any mapped shorelines.")

    # Set layer projection
    gdf.crs = CRS(settings['output_epsg']) 

    # Create GEOJSON folder if it doesn't exist
    geofilepath = inputs['geofilepath']
    if not os.path.isdir(geofilepath):
        os.makedirs(geofilepath)

    # Save GEOJSON layer to file
    gdf.to_file(os.path.join(geofilepath,'%s_output_%s.geojson'%(inputs['sitename'],geomtype)),
                driver='GeoJSON',
                encoding='utf-8')
    print("GeoJSON exported!\n")


#=======================================================================================
# Function:     PROCESS POLYGON CHECK
#
# Description:  This function determines whether or not a polygon should be processed
#               according to its shape ID.
#
# Parameters:   shapeId     - The shape ID of the polygon.
#
# Returns:      True or false indicating if the polygon should be processed or not.

def processPolygonCheck(shapeId):
    polyList = inputs['poly_list']

    if shapeId in polyList:
        return True

    else:
        return False

#=======================================================================================
# Function:     PROCESS POLYGON
#
# Description:  This function processing a single polygon to produce a GeoJSON file.
#
# Parameters:   shapeId     - The shape ID of the polygon.
#               coords      - The coordinates of the polygon
#
# Returns:      None.

def processPolygon(shapeId, coords):
    print(">>>>>>>>>>>>>>>>>>>>>> PROCESSING POLYGON: [{}] >>>>>>>>>>>>>>>>>>>>>>\n".format(shapeId))
    setCurrPolyInputs(shapeId, coords)
    retrieveImages()
    mapShorelines()
    saveAsJPGs()
    exportGeoJson()

#=======================================================================================
# Function:     DISPLAY UPDATE MESSAGE
#
# Description:  This function prints an update message displaying the status of the
#               program and the progress made.
#
# Parameters:   None.
#
# Returns:      None.

def displayUpdateMessage():
    print("|-------------------------------------------------------------------")
    print("|CURRENT STATS:")
    print("|   Successful polygons:         ",polySuccessCount)
    print("|   Remaining polygons:          ",polygonsRemaining)
    print("|   Polygons with errors:        ",len(polyErrs))
    print("|   Processing time:             ",datetime.now()-procStartTime)
    print("|-------------------------------------------------------------------\n")

#=======================================================================================
# Function:     DISPLAY COMPLETE MESSAGE
#
# Description:  This function prints statistics about the program's current run.
#
# Parameters:   None.
#
# Returns:      None.

def displayCompleteMessage():
    print("|===================================================================")
    print("|FINAL STATS:")
    print("|   Total # successful polygons: ",polySuccessCount)
    print("|   Total # polygons with errors:",len(polyErrs))
    print("|   Polygons with errors:        ",polyErrs)
    print("|   Total processing time:       ",datetime.now()-procStartTime)
    print("|   Total run time:              ",datetime.now()-startTime)
    print("|===================================================================\n")

#=======================================================================================
# Function:     PREPARE GEOJSON
#
# Description:  This function prepares GeoJSON files of the coastline using the
#               CoastSat toolkit. All of the resulting GeoJSON files will be stored
#               in one folder.
#
# Parameters:   None.
#
# Returns:      None.

def prepareGeoJSON():
    # Set up
    setGlobalInputs()
    getPolygonsFromCSV()
    setGeoJSONPrepInputs()
    setCoastSatConfig()

    # Variables to track progress
    global polySuccessCount
    global polygonsToProcess
    global polygonsRemaining
    global procStartTime
    procStartTime = datetime.now()
    polygonsRemaining = len(inputs['poly_list'])

    # Process each polygon
    print("Processing polygons...\n")
    for polygon in polygonList:

        # Get the shape ID of the current polygon
        shapeId = polygon[0]

        # Check if we want to process the current polygon with that shapeId
        if processPolygonCheck(shapeId):

            # Process a polygon
            try:
                processPolygon(shapeId,polygon[1])
                polySuccessCount += 1
                polygonsRemaining -= 1
 
            except Exception as e:
                print("\n*!*!*!* ERROR *!*!*!* {} \n".format(str(e)))
                # Keep track of any errored polygons
                polyErrs.append(shapeId)

            # After each polygon is processed display an update message
            displayUpdateMessage()

    # After all polygons are processed display a complete message
    displayCompleteMessage()

#=======================================================================================
# LET'S ACTUALLY RUN IT!

prepareGeoJSON()

print("==================================================================================\n")
