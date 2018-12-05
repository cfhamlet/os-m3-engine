import inspect
from importlib import import_module


def getatters(obj, attrs):
    return [getattr(obj, attr) for attr in attrs if hasattr(obj, attr)]


def load_class(class_path, base_class=None, include_base_class=False):
    module_path, class_name = class_path.rsplit('.', 1)
    _mod = import_module(module_path)
    if not hasattr(_mod, class_name):
        return None
    _cls = getattr(_mod, class_name)
    if not inspect.isclass(_cls):
        return None
    elif base_class is None:
        return _cls
    elif issubclass(_cls, base_class) and (include_base_class or _cls != base_class):
        return _cls
    else:
        return None
