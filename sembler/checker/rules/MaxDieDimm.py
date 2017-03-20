from .. import Rule
from .. import Violation
from .. import Witness
from .. import DesignDict
import logging
from config import rules

logger = logging.getLogger('root')
ruleDict = rules[4]

class Rule4(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        if dd.border:
            edge = dd.border.shape
            (minx, miny, maxx, maxy) = edge.bounds
            w = maxx - minx
            h = maxy - miny
            d = max(w,h)
            if d != 75000 and d > 40000:
                logger.debug("Die Size " + str(d) + " > 40000")
                wit = Witness(Witness.REGION, dd.border.shape)
                dd.violations.add(Violation.ofRule(self, [dd.border], [wit]))
        else:
            logger.error("No border!")

rule4 = Rule4()
Rule.dict[ruleDict[Rule.ID]] = rule4
