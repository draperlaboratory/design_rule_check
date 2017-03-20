from .. import Rule
from .. import Port
from .. import Violation
from .. import Witness
from .. import DesignDict
from .. import Object
from .. import Feature
from config import rules
from shapely.geometry import Polygon, Point, LineString
import NearLineSegment

import logging
logger = logging.getLogger('root')

ruleDict = rules[27]

def r27Check(port,obj):
    d = obj.shape.distance(port.center) - port.radius
    ## d < 0, intersecting and ok
    return d

class Rule27(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        ## this is an aberrant example because ports exist across layers.
        SU8_1 = dd.layers[DesignDict.SU81]
        for objid, port in dd.getPorts().items():
            portBounds = port.center.buffer(port.radius + ruleDict[Rule.THRESH]).bounds
            candidates = SU8_1.index.intersection(portBounds)
            for cind in candidates:
                obj = dd.objects[cind]
                if obj.type == Object.ALIGNMENT_MARK and port.purpose == Port.PAD:
                    ## skip this check, neither object contains fluid
                    continue
                # anything here should be a violation, but let's be careful.
                # later, we can remove this test and just add every obj to
                # the list of violations
                d = r27Check(port,obj)
                if d <= 0:
                    logger.debug("Port intersects a feature, it's automatically ok.")
                if d > 0 and d < ruleDict[Rule.THRESH]:
                    logger.debug("Violated SU81 -> Port pitch rule with distance " + str(d) + "\n\t\t" + str(port.center))
                    wit = Witness(Witness.LINE_SEGMENT, NearLineSegment.portToFeature(port,obj))
                    dd.violations.add(Violation.ofRule(self,[port,obj], [wit]))


rule27 = Rule27()

Rule.dict[ruleDict[Rule.ID]] = rule27
