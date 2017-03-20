from .. import Violation
from .. import DesignDict
from .. import Witness
from shapely.geometry import LineString, Polygon, MultiLineString, MultiPolygon, Point

# vis
import json
from shapely.geometry import mapping

#logging
import logging
logger = logging.getLogger('root')
delta = -1
posDelta = abs(delta)

def check_points(polygon, minwidth):
    coords = list(polygon.exterior.coords)
    toRet = []
    for interior in polygon.interiors:
        for coord in interior.coords:
            coords.append(coord)

    for coord in coords:
        point = Point(coord)
        swell = point.buffer(minwidth)
        remaining = swell.difference(polygon)
        if isinstance(remaining, MultiPolygon):
            ## this is the error case
            wit = Witness(Witness.POINT_RADIUS, (point, minwidth))
            toRet.append(wit)
        elif isinstance(remaining, Polygon):
            ## this is ok
            continue
        else:
            logger.error("Got bizarre result in checkpoints on " + str(point))
    return toRet

def interiorRectangle(p0, p1, minWidth):
    if p0 and p1:
        segment = LineString([p0,p1]);
        if segment.length > posDelta:
            interior_offset = segment.parallel_offset(minWidth, 'right')
            interiorRect = [p0,p1]
            toAdd = list(interior_offset.coords)
            interiorRect.extend(toAdd)
            if len(interiorRect) < 3:
                logger.error("Even worse, got to what should be a failure!")
                logger.error(str(segment.length))
                logger.error("ToAdd " + str(toAdd))
                logger.error("InteriorRect: " + str(interiorRect))
            else:
                return Polygon(interiorRect)


def exteriorRectangle(p0, p1, minWidth):
    segment = LineString([p0,p1]);
    if segment.length > posDelta:
        exterior_offset = segment.parallel_offset(minWidth, 'left')
        exteriorRect = [p0,p1]
        toAdd = list(exterior_offset.coords)
        exteriorRect.extend(toAdd)
        if len(interiorRect) < 3:
            logger.error("Even worse, got to what should be a failure!")
            logger.error(str(segment.length))
            logger.error("ToAdd " + str(toAdd))
            logger.error("InteriorRect: " + str(exteriorRect))
        else:
            return Polygon(exteriorRect)


def addPolygons(ring, interior, minWidth, collection):
    skippedCoincident = 0
    pCoord = False
    for coord in ring:
        if pCoord:
            segment = LineString([coord,pCoord])
            if segment.length > posDelta:
                if interior:
                    rect = interiorRectangle(pCoord, coord, minWidth)
                    if rect:
                        collection.append((rect, True))
                    else:
                        rect = exteriorRectangle(pCoord, coord, minWidth)
                        if rect:
                            collection.append((rect, False))
                pCoord = coord
            else:
                skippedCoincident += 1
        else:
            pCoord = coord
    return skippedCoincident



def minLWInLayer(rule,dd,layerID, threshold):
    layer = dd.layers[layerID]
    objs = layer.objs
    skippedCoincident = 0
    for id1, o1 in objs.items():
        witnesses = check_points(o1.shape, threshold)
        toCheck = []
        checkAgainst = []
        ext = o1.shape.exterior
        interiors = o1.shape.interiors
        # add the exterior to check against
        checkAgainst.append(ext)
        # add rects based on each line segment to test
        skippedCoincident += addPolygons(ext.coords, True, threshold, toCheck)
        for interior in interiors:
            #for each interior surface, add it's describing rectangles
            skippedCoincident += addPolygons(interior.coords, False, threshold, toCheck)
            # also make the interior something we have to check against
            checkAgainst.append(interior)
        ## build a collection to do the test all at once
        mlsCheckAgainst = MultiLineString(checkAgainst)
        ## check the exterior for violations
        violating_rectangles = []
        for (rect, isInterior) in toCheck:
            shrink = rect.buffer(delta)
            if o1.shape.disjoint(shrink):
                continue
            if o1.shape.contains(shrink):
                continue
            if o1.shape.intersects(shrink):
                if isInterior:
                    logger.debug("Witness to violation (interior) at: " + str(shrink.bounds))
                else:
                    logger.debug("Witness to violation (exterior) at: " + str(shrink.bounds))
                violating_rectangles.append(shrink)
                break ## This polygon is bad, go on to the others in the layer.
        if violating_rectangles or witnesses:
            dd.violations.add(Violation.ofRule(rule,[o1], witnesses))
    logger.info("Skipping %i nearly co-incident points in layer %i" % (skippedCoincident, layerID))


def checkObs(rule,dd, objs, threshold):
    skippedCoincident = 0
    for id1, o1 in objs.items():
        toCheck = []
        checkAgainst = []
        ext = o1.shape.exterior
        interiors = o1.shape.interiors
        # add the exterior to check against
        checkAgainst.append(ext)
        # add rects based on each line segment to test
        skippedCoincident += addPolygons(ext.coords, True, threshold, toCheck)
        for interior in interiors:
            #for each interior surface, add it's describing rectangles
            skippedCoincident += addPolygons(interior.coords, False, threshold, toCheck)
            # also make the interior something we have to check against
            checkAgainst.append(interior)
        # build a collection to do the test all at once
        mlsCheckAgainst = MultiLineString(checkAgainst)
        ## check the exterior for violations
        for (rect, isInterior) in toCheck:
            shrink = rect.buffer(delta)
            if o1.shape.disjoint(shrink):
                continue
            if o1.shape.contains(shrink):
                continue
            if o1.shape.intersects(shrink):
                if isInterior:
                    logger.debug("Witness to violation (interior) at: " + str(shrink.bounds))
                else:
                    logger.debug("Witness to violation (exterior) at: " + str(shrink.bounds))
                dd.violations.add(Violation.ofRule(rule,[o1]))
                # early exit on the shape when we hit an issue
                return
    logger.info("Skipping %i nearly co-incident points in layer %i" % (skippedCoincident, DesignDict.METAL))

