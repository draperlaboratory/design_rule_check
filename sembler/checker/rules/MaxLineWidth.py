from .. import DesignDict
from .. import Violation
from .. import Witness
from .. import Feature
from .. import Object
from config import PHYSICAL_LAYERS, SU81
from SamplingSize import maxMinDistance, test
from shapely.geometry import Polygon, MultiPolygon

import logging
logger = logging.getLogger('root')

def checkMaxWidth(rule, dd, layerID, threshold):
    layer = dd.layers[layerID]

    ## Set up the dicitionary of things above and belowme.
    aboveID = layerID + 1
    belowID = SU81
    aboveLayer = None
    belowLayer = None
    if aboveID in PHYSICAL_LAYERS:
        aboveLayer = dd.layers[aboveID]
    if belowID != layerID:
        belowLayer = dd.layers[belowID]

    objs = layer.objs
    for ident, obj in objs.items():
        if obj.type == Object.FEATURE and obj.diameter > threshold:
            ## Object is large enough to test
            bbox = obj.shape.bounds
            cumulative = Polygon(obj.shape)

            ## Add in everything supporing you, so you get the width of the
            ## whole structure to this point
            if belowLayer:
                candidates = belowLayer.index.intersection(bbox)
                for cind in candidates:
                    if not cind in dd.layers[DesignDict.POST].objs:
                        below = belowLayer.objs[cind]
                        if below.shape.contains(cumulative):
                            cumulative = cumulative.union(below.shape)
            ## Subtract out the layer above you, so you're considering only the
            ## portions of the structure that stop at this layer.  Layers that
            ## go deeper / higher will be considered in their own pass.
            if aboveLayer:
                candidates = aboveLayer.index.intersection(bbox)
                for cind in candidates:
                    if not cind in dd.layers[DesignDict.POST].objs:
                        above = aboveLayer.objs[cind]
                        if cumulative.contains(above.shape):
                            cumulative = cumulative.difference(above.shape)

            polygons = []
            if isinstance(cumulative, Polygon):
                polygons = [cumulative]
            else:
                for r in cumulative:
                    polygons.append(r)

            ## Polygons now represent the features on this layer which must be checked
            for shape in polygons:
                (point, dist) = maxMinDistance(shape, dd) ## dist here is a radius of the inscribed circle
                ## so in this line we need to double it.
                if dist * 2 > threshold:
                    logger.debug("Violated max width:" + str(dist) + " > " + str(threshold) + "\n\tWitness centered at:" + str(point))
                    wit = Witness(Witness.POINT_RADIUS, (point,dist))
                    dd.violations.add(Violation.ofRule(rule, [obj], [wit]))
