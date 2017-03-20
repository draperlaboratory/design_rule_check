from .. import Rule
from .. import DesignDict
from LayerBorderBuffer import buffered
from config import rules

ruleDict = rules[35]

class Rule35(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        buffered(self, dd, DesignDict.SU81, ruleDict[Rule.THRESH])

rule35 = Rule35()
Rule.dict[ruleDict[Rule.ID]] = rule35
