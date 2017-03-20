from .. import Rule
from .. import DesignDict
from LayerBorderBuffer import buffered
from config import rules

ruleDict = rules[43]

class Rule43(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        buffered(self, dd, DesignDict.SU82, ruleDict[Rule.THRESH])

rule43 = Rule43()
Rule.dict[ruleDict[Rule.ID]] = rule43
