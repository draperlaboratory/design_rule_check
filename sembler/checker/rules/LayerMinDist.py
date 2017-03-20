from .. import Violation
from .. import Feature
from .. import DesignDict
from shapely.prepared import prep
from .. import Witness
import NearLineSegment
from shapely.geometry import Point

def checkThresh(obj1,obj2, thresh):
    d = obj1.shape.distance(obj2.shape)
    return d < thresh

def minDistInLayer(rule,dd,layerID,thresh):
    layer = dd.layers[layerID]
    objs = layer.objs
    for id1, o1 in objs.items():
        bbox = o1.shape.buffer(thresh).bounds
        candidates = layer.index.intersection(bbox)
        prepared = None
        for cind in candidates:
            o2 = objs[cind]
            if o1.id < o2.id:
                if prepared == None:
                    prepared = prep(o1.shape)
                contained = prepared.contains(o2.shape) or \
                            o2.shape.contains(o1.shape)

                if not contained and checkThresh(o1,o2,thresh):
                    (p1,p2) = NearLineSegment.featureToFeature(o1,o2)
                    wit = Witness(Witness.LINE_SEGMENT, (p1,p2) )
                    dd.violations.add(Violation.ofRule(rule,[o1,o2], [wit]))
