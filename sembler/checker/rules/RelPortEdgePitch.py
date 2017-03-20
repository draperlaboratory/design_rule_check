from .. import Rule
from .. import Port
from .. import Violation
from .. import DesignDict
from .. import Witness
from config import rules
from shapely.geometry import Point, LineString
import logging
import NearLineSegment
logger = logging.getLogger('root')

ruleDict = rules[26]


class Rule26(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        ## this is an aberrant example because ports exist across layers.
        edge = dd.border.shape.exterior
        threshold = ruleDict[Rule.THRESH]
        for objid, port in dd.getPorts().items():
            if port.purpose == Port.UNKNOWN:
                port.setPurpose(dd.layers[DesignDict.METAL].index)
            if port.purpose == Port.PAD:
                r = port.radius
                c = port.center
                d = c.distance(edge)
                val = d - r
                if val < threshold:
                    wit = Witness(Witness.LINE_SEGMENT, NearLineSegment.portToBorder(port,dd.border))
                    dd.violations.add(Violation.ofRule(self,[port], [wit]))
                    logger.debug("Violated relief port to edge pitch:" + str(val) + " < " + str(threshold) + " @ " + str(r))

rule26 = Rule26()

Rule.dict[ruleDict[Rule.ID]] = rule26
