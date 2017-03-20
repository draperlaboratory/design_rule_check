from .. import Rule
from .. import Violation
from .. import Witness
from .. import DesignDict
from config import rules

ruleDict = rules[3]

class Rule3(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        edge = dd.border.shape
        (minx, miny, maxx, maxy) = edge.bounds
        w = maxx - minx
        h = maxy - miny
        d = min(w,h)
        if d < ruleDict[Rule.THRESH]:
            dd.violations.add(Violation.ofRule(self,[dd.border], [Witness(Witness.REGION, dd.border.shape)]))

rule3 = Rule3()
Rule.dict[ruleDict[Rule.ID]] = rule3
