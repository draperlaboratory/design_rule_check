from .. import Rule
from .. import DesignDict
from LayerMinLinewidth import minLWInLayer
from config import rules

ruleDict = rules[5]

class Rule5(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        minLWInLayer(self, dd, DesignDict.METAL, ruleDict[Rule.THRESH])

rule5 = Rule5()
Rule.dict[ruleDict[Rule.ID]] = rule5
