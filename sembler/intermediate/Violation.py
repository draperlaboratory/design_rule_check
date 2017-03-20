from checker import RuleType
import logging
logger = logging.getLogger('root')

class Violation:
    """
    Abstract representation of a rule violation.  Really just a struct,
    containing the rule that was violated, the rule that the violation is
    associated with, and the objects doing the violating.
    """
    count = 0

    def __init__(self, name, description, layerName, entities=[],
                 witnesses=[], inserts=[], ruleID=None, layer=None,
                 ctype=RuleType.PURITY):
        """
        Once we're ready to push witnesses live, we can add an assertion that
        no witness list is empty.
        """
        assert layer != None
        self.id = Violation.count
        Violation.count += 1
        for e in entities:
            if not hasattr(e, 'shape'):
                logger.warning(str(e) + " has no shape feature!")
        self.name = name
        self.desc = description
        self.ruleID = ruleID
        self.dxfLayer = layerName
        self.conflicting = entities
        self.witnesses = witnesses
        self.inserts = inserts
        self.layer = layer
        self.ctype = ctype
        if witnesses == []:
            print "rule", ruleID , "made without witnesses"

    def __str__(self):
        objstr = ""
        for obj in self.conflicting:
            objstr = objstr + " " + str(obj)
        return "Violation Rule " + str(self.ruleID) + ": " + self.desc + objstr

    @staticmethod
    def ofRule(rule, entities=[], witnesses=[]):
        for e in entities:
            if not hasattr(e,'shape'):
                print e, "has no shape"
                assert False
        return  Violation(rule.desc, rule.expl, rule.dxfLayer,
                          entities=entities, witnesses=witnesses,
                          ruleID=rule.id, layer=rule.layers, ctype=rule.ctype)
