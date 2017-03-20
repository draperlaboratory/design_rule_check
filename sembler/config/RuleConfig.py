from checker import Rule
from checker import RuleType

## Layer indexes
METAL = 0
SU81 = 1
SU82 = 2
SU83 = 3
POST = 4
PORTS = 5
BORDER = 6
ALIGNMENT = 7
PURITY=8
LAYERS = range(0,9)
PHYSICAL_LAYERS = [ METAL, SU81, SU82, SU83 ]
## Layer Growth Factor
LAYERGROWTH = 5

rules = {}

ruleDict = {}
ruleDict[Rule.ID] = 3
ruleDict[Rule.ELAYER] = "MIN_WIDTH_FEATURE_DIE_BOUNDARY"
ruleDict[Rule.APPLYTO] = BORDER
ruleDict[Rule.HEADING] = "Die boundary too small"
ruleDict[Rule.DESC] = """
\\par The die boundary is smaller than the minimum die size. The die must be at
least 1 cm x 1 cm (10000 $\\mu$m x 10000 $\\mu$m).
\\par See ERR\\_MIN\\_WIDTH\\_FEATURE\\_DIE\\_BOUNDARY layer in output DXF file.
"""
ruleDict[Rule.CTYPE] = RuleType.HARD
ruleDict[Rule.THRESH] = 10000
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MAX_WIDTH_FEATURE_DIE_BOUNDARY"
ruleDict[Rule.APPLYTO] = BORDER
ruleDict[Rule.HEADING] = "Die boundary too large"
ruleDict[Rule.DESC] = """
\\par The die boundary is larger than the maximum die size. A rectangular die has
dimensions ranging in integral sizes from 1 cm x 1 cm (10000 $\\mu$m x 10000
$\\mu$m) to 4 cm x 4 cm (40000 $\\mu$m x 40000 $\\mu$m), or microscope slide
dimensions of 2.5 cm x 7.5 cm (25000 $\\mu$m x 75000 $\\mu$m).
\\par See ERR\\_MAX\\_WIDTH\\_FEATURE\\_DIE\\_BOUNDARY layer in output DXF file.
"""
ruleDict[Rule.ID] = 4
ruleDict[Rule.CTYPE] = RuleType.HARD
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_WIDTH_FEATURE_METAL"
ruleDict[Rule.APPLYTO] = METAL
ruleDict[Rule.HEADING] = "Minimum trace width not met"
ruleDict[Rule.DESC] = """
\\par A metal trace has a width smaller than the recommended minimum. The minimum
recommended metal trace width is 10 $\\mu$m.  \\par See
WARN\\_MIN\\_WIDTH\\_FEATURE\\_METAL layer in output DXF file.
"""
ruleDict[Rule.ID] = 5
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 10
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_DIST_EDGE2EDGE_METAL"
ruleDict[Rule.APPLYTO] = METAL
ruleDict[Rule.HEADING] =  "Minimum edge-to-edge distance not met"
ruleDict[Rule.DESC] = """
\\par Metal traces are closer to each other than the recommended minimum
distance. The minimum recommended distance between metal traces, from edge to
edge, is 10 $\\mu$m.  \\par See WARN\\_MIN\\_DIST\\_EDGE2EDGE\\_METAL layer in output
DXF file.
"""
ruleDict[Rule.ID] = 6
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 10
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_DIST_EDGE2EDGE_METAL"
ruleDict[Rule.APPLYTO] = METAL
ruleDict[Rule.HEADING] = "METAL Minimum Feature Center to Feature Center Distance"
ruleDict[Rule.DESC] = "Metal features must have a minimum distance between their centers to ensure bonding."
ruleDict[Rule.ID] = 8
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 500
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_WIDTH_FEATURE_L1_SU8"
ruleDict[Rule.APPLYTO] = SU81
ruleDict[Rule.HEADING] = "Minimum feature width not met"
ruleDict[Rule.DESC] = """
\\par A feature in L1\\_SU8 is narrower than the recommended minimum width. The
minimum recommended width of L1\\_SU8 features is 10 $\\mu$m. A feature narrower
than this might not resolve accurately.  \\par See
WARN\\_MIN\\_WIDTH\\_FEATURE\\_L1\\_SU8 layer in output DXF file.
"""
ruleDict[Rule.ID] = 9
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 10
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MAX_WIDTH_FEATURE_L1_SU8"
ruleDict[Rule.APPLYTO] = SU81
ruleDict[Rule.HEADING] = "Maximum feature width exceeded"
ruleDict[Rule.DESC] = """
\\par A feature in L1\\_SU8 is wider than the recommended maximum width. The
maximum recommended width of L1\\_SU8 features is 80 $\\mu$m. A feature wider than
this runs the risk of collapse. To help prevent this, narrow the feature or add
support posts.  \\par See WARN\\_MAX\\_WIDTH \\_FEATURE\\_L1\\_SU8 layer in output DXF
file.
"""
ruleDict[Rule.ID] = 10
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 80
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_DIAMETER_SUPPORT_POST_L1_SU8"
ruleDict[Rule.APPLYTO] = SU81
ruleDict[Rule.HEADING] = "Minimum support post diameter for L1\_SU8 not met"
ruleDict[Rule.DESC] = """
\\par A support post for an L1\\_SU8 feature has a diameter that is smaller than
the recommended minimum diameter. The minimum recommended diameter for support
posts for L1\\_SU8 features is 20 $\\mu$m. Note that the DRC automatically maps
support posts to the SU-8 layers where features exist.  \\par See
WARN\\_MIN\\_DIAMETER\\_SUPPORT\\_POST\\_L1\\_SU8 layer in output DXF file.
"""
ruleDict[Rule.ID] = 11
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 20
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_DIST_EDGE2EDGE_L1_SU8"
ruleDict[Rule.APPLYTO] = SU81
ruleDict[Rule.HEADING] = "Minimum edge-to-edge distance not met"
ruleDict[Rule.DESC] = """
\\par Features in L1\\_SU8 are closer to each other than the recommended minimum
distance. The minimum recommended distance between SU-8 features, from edge to
edge, is 50 $\\mu$m to prevent risk of poor bonding and fluid leakage.  \\par See
WARN\\_MIN\\_DIST\\_EDGE2EDGE\\_L1\\_SU8 layer in output DXF file.
"""
ruleDict[Rule.ID] = 12
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 50
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_WIDTH_FEATURE_L2_SU8"
ruleDict[Rule.APPLYTO] = SU82
ruleDict[Rule.HEADING] = "Minimum feature width not met"
ruleDict[Rule.DESC] = """
\\par A feature in L2\\_SU8 is narrower than the recommended minimum width. The
minimum recommended width of L2\\_SU8 features is 25 $\\mu$m. A feature narrower
than this might not resolve accurately.  \\par See
WARN\\_MIN\\_WIDTH\\_FEATURE\\_L2\\_SU8 layer in output DXF file.
"""
ruleDict[Rule.ID] = 13
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 25
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MAX_WIDTH_FEATURE_L2_SU8"
ruleDict[Rule.APPLYTO] = SU82
ruleDict[Rule.HEADING] = "Maximum feature width exceeded"
ruleDict[Rule.DESC] = """
\\par A feature in L2\\_SU8 is wider than the recommended maximum width. The
maximum recommended width of L2\\_SU8 features is 200 $\\mu$m. A feature wider
than this runs the risk of collapse. To help prevent this, narrow the feature or
add support posts.  \\par See WARN\\_MAX\\_WIDTH\\_FEATURE\\_L2\\_SU8 layer in output
DXF file.
"""
ruleDict[Rule.ID] = 14
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 200
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_DIAMETER_SUPPORT_POST_L1_2_SU8"
ruleDict[Rule.APPLYTO] = SU82
ruleDict[Rule.HEADING] = "Minimum support post diameter for L2\_SU8 not met"
ruleDict[Rule.DESC] = """
\par A support post for an L2\_SU8 feature has a diameter that is smaller than
the recommended minimum diameter. The minimum recommended diameter for support
posts for L2\_SU8 features is 50 $\mu$m. Note that the DRC automatically maps
support posts to the SU-8 layers where features exist, and that the total height
of L2\_SU8 features is the combined thickness of L1\_SU8 and L2\_SU8.  \par See
WARN\_MIN\_DIAMETER\_SUPPORT\_POST\_L2\_SU8 layer in output DXF file.
"""
ruleDict[Rule.ID] = 15
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 50
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_DIST_EDGE2EDGE_L2_SU8"
ruleDict[Rule.APPLYTO] = SU82
ruleDict[Rule.HEADING] =  "Minimum edge-to-edge distance not met"
ruleDict[Rule.DESC] = """
\\par Features in L2\\_SU8 are closer to each other than the recommended minimum
distance. The minimum recommended distance between SU-8 features, from edge to
edge, is 50 $\\mu$m.  \\par See WARN\\_MIN\\_DIST\\_EDGE2EDGE\\_L2\\_SU8 layer in
output DXF file.
"""
ruleDict[Rule.ID] = 16
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 50
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "ENCLOSE_ALL_L2_SU8_IN_L1_SU8"
ruleDict[Rule.APPLYTO] = SU82
ruleDict[Rule.HEADING] = "Unsupported L2\\_SU8 feature"
ruleDict[Rule.DESC] = """
\\par A feature in L2\\_SU8 is not supported by L1\\_SU8 below it. All L2\\_SU8
features must have L1\\_SU8 features defined beneath them.  \\par See
ERR\\_ENCLOSE\\_ALL\\_L2\\_SU8\\_IN\\_L1\\_SU8 layer in output DXF file.
"""
ruleDict[Rule.ID] = 17
ruleDict[Rule.CTYPE] = RuleType.HARD
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_WIDTH_FEATURE_L3_SU8"
ruleDict[Rule.APPLYTO] = SU83
ruleDict[Rule.HEADING] = "Minimum feature width not met"
ruleDict[Rule.DESC] = """
\\par A feature in L3\\_SU8 is narrower than the recommended minimum width. The
minimum recommended width of L3\\_SU8 features is 50 $\\mu$m. A feature narrower
than this might not resolve accurately.  \\par See
WARN\\_MIN\\_WIDTH\\_FEATURE\\_L3\\_SU8 layer in output DXF file.
"""
ruleDict[Rule.ID] = 18
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 50
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MAX_WIDTH_FEATURE_L3_SU8"
ruleDict[Rule.APPLYTO] = SU83
ruleDict[Rule.HEADING] = "Maximum feature width exceeded"
ruleDict[Rule.DESC] = """
\\par A feature in L3\\_SU8 is wider than the recommended maximum width. The
maximum recommended width of L3\\_SU8 features is 400 $\\mu$m. A feature wider
than this runs the risk of collapse. To help prevent this, narrow the feature or
add support posts.  \\par See WARN\\_MAX\\_WIDTH\\_FEATURE\\_L3\\_SU8 layer in output
DXF file.
"""
ruleDict[Rule.ID] = 19
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 400
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_DIAMETER_SUPPORT_POST_L1_2_3_SU8"
ruleDict[Rule.APPLYTO] = SU83
ruleDict[Rule.HEADING] =  """Minimum support post diameter for L3\\_SU8 not met"""
ruleDict[Rule.DESC] = """
\\par A support post for an L3\\_SU8 feature has a diameter that is smaller than
the recommended minimum diameter. The minimum recommended diameter for support
posts for L3\\_SU8 features is 100 $\\mu$m. Note that the DRC automatically maps
support posts to the SU-8 layers where features exist, and that the total height
of L3\\_SU8 features is the combined thickness of L1\\_SU8, L2\\_SU8, and L3\\_SU8.
\\par See WARN\\_MIN\\_DIAMETER\\_SUPPORT\\_POST\\_L3\\_SU8 layer in output DXF file.
"""
ruleDict[Rule.ID] = 20
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 100
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_DIST_EDGE2EDGE_L3_SU8"
ruleDict[Rule.APPLYTO] = SU83
ruleDict[Rule.HEADING] = "Minimum edge-to-edge distance not met"
ruleDict[Rule.DESC] = """
\\par Features in L3\\_SU8 are closer to each other than the recommended minimum
distance. The minimum recommended distance between SU-8 features, from edge to
edge, is 50 $\\mu$m.  \\par See WARN\\_MIN\\_DIST\\_EDGE2EDGE\\_L3\\_SU8 layer in
output DXF file.
"""
ruleDict[Rule.ID] = 21
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 50
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "ENCLOSE_ALL_L3_SU8_IN_L2_SU8"
ruleDict[Rule.APPLYTO] = SU83
ruleDict[Rule.HEADING] = "Unsupported L3\\_SU8 feature"
ruleDict[Rule.DESC] = """
\\par A feature in L3\\_SU8 is not supported by L2\\_SU8 below it. All L3\\_SU8
features must have L2\\_SU8 features defined beneath them.  \\par See
ERR\\_ENCLOSE\\_ALL\\_L3\\_SU8\\_IN\\_L2\\_SU8 layer in output DXF file.
"""
ruleDict[Rule.ID] = 22
ruleDict[Rule.CTYPE] = RuleType.HARD
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "DIAMETER_VERTICAL_PORT"
ruleDict[Rule.APPLYTO] = PORTS
ruleDict[Rule.HEADING] = "Port Radius Constraint"
ruleDict[Rule.DESC] = """
\\par A port in VERTICAL\\_PORT has a diameter that is not one of the specified
acceptable values. Only 1 mm, 2 mm, or 3 mm (1000 $\\mu$m, 2000 $\\mu$m, or 3000
$\\mu$m) diameter holes can be punched. Ports that have other diameters will not
be punched.  \\par See WARN\\_DIAMETER\\_VERTICAL\\_PORT layer in output DXF file.
"""
ruleDict[Rule.ID] = 23
ruleDict[Rule.CTYPE] = RuleType.SOFT
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_DIST_EDGE2EDGE_VERTICAL_PORT"
ruleDict[Rule.APPLYTO] = PORTS
ruleDict[Rule.HEADING] = "Minimum port perimeter-to-perimeter distance not met"
ruleDict[Rule.DESC] = """
\\par Ports are closer to each other than the recommended minimum distance. The
minimum recommended distance between ports, from perimeter to perimeter, is 2 mm
(2000 $\\mu$m). Placing ports closer together than this minimum distance might
result in poor bonding and fluid leakage.  \\par See
WARN\\_MIN\\_DIST\\_EDGE2EDGE\\_VERTICAL\\_PORT layer in output DXF file.
"""
ruleDict[Rule.ID] = 24
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 2000 ## 2mm, minimum distance between ports
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_DIST_DIE_BOUNDARY_VERTICAL_PORT_FLC"
ruleDict[Rule.APPLYTO] = PORTS
ruleDict[Rule.HEADING] = """Minimum distance from port perimeter to die edge not met"""
ruleDict[Rule.DESC] = """
\\par A fluidic port is closer to the edge of the die than the recommended
minimum distance. The minimum recommended distance between the die boundary and
the perimeter of a port used for fluidics is 2 mm (2000 $\\mu$m).  \\par See
WARN\\_MIN\\_DIST\\_DIE\\_BOUNDARY\\_EDGE\\_VERTICAL\\_PORT\\_FLC layer in output DXF
file.
"""
ruleDict[Rule.ID] = 25
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 2000
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_DIST_DIE_BOUNDARY_EDGE_VERTICAL_PORT_ELC"
ruleDict[Rule.APPLYTO] = PORTS
ruleDict[Rule.HEADING] = "Port to Boundary Constraint(Relief)"
ruleDict[Rule.DESC] = "Ports must be a certain distance away from the boundary to ensure a good bond."
ruleDict[Rule.ID] = 26
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 0
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_DIST_L1_SU8_EDGE_VERTICAL_PORT"
ruleDict[Rule.APPLYTO] = SU81
ruleDict[Rule.HEADING] = "Minimum distance from L1\_SU8 edge to port perimeter not met"
ruleDict[Rule.DESC] = """
\\par A feature in L1\\_SU8 is closer to the perimeter of a port than the
recommended minimum distance. The minimum recommended distance between the
perimeter of a port and the edge of any SU-8 feature (except a channel entering
the port) is 1 mm (1000 $\\mu$m).  \\par See
WARN\\_MIN\\_DIST\\_L1\\_SU8\\_EDGE\\_VERTICAL\\_PORT layer in output DXF file.
"""
ruleDict[Rule.ID] = 27
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 1000
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "ARRANGMENT_ALIGNMENT_MARK"
ruleDict[Rule.APPLYTO] = ALIGNMENT
ruleDict[Rule.HEADING] = "Alignment marks not in proper configuration"
ruleDict[Rule.DESC] = """
\par Three alignment marks in proper configuration must be present. To see
predefined alignment marks in proper configuration (triangular pattern with no
more than two co-linear), download the Sembler template files and open a blank
design template.  \par See ERR\_ARRANGEMENT\_ALIGNMENT\_MARK layer in output DXF
file.
"""
ruleDict[Rule.ID] = 30
ruleDict[Rule.CTYPE] = RuleType.HARD
ruleDict[Rule.THRESH] = 5000
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "ERR_PITCH_ALIGNMENT_BORDER"
ruleDict[Rule.APPLYTO] = ALIGNMENT
ruleDict[Rule.HEADING] = "Distance Between Alignment Marks and Border"
ruleDict[Rule.DESC] = "Alignment Marks must be inset from the border to ensure a good bond."
ruleDict[Rule.ID] = 31
ruleDict[Rule.CTYPE] = RuleType.HARD
ruleDict[Rule.THRESH] = 750
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "ERR_ALIGNMENT_COUNT"
ruleDict[Rule.APPLYTO] = ALIGNMENT
ruleDict[Rule.HEADING] = "Incorrect number of alignment mark groupings"
ruleDict[Rule.DESC] = """
\\par The design does not have the recommended number of alignment marks. For
devices with a dimension larger than 2 cm (20000 $\\mu$m), two groupings of
alignment marks in opposite corners are recommended. To see the standard
grouping of three alignment marks in the proper configuration (triangular
pattern with no more than two co-linear), download the Sembler template files
and open a blank template.  \\par See
WARN\\_ARRANGEMENT\\_ALIGNMENT\\_MARK\\_LARGE\\_DIE layer in output DXF file.
"""
ruleDict[Rule.ID] = 32
ruleDict[Rule.CTYPE] = RuleType.HARD
ruleDict[Rule.THRESH] = 3
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_DIST_EDGE2EDGE_BOUNDARY_EDGE_L1_SU8"
ruleDict[Rule.APPLYTO] = SU81
ruleDict[Rule.HEADING] = "Minimum distance from L1\\_SU8 edge to die boundary not met"
ruleDict[Rule.DESC] = """
\\par A feature in L1\\_SU8 (or an alignment mark in REF\\_ALIGNMENT) is closer to
the edge of the die boundary than the recommended minimum distance. The
recommended minimum distance from the edge of an SU-8 feature or alignment mark
to the edge of the die is 750 $\\mu$m.  \\par See
WARN\\_MIN\\_DIST\\_EDGE2EDGE\\_BOUNDARY\\_EDGE\\_L1\\_SU8 layer in output DXF file.
"""
ruleDict[Rule.ID] = 35
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 750
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_WIDTH_BONDPAD_METAL"
ruleDict[Rule.APPLYTO] = METAL
ruleDict[Rule.HEADING] = "Minimum bond pad width not met"
ruleDict[Rule.DESC] = """
\\par A metal bond pad has a width smaller than the recommended minimum. The
minimum recommended metal bond pad width is 100 $\\mu$m.  \\par See
WARN\\_MIN\\_WIDTH\\_BONDPAD\\_METAL layer in output DXF file.
"""
ruleDict[Rule.ID] = 36
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 100
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "ERR_MIN_PITCH_BOND_PADS"
ruleDict[Rule.APPLYTO] = METAL
ruleDict[Rule.HEADING] = "Minimum center-to-center distance not met"
ruleDict[Rule.DESC] = """
\\par Metal bond pads are closer to each other than the recommended minimum
distance. The minimum recommended distance between metal bond pads, from edge
to edge, is 2000 $\\mu$m.  \\par See WARN\\_MIN\\_PITCH\\_BONDPAD\\_METAL layer in
output DXF file.
"""
ruleDict[Rule.ID] = 38
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 2000
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "ERR_INT_BORDER"
ruleDict[Rule.APPLYTO] = BORDER
ruleDict[Rule.HEADING] = "Die boundary not in standard size"
ruleDict[Rule.DESC] = """
\\par The die boundary must be the size of one of Sembler's standard dies. Dies
are available in rectangular shapes with integral dimensions ranging from 1 cm x
1 cm (10000 $\\mu$m x 10000 $\\mu$m) to 4 cm x 4 cm (40000 $\\mu$m x 40000 $\\mu$m),
or with microscope slide dimensions of 2.5 cm x 7.5 cm (25000 $\\mu$m x 75000
$\\mu$m).  \\par See ERR\\_SIZE\\_DIE\\_BOUNDARY layer in output DXF file.
"""
ruleDict[Rule.ID] = 39
ruleDict[Rule.CTYPE] = RuleType.HARD
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "ERR_RECT_BORDER"
ruleDict[Rule.APPLYTO] = BORDER
ruleDict[Rule.HEADING] = "Die boundary not rectangular"
ruleDict[Rule.DESC] = """
\\par The die boundary must be rectangular. Dies are available in rectangular
shapes with integral dimensions ranging from 1 cm x 1 cm (10000 $\\mu$m x 10000
$\\mu$m) to 4 cm x 4 cm (40000 $\\mu$m x 40000 $\\mu$m), or with microscope slide
dimensions of 2.5 cm x 7.5 cm (25000 $\\mu$m x 75000 $\\mu$m).  \\par See
ERR\\_SHAPE\\_DIE\\_BOUNDARY layer in output DXF file.
"""
ruleDict[Rule.ID] = 40
ruleDict[Rule.CTYPE] = RuleType.HARD
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "ENCLOSE_METAL_IN_DIE_BOUNDARY"
ruleDict[Rule.APPLYTO] = METAL
ruleDict[Rule.HEADING] = "Feature outside die boundary"
ruleDict[Rule.DESC] = """
\\par A feature in L0\\_METAL is outside the die boundary. The die boundary must
enclose all metal features.  \\par See ERR\\_ENCLOSE\\_L0\\_METAL\\_IN\\_DIE\\_BOUNDARY
layer in output DXF file."""
ruleDict[Rule.ID] = 33
ruleDict[Rule.CTYPE] = RuleType.HARD
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "ENCLOSE_L1_SU8_IN_DIE_BOUNDARY"
ruleDict[Rule.APPLYTO] = SU81
ruleDict[Rule.HEADING] = "Feature outside die boundary"
ruleDict[Rule.DESC] = """
\\par A feature in L1\\_SU8 is outside the die boundary. The die boundary must
enclose all SU-8 features.  \\par See ERR\\_ENCLOSE\\_L1\\_SU8\\_IN\\_DIE\\_BOUNDARY
layer in output DXF file.
"""
ruleDict[Rule.ID] = 34
ruleDict[Rule.CTYPE] = RuleType.HARD
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "ENCLOSE_L2_SU8_IN_DIE_BOUNDARY"
ruleDict[Rule.APPLYTO] = SU82
ruleDict[Rule.HEADING] = "Feature outside die boundary"
ruleDict[Rule.DESC] = """
\\par A feature in L2\\_SU8 is outside the die boundary. The die boundary must
enclose all SU-8 features.  \\par See ERR\\_ENCLOSE\\_L2\\_SU8\\_IN\\_DIE\\_BOUNDARY
layer in output DXF file.
"""
ruleDict[Rule.ID] = 41
ruleDict[Rule.CTYPE] = RuleType.HARD
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "ENCLOSE_L3_SU8_IN_DIE_BOUNDARY"
ruleDict[Rule.APPLYTO] = SU83
ruleDict[Rule.HEADING] = "Feature outside die boundary"
ruleDict[Rule.DESC] = """
\\par A feature in L3\\_SU8 is outside the die boundary. The die boundary must
enclose all SU-8 features.  \\par See ERR\\_ENCLOSE\\_L3\\_SU8\\_IN\\_DIE\\_BOUNDARY
layer in output DXF file.
"""
ruleDict[Rule.ID] = 42
ruleDict[Rule.CTYPE] = RuleType.HARD
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_DIST_EDGE2EDGE_BOUNDARY_EDGE_L2_SU8"
ruleDict[Rule.APPLYTO] = SU82
ruleDict[Rule.HEADING] = "Minimum distance from L2\\_SU8 edge to die boundary not met"
ruleDict[Rule.DESC] = """
\\par A feature in L2\\_SU8 (or an alignment mark in REF\\_ALIGNMENT) is closer to
the edge of the die boundary than the recommended minimum distance. The
recommended minimum distance from the edge of an SU-8 feature or alignment mark
to the edge of the die is 750 $\\mu$m.  \\par See
WARN\\_MIN\\_DIST\\_EDGE2EDGE\\_BOUNDARY\\_EDGE\\_L2\\_SU8 layer in output DXF file.
"""
ruleDict[Rule.ID] = 43
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 750
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict = {}
ruleDict[Rule.ELAYER] = "MIN_DIST_EDGE2EDGE_BOUNDARY_EDGE_L3_SU8"
ruleDict[Rule.APPLYTO] = SU83
ruleDict[Rule.HEADING] = "Minimum distance from L3\\_SU8 edge to die boundary not met"
ruleDict[Rule.DESC] = """
\\par A feature in L3\\_SU8 (or an alignment mark in REF\\_ALIGNMENT) is closer to
the edge of the die boundary than the recommended minimum distance. The
recommended minimum distance from the edge of an SU-8 feature or alignment mark
to the edge of the die is 750 $\\mu$m.  \\par See
WARN\\_MIN\\_DIST\\_EDGE2EDGE\\_BOUNDARY\\_EDGE\\_L3\\_SU8 layer in output DXF file.
"""
ruleDict[Rule.ID] = 44
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 750
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict ={}
ruleDict[Rule.ELAYER] = "WARN_MAX_DIST_EDGE2EDGE_SUPPORT_POST_L1_SU8"
ruleDict[Rule.APPLYTO] = POST
ruleDict[Rule.HEADING] ="Maximum distance between support posts in L1\\_SU8 exceeded"
ruleDict[Rule.DESC] = """
\\par A support post for an L2\\_SU8 feature has a diameter that is smaller than
the recommended minimum diameter. The minimum recommended diameter for support
posts for L2\\_SU8 features is 50 $\\mu$m. Note that the DRC automatically maps
support posts to the SU-8 layers where features exist, and that the total height
of L2\\_SU8 features is the combined thickness of L1\\_SU8 and L2\\_SU8.  \\par See
WARN\\_MIN\\_DIAMETER\\_SUPPORT\\_POST\\_L2\\_SU8 layer in output DXF file.
"""
ruleDict[Rule.ID] = 45
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 50
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict ={}
ruleDict[Rule.ELAYER] = "WARN_MAX_DIST_EDGE2EDGE_SUPPORT_POST_L2_SU8"
ruleDict[Rule.APPLYTO] = POST
ruleDict[Rule.HEADING] ="Maximum distance between support posts in L2\\_SU8 exceeded"
ruleDict[Rule.DESC] = """
Support posts for L2\\_SU8 features are farther away from each other than the
recommended maximum distance. The maximum recommended distance between support
posts for L2\\_SU8 features, from edge to edge, is 200 $\\mu$m. Note that the DRC
automatically maps support posts to the SU-8 layers where features exist, and
that the total height of L2\\_SU8 features is the combined thickness of L1\\_SU8
and L2\\_SU8.  \\par See WARN\\_MAX\\_DIST\\_EDGE2EDGE\\_SUPPORT\\_POST\\_L2\\_SU8 layer
in output DXF file.
"""
ruleDict[Rule.ID] = 46
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 200
rules[ruleDict[Rule.ID]] = ruleDict

ruleDict ={}
ruleDict[Rule.ELAYER] = "WARN_MAX_DIST_EDGE2EDGE_SUPPORT_POST_L3_SU8"
ruleDict[Rule.APPLYTO] = POST
ruleDict[Rule.HEADING] ="Maximum distance between support posts in L3\\_SU8 exceeded"
ruleDict[Rule.DESC] = """
Support posts for L3\\_SU8 features are farther away from each other than the
recommended maximum distance. The maximum recommended distance between support
posts for L3\\_SU8 features, from edge to edge, is 400 $\\mu$m. Note that the DRC
automatically maps support posts to the SU-8 layers where features exist, and
that the total height of L3\\_SU8 features is the combined thickness of L1\\_SU8,
L2\\_SU8, and L3\\_SU8.  \\par See
WARN\\_MAX\\_DIST\\_EDGE2EDGE\\_SUPPORT\\_POST\\_L3\\_SU8 layer in output DXF file.
"""
ruleDict[Rule.ID] = 47
ruleDict[Rule.CTYPE] = RuleType.SOFT
ruleDict[Rule.THRESH] = 400
rules[ruleDict[Rule.ID]] = ruleDict
