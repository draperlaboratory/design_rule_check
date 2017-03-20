import logging
import gdspy
from config import DxfConfig

logger = logging.getLogger('root')


def generateFabricationOutput(filenameNoExt, outDir, shapelyLayers):

    if outDir[-1] != '/':
        outDir += '/'

    outPath = outDir + filenameNoExt + '-fab.gds'

    logger.info("Converting geometry to GDSII.")

    topCell = gdspy.Cell('TOP')

    # Map layer name to GDS layer number per James e-mail
    layerNumberMap = {
        DxfConfig.METAL: 0,
        DxfConfig.SU8_1: 1,
        DxfConfig.SU8_2: 2,
        DxfConfig.SU8_3: 3,
        DxfConfig.LABEL: 10,
        DxfConfig.VPORT: 11,
        DxfConfig.POSTS: 12,
        DxfConfig.ALIGNMENT: 20,
        DxfConfig.BORDER: 21,
        DxfConfig.CRITICAL_BOND: 22
    }

    for layerName, shapelyObjects in shapelyLayers.iteritems():

        layerNumber = layerNumberMap[layerName]

        if layerName == DxfConfig.VPORT:
            # The 'shapelyObjects' will be dxfgrabber circles ...
            logger.info('Converting the VPORT layer')
            map(lambda circle:
                    __convertDXFCircle2gds(topCell, circle, layerNumber),
                    shapelyObjects)
        else:
            logger.info("Converting shapely geometry for layer " + layerName)
            map(lambda shape:
                    __convertShapely2gds(topCell, shape, layerNumber),
                    shapelyObjects)

    gdspy.gds_print(outPath, unit=1.0e-6, precision=1.0e-9)
    #gdspy.LayoutViewer()


def __convertDXFCircle2gds(topCell, circle, layerNumber):
    center = circle.center[:2]
    disk = gdspy.Round(center, circle.radius, number_of_points=199,
                        layer=layerNumber)
    topCell.add(disk)

def __convertShapely2gds(topCell, shape, layerNumber):

    exterior = list(shape.exterior.coords)
    interiors = [list(interior.coords) for interior in list(shape.interiors)]

    exterior = gdspy.Polygon(exterior, layer=layerNumber)
    interiors = gdspy.PolygonSet(interiors, layer=layerNumber)

    operands = [exterior, interiors]

    # The epsilon value of 1e-7 was chosen to avoid segfaults that would occur
    # at the default value of epsilon (1e-13)
    # If Python is crashing at this line in the future, increase the value of
    # epsilon to correct the issue.
    booled = gdspy.boolean(operands, lambda ext, int: ext and not int,
                           layer=layerNumber, eps=1e-7)

    topCell.add(booled)