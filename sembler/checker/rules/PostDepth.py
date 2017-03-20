from .. import DesignDict
from .. import Post

#logging
import logging
logger = logging.getLogger('root')

def deepestLayer(post, designDict):
    ## From highest to lowest
    for lid in [DesignDict.SU83, DesignDict.SU82, DesignDict.SU81]:
        logger.debug("Checking for inclusion in " + str(lid))
        layer = designDict.layers[lid]
        candidates = layer.index.intersection(post.shape.bounds)
        for cind in candidates:
            supportedShape = layer.objs[cind]
            ## the objects must wholly contain the post to have that be its layer.
            ## Honestly, if a post intersects an object, it's an error.
            if supportedShape.shape.contains(post.shape):
                post.depth = lid
                return post.depth
            else:
                logger.error("Feature intersects Post; this is bad.")
    return DesignDict.METAL


def fillInPosts(designDict):
    for id, obj in designDict.layers[DesignDict.POST].objs.items():
        deepestLayer(obj, designDict)
