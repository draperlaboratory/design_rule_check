from shapely.geometry import Point, Polygon, LineString
from checker import Feature, Port, AlignmentMark

def pointToPolygon(point, polygon):
    lring = LineString(polygon.exterior.coords)    ## Take exterior as linear ring
    d = lring.project(point)           ## Project point onto linear ring, getting distance
    p = lring.interpolate(d)           ## move along ring to get to point of interest
    pointOnPolygon = list(p.coords)[0] ## get the point
    return (point, p)


def polygonToPolygon(poly1, poly2):
    pcoord = poly1.exterior.coords                   ## Take exterior as linear ring
    lring1 = LineString(pcoord)
    lring2 = LineString(poly2.exterior.coords)       ## Take exterior as linear ring
    minD = None
    minP = None
    for p1 in pcoord:
        point = Point(p1)
        d = lring2.project(point)                    ## Project point onto linear ring, getting distance
        if minD == None or abs(minD) > abs(d):
            minD = d
            minP = point                             ## Point on poly1 that gave closest to poly2
    pointOnPoly2 = Point(lring2.interpolate(minD))   ## move along ring to get to point of interest
    return pointToPolygon(pointOnPoly2, poly1)       ## Reduce to the previous solution


def portToFeature(port, feat):
    return pointToPolygon(port.center, feat.shape)

def portToPort(port1, port2):
    return (port1.center, port2.center)

def featureToFeature(feat1, feat2):
    return polygonToPolygon(feat1.shape, feat2.shape)


def featureToBorder(feat, border):
    return polygonToPolygon(feat.shape, border.shape)

def portToBorder(port, border):
    return pointToPolygon(port.center, border.shape)

def alignmentToBorder(am, border):
    return pointToPolygon(am.center, border.shape)

def alignmentToAlignment(am1, am2):
    return (am1.center, am2.center)
