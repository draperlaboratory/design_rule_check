from .. import DesignDict, Violation, Rule, Witness
from config import rules
from shapely.prepared import prep
from shapely.geometry import Polygon

#logging
import logging
logger = logging.getLogger('root')

ruleDict45 = rules[45]
ruleDict46 = rules[46]
ruleDict47 = rules[47]

def fastCheck(threshold, allPosts, candidatePosts, post):
    ## swell the post up to the right size, and make sure we touch something.
    foundNearEnough = False
    for post2 in candidatePosts:
        if post2.id == post.id:
            continue
        if post.shape.distance(post2.shape) <= threshold:
            ## everything is ok
            return True
    return False

def slowCheck(threshold, allPosts, post):
    """ Slower version of fastCheck """
    for p2ind, p2 in allPosts.objs.items():
        if p2ind == post.id:
            continue
        d = p2.shape.distance(post.shape)
        print d, threshold
        if d <= threshold:
            return True
    return False

class PostPitch(Rule):
    def __init__(self, ruleDict, postDepth):
        Rule.__init__(self, ruleDict)
        self.postDepth = postDepth
        self.thresh = ruleDict[Rule.THRESH]

    def check(self, dd):
        allPosts = dd.layers[DesignDict.POST]
        layer = dd.layers[self.postDepth]

        for featID, feature in layer.objs.items():
            ## For every feature in the layer, find relevant posts
            candidatePostIndexes = allPosts.index.intersection(feature.shape.bounds)
            candidatePosts = []
            prepped = prep(feature.shape)
            ## Filter out from bounding box to get real intersections
            for cind in candidatePostIndexes:
                post = allPosts.objs[cind]
                if (self.postDepth == post.depth) and prepped.contains_properly(post.shape):
                    candidatePosts.append(post)

            print "Posts in depth:", len(candidatePosts)
            for post in candidatePosts:
                foundNearEnough = fastCheck(self.thresh, allPosts, candidatePosts, post)
#               foundNearEnough = slowCheck(self.thresh, allPosts, post)
                if (not foundNearEnough):
                    ## Something was bad here
                    dd.violations.add(Violation.ofRule(self, [post], [Witness(Witness.REGION, post.shape)]))


postPitchSU81 = PostPitch(ruleDict45, DesignDict.SU81)
postPitchSU82 = PostPitch(ruleDict46, DesignDict.SU82)
postPitchSU83 = PostPitch(ruleDict47, DesignDict.SU83)
