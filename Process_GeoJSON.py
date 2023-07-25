#=======================================================================================
#=======================================================================================
#
# Program:      GeoJSON Polyline Files to ArcGIS Feature Class using ArcPy
# File Name:    Process_GeoJSON.py
# Author:       Anneke van der Laan
# Version:      1.0
# Date:         April 10, 2023
# Purpose:      EPM GIS Contract
#
# Description:  This program processes GeoJSON polyline files to produce an aggregate 
#               polyline Feature Class using ArcPy tools.
#
# Credit:       The process for dissolving the line segments using buffers and spatial
#               join found in the Esri Community was used as the foundation for this
#               program.
#
#               Source - https://tinyurl.com/cj3m9fyk
#
#=======================================================================================
#=======================================================================================

#=======================================================================================
# SET UP

#Imports
import arcpy
import os
from os import walk
from datetime import datetime

# Track runtime
startTime = datetime.now()

#=======================================================================================
# Function:     LOG
#
# Description:  This function logs an input message to stdout with formatting to
#               display the current time and run time.
#
# Parameters:   message    - The message to log.
#
# Returns:      None.

def log(message):
    now = datetime.now()
    currTime = str(now.strftime("%H:%M:%S:%f"))[:-3]
    runTime = now - startTime
    print("[{}][{}] {}".format(currTime, runTime, message))

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

# TODO: VALIDATE USER INPUTS

def getUserInput(desiredInput, defaultValue):
    log("Input {} or hit ENTER to accept the default value: [{}]".format(desiredInput,defaultValue))
    userInput = sys.stdin.readline().rstrip().lstrip()
    if userInput == "":
        log("Using default value: [{}]".format(defaultValue))
        return defaultValue
    else:
        userInput = userInput.lstrip().rstrip()
        log("Using input value: [{}]".format(userInput))
        return userInput

#=======================================================================================
# Function:     PREP VARIABLES
#
# Description:  This function prepares 6 string variables from user inputs.
#
#               User inputs are the folder name, the GeoJSON folder path, and the
#               output geodatabase. The folder name is used in the names of the
#               output Feature Classes. The Feature Classes are created in the
#               input geodatabase.
#
#               The outputs will be named as follows:
#                   <FOLDER_NAME>_MERGE
#                   <FOLDER_NAME>_SPLIT
#                   <FOLDER_NAME>_BUFFER
#                   <FOLDER_NAME>_DISSOLVE
#                   <FOLDER_NAME>_SPATIAL_JOIN
#                   <FOLDER_NAME>_RESULT
#
# Parameters:   None.
#
# Returns:      None.

def prepVariables():
    log("PREPARE VARIABLES.")
    global  folderName, geoSourceFolder, outputGDB, fcMerge, fcSplit, fcBuffer, fcDissolve, fcSpatialJoin, fcFinalResult
    folderName = getUserInput("FOLDER NAME", "FIVE_POLYS")
    geoSourceFolder = getUserInput("GEOJSON FOLDER PATH", os.path.join(os.getcwd(), 'data', 'GEOJSON', folderName))
    outputGDB = getUserInput("GEO DATABASE PATH:",r"GeoJSON_proc\Upper_Polys.gdb")
    fcMerge         = os.path.join(outputGDB, folderName + "_MERGE")
    fcSplit         = os.path.join(outputGDB, folderName + "_SPLIT")
    fcBuffer        = os.path.join(outputGDB, folderName + "_BUFFER")
    fcDissolve      = os.path.join(outputGDB, folderName + "_DISSOLVE")
    fcSpatialJoin   = os.path.join(outputGDB, folderName + "_SPATIAL_JOIN")
    fcFinalResult   = os.path.join(outputGDB, folderName + "_RESULT")

#=======================================================================================
# Function:     GET GEOJSON FILE NAMES
#
# Description:  This function gets the list of all GeoJSON files in the GeoJSON folder
#               and returns the list of file names.
#
# Parameters:   None.
#
# Returns:      A list of the GeoJSON file names in the GeoJSON folder.

