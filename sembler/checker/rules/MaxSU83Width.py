from .. import Rule
from .. import DesignDict
from MaxLineWidth import checkMaxWidth
from config import rules

ruleDict = rules[19]

class Rule19(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        checkMaxWidth(self, dd, DesignDict.SU83, ruleDict[Rule.THRESH])

rule19 = Rule19()

Rule.dict[ruleDict[Rule.ID]] = rule19
