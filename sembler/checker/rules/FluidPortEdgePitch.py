from .. import Rule
from .. import Port
from .. import Violation
from .. import Witness
from .. import DesignDict
from config import rules
import NearLineSegment


import logging
logger = logging.getLogger('root')

ruleDict = rules[25]

class Rule25(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        ## this is an aberrant example because ports exist across layers.
        edge = dd.border.shape.exterior
        for objid, port in dd.getPorts().items():
            if port.purpose == Port.UNKNOWN:
                port.setPurpose(dd.layers[DesignDict.METAL].index)
            if port.purpose == Port.VPORT:
                r = port.radius
                c = port.center
                d = c.distance(edge) - r
                ## Radius, not diameter
                if d < ruleDict[Rule.THRESH]:
                    wit = Witness(Witness.LINE_SEGMENT, NearLineSegment.portToBorder(port, dd.border))
                    dd.violations.add(Violation.ofRule(self,[port], [wit]))
                    logger.debug("Violated fluid port to edge pitch:" + str(d) + " > " + str(Rule.THRESH) + "@" + str(r))

rule25 = Rule25()

Rule.dict[ruleDict[Rule.ID]] = rule25
