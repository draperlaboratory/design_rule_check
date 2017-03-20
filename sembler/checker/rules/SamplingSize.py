from .. import DesignDict
from shapely.geometry import Polygon, Point, LineString, MultiLineString, MultiPolygon
from shapely.prepared import prep
import random
from math import ceil

# vis
import json
from shapely.geometry import mapping
from shapely.ops import triangulate

from matplotlib import pyplot

#logging
import logging
logger = logging.getLogger('root')

SAMPLES = 1000

def prepPolygon(poly):
     THRESHOLD=10e-6
     toSample = poly
     prepped = prep(poly)
     raw = triangulate(toSample)
     triangles = [x for x in raw if prepped.contains_properly(x.buffer(-THRESHOLD))]
     areas = [ t.area for t in triangles ]
     totalArea = sum(areas)
     numSamples = [ (int) (ceil((x / totalArea) * SAMPLES)) for x in areas ]
     paired = zip(numSamples, triangles)
     return paired, prepped

def prepPolygonSafe(poly):
     THRESHOLD=10e-6
     toSample = Polygon(poly.exterior)
     prepped = prep(toSample)
     raw=[]
     try:
          raw = triangulate(toSample)
     except:
          logger.error( "prepPolygonSafe failed to triangulate a polygon, dumping to failedTriangulation.json.")
          open("failedTriangulation.json", "wb").write(json.dumps(mapping(poly)))
          exit

     triangles = [x for x in raw if prepped.contains_properly(x.buffer(-THRESHOLD))]
     areas = [ t.area for t in triangles ]
     totalArea = sum(areas)
     numSamples = [ (int) (ceil((x / totalArea) * SAMPLES)) for x in areas ]
     paired = zip(numSamples, triangles)
     return paired, prep(poly)

def prepPolygon(poly):
     try:
          return perPolygon(poly)
     except:
          logger.warning("Failed to triangulate a polygon. Using prepPolygonSafe and dumping to failedTriangulationUnsafe.json.")
          open("failedTriangulationUnsafe.json", "wb").write(json.dumps(mapping(poly)))
          return prepPolygonSafe(poly)

def nRandomTriangleSamples(poly, triangles):
     ret = []
     rejected = 0
     for(toSample,triangle) in triangles:
          # What's one extra sample between friends?
          tPoints = triangle.exterior.coords
          (p0x, p0y) = tPoints[0]
          (p1x, p1y) = tPoints[1]
          (p2x, p2y) = tPoints[2]
          p1Transx = p1x - p0x
          p1Transy = p1y - p0y
          p2Transx = p2x - p0x
          p2Transy = p2y - p0y
          cX = p2x - (p2x - p1x) / 2
          cY = p2y - (p2y - p1y) / 2
          while (toSample > 0):
               a1 = random.uniform(0,1)
               a2 = random.uniform(0,1)
               pX = p0x + p1Transx * a1 + p2Transx * a2
               pY = p0y + p1Transy * a1 + p2Transy * a2
               pPoint = Point((pX, pY))
               if poly.intersects(pPoint):
                    ret.append(pPoint)
                    toSample -= 1
               else: #Point might be in the dual space. Reflect about the linesegment, and take sample.
                    dx = pX - cX
                    dy = pY - cY
                    rPPoint = Point((pX - 2 * dx, pY - 2 * dy))
                    if poly.intersects(rPPoint):
                         ret.append(rPPoint)
                         toSample -= 1
                    else:
                         # point was in a hole in the polygon I guess. Report it and try again
                         rejected += 1
     if rejected > 0:
          logger.debug("nRandomTriangleSamples rejected samples: " + str(rejected))
     return ret

def nRandomBBoxSamples(poly, n=SAMPLES):
     (minx, miny, maxx, maxy) = poly.bounds
     ppoly = prep(poly)
     ret = []
     while(n > 0):
          p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
          if ppoly.intersects(p):
               ret.append(p)
               n = n - 1
     return ret

def nRandomSamples(poly):
     AREATHRESHOLD = 0.5
     (minx,miny,maxx,maxy) = poly.bounds
     bbox = Polygon([(minx,miny), (minx, maxy), (maxx,maxy), (maxx, miny)])
     ratio = poly.area / bbox.area
     if ratio > AREATHRESHOLD:
          return nRandomBBoxSamples(poly)
     else:
          paired, prepped = prepPolygon(poly)
          return nRandomTriangleSamples(prepped, paired)


def maxMinDistance(poly, dd):
    allLines = []
    allLines.append(poly.exterior)
    postLayer = dd.layers[DesignDict.POST]
    portLayer = dd.layers[DesignDict.PORTS]
    possiblePosts = postLayer.index.intersection(poly.bounds)
    possiblePorts = portLayer.index.intersection(poly.bounds)
    candidatePosts = []
    prepPoly = prep(poly)
    construct = Polygon(poly)

    for objind in possiblePosts:
         obj = dd.objects[objind]
         if prepPoly.contains_properly(obj.shape):
              candidatePosts.append(obj.shape)

    for objind in possiblePorts:
         obj = dd.objects[objind]
         if prepPoly.contains_properly(obj.shape):
              candidatePosts.append(obj.shape)

    logger.debug(str(len(candidatePosts)) + " candidate support posts")

    for post in candidatePosts:
         ## subtract the post from the polygon interior
         construct = construct.difference(post)

    for interior in construct.interiors:
        candidatePosts.append(Polygon(interior))
        allLines.append(interior)

    allLines = MultiLineString(allLines)

    currentPoint = construct.centroid
    if construct.contains(currentPoint):
         currentDist = allLines.distance(currentPoint)
    else:
         currentDist = None

    triangles, pconstruct = prepPolygon(construct)
    points = nRandomTriangleSamples(pconstruct,triangles)
    for p in points:
         dist = allLines.distance(p)
         if dist > currentDist:
              currentPoint = p
              currentDist = dist
    return (currentPoint, currentDist)


def visResult(poly, currentPoint, dist):
    circle = currentPoint.buffer(dist)
    circle2 = currentPoint.buffer(50)
    toDraw = MultiPolygon([circle,circle2,poly])
    open("exampleInscribed.json", "wb").write(json.dumps(mapping(toDraw)))


def test(poly):
    (currentPoint, dist) = maxMinDistance(poly)
    visResult(poly,currentPoint, dist)

def visPolyTriangle(poly):
     (wtTriangle,pgeom) = prepPolygon(poly)
     triangles = [x[1] for x in wtTriangle]
     toDraw = MultiPolygon(triangles)
     open("toTriangulate.json", "wb").write(json.dumps(mapping(poly)))
     open("exampleTriangulation.json", "wb").write(json.dumps(mapping(toDraw)))


p = Polygon([(0, 0), (0, 2), (1, 1), (2, 1), (3,2), (3, 0), (0, 0)])
