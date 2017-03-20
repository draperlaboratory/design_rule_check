import logging
logger = logging.getLogger('root')

class RuleType:
    SOFT = 0
    HARD = 1
    PURITY = 2

class Rule:
    """
    Abstract representation of the rules to be checked by the design rule
    checker.  Wraps naming / display information for the output pdf and dxf, as
    well as the logic for checking the design against the rule.

    This should never be instantiated.  It's an abstract class.
    """
    ELAYER = "errorLayer"
    APPLYTO = "relevantLayers"
    HEADING = "sectionHeading"
    DESC = "longDesc"
    ID = "id"
    CTYPE = "ConstraintType"
    THRESH = "threshold"
    dict = {}
    count = 0

    def __init__(self, rdesc):

        self.id = rdesc[Rule.ID]
        self.desc = rdesc[Rule.HEADING]
        self.expl = rdesc[Rule.DESC]
        self.layers = rdesc[Rule.APPLYTO]
        self.dxfLayer = rdesc[Rule.ELAYER]
        self.ctype = rdesc[Rule.CTYPE]

        assert (self.layers != None)

        Rule.count += 1
        Rule.dict[self.id] = self

    def __str__(self):
        return "Rule " + str(self.id) + ": " + str(self.desc)

    def check(self, designDict):
        """
        Check the design dictionary for compliance with the rule.  If there are
        violations, add them to the design dictionary.
        """
        raise Exception("Subclasses are expected to override this.")

def sanity():
    """
    Sanity check, makes sure that each rule is stored at an index that aligns
    with its own ID.  We ran into this problem a couple of times during initial
    sembler development.
    """
    logger.debug("Sanity check: rid -> rule.id")
    for(rid, rule) in Rule.dict.items():
        if rid != rule.id:
            logger.critical("rid " + str(rid) + " maps to " + str(rule))
