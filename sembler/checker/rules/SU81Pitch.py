from .. import Rule
from .. import Port
from .. import Violation
from .. import DesignDict
from LayerMinDist import minDistInLayer
from config import rules

ruleDict = rules[12]

class Rule12(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        minDistInLayer(self,dd,DesignDict.SU81, ruleDict[Rule.THRESH])

rule12 = Rule12()

Rule.dict[ruleDict[Rule.ID]] = rule12
