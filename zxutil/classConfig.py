class _gconfigmeta(type):
    def __getattribute__(self, __name: str):
        try:
            return object.__getattribute__(self, __name)
        except AttributeError:
            return None

class _gconfig(metaclass=_gconfigmeta):
    pass
    

class _cconfigMeta(type):
    def __getattribute__(cls, __name: str):
        if __name.startswith("_"):
            return super().__getattribute__(__name)

        item = super().__getattribute__(__name)

        # if instance is a subclass of global_config,
        # return the global_config instance

        if not (hasattr(item, "__class__") and item.__class__ == _gconfigmeta):
            return item

        if hasattr(item, __name):
            return getattr(item, __name)

        else:
            return None

    def has_gconfig(cls, name : str):
        if name.startswith("_"):
            return False
        
        item = super().__getattribute__(name)

        if not (hasattr(item, "__class__") and item.__class__ == _gconfigmeta):
            return False

        return True

class _cconfig(metaclass=_cconfigMeta):
    pass

def has_gconfig(cls, item : str):
    if not (hasattr(cls, "__class__") and cls.__class__ == _cconfigMeta):
        return None

    return cls.__class__.has_gconfig(cls, item)



    