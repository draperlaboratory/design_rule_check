from .. import Rule
from .. import DesignDict
from MaxLineWidth import checkMaxWidth
from config import rules

ruleDict = rules[14]

class Rule14(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        checkMaxWidth(self, dd, DesignDict.SU82, ruleDict[Rule.THRESH])

rule14 = Rule14()

Rule.dict[ruleDict[Rule.ID]] = rule14
