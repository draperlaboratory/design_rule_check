from .. import Rule
from .. import Feature
from .. import Violation
from .. import Witness
from .. import DesignDict
from config import rules


import logging
logger = logging.getLogger('root')

ruleDict = rules[15]

class Rule15(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        posts = dd.layers[DesignDict.POST]
        for fid, feat in posts.objs.items():
            if feat.depth == DesignDict.SU82:
                (minx, miny, maxx, maxy) = feat.shape.bounds
                w = maxx - minx
                h = maxy - miny
                d = max(w,h)
                if d < ruleDict[Rule.THRESH]:
                    wit = Witness(Witness.POINT_RADIUS, (feat.shape.centroid, d))
                    dd.violations.add(Violation.ofRule(self,[feat], [wit]))
                    logger.debug("Violated Post Diameter SU82: " + str(d) + " < " + str(ruleDict[Rule.THRESH]))

rule15 = Rule15()
Rule.dict[ruleDict[Rule.ID]] = rule15
