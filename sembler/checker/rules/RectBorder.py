from .. import Rule
from .. import DesignDict
from .. import Violation
from .. import Witness
from LayerMinLinewidth import checkObs
from math import ceil
from config import rules
from shapely.geometry import Polygon, Point

ruleDict = rules[40]

class Rule40(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        if dd.border:
            prevPoint = None
            coords = dd.border.shape.exterior.coords
            witnesses = []
            for point in coords:
                if prevPoint:
                    (px,py) = prevPoint
                    (tx,ty) = point
                    ## This line is flat in neither x nor y.  We've got a witness to a violation
                    if tx != px and py != ty:
                        witnesses.append(Witness(Witness.LINE_SEGMENT, (Point(prevPoint),Point(point))))
                prevPoint = point
            if witnesses:
                dd.violations.add(Violation.ofRule(self, [dd.border], witnesses))

rule40 = Rule40()
Rule.dict[ruleDict[Rule.ID]] = rule40
