from importlib import import_module
import inspect


def getatters(obj, attrs):
    return [getattr(obj, attr) for attr in attrs if hasattr(obj, attr)]


def getlastattr(attr, *objs):
    for obj in reversed(objs):
        if obj is None:
            continue
        elif hasattr(obj, attr):
            return getattr(obj, attr)

    raise AttributeError("no attribute '%s'" % attr)


def load_class(class_path, base_class, include_base_class=False):
    module_path, class_name = class_path.rsplit('.', 1)
    _mod = import_module(module_path)
    _cls = getattr(_mod, class_name)
    if inspect.isclass(_cls) and \
            issubclass(_cls, base_class) and \
            (include_base_class or _cls != base_class):
        return _cls
    return None
