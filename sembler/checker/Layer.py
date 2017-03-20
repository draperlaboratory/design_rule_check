from rtree import index

class Layer:
    """
    Represents a logical layer of the design of the microfluidic device.
    Something like the metal wafer, or a layer of SU8.  Contains a dictionary of
    the objects on this layer and builds a spatial index (rectangle tree) of
    same.
    """
    count = 0

    def __init__(self, name, ident):
        self.id = ident
        self.objCount = 0
        self.name = name
        self.index = index.Index() ## Create the spatial index
        self.objs = {}

    def add(self,obj):
        """
        Adds a single object to the layer
        """
        self.objs[obj.id] = obj
        self.index.insert(obj.id, obj.bounds())
        self.objCount += 1

    def addCollection(self, objs):
        """
        Adds a group of objects to the layer
        """
        for obj in objs:
            self.objs[obj.id] = obj
            self.objCount += 1
        raise Exception("stub")

    def __str__(self):
        return "Layer " + self.name + " (" + str(self.objects) + " objects)"
