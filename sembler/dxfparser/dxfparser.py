

from math import sin, cos, pi

import copy
import dxfgrabber as dxf
import dxfplotter

from config import DxfConfig

import logging

logger = logging.getLogger('root')

def separateLayers(dwg, layerNames):

    """
    Separates a drawing by layer name and returns the entities of each
    specified layer in a dictionary.

    Drawing inserts are exploded into the individual entities they describe.
    :type dwg: dxfgrabber.drawing.Drawing
    :type layerNames: list
    :return: A dictionary of layernames (key) and entities (value)
    :rtype: dict

    """
    logger.info('Separating layers ...')
    layers = {}

    for layerName in layerNames:
      logger.info('Separating layer ' + layerName)

      # Get all the non-insert entities associated with this layer
      entities = [entity for entity in dwg.entities
                    if entity.layer.upper() == layerName
                    and entity.dxftype != DxfConfig.INSERT
      ]
      layers[layerName] = entities

      insertEntities = parseInsertEntities(dwg, layerName)

      layers[layerName].extend(insertEntities)
      logger.info(layerName + ' separated.')

    logger.info('Layers separated.')

    return layers


def separateStandardLayers(dwg):

    """
    Separates the standard layers as defined by the Sembler documentation.
    :type dwg: dxfgrabber.drawing.Drawing
    :return: A dictionary of layerName, entityList pairs
    :rtype: dict
    """
    return separateLayers(dwg, DxfConfig.VALID_LAYERS)


def separateFabricationLayers(dwg):
    """
    Separates the layers needed to generate the fabrication output in GDS
    :type dwg: dxfgrabber.drawing.Drawing
    :return: A dictionary of layerName, entityList pairs
    :rtype: dict
    """
    return separateLayers(dwg, DxfConfig.FAB_LAYERS)


def translateEntity(entity, offset):

    """
    Translates an entity IN-PLACE by the given offset (dx, dy).

    Currently only handles polylines and circles.
    :type entity: dxfgrabber.entities.LWPolyline
    :type offset: tuple
    """
    dx, dy = offset

    if entity.dxftype == DxfConfig.POLYLINE or entity.dxftype == DxfConfig.LWPOLYLINE:
        entity.points = [(pt[0] + dx, pt[1] + dy, 0) for pt in entity.points]

    elif entity.dxftype == DxfConfig.CIRCLE:
        entity.center = (entity.center[0] + dx, entity.center[1] + dy, 0)

    else:
        logger.warning("Unhandled entity for translation: " + entity.dxftype)


def rotateEntity(entity, theta, origin):

    """
    Rotates an entity IN-PLACE by the given angle about the given origin.

    Currently only handles polylines and circles.
    :type entity: dxfgrabber.entities.LWPolyline
    :type theta: float
    :type origin: tuple
    """
    if theta != 0:

        t = theta * pi / 180.0
        dx, dy, dz = origin

        if entity.dxftype == DxfConfig.POLYLINE or entity.dxftype == DxfConfig.LWPOLYLINE:

            points = [(pt[0] - dx, pt[1] - dy, 0) for pt in entity.points]

            entity.points = [
                (cos(t) * x - sin(t) * y + dx, sin(t) * x + cos(t) * y + dy, 0)
                for x, y, z in points
            ]

        elif entity.dxftype == DxfConfig.CIRCLE:

            c = entity.center
            x, y, z = (c[0] - dx, c[1] - dy, 0)

            entity.center = (cos(t) * x - sin(t) * y + dx,
                             sin(t) * x + cos(t) * y + dy, 0)

        else:
            logger.error("Unhandled rotation: " +  entity.dxftype)


def scaleEntity(entity, scale):

    """
    Scales an entity IN-PLACE by the given scale factor (sx, sy, sz).

    Currently only capable of scaling polylines and circles. Circles can only
    be scaled uniformly in X and Y. Non-uniform scales would create ellipses.
    :type entity: dxfgrabber.entities.LWPolyline
    :type scale: tuple
    """
    if scale != (1, 1, 1):

        sx, sy, sz = scale

        if entity.dxftype == DxfConfig.POLYLINE or entity.dxftype == DxfConfig.LWPOLYLINE:
            entity.points = [
                (pt[0] * sx, pt[1] * sy, 0) for pt in entity.points
            ]

        elif entity.dxftype == DxfConfig.CIRCLE:
            c = entity.center
            r = entity.radius

            x, y, z = (c[0], c[1], 0)

            entity.center = (x * sx, y * sy, 0)

            if abs(sx) == abs(sy):
                entity.radius = r * abs(sx)
            else:
                logger.debug('Non-uniform scaling on circle. ScaleX: '
                                + sx + ' ScaleY:' + sy)

        else:
            logger.error( "Unhandled scaling: " +  entity.dxftype)


