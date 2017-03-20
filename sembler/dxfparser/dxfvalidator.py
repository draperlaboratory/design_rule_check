

import itertools
import logging
from collections import defaultdict
from math import sqrt, pi

from shapely.validation import explain_validity
from shapely.geometry import Point

from config import DxfConfig, PurityConfig, RuleConfig, Translations
import dxf2shapely
import intermediate

logger = logging.getLogger('root')

class BadInsert(object):
    """
    A simple container to associate insert objects with the entities they
    contain.
    """
    def __init__(self, insert, block):
        """
        Initalizes a BadInsert
        :type insert: dxfgrabber.entities.Insert
        :type block: list
        """
        self.insert = insert
        self.block = block


def checkDrawingPurity(drawing):
    """
    Checks a drawing for purity failures.
    :type drawing: dxfgrabber.drawing.Drawing
    :return: A list of violations
    :rtype: list[Violation]
    """

    layers = defaultdict(list)

    for entity in drawing.entities:
        if entity.layer in DxfConfig.VALID_LAYERS:
            layers[entity.layer].append(entity)

    purityFailures = [
        _checkForValidLayers(drawing),
        _checkForInvalidBoundary(drawing),
        _checkForInvalidEntityTypes(drawing, layers),
        _checkForOpenPolylines(drawing, layers),
        _checkForSelfIntersectingPolylines(drawing, layers)
    ]

    result = list(itertools.chain.from_iterable(purityFailures))

    return result

def findTinyEntities(drawing):
    """
    Finds all entities below a given hueristic threshold, depending on entity
    type. Moves the offending entities to a layer for the user to review.
    :type drawing: dxfgrabber.drawing.Drawing
    :return: List of a single violation, to simplify code downstream
    :rtype: list[intermediate.Violation]
    """

    tinyEntities = []
    tinyInserts = []
    violation = []

    for entity in drawing.entities:
        if entity.layer in DxfConfig.VALID_LAYERS:

            if entity.dxftype == DxfConfig.INSERT:
                tinyInsert = _checkInsertForTinyEntities(entity, drawing)
                if tinyInsert:
                    tinyInserts.append(tinyInsert)
            elif isEntityTiny(entity):
                tinyEntities.append(entity)

    if tinyEntities or tinyInserts:
        for entity in tinyEntities:
            entity.layer = DxfConfig.LAYER_SMALL_ENTITIES
        for insert in tinyInserts:
            _moveTinyInsertToLayer(insert, DxfConfig.LAYER_SMALL_ENTITIES)

        name = PurityConfig.SmallEntities.HEADER
        description = PurityConfig.SmallEntities.DESCRIPTION
        errorLayerName = DxfConfig.LAYER_SMALL_ENTITIES
        originatingLayer = Translations.layerNameToNum(DxfConfig.SU8_1)

        violation.append(intermediate.Violation(name, description,
                                            errorLayerName,
                                            entities=tinyEntities,
                                            inserts=tinyInserts,
                                            layer=originatingLayer,
                                            ruleID=1000,
                                            ctype=RuleConfig.RuleType.SOFT))
    return violation

def isEntityTiny(entity):

    result = False
    dxftype = entity.dxftype

    if dxftype == DxfConfig.POLYLINE or dxftype == DxfConfig.LWPOLYLINE:
        perimeter = __calculatePerimeter(entity)
        if perimeter <= DxfConfig.TINY_POLYLINE_THRESHOLD:
            result = True

    elif dxftype == DxfConfig.LINE:
        x1, y1 = entity.start[0], entity.start[1]
        x2, y2 = entity.end[0], entity.end[1]

        length = sqrt((x2 - x1)**2 + (y2 - y1)**2)

        if length <= DxfConfig.TINY_LINE_LENGTH_THRESHOLD:
            result = True

    elif dxftype == DxfConfig.ARC:

        if entity.startangle > entity.endangle:
            arcLength = (360 - entity.startangle + entity.endangle) / 360.0 \
                        * 2.0 * pi *entity.radius
        else:
            arcLength = abs(entity.endangle - entity.startangle) / 360.0 \
                        * 2.0 * pi * entity.radius

        if arcLength <= DxfConfig.TINY_LINE_LENGTH_THRESHOLD:
            result = True

    elif dxftype == DxfConfig.CIRCLE:
        if entity.radius <= DxfConfig.TINY_RADIUS_THRESHOLD:
            result = True

    return result

