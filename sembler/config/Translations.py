import DxfConfig
import RuleConfig

nameMap = {
    DxfConfig.METAL: RuleConfig.METAL,
    DxfConfig.SU8_1: RuleConfig.SU81,
    DxfConfig.SU8_2: RuleConfig.SU82,
    DxfConfig.SU8_3: RuleConfig.SU83,
    DxfConfig.VPORT: RuleConfig.PORTS,
    DxfConfig.POSTS: RuleConfig.POST,
    DxfConfig.ALIGNMENT: RuleConfig.ALIGNMENT,
    DxfConfig.BORDER: RuleConfig.BORDER
}

def layerNumToName(i):
    """
    Maps indexes (integers) onto human readable strings suitable for inclusion
    in latex.
    """
    if i == RuleConfig.SU81:
        return "L1\_SU8"
    elif i == RuleConfig.SU82:
        return "L2\_SU8"
    elif i == RuleConfig.SU83:
        return "L3\_SU8"
    elif i == RuleConfig.METAL:
        return "METAL"
    elif i == RuleConfig.POST:
        return "POSTS"
    elif i == RuleConfig.PORTS:
        return "PORTS"
    elif i == RuleConfig.BORDER:
        return "BORDER"
    elif i == RuleConfig.ALIGNMENT:
        return "ALIGNMENT"
    elif i == RuleConfig.PURITY:
        return "UNREADABLE"
    else:
        raise Exception("Didn't recognize", i)

def layerNameToNum(layerName):
    """
    Maps constant string layer names from DXF into integer indexes expected by
    Design Dictionary.
    """
    if layerName not in nameMap.keys():
        raise Exception("Didn't recognize ", layerName)
    else:
        return nameMap[layerName]
