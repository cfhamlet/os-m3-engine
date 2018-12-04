
def getatters(obj, attrs):
    return [getattr(obj, attr) for attr in attrs if hasattr(obj, attr)]


def getlastattr(attr, *objs):
    for obj in reversed(objs):
        if obj is None:
            continue
        elif hasattr(obj, attr):
            return getattr(obj, attr)

    raise AttributeError("no attribute '%s'" % attr)
