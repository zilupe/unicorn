_missing = object()


def init_instance_dict_safely(instance, kwargs):
    """
    Update instance.__dict__ with only those kwargs
    that the class has declared or has inherited.

    This allows using class attributes as fallback values and not having
    to specify all kwargs in initialiser declarations and still guards
    developers against accidentally passing incorrect kwargs.
    """
    cls = instance.__class__
    for k, v in kwargs.items():
        if hasattr(cls, k):
            instance.__dict__[k] = v
        else:
            raise ValueError('Unexpected kwarg {!r} passed to {} initialiser'.format(k, cls.__name__))
