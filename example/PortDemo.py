from DesignObjects import *
from ExampleRules import *
from rtree import index
from shapely.geometry import mapping, MultiPolygon
import sys
import cProfile
import re
import json
from Violation import *

def makePorts(pdim):
    ports = []
    rng = range(0,pdim)
    for x in rng:
        for y in rng:
            ports.append(Port((x * 200, y * 200), 10))
    ports.append(Port((100,100),200))
    return ports

## demo
def demo(ports,pdim):
    violations = []
    print "Checking " + str(len(ports)) + " ports"
    rng = range(0,pdim)

    inds = range(0,len(ports) - 1)

    for i in inds:
        pi = ports[i]
        if not rule28.apply((pi,)):
            violations.append(Violation(rule28, [pi]))
        for j in range(i+1, len(ports) - 1):
            pj = ports[j]
            if not rule27.apply((pi,pj)):
                violations.append(Violation(rule27, [pi,pj]))
    return violations

def demo2(ports):
    print "Checking " + str(len(ports)) + " ports"
    violations = []
    idx = index.Index()
    ## add everything to the spatial index
    for p in ports:
        (pid, (pminx,pminy,pmaxx,pmaxy)) = p.boundingBox()
        idx.insert(pid, (pminx,pminy,pmaxx,pmaxy))
    ## now check the rules
    for p in ports:
        if not rule28.apply((p,)):
            violations.append(Violation(rule28, [p]))
        # find things that could violate rule 27?
        possible = p.center.buffer(250).bounds  ## How do I do this generally?
        candidates = idx.intersection(possible)
        for c in candidates:
            pj = ports[c]
            if not rule27.apply((p,pj)):
                violations.append(Violation(rule27, [p,pj]))
    return violations

def getShape(p):
    return p.shape

if __name__ == '__main__':
    sz = int(sys.argv[1])
    dtype = int(sys.argv[2])
    ports = makePorts(sz)
    pShapes = map(getShape,ports)

    open("demoedFile.geojson", "wb").write(json.dumps(mapping(MultiPolygon(pShapes))))
    if(dtype == 0):
        violations = demo(ports,sz)
    else:
        violations = demo2(ports)
    for v in violations:
        print v
    print "Goodbye."
