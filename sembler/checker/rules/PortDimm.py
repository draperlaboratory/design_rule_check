from .. import Rule
from .. import Port
from .. import Violation
from .. import Witness
from .. import DesignDict
from config import rules

ruleDict = rules[23]

class Rule23(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        ## this is an aberrant example because ports exist across layers.
        for objid, port in dd.getPorts().items():
            r = port.radius
            ## Radius, not diameter
            if not (r == 500 or r == 1000 or r == 1500):
                wit = Witness(Witness.POINT_RADIUS, (port.center, r))
                dd.violations.add(Violation.ofRule(self,[port], [wit]))

rule23 = Rule23()

Rule.dict[ruleDict[Rule.ID]] = rule23
