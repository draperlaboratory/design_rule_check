import os
import sys
import argparse
import dxfgrabber as dxf
import ezdxf
import time
import logging
import copy

import checker
import checker.rules
import dxfparser
import json

from config import version
from config import layerNameToNum
from config import DxfConfig
from config import PURITY

from intermediate import Violation
from intermediate import ViolationSummary

from dxfparser import dxfvalidator, dxfwriter, dxf2shapely, gdswriter
from shapely.geometry import Polygon
from sql_interactions import setProjectID

logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)
logger.propagate = False

# Control Variables
DEBUG = False
GENCHECKPLOTS = True
CHECKDESIGN = True


def purityCheck(dwg):
    """
    Perform design purity check against the dxf file.  Set purity errors field
    of the resultJSON dictionary, and return a dictionary of purity failures
    found by the dxfvalidator.
    :type dwg: dxfgrabber.drawing.Drawing
    :type filename: str
    :type filePath: str
    :type outDir: str
    :type resultJSON: dict
    """

    logger.info("Checking design purity")
    purityFailures = dxfvalidator.checkDrawingPurity(dwg)
    logger.info("Purity check complete")

    return purityFailures


def populateDD(designDict, layers):
    """
    Converts an ingested DXF into a design dictionary.

    We ingest twice because a large amout of additional data is computed during
    construction of a design dictionary.  Buffered geometry, spatial index,
    intent of features, and so on.  These aren't free, so we don't compute them
    until we need them, lest a purity error cause us to throw them out.
    :type designDict: checker.DesignDict.DesignDict
    :type layers: dict
    """

    shapelyLayers = {}

    ## Add the ports upfront, since you have to filter other objects based on them
    for dxfport in layers[DxfConfig.VPORT]:
        designDict.addPort(checker.Port(dxfport.center, dxfport.radius))

    for layerName, layer in layers.iteritems():
        logger.info("converting " + layerName)
        layerObjs = dxfparser.calculatePolarity(
            dxfparser.convertLayer(layer), layerName)
        shapelyLayers[layerName] = layerObjs
        layerSig = layerNameToNum(layerName)

        if layerName == DxfConfig.ALIGNMENT:
            for _alignmentMark in layerObjs:
                alignmentMark = checker.AlignmentMark(_alignmentMark.centroid)
                designDict.addAlignment(alignmentMark)

        elif layerName == DxfConfig.BORDER:

            # There should only be one entity on the border layer at this point
            border = dxf2shapely.polyline2polygon(layer[0])
            if border:
                designDict.setBorder(Polygon(border))
            else:
                logger.critical("Border unable to be added to design dictionary")
                raise ValueError("Border unable to be added to design dictionary")
        elif layerName == DxfConfig.POSTS:
            for entity in shapelyLayers[layerName]:
                toAdd = checker.Post(entity)
                designDict.addPost(toAdd)

        elif layerName != DxfConfig.VPORT:
            logger.info("generating objects into " + str(layerSig))
            for obj in layerObjs:
                toAdd = checker.Feature(obj)
                designDict.addToLayer(toAdd, layerSig)

    ## figure out what posts are meant to be, add them to layers
    checker.rules.fillInPosts(designDict)


def printFailures(purityFailures, designDict, resultJSON, checkplots, outDir):
    """
    Generates the summary pdf output by the DRC process.

    By side effect, populates the errors field of the resultJSON, including how
    many hard and soft errors were found by the design rule checker.  The path
    to the pdf is also added.
    :type purityFailures: list
    :type designDict: checker.DesignDict.DesignDict
    :type resultJSON: dict
    :type checkplots: list
    :type outDir: str
    """
    logger.info("checkplots: " + ', '.join(checkplots))
    s = checker.outputPDF(designDict.violations,
                          checkplots, resultJSON["in_dxf"], outDir, version)
    logger.info("Found " + str(designDict.violationCount()) + " violations")
    (hard,soft) = designDict.getViolationCounts()
    resultJSON["errors"]["soft_violations"] = soft
    resultJSON["errors"]["hard_violations"] = hard
    resultJSON["summary"] = s

