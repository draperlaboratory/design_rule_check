
class Witness:
    """
    Represents a demonstration of a violated rule.  Useful for providing
    feedback to users, either visual feedback of issues in the dxf / etc files,
    or coordinate-based feedback for checkplots in the summary output pdfs.
    """

    POINT_RADIUS = 0
    LINE_SEGMENT = 1
    REGION = 2
    POINT = 3

    typStringDict = {
        POINT_RADIUS : "POINT_RADIUS",
        LINE_SEGMENT : "LINE_SEGMENT",
        REGION : "REGION",
        POINT : "POINT"
    }

    def __init__(self, typ, geometry):
        assert(typ >= Witness.POINT_RADIUS and typ <= Witness.POINT)
        self.typ = typ
        self.geometry = geometry

    def typeAsString(self):
        return Witness.typStringDict.get(self.typ, "INVALID_TYPE")

    def __str__(self):
        objstr = self.typeAsString()
        if (self.typ == Witness.POINT_RADIUS):
            (point,radius) = self.geometry
            objstr = "%s: { Center: %s Radius: %s }" % (objstr, str(point), str(radius))
        elif (self.typ == Witness.LINE_SEGMENT):
            (start,end) = self.geometry
            objstr = "%`s: { Start: %s End: %s }" % (objstr, str(start), str(end))
        elif (self.typ == Witness.REGION):
            region = Witness.geometry
        else:
            objstr = "%s: {%s}" % (objstr, str(self.geometry))
        return objstr
