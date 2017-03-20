from .. import Rule
from .. import Violation
from .. import Witness
from .. import DesignDict
from config import rules, METAL
from shapely.geometry import Polygon

ruleDict = rules[33]

class Rule33(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        if dd.border:
            edge = dd.border.shape
            layer = dd.layers[METAL]
            for objid, obj in layer.objs.items():
                if not obj.shape.within(dd.border.shape):
                    wit = Witness(Witness.REGION, obj.shape.difference(dd.border.shape))
                    dd.violations.add(Violation.ofRule(self,[obj], [wit]))

rule33 = Rule33()
Rule.dict[ruleDict[Rule.ID]] = rule33
