from .. import Rule
from .. import AlignmentMark
from .. import Violation
from .. import DesignDict
from config import rules
from .. import Witness

ruleDict = rules[32]


class Rule32(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        alignments = dd.getAlignments()
        count = len(alignments)
        metal = dd.layers[DesignDict.METAL]
        (minx, miny, maxx, maxy) = dd.border.shape.bounds
        d = max(maxx - minx, maxy - miny)
        print d, count
        if len(metal.objs) > 0:
            if count < 3 or (d >= 20000 and count < 6):
                wits = []
                for aid,am in alignments.items():
                    wits.append(Witness(Witness.REGION, am.shape))
                dd.violations.add(Violation.ofRule(self, witnesses=wits))

rule32 = Rule32()

Rule.dict[ruleDict[Rule.ID]] = rule32
