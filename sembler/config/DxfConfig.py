

from checker.Rule import RuleType

# Required layer names for DRC
METAL         = 'L0_METAL'
SU8_1         = 'L1_SU8'
SU8_2         = 'L2_SU8'
SU8_3         = 'L3_SU8'
VPORT         = 'VERTICAL_PORT'
POSTS         = 'SUPPORT_POST'
ALIGNMENT     = 'REF_ALIGNMENT'
BORDER        = 'REF_DIE_BOUNDARY'

# Other layer names
LABEL         = 'LABEL'
CRITICAL_BOND = 'REF_CRITICAL_BOND'

# Purity failure layer names
LAYER_OPEN_POLY             = 'ERR_OPEN_POLYLINES'
LAYER_INVALID_ENTITY        = 'ERR_INVALID_ENTITIES'
LAYER_INTERSECTING_POLYLINE = 'ERR_SELF_INTERSECTION'
LAYER_INVALID_BORDER        = 'ERR_INVALID_BORDER'
LAYER_SMALL_ENTITIES         = u'WARN_SMALL_ENTITIES'

# DXF entity name constants
LINE        = 'LINE'
ARC         = 'ARC'
CIRCLE      = 'CIRCLE'
POLYLINE    = 'POLYLINE'
LWPOLYLINE  = 'LWPOLYLINE'
INSERT      = 'INSERT'
# TEXT ?

# The layers that will be checked
VALID_LAYERS = [ ALIGNMENT, BORDER, SU8_1, SU8_2, SU8_3, METAL, VPORT, POSTS ]
# The only allowed DXF entities for checking
VALID_ENTITIES = [ CIRCLE, POLYLINE, LWPOLYLINE, INSERT ]
# They layers needed for fabircation output
FAB_LAYERS = [ ALIGNMENT, BORDER, SU8_1, SU8_2, SU8_3, METAL, VPORT, POSTS,
               CRITICAL_BOND ]

# This dictionary dictates what gets written to the dxfs that fail the
# rule checking.
COLOR_MAP = {
    RuleType.HARD: 10,
    RuleType.SOFT: 50,
    RuleType.PURITY: 30
}

# All arcs being discretized must have a value larger than this epsilon, in um
DISCRETIZE_ARC_EPSILON = 1e-10

# The maximum length of a discretized arc segment, in um
MAX_DISCRETIZED_SEGMENT_LENGTH = 100

# Resolution of circle discretization as a function of radius.
# With a radius of R, and a resolution of Z, a quarter circle will have R*Z
# segments. Z is in units of segments/um.
CIRCLE_SEGMENTS_PER_UM = 2

# During layer unioning, the amount to buffer each layer to account for
# floating point rounding and discretization differences, in um.
# It is currently left at 0 without any noticeable effects. This value may
# not be necessary anymore but is left here as a placeholder, just in case.
UNION_LAYER_BUFFER = .00

# Threshold distance for considering a polyline as good as closed, in um
CLOSED_POLYLINE_THRESHOLD = 3

TINY_RADIUS_THRESHOLD = 1
TINY_LINE_LENGTH_THRESHOLD = 1
TINY_POLYLINE_THRESHOLD = 1
