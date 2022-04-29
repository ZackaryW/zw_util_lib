import dataclasses
from types import MappingProxyType
from typing import FrozenSet
from zxutil.umodel.attrs import U_ValidationError
from zxutil.umodel.ustats import UTrackerStats
from zxutil.cond import CondField, CondLex

class UTracker(type):
    __analyzed : dict= {}
    __instances : dict = {}

    def __call__(cls, *args, **kwargs):
        """
        constructor method
        """
        # sep to avoid name conflict for different cls
        stats = cls.get_stats()

        # get primary key
        primary_key = stats.primary_key
        # get primary key value
        primary_key_value = kwargs.get(primary_key, None)
        try:
            primary_key_value = str(primary_key_value)
        except:
            raise U_ValidationError(f"primary key value must be castable to str")

        if primary_key_value is None:
            raise ValueError("primary key value is None")
        # check if primary key value is unique
        if primary_key_value in cls.__instances[cls]:
            raise U_ValidationError("cannot instantiate with duplicate primary key value")
        instance = super().__call__(*args, **kwargs)
        cls.__instances[cls][primary_key_value] = instance
        return instance

    def yield_instance(cls, **kwargs):
        if cls not in cls.__instances:
            return

        instances : dict = cls.__instances[cls]
        
        if len(kwargs) == 0:
            for key, val in instances.items():
                yield key, val
            return 

        condlex = CondLex(**kwargs)

        for key, val in instances.items():
            datadict = dataclasses.asdict(val)
            if condlex.match(**datadict):
                yield key, val

    def yield_field(cls, fieldname : str, yield_all : bool = False, **kwargs):
        stats : UTrackerStats = cls.get_stats()
        if fieldname not in stats.all_fields:
            return

        for key, val in cls.yield_instance(**kwargs):
            attr = getattr(val, fieldname, None)
            if attr is None:
                continue
            if yield_all:
                yield attr, key, val
            else:
                yield attr
        

    def yield_keys(cls, **kwargs):
        for key, val in cls.yield_instance(**kwargs):
            yield key

    def get_stats(cls) -> UTrackerStats:
        if cls not in cls.__instances:
            cls.__instances[cls] = {}

        if cls not in cls.__analyzed:
            cls.__analyzed[cls] = UTrackerStats.analyze_uitem(cls)

        return cls.__analyzed[cls]

    def remove(cls, **kwargs):
        if cls not in cls.__instances:
            return
        instances  = cls.__instances[cls].keys()

        frozekeys = frozenset(instances)
        for key in frozekeys:
            condlex = CondLex(**kwargs)
            datadict = dataclasses.asdict(cls.__instances[cls][key])
            if condlex.match(**datadict):
                del cls.__instances[cls][key]
    
    def remove_this(cls, item):
        if cls not in cls.__instances:
            return
    
        if item.__class__ not in cls.__instances:
            return

        # get primary key
        try:
            del cls.__instances[cls][item.primary_key]
        except:
            pass
    
    def check_unique(cls, key : str, value, ignore_this = None, **kwargs):
        stats = cls.get_stats()
        if not stats.is_unique_key(key):
            return None

        for attr, kkey, kval in cls.yield_field(key,yield_all=True, **kwargs):
            if ignore_this == kkey:
                continue
            if attr == value:
                return False

        return True

    def check_iterable_unique(cls, key : str, value, ignore_this = None, **kwargs):
        stats = cls.get_stats()

        if not stats.is_iterable_unique_key(key):
            return None

        unique = set()
        for attr, kkey, kval in cls.yield_field(key,yield_all=True, **kwargs):
            if ignore_this == kkey:
                continue
            unique.update(attr)

        if value in unique:
            return False

        return True