
from dataclasses import dataclass
import dataclasses
import inspect
import json
import logging
import os
from pprint import pprint
import typing
from zxutil.FUNCS import parse_json
from zxutil.umodel.attrs import U_InvalidBehavior, U_ValidationError
from zxutil.umodel.utracker import UTracker

@dataclass
class UItem(metaclass=UTracker):
    """
    base UItem class
    
    name : typing.Union[str, UPrimaryKey, [funcs to check]]
    
    """
    # ANCHOR internals
    def __setattr__(self, name: str, val) -> None:
        stats = self._tracker.get_stats()
        if name.startswith("_"):
            return object.__setattr__(self, name, val)
        
        if name not in stats.all_fields:
            return

        # check if name is primary key
        if name == stats.primary_key and self.primary_key is not None:
            raise U_InvalidBehavior("primary key can't be changed")

        # cast value
        val = stats.set_cast(name, val)
        
        if (
            stats.is_unique_key(name)
            and not self._tracker.check_unique(name, val, self.primary_key)
        ):
            raise U_ValidationError(f"{name} is not unique ({val})")

        if (
            stats.is_iterable_unique_key(name)
            and not self._tracker.check_iterable_unique(name, val, self.primary_key)
        ):
            raise U_ValidationError(f"{name} is not unique (iterable) ({val})")

        val = self._tracker.check_callables(name, val, self.primary_key,self)

        object.__setattr__(self, name, val)

    def __del__(self):
        self._tracker.remove_this(self)

    def export_this(self, path : str):
        data = {}
        if os.path.exists(path):
            with open(path, "r") as f:
                data =json.load(f)

        if self.primary_key is None:
            raise ValueError("primary key is None")

        primary_key_label = self._tracker.get_stats().primary_key

        if isinstance(data, dict):
            data.update(self.tojson())
            with open(path, "w") as f:
                json.dump(data, f)

        if not isinstance(data, list):
            raise ValueError("data is not dict/list")
        
        exist = False

        for i, item in enumerate(data):
            if item[primary_key_label] == self.primary_key:
                data[i] = self.todict()
                exist = True
                break
        
        if not exist:
            data.append(self.todict())

        with open(path, "w") as f:
            json.dump(data, f)

    # ANCHOR export methods
    def todict(self):
        return dataclasses.asdict(self)

    def tojson(self):
        data = self.todict()
        primary_key_label = self._tracker.get_stats().primary_key
        data.pop(primary_key_label)
        return {str(self.primary_key): data}

    # ANCHOR PROPERTY
    @property
    def _tracker(self):
        return self.__class__

    @property
    def primary_key(self):
        key = self._tracker.get_stats().primary_key
        return getattr(self, key, None)

    # ANCHOR CLASSMETHOD
    @classmethod
    def get(cls, **kwargs):
        for key, val in cls.yield_instance(**kwargs):
            return val
    
    @classmethod
    def export_all(cls, path= None, update: bool = False):
        data = {}
        data2 = None
        if update and path is not None:
            data2 =parse_json(path)
        
        if data2 is not None and isinstance(data2, dict):
            data = data2

        for key, val in cls.yield_instance():
            val : UItem
            data.update(val.tojson())

        if path is None:
            return data

        with open(path, "w") as f:
            json.dump(data, f)

    @classmethod
    def export(cls, path : str=None,update_: bool = False, **kwargs):
        if len(kwargs) == 0:
            return cls.export_all(path)

        data = {}
        data2 = None
        if update_ and path is not None:
            data2 =parse_json(path)
        
        if data2 is not None and isinstance(data2, dict):
            data = data2

        for key, val in cls.yield_instance(**kwargs):
            val : UItem
            data.update(val.tojson())
            
        if path is None:
            return data

        with open(path, "w") as f:
            json.dump(data, f)
  
    @classmethod
    def create(cls, _filter: bool = False, **kwargs):
        # inspect
        if _filter:
            kwargs = {k:v for k,v in kwargs.items() if k in cls.get_stats().all_fields}
        return cls(**kwargs)

    @classmethod
    def from_dict(cls, json_data: typing.Union[str, dict]):
        json_data = parse_json(json_data)
        if json_data is None:
            return None

        if isinstance(json_data, dict):
            for key, val in json_data.items():
                val[cls.get_stats().primary_key] = key
                return cls.create(**val)