def extractInsertEntities(dwg, insert, layerName):

    """
    Takes an insert and explodes it into the corresponding entities it
    describes. Performs all scale, rotation, and translations as appropriate.
    :type dwg: dxfgrabber.drawing.Drawing
    :type insert: dxfgrabber.entities.Insert
    :type layerName: str
    :return: A list of the entities the insert describes
    :rtype: list
    """
    entities = []

    block = dwg.blocks.get(insert.name)

    for r in xrange(insert.row_count):
        for c in xrange(insert.col_count):

            for entity in block:

                if entity.dxftype != DxfConfig.INSERT \
                        and entity.layer.upper() == layerName:
                    newEntity = copy.deepcopy(entity)

                    xOffset = insert.insert[0] + c * insert.col_spacing
                    yOffset = insert.insert[1] + r * insert.row_spacing

                    scaleEntity(newEntity, insert.scale)
                    translateEntity(newEntity, (xOffset, yOffset))
                    rotateEntity(newEntity, insert.rotation, insert.insert)

                    entities.append(newEntity)

                elif entity.dxftype == DxfConfig.INSERT:
                    # Call extract entities
                    e = extractInsertEntities(dwg, entity, layerName)
                    for ent in e:

                        newEntity = copy.deepcopy(ent)

                        xOffset = insert.insert[0] + c * insert.col_spacing
                        yOffset = insert.insert[1] + r * insert.row_spacing

                        scaleEntity(newEntity, insert.scale)
                        translateEntity(newEntity, (xOffset, yOffset))
                        rotateEntity(newEntity, insert.rotation, insert.insert)

                        entities.append(newEntity)

    return entities


def parseInsertEntities(dwg, layerName):

    """
    Searches through a drawing for inserts and explodes them into the entities
    they describe.
    :type dwg: dxfgrabber.drawing.Drawing
    :type layerName: str
    :return: A list containing all the entities that insert describes
    :rtype: list
    """
    logger.info('Parsing insert entities ...')
    entities = []
    inserts = [entity for entity in dwg.entities if entity.dxftype == DxfConfig.INSERT]

    for insert in inserts:
        entities.extend(extractInsertEntities(dwg, insert, layerName))
    logger.info('Insert entities parsed.')

    return entities


if __name__ == '__main__':
    # filename = argv[1]

    BETA_DIR = "..\\..\\designs\\beta"
    SANDBOX_DIR = "..\\..\designs\\sandbox"

    SQZ_1 = BETA_DIR + "\\SQZ_design\\MAMBO.Beta.SQZ.20150622.D1.dxf"
    SQZ_2 = BETA_DIR + "\\SQZ_design\\MAMBO.Beta.SQZ.20150622.D2.dxf"
    SQZ_3 = BETA_DIR + "\\SQZ_design\\MAMBO.Beta.SQZ.20150622.D3.dxf"
    SQZ_FIX = BETA_DIR + "\\SQZ_design\\fixed\\sqz_purity_fixed.dxf"

    TEST_1 = SANDBOX_DIR + "\\test_su8_01.dxf"

    AUDION_1 = BETA_DIR + "\\Audion_design\\MAMBO.Beta.ADN.20150622.D1.dxf"

    filename = SQZ_3

    logger.info('Loading' + filename + '...')

    layersToSeparate = [DxfConfig.SU8_1, DxfConfig.SU8_2, DxfConfig.SU8_3,
                        DxfConfig.METAL, DxfConfig.VPORT]

    dwg = dxf.readfile(filename)
    logger.info("AutoCAD version" + str(dwg.dxfversion))
    layers = separateLayers(dwg, layersToSeparate)

    dxfplotter.plotAllLayers(layers, layersToSeparate, xlim=[-500, 10500],
                             ylim=[-500, 20500])


