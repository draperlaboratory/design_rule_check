import Violation
from checker import Rule, RuleType
from config import LAYERS, layerNumToName

class ViolationSummary:
    """
    Abstract Representation of a set of rule vialotians
    """

    def __init__(self):
        self.violations = []
        self.violationsByLayer = {}
        self.purityViolationsByLayer = {}
        self.hardViolationsByLayer = {}
        self.softViolationsByLayer = {}
        self.hardCount = 0
        self.softCount = 0
        self.purityCount = 0
        self.sawHard = False
        self.sawSoft = False
        self.sawPurity = False
        ## Initialize counts to 0
        for layer in LAYERS:
            self.violationsByLayer[layer] = {}
            self.hardViolationsByLayer[layer] = 0
            self.softViolationsByLayer[layer] = 0
            self.purityViolationsByLayer[layer] = 0

    def tex(self):
        """
        Return a latex table representing the ViolationSummary
        """
        outputString = """
        \\begin{tabular}{l|r|r|r}
        Layer & Unreadable & Rules & Guidelines \\\\\hline"""
        for layer in LAYERS:
            ps = self.purityViolationsByLayer[layer]
            rs = self.hardViolationsByLayer[layer]
            gs = self.softViolationsByLayer[layer]
            lname = layerNumToName(layer)
            outputString = "%s\n%s & %i & %i & %i \\\\" % (outputString, lname, ps, rs, gs)
        outputString = "%s\n\\end{tabular}" % outputString
        return outputString

    def add(self,violation):
        """
        Add a single violation to the set of all violations seen.
        """
        self.violations.append(violation)
        lviols = self.violationsByLayer[violation.layer]
        if violation.ruleID in lviols:
            lviols[violation.ruleID].append(violation)
        else:
            lviols[violation.ruleID] = [ violation ]
        self.violationsByLayer[violation.layer] = lviols

        ## Set bools on what sorts of errors I've seen.
        if violation.ctype == RuleType.PURITY:
            self.sawPurity = True
            self.purityCount += 1
            self.purityViolationsByLayer[violation.layer] += 1

        elif violation.ctype == RuleType.HARD:
            self.hardCount += 1
            self.hardViolationsByLayer[violation.layer] += 1
            self.sawHard = True

        elif violation.ctype == RuleType.SOFT:
            self.softCount += 1
            self.softViolationsByLayer[violation.layer] += 1
            self.sawSoft = True

        else:
            print "Invalid ctype: ", violation.ctype
            exit

    @staticmethod
    def ofList(vList):
        """
        Construct a violation summary object from a list of violations
        """
        obj = ViolationSummary()
        for v in vList:
            obj.add(v)
        return obj

    @staticmethod
    def ofDict(vDict):
        """
        Construct a viloation summary from a dictionary.  Assume Violation ID -> Instances mapping
        """
        obj = ViolationSummary()
        for (id, violations) in vDict:
            for v in violations:
                obj.add(v)
        return obj
