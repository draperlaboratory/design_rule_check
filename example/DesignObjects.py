from shapely.geometry import Point, Polygon


class Port:
    count = 0
    ## I'm assuming center is (x,y), but it would also work with Point
    def __init__(self, center, radius):
        self.id = Port.count
        Port.count += 1
        self.center = Point(center)
        self.radius = radius
        self.shape = Point(center).buffer(radius)

    def boundingBox(self):
        return (self.id,
                (self.center.x - self.radius, self.center.y - self.radius,
                 self.center.x + self.radius, self.center.y + self.radius))

    def __str__(self):
       return "Port " + str(self.id)


class Channel:
    count = 0

    def __init__(self,something):
        self.id = Channel.count
        Channel.count += 1
        raise Exception("Stub")
        ## and then something to actually set up the thing

    def __str__(self):
        return "Channel " + str(self.id)


class Feature:
    count = 0

    def __init__(self,something):
        self.id = Feature.count
        Feature.count += 1
        raise Exception("Stub")

    def __str__(self):
        return "Feature " + str(self.id)


class Rule:
    count = 0

    def __init__(self, description):
        self.id = Rule.count
        self.desc = description
        Rule.count += 1

    def __init__(self, description, operandTypes):
        self.id = Rule.count
        self.desc = description
        self.numOperands = len(operandTypes)
        self.argSig = operandTypes
        Rule.count += 1

    def __init__(self, description, operandTypes, rID):
        self.id = rID
        ## now the rules might not be contiguous
        Rule.count = max(rID, Rule.count)
        self.desc = description
        self.numOperands = len(operandTypes)
        self.argSig = operandTypes
        Rule.count += 1

    def __str__(self):
        return "Rule " + str(self.id) + ": " + self.desc


    def applicable(self,args):
        if len(args) != self.numOperands:
            return False
        else:
            for i in range(0, self.numOperands - 1):
                if not isinstance(args[i], self.argSig[i]):
                    return False
            return True

    def apply(self,args):
        if self.applicable(args):
            if hasattr(self, 'fn'):
                return self.fn(args)
            else:
                raise Exception("Rule is missing its function property.")
        else:
            print "Can't apply Rule " + str(self.id) + " to " + str(args)
            print "Expected " + str(self.argSig)
            raise Exception("Args Don't Match Signature")


