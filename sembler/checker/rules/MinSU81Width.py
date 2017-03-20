from .. import Rule
from .. import DesignDict
from LayerMinLinewidth import minLWInLayer
from config import rules

ruleDict = rules[9]

class Rule9(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        minLWInLayer(self, dd, DesignDict.SU81, ruleDict[Rule.THRESH])

rule9 = Rule9()
Rule.dict[ruleDict[Rule.ID]] = rule9
