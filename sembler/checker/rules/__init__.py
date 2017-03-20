## General Support for other rules
from LayerMinDist import minDistInLayer
from SupportCheck import checkSupport
from PostDepth import fillInPosts
from LayerBorderBuffer import buffered

## Numbered rules from Salil's spreadsheet
from MinDieDimm import rule3
from MaxDieDimm import rule4
from MinMetalWidth import rule5
from MetalEdgePitch import rule6
from MetalBondPitch import rule8
from MinSU81Width import rule9
from MaxSU81Width import rule10
from MinPostDimmSU81 import rule11
from SU81Pitch import rule12
from MinSU82Width import rule13
from MaxSU82Width import rule14
from MinPostDimmSU82 import rule15
from SU82Pitch import rule16
from SupportedSU82 import rule17
from MinSU83Width import rule18
from MaxSU83Width import rule19
from MinPostDimmSU83 import rule20
from SU83Pitch import rule21
from SupportedSU83 import rule22
from PortDimm import rule23
from PortPitch import rule24
from FluidPortEdgePitch import rule25
from RelPortEdgePitch import rule26
from SU81PortPitch import rule27
from AlignmentPitch import rule30
from AlignmentBorderPitch import rule31
from AlignmentCount import rule32
from SU81EdgePitch import rule35
from SU82EdgePitch import rule43
from SU83EdgePitch import rule44
from MinBondpadWidth import rule36

from BondpadPitch import rule38
from BorderSize import rule39
from RectBorder import rule40

from MetalInBounds import rule33
from L1SU8InBounds import rule34
from L2SU8InBounds import rule41
from L3SU8InBounds import rule42
from MaxPostPitch import postPitchSU81, postPitchSU82, postPitchSU83
import NearLineSegment
