from .. import Rule
from .. import DesignDict
from MaxLineWidth import checkMaxWidth
from config import rules

ruleDict = rules[10]

class Rule10(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        checkMaxWidth(self, dd, DesignDict.SU81, ruleDict[Rule.THRESH])

rule10 = Rule10()

Rule.dict[ruleDict[Rule.ID]] = rule10
