from .. import Rule
from .. import Violation
from .. import DesignDict
from SupportCheck import checkSupport
from config import rules

ruleDict = rules[22]

class Rule22(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        SU8_2 = dd.layers[DesignDict.SU82]
        SU8_3 = dd.layers[DesignDict.SU83]
        checkSupport(self, dd, SU8_2, SU8_3)

rule22 = Rule22()

Rule.dict[ruleDict[Rule.ID]] = rule22
