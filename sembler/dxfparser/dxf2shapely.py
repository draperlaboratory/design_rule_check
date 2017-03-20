from shapely.geometry.polygon import LinearRing, LineString, Polygon
from shapely.geometry import Point, MultiPolygon
from shapely.ops import unary_union
from shapely.prepared import prep

from config import DxfConfig

from matplotlib import pyplot
from descartes import PolygonPatch

from math import atan, atan2, sin, cos, pi
from rtree import index

import logging

logger = logging.getLogger('root')

DEBUG = False

def _convertBulge(start, end, bulge):
    """
    Converts an AutoCAD arc of two points and a bulge value to a center point,
    radius, start and end angle.
    Uses http://www.afralisp.net/archive/lisp/Bulges1.htm as a guide
    :param start: Start point tuple (x0, y0)
    :param end: End point tuple (x1, y1)
    :param bulge: Bulge value for this segment
    :type start: tuple
    :type end: tuple
    :type bulge: float
    :return: Center, start angle, end angle, radius
    """

    x0, y0 = start
    x1, y1 = end

    chord = ((x1 - x0)**2 + (y1 - y0)**2)**.5
    angle = 4.0 * atan(bulge)

    r = (chord / 2.0) / sin(angle / 2.0)
    startEndAngle = _angleBetweenPoints(start, end)
    angleToCenter = pi / 2.0 - angle / 2.0 + startEndAngle

    center = _polar(start, angleToCenter, r)

    startAngle = _angleBetweenPoints(center, start)
    endAngle   = _angleBetweenPoints(center, end)

    if bulge < 0:
        while endAngle > startAngle:
            endAngle -= 2 * pi
    else:
        while endAngle < startAngle:
            endAngle += 2 * pi

    return center, abs(r), startAngle, endAngle

def  _angleBetweenPoints(p1, p2):
    """
    Returns the angle of the line between two points made to the X-axis in
    radians
    :type p1: tuple
    :type p2: tuple
    :return: Angle in radians
    :rtype: float
    """

    x1, y1 = p1
    x2, y2 = p2

    v1, v2 = x2 - x1, y2 - y1

    return atan2(v2, v1)

def _polar(pt, angle, distance):
    """
    Returns the point at a specified angle and distance from a point
    Mirrors the functionality of AutoLISPs polar function
    http://help.autodesk.com/view/ACD/2016/ENU/?guid=GUID-6A84BFD3-8788-45B1-AB52-5E83F0C5286E
    :param pt: The start point
    :param angle: The angle (in radians) relative to the X axis
    :param distance: The distance from the specified start point
    :type pt: tuple
    :type angle: float
    :type distance: float
    :return: The point at distance and angle from pt
    """
    x0, y0 = pt

    dx = distance * cos(angle)
    dy = distance * sin(angle)

    return (x0 + dx, y0 + dy)

def _discretizeArc(arc, nPoints=50):
    """
    Takes an arc specified as (center, radius, startAngle, endAngle) and
    discretizes it into nPoints line segments
    :type arc: tuple
    :type nPoints: int
    :return: A list of points corresponding to the discretized arc
    :rtype: list[tuple]
    """

    center, radius, startAngle, endAngle = arc

    if radius < DxfConfig.DISCRETIZE_ARC_EPSILON:
        raise ValueError("_discretizeArc received radius of size less than "
                         "epsilon.")

    cx = center[0]
    cy = center[1]
    discretized = []
    step = float(endAngle - startAngle) / (nPoints - 1)
    ## We don't say which way we're traversing the polygon, so we don't know
    ## if step is positive or negative.  That's why we've got the conditional here
    if step > 0:
        ## Step must be at least epsilon / radius to avoid discarding points as too near.
        step = max(step, DxfConfig.DISCRETIZE_ARC_EPSILON / radius)
        step = min(step, DxfConfig.MAX_DISCRETIZED_SEGMENT_LENGTH / radius)
    else:
        step = min(step, -DxfConfig.DISCRETIZE_ARC_EPSILON / radius)
        step = max(step, -DxfConfig.MAX_DISCRETIZED_SEGMENT_LENGTH / radius)
    a = startAngle
    while (startAngle < endAngle and a < endAngle) or (startAngle > endAngle and a > endAngle):
        dx = radius * cos(a)
        dy = radius * sin(a)
        px = cx + dx
        py = cy + dy
        discretized.append((px,py))
        a += step
    return discretized