# HMMM: SHOULD FEATURE CLASSES BE CREATED AS FILES ARE WALKED THROUGH?

def getGeoJSONFileNames():
    geoFileNames = next(walk(geoSourceFolder), (None, None, []))[2]  # [] if no file
    log("FOUND {} GEOJSON FILES.".format(len(geoFileNames)))
    return geoFileNames

#=======================================================================================
# Function:     CREATE FEATURE CLASSES FROM GEOJSON
#
# Description:  This function creates a Feature Class for every input GeoJSON file. The
#               name of each Feature Class is "OUTPUT_{NUMBER}" where the number is
#               extracted from the processed GeoJSON file name which represents the
#               polygon number.
#
# Parameters:   geoFileNames    - The list of GeoJSON file names.
#
# Returns:      A list of all of the output Feature Class names created from the input
#               GeoJSON files.

def createFeatureClassesFromGeoJSON(geoFileNames):
    # Keep track of the outputs for merging later
    outputFeatureClasses = []
    # Process each geojson file into a feature class
    log("CREATING A FEATURE CLASS FOR EACH GEOJSON FILE.")
    for currGeoFileName in geoFileNames:
        currGeoFilePath = os.path.join(geoSourceFolder, currGeoFileName)
        end = currGeoFileName.rfind("_output")
        beg = currGeoFileName[:end].rfind("_") + 1
        currOutputName = folderName + "_POLYGON_" + currGeoFileName[beg:end]
        outputFC = os.path.join(outputGDB, currOutputName)
        outputFeatureClasses.append(outputFC)
        arcpy.conversion.JSONToFeatures(currGeoFilePath, outputFC, 'POLYLINE')
    log("CREATED {} FEATURE CLASSES.".format(len(outputFeatureClasses)))
    return outputFeatureClasses

#=======================================================================================
# Function:     MERGE FEATURE CLASSES
#
# Description:  This function creates a new Feature Class that is the result of merging
#               many Feature Classes using the Merge Tool.
#
# Parameters:   featureClassNames    - The list of Feature Class names.
#
# Returns:      None.

def mergeFeatureClasses(featureClassNames):
    log("MERGING ALL FEATURE CLASSES INTO ONE.")
    arcpy.management.Merge(featureClassNames, fcMerge)

#=======================================================================================
# Function:     SPLIT MERGED LINES
#
# Description:  This function creates a new Feature Class that is the result of
#               splitting the merged polyline Feature Class into multiple line
#               segments at its vertices using the Split Line Tool.
#
# Parameters:   None.
#
# Returns:      None.

def splitMergedLines():
    log("SPLITTING LINES OF MERGED FEATURE CLASS INTO LINE SEGMENTS.")
    arcpy.management.SplitLine(fcMerge, fcSplit)

#=======================================================================================
# Function:     REMOVE LONG LINES
#
# Description:  This function removes line segments from the Feature Class result of
#               the Split Line Tool that have a Shape Length greater than 40 using an
#               Update Cursor.
#
# Parameters:   None.
#
# Returns:      None.

# TODO: 40 IS A RANDOM VALUE. MIGHT WANT TO TWEAK THIS/PUT MORE THOUGHT INTO THE LIMIT

def removeLongLines():
    log("REMOVING LONG LINE SEGMENTS FROM SPLIT.")
    deleteCount = 0
    with arcpy.da.UpdateCursor(fcSplit, "Shape_Length") as updateCursor:
        for row in updateCursor:
            if row[0] > 40:
                updateCursor.deleteRow()
                deleteCount += 1
    log("REMOVED {} LINE SEGMENTS.".format(str(deleteCount)))

#=======================================================================================
# Function:     CREATE BUFFER
#
# Description:  This function creates a Feature Class representing a buffer of 2 metres
#               around each of the remaining line segments using the Buffer Tool. 
#
# Parameters:   None.
#
# Returns:      None.

