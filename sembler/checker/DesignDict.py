from math import ceil, floor
import threading

from rtree import index

from Layer import Layer
from Rule import Rule
from Rule import RuleType
from DesignObject import Object, Border
from config import DxfConfig, RuleConfig
from intermediate import ViolationSummary

import logging
logger = logging.getLogger('root')

LOUD = False

def roundedSub(big, small):
    delta = big - small
    cd = ceil(delta)
    fd = floor(delta)
    if abs(delta - cd) > (delta - fd):
        return fd
    else:
        return cd

class CheckThread (threading.Thread):
    """
    Wraps the idea of checking a rule against the design dictionary into a
    class.  The class provides a single run method, which is meant to be the
    execution of the thread.
    """
    def __init__(self, threadID, rule, dd):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.rule = rule
        self.dd = dd

    def run(self):
        """
        Checks the rule represented by the thread against the design dictionary"
        """
        logger.info("Checking " + str(self.rule))
        self.rule.check(self.dd)
        logger.info("Done Checking " + str(self.rule))

class DesignDict:
    """
    Wraps objects in DXF design into a single logical item.  Handles everything
    from ingestion to running rules against the ingested design.
    """
    ## Layer indexes
    METAL = RuleConfig.METAL
    SU81 = RuleConfig.SU81
    SU82 = RuleConfig.SU82
    SU83 = RuleConfig.SU83
    POST = RuleConfig.POST
    PORTS = RuleConfig.PORTS
    BORDER = RuleConfig.BORDER
    ALIGNMENT = RuleConfig.ALIGNMENT
    LAYERS = RuleConfig.LAYERS
    ## Layer Growth Factor
    LAYERGROWTH = RuleConfig.LAYERGROWTH

    def __init__(self):
        ## Layers indexed so I can see what previous and next layers are
        ## trivially
        self.dimm = None
        self.objects = {}
        self.ports = Layer("Ports", DesignDict.PORTS)
        self.alignments = {}
        self.layers = []
        self.layers.append(Layer("Metal", DesignDict.METAL))
        self.layers.append(Layer("SU8_1", DesignDict.SU81))
        self.layers.append(Layer("SU8_2", DesignDict.SU82))
        self.layers.append(Layer("SU8_3", DesignDict.SU83))
        self.layers.append(Layer("POST", DesignDict.POST))
        self.layers.append(self.ports)
        self.border = False
        ## Violations are gonna be lists of lists.
        self.violations = ViolationSummary()

    def __str__(self):
        objCount = "Design with " + str(Object.count) + " objects"
        vioCount = " and " + str(self.violationCount()) + " violations"
        return objCount + vioCount

    def addToLayer(self,obj,layer):
        """
        Adds a designObject (obj) to the specified layer (integer) of the design
        dictionary.
        """
        ## Filter objects inside ports
        if layer != DesignDict.METAL:
            possibleHits = self.ports.index.intersection(obj.shape.bounds)
            for objind in possibleHits:
                port = self.ports.objs[objind]
                if port.shape.contains(obj.shape):
                    return

        if layer not in DesignDict.LAYERS:
            raise Exception("Supplied layer", layer, "not in range.")
        else:
            self.layers[layer].add(obj)
            self.objects[obj.id] = obj

    def getLayer(self,id):
        """
        Accesses a layer of the device contained in the design dictionary.
        """
        return self.layers[id]

    def addPort(self, port):
        """
        Adds a port to the port layer.
        """
        if port.id in self.ports.objs or port.id in self.objects:
            raise Exception("Object collision on id", port.id)
        self.ports.add(port)
        self.objects[port.id] = port

    def getPorts(self):
        """
        Return the collection of ports from the port layer.

        Note that this doesn't give you the port layer itself.  You need
        getLayer for that.
        """
        return self.ports.objs

    def populateSize(self, runJson):
        """
        Compute the device's size using information from the border layer.
        """
        if self.border:
            dimms = self.border.bounds
            logger.debug("Setting border from " + str(dimms))
            (minx,miny,maxx,maxy) = self.border.shape.bounds
            ## Do some rounding on X
            dx = roundedSub(maxx, minx)
            sxHalfCM = ceil(dx / 5000)
            # Now we do the same rounding on Y
            dy = roundedSub(maxy,miny)
            syHalfCM = ceil(dy / 5000)
            sx = sxHalfCM / 2
            sy = syHalfCM / 2
            sizeString = "%.1f x %.1f cm" % (sx,sy)
            self.dimm = (sx,sy)
        else:
            logger.error('Invalid border defined.')
            sizeString = "InvalidBorder!"
        runJson["size"] = sizeString

    def addAlignment(self, align):
        """
        Adds an alignment mark to the alignment mark layer.
        """
        if align.id in self.alignments or align.id in self.objects:
            raise Exception("Object collision on id", align.id)
        self.addToLayer(align, DesignDict.METAL)
        self.addToLayer(align, DesignDict.SU81)
        self.alignments[align.id] = align
        self.objects[align.id] = align

    def addPost(self, post):
        """
        Adds a support post to the support post layer.
        """
        possibleHits = self.ports.index.intersection(post.shape.bounds)
        for objind in possibleHits:
            port = self.ports.objs[objind]
            if port.shape.contains(post.shape):
                return
        self.objects[post.id] = post
        self.layers[DesignDict.POST].add(post)

    def getAlignments(self):
        """
        Return a dictionary of alignment marks present in the design
        """
        return self.alignments

    def violationCount(self):
        """
        Compute and return the number of violations associated with the design dictionary.

        If you ask for this number before checking the rules, you'll get the number 0 back,
        despite the design potentially containing errors.
        """
        return len(self.violations.violations)

    def getPortIndex(self):
        """
        Returns a spatial index for the ports in the design.
        """
        ## Already there
        if(hasattr(self, 'portIndex')):
            return self.portIndex
        ## Not made yet, make the port index
        else:
            self.portIndex = index.Index()
            portDict = self.getPorts()
            for key, port in portDict.items():
                self.portIndex.insert(key, port.shape.bounds)
            return self.portIndex

    def setBorder(self, b):
        """
        Set the border object (b) for the design dictionary
        """
        self.border = Border(b)

    def check(self,rid):
        """
        Check the design in the dictionary for compliance against the rule
        associated with the index (rid)
        """
        rule = Rule.dict[rid]
        rule.check(self)

    def checkAllThreaded(self):
        """
        Check the design in the dictionary for complaince with all rules
        described in the rule dictionary (Rule.dict).

        This implementaton is singled threaded.
        """
        threads = []
        for rid, rule in Rule.dict.items():
            logger.info("Spawning thread for rule " + str(rule))
            t = CheckThread(rid, rule, self)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def checkAllSingleThread(self):
        """
        Check the design in the dictionary for complaince with all rules
        described in the rule dictionary (Rule.dict).

        This implementaton uses a thread for each rule.
        """
        ind = 0
        length = len(Rule.dict)
        for rid, rule in Rule.dict.items():
            ind += 1
            logger.info("Checking " + str(ind) + " of " + str(length))
            logger.info("Checking " + str(rule))
            rule.check(self)
            logger.info("Done Checking " + str(rule))
            ## here's where we would update the TANK interface by posting that ind is done
            print "Checking rule", ind, "of", length, "Rule", rid

    def checkAll(self):
        """
        Wrapper around one of checkAllThreaded or checkAllSingleThread.
        """
        logger.info("Checking " + str(len(Rule.dict)) + " rules")
        self.checkAllSingleThread()

    def getViolationCounts(self):
        """
        Counts violations in the violation dictionary associated with the design
        dictionary.

        Returns a tuple of hard violations and soft violations.

        If you run this before checking the rules, you'll get (0,0) back,
        despite there potentially being violations in the design dictionary.
        """
        return (self.violations.hardCount, self.violations.softCount)

    def getObjCounts(self):
        """
        Returns a dictionary mapping Layer Names to Number of Objects in that layer.
        """
        ret = {}
        for layer in self.layers:
            ret[layer.name] = layer.objCount
        return ret