def checkRules(purityFailures, designDict, checkPlots, resultJSON, filename,
               filePath, outDir):
    """
    Given an ingested dxf (designDict), check to make sure the design adheres to
    the rules laid out by the DRC.
    :type purityFailures: list[dxfvalidator.PurityFailure]
    :type designDict: checker.DesignDict.DesignDict
    :type checkPlots: list
    :type resultJSON: dict
    :type filename: str
    :type filePath: str
    :type outDir: str
    """
    checker.sanity()
    if CHECKDESIGN:
        logger.info("Checking rules")
        designDict.checkAll()
        printFailures(purityFailures, designDict, resultJSON, checkPlots, outDir)

        violations = designDict.violations.violations
        return dxfwriter.generateDRCFailureOutput(filename, filePath, outDir,
                                                  violations)


def generateCheckPlots(designDict, resultJSON, filename, outDir):
    """
    Produces checkplots of an ingested DXF (designDict).  These plots are
    included in the summary output.
    :type designDict: checker.DesignDict.DesignDict
    :type resultJSON: dict
    :type filename: str
    :type outDir: str
    """
    if GENCHECKPLOTS:
        logger.info("Generating checkplots")
        checkPlotLocations = checker.drawAllLayers(designDict, filename, outDir)
        return checkPlotLocations
    else:
        return []

def loadDXF(filename):
    """
    Parse a dxf file from a path
    :rtype : dxfgrabber.drawing.Drawing
    :type filename: str
    """
    logger.info('Loading ' + filename)
    dwg = dxf.readfile(filename)
    logger.info('Loaded. AutoCAD version: ' + str(dwg.dxfversion))

    # Adding this because apparently dxfgrabber will open some files that
    # aren't valid DXFs without throwing an exception
    ezdxf.readfile(filename)

    return dwg

