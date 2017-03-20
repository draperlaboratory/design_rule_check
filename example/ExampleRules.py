### Example Rules
from DesignObjects import *

rule27 = Rule("Minimum Port to Port Distance", (Port,Port), 27)

## Dog slow
def r27fun ((p1,p2)):
    return p1.shape.distance(p2.shape) >= 100

## Super quick
def r27funb ((p1,p2)):
    if p1.id == p2.id:
        return True
    d = p1.center.distance(p2.center)
    d -= p1.radius
    d -= p2.radius
    return d >= 100

rule27.fn = r27funb

rule28 = Rule("Port Diameter Constraint", (Port,), 28)
def r28fun((p1,)):
    return p1.radius == 10 or p1.radius == 20 or p1.radius == 30

rule28.fn = r28fun
