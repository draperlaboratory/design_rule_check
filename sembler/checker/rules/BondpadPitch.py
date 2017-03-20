from .. import Rule
from .. import DesignDict
from .. import Violation
from .. import Witness
from config import rules
import NearLineSegment

ruleDict = rules[38]

class Rule38(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        layer = dd.layers[DesignDict.METAL]
        bonds = {}
        ports = dd.ports
        for oid, obj in layer.objs.items():
            relevantPorts = dd.ports.index.intersection(obj.shape.bounds)
            for portID in relevantPorts:
                port = dd.ports.objs[portID]
                if port.shape.intersects(obj.shape) or obj.shape.contains(port.shape):
                    bonds[portID] = port

        for id1, o1 in bonds.items ():
            for id2, o2 in bonds.items ():
                if id1 < id2:
                    d = o2.center.distance(o1.center)
                    d -= o2.radius
                    d -= o1.radius
                    if d < ruleDict[Rule.THRESH]:
                        wit = Witness(Witness.LINE_SEGMENT, NearLineSegment.portToPort(o1,o2))
                        dd.violations.add(Violation.ofRule(self,[o1,o2], [wit]))

rule38 = Rule38()
Rule.dict[ruleDict[Rule.ID]] = rule38
