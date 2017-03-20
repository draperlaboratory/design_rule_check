from .. import Rule
from .. import Violation
from .. import Witness
from .. import DesignDict
from config import rules, SU81

ruleDict = rules[34]

class Rule34(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        if dd.border:
            edge = dd.border.shape
            layer = dd.layers[SU81]
            for objid, obj in layer.objs.items():
                if not obj.shape.within(dd.border.shape):
                    wit = Witness(Witness.REGION, obj.shape.difference(edge))
                    dd.violations.add(Violation.ofRule(self,[obj], [wit]))

rule34 = Rule34()
Rule.dict[ruleDict[Rule.ID]] = rule34
