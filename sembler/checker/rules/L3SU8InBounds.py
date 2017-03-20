from .. import Rule
from .. import Violation
from .. import Witness
from .. import DesignDict
from config import rules, SU83

ruleDict = rules[42]

class Rule42(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        if dd.border:
            edge = dd.border.shape
            layer = dd.layers[SU83]
            for objid, obj in layer.objs.items():
                if not obj.shape.within(dd.border.shape):
                    wit = Witness(Witness.REGION, obj.shape.difference(edge))
                    dd.violations.add(Violation.ofRule(self,[obj], [wit]))

rule42 = Rule42()
Rule.dict[ruleDict[Rule.ID]] = rule42
