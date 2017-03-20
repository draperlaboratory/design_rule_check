from .. import Rule
from .. import Port
from .. import Violation
from .. import DesignDict
from LayerMinDist import minDistInLayer
from config import rules

ruleDict = rules[21]

class Rule21(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        minDistInLayer(self,dd,DesignDict.SU83, ruleDict[Rule.THRESH])

rule21 = Rule21()

Rule.dict[ruleDict[Rule.ID]] = rule21
