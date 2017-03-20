from .. import Rule
from .. import Violation
from .. import DesignDict
from SupportCheck import checkSupport
from config import rules

ruleDict = rules[17]

class Rule17(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        SU8_1 = dd.layers[DesignDict.SU81]
        SU8_2 = dd.layers[DesignDict.SU82]
        checkSupport(self, dd, SU8_1, SU8_2)

rule17 = Rule17()

Rule.dict[ruleDict[Rule.ID]] = rule17
