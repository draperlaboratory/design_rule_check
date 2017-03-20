from .. import Rule
from .. import DesignDict
from LayerMinLinewidth import minLWInLayer
from config import rules

ruleDict = rules[13]

class Rule13(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        minLWInLayer(self, dd, DesignDict.SU82, ruleDict[Rule.THRESH])

rule13 = Rule13()
Rule.dict[ruleDict[Rule.ID]] = rule13
