def baseclasses(cls, bases=None):
    """Returns a flat list of all baseclasses according to the method
    resolution order. Includes `cls`.
    """
    if bases is None:
        bases = []

    bases.append(cls)

    for base in cls.__bases__:
        if base not in bases:
            baseclasses(base, bases)

    return bases
