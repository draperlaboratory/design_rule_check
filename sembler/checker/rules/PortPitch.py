from .. import Rule
from .. import Port
from .. import Violation
from .. import Witness
from .. import DesignDict
from config import rules

ruleDict = rules[24]

def r24Check(p1,p2):
    if p1.id == p2.id:
        return False
    d = p1.center.distance(p2.center)
    d -= p1.radius
    d -= p2.radius
    return ruleDict[Rule.THRESH] > d

class Rule24(Rule):

    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        ## this is an aberrant example because ports exist across layers.
        p1Index = dd.getPortIndex()
        portDict = dd.getPorts()
        for objid, p1 in portDict.items():
            bbox = p1.center.buffer(ruleDict[Rule.THRESH]).bounds
            candidates = p1Index.intersection(bbox)
            for c in candidates:
                if(p1.id < c):
                    p2 = dd.objects[c]
                    if r24Check(p1, p2):
                        wit = Witness(Witness.LINE_SEGMENT, (p1.center, p2.center))
                        dd.violations.add(Violation.ofRule(self, [p1,p2], [wit]))
                # else, we catch it on the latter half.

rule24 = Rule24()

Rule.dict[ruleDict[Rule.ID]] = rule24
