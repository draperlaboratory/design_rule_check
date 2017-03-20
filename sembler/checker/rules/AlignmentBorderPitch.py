from .. import Rule
from .. import AlignmentMark
from .. import Violation
from .. import Witness
from .. import DesignDict
from config import rules
import NearLineSegment

ruleDict = rules[31]


class Rule31(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        alignments = dd.getAlignments()
        border = dd.border.shape.exterior
        metal = dd.layers[DesignDict.METAL]
        if len(metal.objs) == 0:
            return
        for i, ai in alignments.items():
            # dist1 = ai.shape.distance(border)
            # Distance 2 is cheaper to computer, and equivalent to distance 1
            dist2 = ai.center.distance(border)
            dist2 -= 250
            d = dist2 - ruleDict[Rule.THRESH] + 10e-3
            if d < 0:
                wit = Witness(Witness.LINE_SEGMENT, NearLineSegment.alignmentToBorder(ai, dd.border))
                dd.violations.add(Violation.ofRule(self,[ai], [wit]))

rule31 = Rule31()

Rule.dict[ruleDict[Rule.ID]] = rule31
