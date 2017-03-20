from .. import Rule
from .. import Port
from .. import Violation
from .. import DesignDict
from LayerMinDist import minDistInLayer
from config import rules

ruleDict = rules[16]

class Rule16(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        minDistInLayer(self,dd,DesignDict.SU82, ruleDict[Rule.THRESH])

rule16 = Rule16()

Rule.dict[ruleDict[Rule.ID]] = rule16
