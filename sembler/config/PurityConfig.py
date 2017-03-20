

import DxfConfig
import re

def texify(s):
    return re.sub('_', '\_', s)

class InvalidBoundary():

    HEADER = "Invalid Boundary"

    TOO_MANY_OBJECTS = """
    Too many objects were found on the boundary layer. Sembler requires a \
    single, rectangular object on the boundary layer.\
    """

    NO_OBJECTS =  """\
    The design file does not contain a die boundary. The die boundary must be \
    defined in the %(layer)s layer. To see an example of a defined \
    die boundary, download the Sembler template files and open a blank design \
    template.\
    """ % {'layer': DxfConfig.BORDER}

    INVALID_ENTITY = """\
    An invalid entity type was provided for the boundary. The boundary must \
    be provided as a polyline.\
    """

    AMBIGUOUS = """\
    The detected border contained too many vertices and may not be \
    rectangular. Required vertices: 4\
    """

    TOO_SMALL = """\
    The boundary has a side that is too small. The minimum size for the side \
    of a boundary is 1 cm.\
    """

    NON_RECTANGULAR = """\
    The boundary provided was of a non-rectangular shape. The boundary must \
    be rectangular.\
    """

class OpenPolyline():

    HEADER = "Open Polylines"

    DESCRIPTION = """\
    A provided feature is an open polyline. All polylines must be closed. \
    See %(layer)s layer in output DXF file.\
    """ % {'layer': texify(DxfConfig.LAYER_OPEN_POLY)}

class InvalidEntities():

    HEADER = "Invalid Entities"

    DESCRIPTION = """\
    A provided feature is an entity that is not accepted by the DRC. Every \
    feature must be a closed polyline consisting only of line and arc \
    segments. See %(layer)s layer in output DXF file.\
    """ % {'layer': texify(DxfConfig.LAYER_INVALID_ENTITY)}

class MissingLayers():

    HEADER = "Missing Layers"

    DESCRIPTION = """\
    Layers are is missing from the design file. The design must \
    contain all standard Sembler layers as defined in the Sembler Design \
    Rules and Process Description (PDF), even if some of these layers are \
    empty. To see the required layers, download the Sembler template files \
    and open a blank design template.
    """

class SelfIntersecting():

    HEADER = 'Self-intersection'
    DESCRIPTION = """\
    A feature intersects itself in one or more locations. See the %(layer)s \
    layer in output DXF file.\
    """ % {'layer': texify(DxfConfig.LAYER_INTERSECTING_POLYLINE)}

class SmallEntities():

    HEADER = 'Small Entities Detected'
    DESCRIPTION = """\
    Sometimes features too small for us to resolve in our fabrication process \
    (and possibly too small to see in the design software) are accidentally \
    included in a design. We have found such unresolveable features (points, \
    line segments, etc.) in this design. They have been removed from \
    processing and placed in layer %(layer)s for your reference.
    """ % {'layer': texify(DxfConfig.LAYER_SMALL_ENTITIES)}

