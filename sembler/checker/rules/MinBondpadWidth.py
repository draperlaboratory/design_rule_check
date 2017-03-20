from .. import Rule
from .. import DesignDict
from .. import Feature
from LayerMinLinewidth import checkObs
from config import rules
from shapely.geometry import Polygon

ruleDict = rules[36]

class Rule36(Rule):
    def __init__(self):
        Rule.__init__(self, ruleDict)

    def check(self,dd):
        layer = dd.layers[DesignDict.METAL]
        bonds = {}
        ports = dd.ports
        for oid, obj in layer.objs.items():
            intersectingPorts = dd.ports.index.intersection(obj.shape.bounds)
            ## there are potentially intersecting ports
            if intersectingPorts:
                for pind in intersectingPorts:
                    port = dd.layers[DesignDict.PORTS].objs[pind]
                    ## the port really intersects the object
                    if port.shape.intersects(obj.shape):
                        ## the bond pad is the intersection of the port and the obj shape
                        ## We create a bond pad one at a time because we assume non-overlapping ports
                        ## Otherwise, a trace with a bond pad at two ends would come back empty.
                        shapeprime = obj.shape
                        shapeprime = shapeprime.intersection(port.shape)
                        objprime = Feature(shapeprime)
                        bonds[oid] = objprime
        checkObs(self,dd,bonds,ruleDict[Rule.THRESH])

rule36 = Rule36()
Rule.dict[ruleDict[Rule.ID]] = rule36