def parseArguments():
    """
    Pulls command line arguments into more canonical forms.  Also generates the
    help messages for when the wrong number of arguments are provided, or --help
    is submitted.
    :rtype : str, str, str
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help='The .dxf file to process')
    parser.add_argument('in_dir',
                        help='The directory the file resides in')
    parser.add_argument('out_dir',
                        help='The directory where results will be written')
    ## parse_args doesn't support var-args
    parser.add_argument('project_id', nargs='?', default=None, help='numeric ID of project in database.')
    parser.add_argument('--fab', help='Outputs a DXF suited for fabrication',
                        action='store_true')

    args = parser.parse_args()

    filename = args.filename
    inputDirectory = args.in_dir
    outputDirectory = args.out_dir
    fabricationOutput = args.fab
    project_id = args.project_id

    if inputDirectory[-1] != '/':
        inputDirectory += '/'
    if outputDirectory[-1] != '/':
        outputDirectory += '/'

    return filename, inputDirectory, outputDirectory, fabricationOutput, project_id

def areArgumentsValid(filename, inDir, outDir, projectID):
    """
    Makes sure the file, input and output directories exist.
    Returns True if arguments are valid, False otherwise
    :rtype : bool
    :type filename: str
    :type inDir: str
    :type outDir: str
    :type projectID : int
    """

    args = [inDir, outDir, inDir + filename]
    missingArguments = [arg for arg in args if not os.path.exists(arg)]

    if missingArguments:

        errorMessage = 'File and/or directory(s) do not exist: ' + \
                        ', '.join(missingArguments)

        print errorMessage
        logger.critical(errorMessage)
        return False

    return True

def configureLogger(filename, outputDirectory):
    """
    Sets up the logging file, and logger levels
    :type filename: str
    :type outputDirectory: str
    """
    fh = logging.FileHandler(outputDirectory + filename + '.log', mode='w')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
    fh.setFormatter(formatter)

    logger.addHandler(fh)

def writeJSON(resultJSON, jsonFilename):
    """
    Produces the result json file associated with a drc run

    Also dumps the json out to standard out
    :type resultJSON: dict
    :type jsonFilename: str
    """
    logger.info('Writing results to JSON')
    with open(jsonFilename, 'w') as outfile:
        print json.dumps(resultJSON, separators=(",", ":"), indent=3)
        json.dump(resultJSON, outfile, separators=(",", ":"), indent=3)

def createFabricationOutput(filename, inputDirectory, outputDirectory):
    filepath = inputDirectory + filename
    filenameNoExt = filename.replace('.dxf', '')

    dwg = loadDXF(filepath)
    unionableLayers = dxfparser.separateFabricationLayers(dwg)

    # Add the support posts to all layers that they affect
    for layer in [DxfConfig.SU8_1,DxfConfig.SU8_2, DxfConfig.SU8_3]:
        unionableLayers[layer].extend(
            copy.deepcopy(unionableLayers[DxfConfig.POSTS]))

    # Add the VPORTS to SU8_1, per James' instruction
    unionableLayers[DxfConfig.SU8_1].extend(
        copy.deepcopy(unionableLayers[DxfConfig.VPORT]))

    for entity in unionableLayers[DxfConfig.SU8_1]:
        if entity.layer == DxfConfig.VPORT:
            entity.layer = DxfConfig.SU8_1

    processedLayers = {}

    for layerName, layer in unionableLayers.iteritems():
        logger.info("Converting " + layerName)
        processedLayers[layerName] = \
            dxfparser.calculatePolarity(
                dxfparser.convertLayer(layer), layerName)

    gdswriter.generateFabricationOutput(filenameNoExt, outputDirectory,
                                            processedLayers)


def runDRC(filename, inputDirectory, outputDirectory, resultJSON):

    filepath = inputDirectory + filename
    filenameNoExt = filename.replace('.dxf', '')
    resultJSON["in_dxf"] = filepath
    resultJSONfilename = outputDirectory + filenameNoExt + '-result.json'

    try:
        dwg = loadDXF(filepath)
        resultJSON["errors"]["invalid_dxf"] = False
    except:
        logger.critical('Unexpected error opening: ' + filepath)

        failure = Violation('Invalid DXF',
                            'There was an error opening your dxf file.',
                            'UNREADABLE',
                            layer=PURITY)
        violations = ViolationSummary.ofList([failure])
        checker.outputPDF(violations, None, resultJSON["in_dxf"],
                          outputDirectory, version)

        resultJSON["errors"]["purity"] = True
        resultJSON["errors"]["invalid_dxf"] = True
        resultJSON["end_time"] = time.time()
        writeJSON(resultJSON, resultJSONfilename)

        return 0


    designDict = checker.DesignDict()

    logger.info("Searching for tiny entities")
    tinyEntities = dxfvalidator.findTinyEntities(dwg)
    logger.info("Tiny entity search complete")

    purityFailures = purityCheck(dwg)

    violations = purityFailures + tinyEntities

    if purityFailures:
        dxfwriter.generatePurityFailureOutput(
            filenameNoExt,
            filepath,
            outputDirectory,
            violations)
        resultJSON["errors"]["purity"] = True

    else:
        resultJSON["errors"]["purity"] = False

    designDict.violations = ViolationSummary.ofList(violations)

    if (not DEBUG) and purityFailures:
        logger.error('Purity failures: ' + str(purityFailures))
        checker.outputPDF(designDict.violations, None, resultJSON["in_dxf"],
                          outputDirectory, version)

        outDxf = outputDirectory + filenameNoExt + '-err.dxf'

        resultJSON["out_dxf"] = outDxf
        resultJSON["end_time"] = time.time()
        writeJSON(resultJSON, resultJSONfilename)
        ## Skip the rest of everything.  Purity failures.
        return 0

    layers = dxfparser.separateStandardLayers(dwg)
    populateDD(designDict, layers)
    designDict.populateSize(resultJSON)

    ## Draw the checkplots
    checkPlots = generateCheckPlots(designDict, resultJSON, filename,
                                    outputDirectory)

    ## Validate the design
    out = checkRules(purityFailures, designDict, checkPlots, resultJSON,
                     filenameNoExt, filepath, outputDirectory)
    resultJSON["out_dxf"] = out

    endTime = time.time()
    resultJSON["end_time"] = endTime
    resultJSON["counts"] = designDict.getObjCounts()
    writeJSON(resultJSON, resultJSONfilename)

    logger.info('Run complete.')

    return 0

def main():
    """
    Runs the DRC end to end on an input file.
    """
    startTime = time.time()

    resultJSON = {}
    resultJSON["start_time"] = startTime
    resultJSON["errors"] = {}

    filename, inputDirectory, outputDirectory, \
        fabricationOutput, projectID = parseArguments()

    if not areArgumentsValid(filename, inputDirectory, outputDirectory, projectID):
        resultJSON["errors"]["bad_arguments"] = True
        return 1

    configureLogger(filename, outputDirectory)

    if fabricationOutput:
        return createFabricationOutput(filename, inputDirectory,
                                        outputDirectory)
    else:
        return runDRC(filename, inputDirectory, outputDirectory, resultJSON)

if __name__ == '__main__':
    sys.exit(main())
