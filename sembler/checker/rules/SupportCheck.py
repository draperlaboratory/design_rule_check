from .. import Rule
from .. import Violation
from .. import DesignDict
from .. import Witness
from .. import Feature
from shapely.prepared import prep
from shapely.geometry import Polygon, MultiPolygon

THRESHOLD =10e-6

#logging
import logging
logger = logging.getLogger('root')

def supported(below, above):
    logger.info("Checking support ...")
    # These log statements create massive log files if the polygons are complex
    # logger.debug(str(below) + " " + str(below.shape))
    # logger.debug(str(above) + " " + str(above.shape))
    pBelow = prep(below.shape)
    included = pBelow.contains_properly(above.shape) or below.shape.almost_equals(above.shape)
    logger.info("Supported: " + str(included))
    return included

def checkSupport(rule, dd, belowLayer, aboveLayer):
    objs = aboveLayer.objs
    for id2, o2 in objs.items():
        ## Support posts are supported -- you don't have to check
        bbox = o2.shape.bounds
        cumulative = Polygon(o2.shape)
        o2_supported = False
        ## things below that might support the object
        candidates = belowLayer.index.intersection(bbox)
        for cind in candidates:
            if not cind in dd.layers[DesignDict.POST].objs:
                o1 = belowLayer.objs[cind]
                if supported(o1,o2):
                    o2_supported = True
                    break
                else:
                    cumulative = cumulative.difference(o1.shape)
        ## we didn't leave the inner loop with a return.
        ## the above object isn't supported.
        if not o2_supported:
            wit = []
            if isinstance(cumulative, Polygon):
                wit.append(Witness(Witness.REGION, cumulative))
            elif isinstance(cumulative, MultiPolygon):
                for r in cumulative:
                    wit.append(Witness(Witness.REGION, r))
            else:
                raise "Unrecognized type"
            dd.violations.add(Violation.ofRule(rule,[o2], wit))