def _checkInsertForTinyEntities(insert, drawing):

    tinyEntityBlock = []

    block = drawing.blocks.get(insert.name)
    for entity in block:
        if entity.dxftype == DxfConfig.INSERT:
            result = _checkInsertForTinyEntities(entity, drawing)
            if result:
                tinyEntityBlock.append(result)
        elif isEntityTiny(entity):
            tinyEntityBlock.append(entity)

    if tinyEntityBlock:
        badInsert = BadInsert(insert, tinyEntityBlock)
    else:
        badInsert = None

    return badInsert

def _checkForInvalidBoundary(drawing):
    """
    Checks to make sure a valid boundary object is provided for a given drawing
    :type drawing: dxfgrabber.drawing.Drawing
    :return: Returns a violation if invalid, None otherwise
    :rtype: Violation | None
    """

    logger.info('Checking for invalid boundary ...')
    description = ''
    result = []
    invalidBoundary = []

    boundaryObjects = [entity for entity in drawing.entities
                       if entity.layer == DxfConfig.BORDER]

    originatingLayer = RuleConfig.BORDER

    # Check for more than one object on the boundary layer
    if len(boundaryObjects) > 1:
        logger.error("Too many objects on the boundary layer.")
        description = PurityConfig.InvalidBoundary.TOO_MANY_OBJECTS
        description += " Found: " + str(len(boundaryObjects))
        invalidBoundary = boundaryObjects

    # Check for no objects on the boundary layer
    elif len(boundaryObjects) == 0:
        logger.error("No boundary objects found.")
        description = PurityConfig.InvalidBoundary.NO_OBJECTS
        invalidBoundary = boundaryObjects

    # At this point, we are working with a single boundary object
    else:
        boundaryObject = boundaryObjects[0]
        entityType = boundaryObject.dxftype

        # Check to make sure that single object is a polyline
        if entityType != DxfConfig.LWPOLYLINE and \
                        entityType != DxfConfig.POLYLINE:
            logger.error("Invalid entity type " + str(entityType) +
                         " for border.")
            description = PurityConfig.InvalidBoundary.INVALID_ENTITY
            invalidBoundary = boundaryObjects

    if invalidBoundary or description:
        name = 'Invalid Border'
        errorLayerName = DxfConfig.LAYER_INVALID_BORDER
        violation = intermediate.Violation(name, description, errorLayerName,
                                        entities=invalidBoundary,
                                        layer=originatingLayer,
                                        ruleID=1000)
        result.append(violation)

    logger.info('Invalid boundary check complete.')
    return result


def _checkForSelfIntersectingPolylines(drawing, layers):
    """
    Checks all polylines in a drawing for self-intersection.
    :type drawing: dxfgrabber.drawing.Drawing
    :return: A violation if self-intesections found, None otherwise.
    :rtype: Violation | None
    """
    logger.info('Checking for self-intersecting polylines ...')

    result = []

    for layerName, entities in layers.iteritems():

        xPolylines = []
        badInserts = []
        witnesses = []

        for entity in entities:
            if entity.dxftype == DxfConfig.POLYLINE or \
                            entity.dxftype == DxfConfig.LWPOLYLINE:
                    # Only check for intersection if its closed already.
                    # this is to mitigate how we handle moving entities to
                    # other layers.
                    if entity.is_closed:
                        intersection = _checkPolylineSelfIntersecting(entity)
                        if intersection:
                            xPolylines.append(entity)
                            witness = intermediate.Witness(
                                                    intermediate.Witness.POINT,
                                                    intersection)
                            witnesses.append(witness)
            elif entity.dxftype == DxfConfig.INSERT:
                badInsert = _checkInsertForIntersectingPolylines(entity, drawing)
                if badInsert:
                    badInserts.append(badInsert)

        if xPolylines or badInserts:

            name = PurityConfig.SelfIntersecting.HEADER
            description = PurityConfig.SelfIntersecting.DESCRIPTION
            errorLayerName = DxfConfig.LAYER_INTERSECTING_POLYLINE
            originatingLayer = Translations.layerNameToNum(layerName)

            violation = intermediate.Violation(name, description,
                                               errorLayerName,
                                                entities=xPolylines,
                                                inserts=badInserts,
                                                layer=originatingLayer,
                                                witnesses=witnesses,
                                                ruleID=1000)

            result.append(violation)

    logger.info('Self-intersecting polyline check complete.')

    return result


def _checkPolylineSelfIntersecting(polyline):
    """
    Checks a polyline to determine if it is self-intersecting.
    :type polyline: dxfgrabber.entities.LWPolyline
    :return: True if polyline is self-intersecting, False if not
    :rtype: bool
    """

    intersectionPoint = None

    if len(polyline.points) < 3 and polyline.is_closed:
        return True

    polygon = dxf2shapely.polyline2polygon(polyline)
    validity =  explain_validity(polygon)
    if 'Self-intersection' in validity:
        pointString = validity[validity.index('[')+1:-1]
        intersectionPoint = map(float, pointString.split())
        logger.error('Self-intersection found at: ' + str(intersectionPoint))

    return intersectionPoint

