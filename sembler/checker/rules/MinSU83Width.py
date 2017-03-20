from .. import Rule
from .. import DesignDict
from LayerMinLinewidth import minLWInLayer
from config import rules

ruleDict = rules[18]

class Rule18(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        minLWInLayer(self, dd, DesignDict.SU83, ruleDict[Rule.THRESH])

rule18 = Rule18()
Rule.dict[ruleDict[Rule.ID]] = rule18
