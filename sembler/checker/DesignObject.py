from shapely.geometry import Point, Polygon, LineString
from config.RuleConfig import METAL

import logging
logger = logging.getLogger('root')

## All Dimmensions are in micro-meters (\mu meters)

class Object:
    """
    Something that's drawn in the microfluidics device.  A port, a channel, etc.

    Object should never be directly instantiated.  You always want one of the
    subclasses.
    """
    count = 0
    PORT = 0
    FEATURE = 1
    ALIGNMENT_MARK = 2
    BORDER = 3

    def strOfType(self):
        if self.type == Object.PORT:
            return "PORT"
        if self.type == Object.FEATURE:
            return "FEATURE"
        if self.type == Object.ALIGNMENT_MARK:
            return "ALIGNMENT MARK"
        if self.type == Object.BORDER:
            return "BORDER"
        logger.critical("Unrecognized type " + str(self.type))
        raise Exception("Unrecognized type " + str(self.type))

    def __str__(self):
        return self.strOfType() + " " + str(self.id)

    def bounds(self):
        """
        Return the bounding box of the feature.
        """
        return self.shape.bounds

class Port(Object):
    """
    A port, typically made with a byopsy punch.  These are always circular, and
    always go through all SU8 layers, straight down to the middle.
    """
    count = 0
    UNKNOWN = 0
    VPORT = 1
    PAD = 2

    def __init__(self, center=None, radius=None, ident=None): ## Port Init
        "Docstring"
        if center is None:
            logger.critical("Ports must have a centroid.")
            raise Exception("Ports must have a centroid.")
        if radius is None:
            logger.critical("Ports must have a radius.")
            raise Exception ("Ports must have a radius.")
        # Set up the fields
        if ident is None:
            self.id = Object.count
        else:
            self.id = ident
            Object.count = ident
            Port.count = ident
        self.center = Point(center)
        self.radius = radius
        self.shape = Point(center).buffer(radius)
        self.type = Object.PORT
        self.purpose = Port.UNKNOWN
        Object.count += 1
        Port.count += 1

    def setPurpose(self, metalIndex):
        """
        Sets the purpose of the port by considering what's underneath it.

        If a port doesn't go down over a metal feature, it's almost certainly
        meant for liquids.  If it goes down over a large metal feature, it's
        almost certainly a relief cut to allow someone to attach an electrical
        lead.  These different kinds of ports have different rules associated
        with them, and we don't get the information from the DXF directly, so
        this method makes it's best guess.
        """
        candidates = metalIndex.intersection(self.shape.bounds)
        underneath = 0
        for cind in candidates:
            underneath += 1
        if underneath == 0:
            self.purpose = Port.VPORT
        else:
            self.purpose = Port.PAD


class Border(Object):
    def __init__(self, polygon):
        self.shape = polygon
        self.type = Object.BORDER
        self.id = -1


class Feature(Object):
    """
    Something in metal or SU8.  A shape (polygon, typically) meant to represent
    a trace or a channel.
    """
    count = 0
    SUPPORT = 1
    CHANNEL = 2
    ALIGNMENT = 3

    def __init__(self, polygon=None, ident=None): ## Feature init w/ polygon
        if polygon is None:
            logger.critical("Features must have a polygon.")
            raise Exception("Features must have a polygon.")
        if ident is None:
            self.id = Object.count
        else:
            self.id = ident
            Object.count = ident
            Feature.count = ident
        Object.count += 1
        Feature.count += 1
        self.shape = Polygon(polygon)
        (minx,miny, maxx, maxy) = self.shape.bounds
        w = maxx - minx
        h = maxy - miny
        d = min(w,h)
        ## We have to know apprx. diameter if we want to know if structures could be supported.
        self.diameter = d
        self.type = Object.FEATURE
        self.purpose = Feature.CHANNEL

class Post(Feature):
    def __init__(self, polygon=None, ident=None):
        Feature.__init__(self,polygon=polygon, ident=ident)
        self.purpose = Feature.SUPPORT
        self.depth = METAL

class AlignmentMark(Object):
    """
    Alignment marks exist in both SU8 and Metal layers, and are meant to help
    the technicial attach the SU8 to the metal in such a way that the two pieces
    align as the original DXF stipulated.

    There are rules that apply to alignment marks that are not applied to
    features in either the metal or l1_su8 layers, so these need to be treated
    specially.  Since these objects exist in multiple layers, I didn't make them
    derivatives of features. They seem different.
    """
    count = 0
    SIZE = 1000

    def __init__(self, center=None, ident=None): ## Alignment init
        if center is None:
            logger.critical("AlignmentMarks must have a centroid.")
            raise Exception("AlignmentMarks must have a centroid.")
        # Set up the fields
        if ident is None:
            self.id = Object.count
        else:
            self.id = ident
            Object.count = ident
            Port.count = ident

        Object.count += 1
        AlignmentMark.count += 1
        self.center = Point(center)
         ## or whatever the size of that outer circle is
        cX = center.x
        cY = center.y
        l = 500 / 2
        s = 100 / 2
        self.diameter = 1000

        rect1 = Polygon([(center.x - l, center.y - s), (center.x - l, center.y + s),
                         (center.x + l, center.y + s), (center.x + l, center.y - s)])
        rect2 = Polygon([(center.x - s, center.y - l), (center.x - s, center.y + l),
                         (center.x + s, center.y + l), (center.x + s, center.y - l)])

        self.shape = rect1.union(rect2)
        self.purpose = Feature.ALIGNMENT
        self.type = Object.ALIGNMENT_MARK
