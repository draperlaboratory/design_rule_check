from .. import Rule
from .. import Feature
from .. import Violation
from .. import Witness
from .. import DesignDict
from config import rules

ruleDict = rules[20]

class Rule20(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        posts = dd.layers[DesignDict.POST]
        for fid, feat in posts.objs.items():
            if feat.depth == DesignDict.SU83:
                (minx, miny, maxx, maxy) = feat.shape.bounds
                w = maxx - minx
                h = maxy - miny
                d = max(w,h)
                if d < ruleDict[Rule.THRESH]:
                    wit = Witness(Witness.POINT_RADIUS, (feat.shape.centroid, d))
                    dd.violations.add(Violation.ofRule(self,[feat], [wit]))

rule20 = Rule20()
Rule.dict[ruleDict[Rule.ID]] = rule20