def _checkForValidLayers(drawing):
    """
    Checks to ensure all required layers are present in the drawing
    :type drawing: dxfgrabber.drawing.Drawing
    :return: A violation containing a list of the missing layers, None
    otherwise
    :rtype: intermediate.Violation | None
    """
    logger.info('Checking for valid layers ...')
    result = []
    layersToCheck = DxfConfig.VALID_LAYERS

    missingLayers = [layer for layer in layersToCheck
                        if layer not in drawing.layers]

    if missingLayers:
        name = PurityConfig.MissingLayers.HEADER
        description = PurityConfig.MissingLayers.DESCRIPTION
        # description += "Layers missing: " + \
        #               string.replace((', '.join(missingLayers)), '_', '\_')

        for layer in missingLayers:
            violation = intermediate.Violation(name, description, layer,
                                        layer=RuleConfig.PURITY,
                                        ruleID=1000)
            result.append(violation)

    logger.info('Valid layer check complete.')
    return result


def _checkForInvalidEntityTypes(drawing, layers):
    """
    Checks to ensure that all entities are of an accepted type.
    :type drawing: dxfgrabber.drawing.Drawing
    :return: A violation containing all of the non-conforming entities,
    None otherwise
    :rtype: intermediate.Violation | None
    """
    logger.info('Checking for invalid entity types ...')

    validEntityTypes = [DxfConfig.CIRCLE, DxfConfig.POLYLINE,
                        DxfConfig.LWPOLYLINE]

    result = []

    for layerName, entities in layers.iteritems():

        invalidEntities = []
        badInserts = []

        for entity in entities:
            if entity.dxftype not in validEntityTypes:
                if entity.dxftype == DxfConfig.INSERT:
                    badInsert = _checkInsertForInvalidEntities(entity, drawing,
                                                            validEntityTypes)
                    if badInsert:
                        badInserts.append(badInsert)
                else:
                    invalidEntities.append(entity)

        if invalidEntities or badInserts:

            name = PurityConfig.InvalidEntities.HEADER
            description = PurityConfig.InvalidEntities.DESCRIPTION
            errorLayerName = DxfConfig.LAYER_INVALID_ENTITY
            originatingLayer = Translations.layerNameToNum(layerName)

            violation = intermediate.Violation(name, description,
                                                errorLayerName,
                                                entities=invalidEntities,
                                                inserts=badInserts,
                                                layer=originatingLayer,
                                                ruleID=1000)

            result.append(violation)

    logger.info('Invalid entity check complete.')

    return result


def _isOnValidLayer(entity):
    return entity.layer in DxfConfig.VALID_LAYERS

def _isPolylineOpen(entity, attemptClose=True):
    """
    Checks to see if a polyline is open. If so, will attempt to close it if
    the start and end points are below a threshold distance apart. If the
    entity passed to the function is not a Polyline, will return False.
    :type entity: Polyline or LWPolyline
    :return: True if a polyline is open and can't be closed, False if the
        entity is closed or is not a polyline
    :rtype: bool
    """

    gap = None

    if entity.dxftype == DxfConfig.POLYLINE or \
        entity.dxftype == DxfConfig.LWPOLYLINE:
            if entity.is_closed:
                return gap
            else:
                if attemptClose:
                    if _closePolyline(entity):
                        return gap
                start = Point(entity.points[0][0], entity.points[0][1])
                end = Point(entity.points[-1][0], entity.points[-1][1])
                gap = (start, end)

    return gap

def _closePolyline(polyline):
    """
    Attempts to close a polyline. If the polyline gap is greater than the
    threshold, will not close the polyline. Returns True if the polyline was
    successfully closed, False otherwise.
    :type polyline: dxfgrabber.entities.Polyline or
        dxfgrabber.entities.LWPolyline
    :return: True if polyline could be closed, False otherwise
    :rtype: bool
    """

    p1 = polyline.points[0]
    p2 = polyline.points[-1]
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]

    if ((y2 - y1)**2 + (x2 - x1)**2) <= DxfConfig.CLOSED_POLYLINE_THRESHOLD**2:
        polyline.points.append((x1, y1))
        polyline.is_closed = True
        return True
    else:
        return False

