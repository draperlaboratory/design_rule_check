from DesignDict import DesignDict

from shapely.geometry import mapping, MultiPolygon, Polygon
from shapely.ops import cascaded_union
import json
import subprocess
import os ## To get the path / basename of the input file
import re

import logging
logger = logging.getLogger('root')

jsonExt = ".json"
pdfExt = ".pdf"

metal = "_metal"
su81 = "_SU8_1"
su82 = "_SU8_2"
su83 = "_SU8_3"

ogr_deploy = "/usr/local/bin/ogr2ogr"
ogr_jordan = "/usr/bin/ogr2ogr"
ogr = None

if os.path.exists(ogr_jordan):
    ogr = ogr_jordan
else:
    ogr = ogr_deploy

def makeAlignmentMark(cX, cY):
    """
    Produce the shapely representation of an alignment mark centered at cX, cY.
    """
    llx = cX - 125
    lrx = cX + 125
    slx = cX - 100
    srx = cX + 100
    lhy = cY - 50
    uhy = cY + 50
    ## The crossbar
    lowerCross = Polygon([(llx, lhy), (slx, uhy), (srx, uhy), (lrx, lhy)])
    upperCross = Polygon([(slx, lhy), (llx, uhy), (lrx, uhy), (srx, lhy)])
    lx = cX - 50
    rx = cX + 50
    lly = cY - 125
    sly = cY - 100
    luy = cY + 125
    suy = cY + 100
    leftVert = Polygon([ (lx,lly), (lx, luy), (rx, suy), (rx, sly)])
    rightVert = Polygon([ (lx,sly), (lx, suy), (rx, luy), (rx, lly)])
    ret = cascaded_union([lowerCross, upperCross, leftVert, rightVert])
    return ret

def mangleFile(filename):
    """
    :param filename: The dxf filename
    :return: The filename with no extension, stripped of any characters
    that may cause LaTeX any hiccups
    """
    noExtension = os.path.splitext(filename)[0]
    ret = re.sub("\.","_", noExtension) ## latex peculuarities
    return ret


def commandString(inFile, outFile):
    """
    Produce the command string for generating pdf output from geojson via
    ogr2ogr
    """
    return [ogr, "-F", "PDF", outFile, inFile]


def drawLayer(dd, layerID, outPath, drawPort = True):
    """
    Renders a layer (layerID) of the design dictionary (dd) as a pdf, stored at
    outPath.
    """
    layer = dd.layers[layerID]

    ## the shapes on this layer
    allShapes = []
    for id, obj in layer.objs.items():
        toAdd = obj.shape
        if toAdd.is_valid:
            allShapes.append(toAdd)

    ## the ports, which go over all layers
    if drawPort:
        for id, obj in dd.getPorts().items():
            portRelief = obj.center.buffer(obj.radius - 10)
            toAdd = obj.shape.difference(portRelief)
            allShapes.append(toAdd)

    ## the alignment marks, which only go on metal but help in orienting
    for id, obj in dd.alignments.items():
        cx = obj.center.x
        cy = obj.center.y
        mark = makeAlignmentMark(cx,cy)
        allShapes.append(mark)

    if(len(allShapes) > 0):
        if dd.border:
            allShapes.append(dd.border.shape)
        else:
            logger.debug("Layer had no border, expect inverted checkplots")
        toRender = MultiPolygon(allShapes)
        logger.debug("Drawing layer to " + outPath)
        open(outPath, "wb").write(json.dumps(mapping(toRender)))
        return True
    else:
        logger.debug("Skipping empty layer " + outPath)
    return False


def allJsonLayers(dd, outPath):
    """
    Produce file names and geojson representing each layer.
    """
    metalBase = outPath + metal
    portAlignment = outPath + metal + "portAlignment"
    SU81Base = outPath + su81
    SU82Base = outPath + su82
    SU83Base = outPath + su83

    outPathMetal = metalBase + jsonExt
    outPathPortAlignment = portAlignment + jsonExt
    outPathSU81 = SU81Base + jsonExt
    outPathSU82 = SU82Base + jsonExt
    outPathSU83 = SU83Base + jsonExt

    drewMetal = drawLayer(dd, DesignDict.METAL, outPathMetal, drawPort=False)
    drewPortAlignment = drawLayer(dd, DesignDict.METAL, outPathPortAlignment)
    drewSU81 = drawLayer(dd, DesignDict.SU81, outPathSU81)
    drewSU82 = drawLayer(dd, DesignDict.SU82, outPathSU82)
    drewSU83 = drawLayer(dd, DesignDict.SU83, outPathSU83)
    return (drewMetal, drewPortAlignment, drewSU81, drewSU82, drewSU83)


def convertLayers(outDir, basePath, (drewMetal, drewPortAlignment, drewSU81, drewSU82, drewSU83)):
    """
    Convert all of the geojson to pdfs representing the layers
    """
    portAlignment = basePath + metal + "portAlignment"
    metalBase = basePath + metal
    SU81Base = basePath + su81
    SU82Base = basePath + su82
    SU83Base = basePath + su83

    jsonPortAlignment = outDir + portAlignment + jsonExt
    jsonMetal = outDir + metalBase + jsonExt
    jsonSU81 = outDir + SU81Base + jsonExt
    jsonSU82 = outDir + SU82Base + jsonExt
    jsonSU83 = outDir + SU83Base + jsonExt

    pdfPortAlignment = portAlignment + pdfExt
    pdfMetal = metalBase + pdfExt
    pdfSU81 = SU81Base + pdfExt
    pdfSU82 = SU82Base + pdfExt
    pdfSU83 = SU83Base + pdfExt

    drawPaths = []

    if drewPortAlignment:
        logger.info("Converting Port Alignment to pdf")
        subprocess.call(commandString(jsonPortAlignment, outDir + pdfPortAlignment))
        drawPaths.append(pdfPortAlignment)

    if drewMetal:
        logger.info("Converting METAL layer to pdf")
        subprocess.call(commandString(jsonMetal, outDir + pdfMetal))
        drawPaths.append(pdfMetal)

    if drewSU81:
        logger.info("Converting SU81 layer to pdf")
        subprocess.call(commandString(jsonSU81, outDir + pdfSU81))
        drawPaths.append(pdfSU81)

    if drewSU82:
        logger.info("Converting SU82 layer to pdf")
        subprocess.call(commandString(jsonSU82, outDir + pdfSU82))
        drawPaths.append(pdfSU82)

    if drewSU83:
        logger.info("Converting SU83 layer to pdf")
        subprocess.call(commandString(jsonSU83, outDir +  pdfSU83))
        drawPaths.append(pdfSU83)

    return drawPaths

def drawAllLayers(dd, filename, outDir):
    """
    The only bit of functionality exposed to the outside.  Do all of the
    rendering and conversion for the design dictionary.  Make the checkplots.
    """
    if os.path.exists(ogr_deploy):
        ogr = ogr_deploy

    else:
        ogr = ogr_jordan

    if os.path.exists(ogr):
        mangledFilename = mangleFile(filename)
        outPath = outDir + mangledFilename
        return convertLayers(outDir, mangledFilename, allJsonLayers(dd, outPath))

    else:
        logger.error("Couldn't find ogr: " + ogr)
        return []
