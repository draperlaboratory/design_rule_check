from .. import Rule
from .. import AlignmentMark
from .. import Violation
from .. import Witness
from .. import DesignDict
from config import rules
import NearLineSegment
from shapely.geometry import LineString, Polygon

ruleDict = rules[30]

class Rule30(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        ## this is an aberrant example because ports exist across layers.
        alignments = dd.getAlignments()
        violated = []
        allMarks = []
        metal = dd.layers[DesignDict.METAL]
        count = 0
        if len(metal.objs) == 0:
            return
        centers = []
        for i, ai in alignments.items():
            allMarks.append(ai)
            centers.append((ai.center.x,ai.center.y))
            for j, aj in alignments.items():
                if i < j:
                    dist = ai.center.distance(aj.center)
                    if dist < ruleDict[Rule.THRESH]:
                        wit = Witness(Witness.LINE_SEGMENT, NearLineSegment.alignmentToAlignment(ai,aj))
                        violated.append(wit)
        alignShape = LineString(centers)
        (minx,miny,maxx,maxy) = alignShape.bounds
        dx = maxx - minx
        dy = maxy - miny
        ## then we decide if this was not co-linear enough.
        if violated:
            dd.violations.add(Violation.ofRule(self,allMarks, violated))
        elif dx < ruleDict[Rule.THRESH] or dy < ruleDict[Rule.THRESH]:
            poly = Polygon([(minx,miny), (minx, maxy), (maxx,maxy), (maxx,maxy)])
            wit = Witness(Witness.REGION, poly)
            dd.violations.add(Violation.ofRule(self,allMarks, [wit]))

rule30 = Rule30()

Rule.dict[ruleDict[Rule.ID]] = rule30