def _checkForOpenPolylines(drawing, layers):
    """
    Checks all polylines in a drawing to ensure that they are closed
    :type drawing: dxfgrabber.drawing.Drawing
    :return: A violation containing the open polylines
    :rtype: intermediate.Violation | None
    """
    logger.info('Checking for open polylines ...')

    result = []

    for layerName, entities in layers.iteritems():

        openPolylines = []
        badInserts = []
        witnesses = []

        for entity in entities:
            if entity.dxftype == DxfConfig.INSERT:
                badInsert = _checkInsertForOpenPolylines(entity, drawing)
                if badInsert:
                    badInserts.append(badInsert)
            else:
                openPolyline = _isPolylineOpen(entity)
                if openPolyline:
                    openPolylines.append(entity)
                    witness = intermediate.Witness(
                                    intermediate.Witness.LINE_SEGMENT,
                                    openPolyline)
                    witnesses.append(witness)

        if openPolylines or badInserts:
            name = PurityConfig.OpenPolyline.HEADER
            description = PurityConfig.OpenPolyline.DESCRIPTION
            errorLayerName = DxfConfig.LAYER_OPEN_POLY
            originatingLayer = Translations.layerNameToNum(layerName)
            violation = intermediate.Violation(name, description,
                                                errorLayerName,
                                                entities=openPolylines,
                                                inserts=badInserts,
                                                layer=originatingLayer,
                                                witnesses=witnesses,
                                                ruleID=1000)
            result.append(violation)



    logger.info('Open polyline check complete.')
    return result

def _checkInsertForIntersectingPolylines(insert, drawing):
    """

    :type insert:
    :type drawing: dxfgrabber.drawing.Drawing
    :return:
    :rtype:
    """
    xPolylineBlock = []

    block = drawing.blocks.get(insert.name)
    for entity in block:
        if entity.dxftype == DxfConfig.POLYLINE or \
                        entity.dxftype == DxfConfig.LWPOLYLINE:
            if entity.is_closed:
                if _checkPolylineSelfIntersecting(entity):
                    logger.info('Self intersecting polyline in block' +
                                insert.name)
                    xPolylineBlock.append(entity)
        elif entity.dxftype == DxfConfig.INSERT:
            result = _checkInsertForIntersectingPolylines(entity, drawing)
            if result:
                xPolylineBlock.append(result)

    if xPolylineBlock:
        badInsert = BadInsert(insert, xPolylineBlock)
    else:
        badInsert = None

    return badInsert

def _checkInsertForOpenPolylines(insert, drawing):
    """

    :type insert: dxfgrabber.entities.Insert
    :type drawing: dxfgrabber.drawing.Drawing
    :return:
    :rtype: BadInsert | None
    """

    openPolylineBlock = []

    block = drawing.blocks.get(insert.name)
    for entity in block:
        if entity.dxftype == DxfConfig.POLYLINE or \
                        entity.dxftype == DxfConfig.LWPOLYLINE:
            if _isPolylineOpen(entity):
                openPolylineBlock.append(entity)

        elif entity.dxftype == DxfConfig.INSERT:
            result = _checkInsertForOpenPolylines(entity, drawing)
            if result:
                openPolylineBlock.append(result)

    if openPolylineBlock:
        badInsert = BadInsert(insert, openPolylineBlock)
    else:
        badInsert = None

    return badInsert

def _checkInsertForInvalidEntities(insert, drawing, validEntityTypes):
    """

    :type insert:
    :type drawing: dxfgrabber.drawing.Drawing
    :type validEntityTypes:
    :return:
    :rtype:
    """

    invalidEntityBlock = []

    block = drawing.blocks.get(insert.name)
    for entity in block:
        if entity.layer in DxfConfig.VALID_LAYERS:
            if entity.dxftype not in validEntityTypes:
                if entity.dxftype == DxfConfig.INSERT:
                    result = _checkInsertForInvalidEntities(entity, drawing,
                                                            validEntityTypes)
                    if result:
                        invalidEntityBlock.append(result)
                else:
                    invalidEntityBlock.append(entity)

    if invalidEntityBlock:
        badInsert = BadInsert(insert, invalidEntityBlock)
    else:
        badInsert = None

    return badInsert

def _moveTinyInsertToLayer(insert, layerName):
    for entity in insert.block:
        if isinstance(entity, BadInsert):
            _moveTinyInsertToLayer(insert, layerName)
        else:
            entity.layer = layerName

def __calculatePerimeter(polyline):
    perimeter = 0

    for p1, p2 in zip(polyline.points, polyline.points[1:]):
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]

        perimeter += sqrt((x2 - x1)**2 + (y2 - y1)**2)

    if polyline.is_closed:
        x1, y1 = polyline.points[-1][0], polyline.points[-1][1]
        x2, y2 = polyline.points[0][0], polyline.points[0][1]

        perimeter += sqrt((x2 - x1)**2 + (y2 - y1)**2)

    return perimeter
