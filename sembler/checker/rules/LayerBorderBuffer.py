from .. import Violation
from .. import Witness
from .. import DesignDict
import NearLineSegment

#logging
import logging
logger = logging.getLogger('root')

def checkThresh(obj1,obj2, thresh):
    d = obj1.shape.distance(obj2.shape)
    return d < THRESHOLD

def buffered(rule,dd,layerID,thresh):
    layer = dd.layers[layerID]
    objs = layer.objs
    border = dd.border.shape.exterior
    for id1, o1 in objs.items():
        dist = border.distance(o1.shape)
        if dist < thresh:
            wit = Witness(Witness.LINE_SEGMENT, NearLineSegment.featureToBorder(o1, dd.border))
            logger.debug("Border violation: " + " " + str(o1.shape) + " " + str(border) + " " + str(thresh) + " " + str(dist))
            dd.violations.add(Violation.ofRule(rule,[o1], [wit]))
