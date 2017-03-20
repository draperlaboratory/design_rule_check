

import ezdxf

from dxfvalidator import BadInsert
from config import DxfConfig
import intermediate

import logging
logger = logging.getLogger('root')

def generatePurityFailureOutput(filenameNoExt, filePath, outDir,
                                purityFailures):
    """
    Creates the annotated DXF from a list of purity failures
    :type filenameNoExt: str
    :type filePath: str
    :type outDir: str
    :type purityFailures: list[intermediate.Violation]
    """
    logger.info("Purity check failed")

    if outDir[-1] != '/':
        outDir += '/'

    dwg = ezdxf.readfile(filePath)

    for failure in purityFailures:
        if failure.dxfLayer:
            color = DxfConfig.COLOR_MAP[failure.ctype]
            _createLayer(dwg, failure.dxfLayer, color)

            # Render conflicting geometry ONLY if there is no witness
            if failure.witnesses:
                for witness in failure.witnesses:
                    __renderWitness(witness, dwg, failure.dxfLayer)
            elif failure.conflicting:
                for entity in failure.conflicting:
                    _moveToLayer(entity, failure.dxfLayer, dwg)

            if failure.inserts:
                for insert in failure.inserts:
                    _parseBadInsert(insert, failure.dxfLayer, dwg)


    try:
        dwg.saveas(outDir + filenameNoExt + '-err.dxf')
    except:
        logger.exception("Error writing Purity Failure to DXF: ")
        raise


def generateDRCFailureOutput(filenameNoExt, filePath, outDir, violations):

    """
    Creates the annotated DXF from a dictionary of violations.
    :type filenameNoExt: str
    :type filePath: str
    :type outDir: str
    :type violations: list[intermediate.Violation]
    :return: :rtype: :raise:
    """
    logger.info('Generating error layers')

    if outDir[-1] != '/':
        outDir += '/'


    # Open the original DXF
    dwg = ezdxf.readfile(filePath)
    # For every rule that was violated:
    for violation in violations:
        layerName = violation.dxfLayer
        color = DxfConfig.COLOR_MAP[violation.ctype]
        _createLayer(dwg, layerName, color)
        # A feature can be a witness or a real drawing feature
        if not violation.witnesses:
            for feature in violation.conflicting:

                if hasattr(feature, 'shape'):
                    # Convert the shapely object to dxf and put it on a layer
                    __convertPolygon2Polyline(dwg, feature.shape, layerName)
                else:
                    _moveToLayer(feature, layerName, dwg)

        for witness in violation.witnesses:
            __renderWitness(witness, dwg, layerName)

    # Save the DXF as a new file
    outpath = outDir + filenameNoExt + '-err.dxf'
    try:
        dwg.saveas(outpath)
    except:
        logger.exception("Error writing DRC Failure to DXF: ")
        raise

    return outpath

def __renderWitness(witness, drawing, layerName):

    renderMap = {
        intermediate.Witness.REGION: __renderRegion,
        intermediate.Witness.LINE_SEGMENT: __renderLineSegment,
        intermediate.Witness.POINT_RADIUS: __renderPointRadius,
        intermediate.Witness.POINT: __renderPoint
    }

    renderMap[witness.typ](witness.geometry, drawing, layerName)

def __renderPoint(point, drawing, layerName):
    __convertPoint2Marker(point, drawing, layerName)

def __renderRegion(region, drawing, layerName):
    __convertPolygon2Polyline(drawing, region, layerName)

def __renderLineSegment(lineSegment, drawing, layerName):
    __convertPoints2Line(lineSegment, drawing, layerName)

def __renderPointRadius(pointRadius, drawing, layerName):
    __convertPointRadius2Circle(pointRadius, drawing, layerName)

def _parseBadInsert(insert, layer, dwg):
    """
    Takes an insert and moves all entities within it to the specified layer
    :type insert: dxfparser.dxfvalidator.BadInsert
    :type layer: str
    :type dwg: ezdxf.drawing.Drawing
    """
    for entity in insert.block:
        if isinstance(entity, BadInsert):
            _parseBadInsert(entity, layer, dwg)
        else:
            e = _getEntityFromDwg(dwg, entity.handle)
            if e:
                e.dxf.layer = layer


