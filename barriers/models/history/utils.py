class PolymorphicBase:
    """
    Allows a class to delegate to a subclass

    Will delegate to a subclass depending on the value of cls.key
    """

    key = None
    class_lookup = {}
    subclasses = tuple()

    def __new__(cls, data):
        if not cls.class_lookup:
            cls.init_class_lookup()

        subclass = cls.class_lookup.get(data[cls.key])
        return subclass(data)

    @classmethod
    def init_class_lookup(cls):
        for subclass in cls.subclasses:
            cls.class_lookup[getattr(subclass, cls.key)] = subclass
