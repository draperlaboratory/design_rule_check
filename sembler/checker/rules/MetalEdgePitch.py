from .. import Rule
from .. import Port
from .. import Violation
from .. import DesignDict
from LayerMinDist import minDistInLayer
from config import rules

ruleDict = rules[6]

class Rule6(Rule):
    def __init__(self):
        Rule.__init__(self,ruleDict)

    def check(self,dd):
        minDistInLayer(self,dd,DesignDict.METAL, ruleDict[Rule.THRESH])

rule6 = Rule6()

Rule.dict[ruleDict[Rule.ID]] = rule6