def _linspace(a, b, n=100):
    """
    Creates a list of n linearly spaced values between a and b
    :type a: float
    :type b: float
    :type n: int
    :return: A list of linearly spaced values between a and b
    :rtype: list[float]
    """

    if n < 2:
        return b
    step = (float(b) - a) / (n - 1)
    ## Don't generate the last element because we only ever use this in discretizeArc
    ## Where we pop off the last element anyway
    return [step * i + a for i in xrange(n-1)]

def polyline2polygon(polyline, offsets=(0, 0)):
    """
    Creates a shapely Polygon object from a polyline. Discretizes any arcs
    found in the polyline.
    :type polyline: dxfgrabber.entities.LWPolyline
    :type offsets: tuple
    :return: A shapely Polygon object
    :rtype: shapely.geometry.polygon.Polygon
    """

    points = polyline.points
    bulges = polyline.bulge

    dx, dy = offsets
    polygonPoints = []

    if len(points) < 3:
        raise ValueError('Two points does not a polygon make.')

    if not polyline.is_closed:
        raise ValueError('Received an open polyline when converting to polygon')

    points.append(polyline.points[0])
    bulges.append(polyline.bulge[0])

    for idx, vertex in enumerate(zip(points[:-1], bulges[:-1])):
        # A bulge of 0 is a straight segment
        pt, bulge = vertex
        pt2 = points[idx + 1]

        if bulge == 0:
            polygonPoints.append((pt[0] + dx, pt[1] + dy))

        elif pt[0:2] == pt2[0:2]:
            # Duplicate points in the polyline. Skip it.
            continue

        else:
            # Any other value is an arc
            # Only send the x,y coords from 3d points. We're assuming planar.
            arc = _convertBulge(pt[0:2], pt2[0:2], bulge)
            discretizedArc = _discretizeArc(arc)
            polygonPoints.extend(discretizedArc)

    pt1 = polygonPoints[0]
    points = [pt1]
    for pt2 in polygonPoints:
        dist = (pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2
        if not (dist < 1):
            points.append(pt2)
            pt1 = pt2
    ## Filtering might make the polygon not exist legally
    ## In that case, don't apply the filter
    if len(points) < 3:
        points = polygonPoints

    poly = None
    if points:
        poly = Polygon(points)
    return poly

def polyline2linearRing(polyline, offsets=(0, 0)):
    """
    Creates a shapely linear ring object from a polyline.
    Currently *DOES NOT* convert arcs.
    :type polyline: dxfgrabber.entities.LWPolyline
    :type offsets: tuple
    :return: A shapely LinearRing
    :rtype: shapely.geometry.polygon.LinearRing
    """

    points = polyline.points
    if polyline.is_closed:
        points.append(polyline.points[0])

    dx, dy = offsets
    offsetPoints = [(pt[0] + dx, pt[1] + dy) for pt in points]

    return LinearRing(offsetPoints)

def polyline2lineString(polyline, offsets=(0, 0)):
    """
    Creates a shapely line string object from a polyline.
    Currently *DOES NOT* convert arcs.
    :type polyline: dxfgrabber.entities.LWPolyline
    :type offsets: tuple
    :return: A shapely LineString
    :rtype: shapely.geometry.polygon.LineString
    """

    points = polyline.points

    dx, dy = offsets
    offsetPoints = [(pt[0] + dx, pt[1] + dy) for pt in points]

    return LineString(offsetPoints)

def circle2shapelyCircle(circle, offsets=(0, 0)):
    """
    Takes a DXF circle object and discretizes it to create a shapely object.
    :type circle: dxfgrabber.entities.Circle
    :type offsets: tuple
    :return: A shapely object
    :rtype: (shapely Polygon? LinearRing?)
    """

    dx, dy = offsets

    x, y, z = circle.center
    r = circle.radius

    p = Point(x + dx, y + dy)

    # This should be turned on when a good value is agreed upon.
    # shapelyCircle = p.buffer(r, DxfConfig.CIRCLE_SEGMENTS_PER_UM)

    shapelyCircle = p.buffer(r)

    return shapelyCircle

def _circle2DRCCircle(circle, offsets=(0, 0)):
    """
    Converts a dxf circle object to an object readable by the rule checker
    :type circle: dxfgrabber.entities.Circle
    :type offsets: tuple
    :return: A circle readable by the DRC
    :rtype: dxfgrabber.entities.Circle
    """
    return circle

def convertLayer(layer):
    """
    Takes in a list of dxfgrabber entities and converts them to the correct
    shapely object
    :param layer: A list of dxfgrabber entities
    :type layer: list
    :return: A list of shapely objects
    :rtype: list
    """
    shapelyLayer = []

    for entity in layer:
        if entity.dxftype == DxfConfig.POLYLINE or \
                        entity.dxftype == DxfConfig.LWPOLYLINE:
            shapelyObject = polyline2polygon(entity)
        elif entity.dxftype == DxfConfig.CIRCLE:
            if entity.layer == DxfConfig.VPORT:
                shapelyObject = _circle2DRCCircle(entity)
            else:
                shapelyObject = circle2shapelyCircle(entity)
        else:
            if not DEBUG:
                logger.critical('Unknown entity type: ' + str(entity.dxftype))
                raise ValueError('Unknown entity type', entity.dxftype)

        if shapelyObject is not None:
            shapelyLayer.append(shapelyObject)

    return shapelyLayer

def setify(collection):
    """
    Discards all duplicate shapely elements in the given collection
    :type collection: list
    :return: The list of elements in the collection with duplicates removed
    :rtype: list
    """
    contains = []
    for el in collection:
        acceptable = True
        for c in contains:
            if c.almost_equals(el):
                logger.warning("Discarding duplicate polygon during unioning")
                acceptable = False
        if acceptable:
            contains.append(el)
    return contains

def quadTreeSetify(collection):
    """
    Discards all duplicate shapely elements in the given collection
    :type collection: list
    :return: The list of elements in the collection with duplicates removed
    :rtype: list
    """
    contains = []
    qtree = index.Index()
    ind = 0
    for el in collection:
        possibleHits = qtree.intersection(el.bounds)
        acceptable = True
        for pInd in possibleHits:
            p = contains[pInd]
            if p.equals(el) or p.almost_equals(el):
                acceptable = False
                continue
        if acceptable:
            contains.append(el)
            qtree.insert(ind,el.bounds)
            ind = ind + 1
    return contains

def bufferLayer(layer, distance):
    """
    Takes all shapes on a given layer and buffers them by a fixed value
    :type layer: list or MultiPolygon
    :type distance: float
    :rtype: list
    """
    bufferedLayer = []
    for shape in layer:
        bufferedLayer.append(shape.buffer(distance))
    return bufferedLayer

def findShapesInHoles(shapes, layer):
    """

    :type shapes: list
    :type layer: shapely.geometry.multipolygon.MultiPolygon
    :return:
    :rtype:
    """
    inHoles = []

    for polygon in layer:

        temp_inHoles = []
        # Loop through the 'holes' of the polygon
        for interiorRing in polygon.interiors:
            # Prep it for faster calculamating
            preppedInterior = prep(Polygon(interiorRing))
            # Find every shaped contained by the 'hole'
            temp_inHoles.extend(
                filter(preppedInterior.contains_properly, shapes))

        inHoles.extend(temp_inHoles)

    # If no shapes lie within any 'holes', return an empty list
    nothingInHoles = all(map(lambda x: x == [], inHoles))
    if nothingInHoles:
        inHoles = []

    return inHoles

def findContainedShapes(shapes, layer):
    """
    Finds all shapes that are fully contained within the polygons on the
    provided layer.
    :type shapes: list[shapely.geometry.polygon.Polygon]
    :type layer: shapely.geometry.multipolygon.MultiPolygon or
    list[shapely.geometry.polygon.Polygon]
    :return: A list of lists. The list at index i corresponds to the polygons
    contained by the shape found at layer[i].
    :rtype: list[list]
    """
    contained = []

    for polygon in layer:
        # Prep the shape for faster calculating
        preppedPolygon = prep(polygon)
        # Find every shape that is contained by the polygon
        temp_contained = filter(preppedPolygon.contains_properly, shapes)
        contained.append(temp_contained)

    # If no shapes lie within any polygons on the layer, return an empty list
    nothingContained = all(map(lambda x: x == [], contained))
    if nothingContained:
        contained = []

    return contained


def nestedUnion(layer):
    """
    Unions together all shapes on a layer, taking into account nesting.
    Shapes with nested geometry will be treated correctly as positive or
    negative space.
    :param layer: A list of shapely objects to union
    :type layer: list
    :return: The list of objects, post-union
    :rtype: list
    """

    bufferedLayer = bufferLayer(layer, DxfConfig.UNION_LAYER_BUFFER)
    unioned = unary_union(bufferedLayer)

    # if DEBUG:
    #     plotDebug(unioned, 'Unioned', (-10000, 10000), (-5000, 5000))

    # If unioned is a single polygon, turn it into a MultiPolygon to generalize
    # the rest of the code
    if not isinstance(unioned, MultiPolygon):
        unioned = MultiPolygon([unioned])

    contained = findContainedShapes(bufferedLayer, unioned)

    # if DEBUG:
    #     for c in contained:
    #         plotDebug(c, 'Contained', (-10000, 10000), (-5000, 5000))
    #     for i in inHoles:
    #         plotDebug(i, 'In Hole', (-10000, 1000), (-5000, 5000))

    while contained:
        newLayer = []

        for i, unionedShape in enumerate(unioned):

            for interiorShape in contained[i]:
                unionedShape = unionedShape.difference(interiorShape)

            if isinstance(unionedShape, MultiPolygon):
                newLayer.extend(list(unionedShape))
            else:
                newLayer.append(unionedShape)

        unioned = unary_union(newLayer)

        if not isinstance(unioned, MultiPolygon):
            unioned = MultiPolygon([unioned])

        inHoles = findShapesInHoles(bufferedLayer, unioned)

        # If there are shapes contained within holes, union them all and
        # add them to the unioned list
        if inHoles:
            holeUnion = nestedUnion(inHoles)
            unionedList = list(unioned)

            unioned = MultiPolygon(holeUnion + unionedList)

        contained = findContainedShapes(bufferedLayer, unioned)

    # Unbuffer the layer before returning
    unioned = bufferLayer(unioned, -DxfConfig.UNION_LAYER_BUFFER)

    return unioned


def calculatePolarity(shapelyLayer, layerName=None):
    """

    :type shapelyLayer: list
    :type layerName: str
    :return:
    :rtype:
    """

    if layerName == DxfConfig.VPORT:
        return shapelyLayer

    # no objects, nothing to do
    if len(shapelyLayer) <= 1:
        return shapelyLayer

    shapelyLayer = quadTreeSetify(shapelyLayer)
    unionedLayer = nestedUnion(shapelyLayer)

    if DEBUG:
        plotDebug(unionedLayer, layerName, (-10000, 10000), (-5000, 5000))

    return unionedLayer

def plotDebug(polygons, layerName, xrange, yrange):
    """
    Plots the set of given polygons and gives the plot a title of layerName
    :type polygons: list
    :type layerName: str
    :type xrange: tuple
    :type yrange: tuple
    """

    fig = pyplot.figure(1, figsize=(10, 10), dpi=90)
    ax = fig.add_subplot(111)

    for ob in polygons:
        p = PolygonPatch(ob, fc='g', ec='g', alpha=0.5, zorder=1)
        ax.add_patch(p)

    ax.set_xlim(*xrange)
    ax.set_ylim(*yrange)
    ax.set_aspect(1)
    ax.set_title(layerName)

    pyplot.show()