def _getEntityFromDwg(dwg, handle):
    """
    Gets an entity matching the specified handle from a drawing
    :type dwg: ezdxf.drawing.Drawing
    :type handle: str
    :return: The entity corresponding to the given handle
    """

    try:
        entity = dwg.get_dxf_entity(handle)
    except KeyError:
        msg = 'Could not find entity with handle: ' + str(handle)
        logger.critical(msg)
        raise Exception(msg)

    return entity


def _moveToLayer(entity, layer, dwg):
    """
    Moves an entity by handle to the specified layer
    :type entity: Spline or Line or Arc or LWPolyline
    :type layer: str
    :type dwg: ezdxf.drawing.Drawing
    :raise Exception: Exceptions are for problems with entity handles
    """
    handle = entity.handle

    if not handle:
        logger.critical("No handle detected for entity:"
                        + str(entity.dxftype))
        raise Exception("No handle detected for entity:"
                        + str(entity.dxftype))

    queryString = '*[handle=="' + handle + '"]'
    entities = dwg.entities.query(queryString)
    if entities:
        if len(entities) is not 1:
            logger.critical('Multiple entities found with handle '
                            + str(handle))
            raise Exception('Multiple entities found with handle',
                            handle)
        else:
            e = entities[0]
            e.dxf.layer = layer
    else:
        logger.critical('No entities found with handle' + str(handle))
        raise Exception('No entities found with handle', handle)

def __polygon2Polyline(dwg, coords, attrs):
    """
    Takes a list of coordinates and creates a polyline from it with the given
    attributes.
    :type dwg: ezdxf.drawing.Drawing
    :type coords: list
    :type attrs: dict
    """
    if dwg.dxfversion == 'AC1009':
        dwg.modelspace().add_polyline2d(coords, dxfattribs=attrs)
    else:
        dwg.modelspace().add_lwpolyline(coords, dxfattribs=attrs)

def __convertPoint2Marker(point, drawing, layerName):
    WITNESS_RADIUS = 50
    LINE_HALF_LENGTH = 60
    v_start = (point[0], point[1] + LINE_HALF_LENGTH)
    v_end = (point[0], point[1] - LINE_HALF_LENGTH)
    h_start = (point[0] + LINE_HALF_LENGTH, point[1])
    h_end = (point[0] - LINE_HALF_LENGTH, point[1])

    attributes = {'layer': layerName}
    drawing.modelspace().add_circle(point, WITNESS_RADIUS, attributes)
    attributes = {'layer': layerName}
    drawing.modelspace().add_line(v_start, v_end, attributes)
    attributes = {'layer': layerName}
    drawing.modelspace().add_line(h_start, h_end, attributes)

def __convertPoints2Line(points, drawing, layerName):
    attributes = {'layer': layerName}
    start = (points[0].x, points[0].y)
    end = (points[1].x, points[1].y)
    drawing.modelspace().add_line(start, end, attributes)

def __convertPointRadius2Circle(pointRadius, drawing, layerName):
    attributes = {'layer': layerName}
    point = (pointRadius[0].x, pointRadius[0].y)
    radius = pointRadius[1]
    drawing.modelspace().add_circle(point, radius, attributes)

def __convertPolygon2Polyline(dwg, shape, layerName):
    """
    Takes a shapely Polygon and converts it to a DXF polyline.

    :type dwg: ezdxf.drawing.Drawing
    :type shape: shapely.geometry.polygon.Polygon
    :type layerName: str
    """
    attributes = {'layer': layerName}
    exterior = list(shape.exterior.coords)
    interiors = list(shape.interiors)

    for interior in interiors:
        __polygon2Polyline(dwg, list(interior.coords), attributes)

    __polygon2Polyline(dwg, exterior, attributes)


def _createLayer(dwg, layerName, color=10):
    """
    Creates a layer in the specified drawing with the specified color.

    This will not overwrite existing layers of the same name.
    :type dwg: ezdxf.drawing.Drawing
    :type layerName: str
    :type color: int
    """
    if layerName not in dwg.layers:
        logger.info("Creating layer " + layerName +
                        " with color " + str(color))
        dwg.layers.create(name=layerName,
                          dxfattribs={
                              'color': color
                          })
