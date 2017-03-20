## Minimum Pitch for Metal Layer Features (center to center)
from .. import Rule
from .. import DesignDict
from .. import Violation
from .. import Witness
from config import rules

ruleDict = rules[8]

def checkThresh(obj1,obj2):
    d = obj1.shape.centroid.distance(obj2.shape.centroid)
    return d < ruleDict[Rule.THRESH]

class Rule8(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self, dd):
        layer = dd.layers[DesignDict.METAL]
        objs = layer.objs
        for id1, o1 in objs.items():
            bbox = o1.shape.buffer(ruleDict[Rule.THRESH]).bounds
            candidates = layer.index.intersection(bbox)
            for cind in candidates:
                o2 = objs[cind]
                # anything here should be a violation, but let's be careful.
                # later, we can remove this test and just add every obj to
                # the list of violations
                if o1.id < o2.id and checkThresh(o1,o2):
                    wit = Witness(Witness.LINE_SEGMENT, (o1.shape.centroid, o2.shape.centroid))
                    dd.violations.add(Violation.ofRule(self,[o1,o2], [wit]))



rule8 = Rule8()
Rule.dict[ruleDict[Rule.ID]] = rule8
