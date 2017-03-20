from .. import Rule
from .. import DesignDict
from LayerBorderBuffer import buffered
from config import rules

ruleDict = rules[44]

class Rule44(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        buffered(self, dd, DesignDict.SU83, ruleDict[Rule.THRESH])

rule44 = Rule44()
Rule.dict[ruleDict[Rule.ID]] = rule44
