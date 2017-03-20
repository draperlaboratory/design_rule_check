from .. import Rule
from .. import DesignDict
from .. import Violation
from .. import Witness
from math import ceil
from config import rules, FP_EQUAL_FUZZ
from shapely.geometry import Polygon, Point

ruleDict = rules[39]
EPSILON = FP_EQUAL_FUZZ

def closeEnough(d):
    if d  <= EPSILON:
        return True
    elif abs(10000 - d) <= EPSILON:
        return True
    elif abs(20000 - d) <= EPSILON:
        return True
    elif abs(30000 - d) <= EPSILON:
        return True
    elif abs(40000 - d) <= EPSILON:
        return True
    else:
        return False

class Rule39(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        if dd.dimm:
            sizeMax = max(dd.dimm[0], dd.dimm[1])
            sizeMin = min(dd.dimm[0], dd.dimm[1])
            sizeMax -= 7.5
            sizeMin -= 2.5

            slide = abs(sizeMax) < EPSILON and abs(sizeMin) < EPSILON

            if not slide:
                points = dd.border.shape.exterior.coords
                wit = []
                prev = None
                for c in points:
                    p1 = Point(c)
                    if prev:
                        d = p1.distance(prev)
                        ok = closeEnough(d)
                        if not ok:
                            wit.append(Witness(Witness.LINE_SEGMENT, (prev, p1)))
                    prev = p1
                if wit:
                    dd.violations.add(Violation.ofRule(self, [dd.border], wit))

        else:
            ## there's no border for the device
            dd.violations.add(Violation.ofRule(self))

rule39 = Rule39()
Rule.dict[ruleDict[Rule.ID]] = rule39
