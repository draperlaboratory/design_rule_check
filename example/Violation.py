
class Violation:
    count = 0

    def __init__(self, rule, objects):
        self.id = Violation.count
        Violation.count += 1
        self.desc = rule.desc
        self.ruleID = rule.id
        self.conflicting = objects

    def __str__(self):
        objstr = ""
        for obj in self.conflicting:
            objstr = objstr + " " + str(obj)
        return "Violation Rule " + str(self.ruleID) + ": " + self.desc + objstr