# TODO: 2 METRES IS A RANDOM VALUE. MIGHT WANT TO TWEAK THIS/PUT MORE THOUGHT INTO THE VALUE

def createBuffer():
    log("CREATING A BUFFER FROM THE REMAINING LINE SEGMENTS.")
    arcpy.analysis.Buffer(fcSplit, fcBuffer, "2 Meters")

#=======================================================================================
# Function:     DISSOLVE BUFFER
#
# Description:  This function creates a Feature Class which is the result of dissolving
#               the buffer Feature Class using the Dissolve Tool.
#
# Parameters:   None.
#
# Returns:      None.

def dissolveBuffer():
    log("DISSOLVING THE OVERLAPPING BUFFER LINES INTO SINGLE PART FEATURES.")
    arcpy.management.Dissolve(fcBuffer,
                              fcDissolve,
                              "",
                              "",
                              'SINGLE_PART',
                              'DISSOLVE_LINES')

#=======================================================================================
# Function:     ADD ID FIELD TO DISSOLVED BUFFER
#
# Description:  This function adds a new 'ID' field to the dissolved buffer Feature
#               Class and populates it with the same value as the 'ObjectID' field
#               for each dissolved buffer using the Calculate Field Tool. This field
#               will be used later when the line segments are merged according to the
#               merged buffers.
#
# Parameters:   None.
#
# Returns:      None.

def addIdFieldToDissolvedBuffer():
    log("ADDING A NEW ID FIELD TO THE DISSOLVED BUFFER LINES.")
    arcpy.management.CalculateField(fcDissolve,
                                    'ID',
                                    '!OBJECTID!',
                                    "PYTHON3")

#=======================================================================================
# Function:     PERFORM SPATIAL JOIN USING DISSOLVED BUFFER
#
# Description:  This function creates a Feature Class which joins the attributes of the
#               dissolved buffers and the polyline segments with which they overlap
#               using the Spatial Join Tool.
#
# Parameters:   None.
#
# Returns:      None.

def performSpatialJoinUsingDissolvedBuffer():
    log("PERFORMING A SPATIAL JOIN OF THE DISSOLVED BUFFERS AND LINE SEGMENTS.")
    arcpy.analysis.SpatialJoin(fcSplit,
                               fcDissolve,
                               fcSpatialJoin)

#=======================================================================================
# Function:     DISSOLVE SPATIAL JOIN
#
# Description:  This function creates a Feature Class which is the result of dissolving
#               the split line segments according to the ID that was assigned during the
#               spatial join with the dissolved buffers 
#
# Parameters:   None.
#
# Returns:      None.

def dissolveSpatialJoin():
    log("DISSOLVING THE SPATIAL JOIN TO GET THE FINAL RESULTS.")
    arcpy.management.Dissolve(fcSpatialJoin,
                              fcFinalResult,
                              "ID",
                              "",
                              'MULTI_PART',
                              'DISSOLVE_LINES')

#=======================================================================================
# Function:     PROCESS GEOJSON
#
# Description:  This function executes the many steps of the process to create a
#               merged polyline Feature Class using many GeoJSON file inputs.
#
# Parameters:   None.
#
# Returns:      None.

def processGeoJSON():
    log("PROCESSING GEOJSON!")
    prepVariables()
    geoFileNames = getGeoJSONFileNames()
    if len(geoFileNames)==0 :
       log("NO GEOJSON FILES FOUND TO PROCESS.")
       raise SystemExit
    featureClassNames = createFeatureClassesFromGeoJSON(geoFileNames)
    mergeFeatureClasses(featureClassNames)
    splitMergedLines()
    removeLongLines()
    createBuffer()
    dissolveBuffer()
    addIdFieldToDissolvedBuffer()
    performSpatialJoinUsingDissolvedBuffer()
    dissolveSpatialJoin()
    log("ALL DONE!")
    
#=======================================================================================
# LET'S ACTUALLY RUN IT!
processGeoJSON()
