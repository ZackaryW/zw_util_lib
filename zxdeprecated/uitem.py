from dataclasses import dataclass
import dataclasses
import logging
from pprint import pprint
import typing
from zxutil.FUNCS import parse_json
import json 
import inspect 

class PrimaryJsonKey:pass

class UniqueKey:pass

class UniqueSet:pass

class UniqueConflict(Exception):pass

class ValidationFail(Exception):
    def __init__(self,msg, problematic_key : str, validation_func : typing.Callable, exception : Exception):
        self.msg = msg
        self.problematic_key = problematic_key
        self.validation_func = validation_func
        self.exception = exception
        super().__init__(msg)

@dataclass
class UItem:
    _tracker : 'UTracker'
    
    def __unique_pass(self, name, value):
        """
        ✔ check if there is any collision of unique fields
        """
        if name not in self._tracker.unique_keys and name != self.primary_key:
            return

        if value is None:
            return

        for item in self._tracker.yield_all():
            if item == self:
                continue
        
            
            if (got_item := getattr(item, name, None)) == value:
                raise UniqueConflict(f"{name} is a unique key, but {value} is already in use")

            if isinstance(got_item, (list, tuple, set)) and name in self._tracker.unique_set:
                # if value is the same in any 
                for v in value:
                    if v in item:
                        raise UniqueConflict(f"repeated value {v} in {name}")

    def __setitem__(self, key : str, value) -> None:
        """
        ✔ set the item
        """
        if key in self.field_keys:
            setattr(self, key, value)
            return
        
        if "other" not in self.data():
            self.data()["other"] = {}

        self.data()["other"][key] = value

    def __getitem__(self, key : str) -> typing.Any:
        """
        ✔ get the item
        """
        if key in self.field_keys:
            return self.data()[key]

        if "other" not in self.data():
            return None
        
        return self.data()["other"][key]

    def _set_else(self, **kwargs) -> None:
        """
        ✔ set the item
        """
        if "other" not in self.data():
            self.data()["other"] = {}


        self.data()["other"].update(kwargs)

    def __setattr__(self, name : str, value) -> None:
        if getattr(self, name, None) == value:
            return

        if name.startswith("_"):
            return super().__setattr__(name, value)

        if name == self.primary_key:
            value = str(value)

        if name == self.primary_key and self.primary_key_val is not None:
            raise ValueError(f"{name} is a primary key, u cant fucking do it")

        if name in self.field_keys:
            value = self._tracker.validate(name, value, self)

            self.__unique_pass(name, value)
            data = self.data()
            
                
            data[name] = value
            return
        
        super().__setattr__(name, value)

    def __getattr__(self, name : str):
        if name.startswith("_"):
            return super().__getattr__(name)

        if name in self.field_keys and name in self.data():
            return self.data()[name]

        return None 

    def __delattr__(self, name : str) -> None:
        if name in self.field_keys:
            del self.data()[name]
            return
        
        super().__delattr__(name)

    def __contains__(self, item : str):
        if item in self.field_keys:
            return item in self.data()

        return super().__contains__(item)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.primary_key_val}>"
    
    def __str__(self):
        return f"<{self.__class__.__name__} {self.primary_key_val}>"

    @property
    def field_keys(self) -> typing.List[str]:
        """
        ✔ get all field keys
        """
        return self._tracker.field_keys

    def data(self) -> dict:
        """
        ✔ return the data of the item
        """
        if self.primary_key_val not in self._tracker._data:
            self._tracker._data[self.primary_key_val] = {}
        return self._tracker._data[self.primary_key_val]

    def to_dict(self) -> dict:
        """
        ✔ return the item as a dict
        """
        data = dict(self.data()).copy()
        data[self.primary_key] = self.primary_key_val
        return data

    @property
    def primary_key_val(self):
        """
        ✔ get primary key value
        """
        return getattr(self, self._tracker.primary_key, None)

    @property
    def primary_key(self):
        """
        ✔ get primary key
        """
        return self._tracker.primary_key

    def match(self, **kwargs) -> bool:
        """
        ✔ check if the item matches the kwargs
        """
        if len(kwargs) == 0 or not kwargs:
            return True

        if self.primary_key in kwargs and self.primary_key_val != str(kwargs.get(self.primary_key, None)):
            return False

        if len(kwargs) == 1 and self.primary_key in kwargs:
            return True
            
        for k, v in self.data().items():
            if k not in kwargs:
                continue
            if kwargs[k] != v:
                return False

        return True

    def update(self, **kwargs) -> None:
        """
        ✔ update the item
        """
        for key, value in kwargs.items():
            self.__setitem__(key, value)



@dataclass
class UTracker:
    uitem_type : UItem
    data : typing.Union[str, dict] = dataclasses.field(default_factory=dict)
    field_keys : typing.List[str] = dataclasses.field(init=False)
    verification_model : typing.Dict[str, typing.Union[typing.Callable, typing.Type]] = dataclasses.field(default_factory=dict)
    primary_key : str = None,
    unique_keys : typing.List[str] = None
    unique_set : typing.List[str] = None
    field_keys : typing.List[str] = None
    json_save_path : str = None

    def validate(self, name: str, value, item :UItem = None):
        """
        ✔ validate the item
        """
        if name not in self.verification_model:
            return value

        
        validation = self.verification_model[name]

        if isinstance(validation, typing.Type):
            return validation(value)
        
        validation : callable

        params = {
            "value": value,
            "name" : name,
            "item" : item,
            "tracker" : self,
        }

        params[name] = value

        needed_params = inspect.signature(validation).parameters
        params = {k: v for k, v in params.items() if k in needed_params}

        try:
            # get parameters needed for validation
            res = validation(**params)
            if isinstance(res, bool) and not res:
                raise
            elif isinstance(res, bool) and res:
                pass
            else:
                value = res   
        
        except Exception as e:
            raise ValidationFail(f"{name} failed validation", name, validation, e)

        return value

    def __post_init__(self):

        # 
        logging.debug("loading data")
        if isinstance(self.data, str):
            self.json_save_path = self.data
            logging.debug(f"loading data from {self.json_save_path}")
            self.data = parse_json(self.data)

        # * check data type
        if not isinstance(self.data, dict):
            raise TypeError("data is not a dict")
        
        verification_updates = {}
        if any(
            x is None for x in [self.primary_key,self.unique_keys, self.field_keys ,self.unique_set]
        ):
            self.primary_key, self.unique_keys, self.field_keys, self.unique_set, verification_updates = self._parse_datafields(self.uitem_type)
        
        
        self._objects = []
        self._data = {}
        
        if len(self.data) > 0:
            logging.debug("loading objects")

        for k, v in self.data.items():
            if not isinstance(v, dict):
                raise TypeError("data is not a dict")

            kwargs = {}
            kwargs.update(v)
            kwargs[self.primary_key] = k

            self.create_item(**kwargs)

        del self.data
        
        # verify model
        if self.verification_model:
            for k, v in self.verification_model.items():
                if callable(v) or isinstance(v, type):
                    continue
                raise TypeError("verfication value is not callable or type")

            for k,v in verification_updates.items():
                if k not in self.verification_model:
                    self.verification_model[k] = v
                
        else:
            self.verification_model = {}
            

    def yield_all(self,reverse_condition : bool = False, **kwargs):
        """
        ✔ get all items that match the kwargs
        """
        if len(kwargs) == 0 or not kwargs:
            for item in self._objects:
                yield item

        for item in self._objects:
            match_flag = item.match(**kwargs)

            if match_flag != reverse_condition:
                yield item

    def get_all(self,reverse_condition : bool = False, **kwargs):
        """
        ✔ get all items that match the kwargs
        """
        if len(kwargs) == 0 or not kwargs:
            return self._objects

        items = []
        for item in self._objects:
            match_flag = item.match(**kwargs)
            if match_flag != reverse_condition:
                items.append(item)
        
        return items

    def get_fields(self,*fields, reverse_condition : bool = False,**kwargs):
        ret = {}
        for item in self.yield_all(reverse_condition=reverse_condition,**kwargs):
            
            for field in fields:
                if field not in ret:
                    ret[field] = []

                ret[field].append(getattr(item, field))
        
        return ret

    def get_field(self, field : str,reverse_condition : bool = False, **kwargs):
        ret = []
        for item in self.yield_all(reverse_condition=reverse_condition,**kwargs):
            ret.append(getattr(item, field))
        
        return ret

    def get_one(self, reverse_condition : bool = False, **kwargs):
        """
        ✔ get one item that match the kwargs
        """
        for item in self.yield_all(reverse_condition=reverse_condition,**kwargs):
            return item

        
    def yield_field(self, field : str, reverse_condition : bool = False, **kwargs):
        """
        ✔ yield all items that match the kwargs
        """
        for item in self._objects:
            item : UItem
            match_flag = item.match(**kwargs)
            if match_flag != reverse_condition:
                yield getattr(item, field)
    

    def create_item(self, other:dict =None ,**kwargs):
        """
        ✔ create a new item
        """
        
        if (pval := kwargs.get(self.primary_key, None)) is None:
            raise ValueError(f"{self.primary_key} (primary key) is not found")


        if pval in self._data:
            raise ValueError(f"{pval} already exists")

        item_type : UItem = self.uitem_type
        
        kkwargs = {"_tracker": self}


        # filter 
        for k in list(kwargs.keys()):
            if k in self.field_keys or k == self.primary_key:
                kkwargs[k] = kwargs.pop(k)
    
        item : UItem = item_type(
            **kkwargs
        )

        if not other:
            other = kwargs
        else:
            other.update(kwargs)

        if len(other) > 1:
            item._set_else(**other)

        self._objects.append(item)
        
        return item

    def update_item(self, **kwargs):
        """
        ✔ update an item
        """
        if pval := kwargs.get(self.primary_key, None) is None:
            raise ValueError(f"{self.primary_key} (primary key) is not found")

        if pval not in self._data:
            raise ValueError(f"{pval} not found")

        item : UItem = self.get_one(**{self.primary_key : pval})
        item.update(**kwargs)

        return item

    def save(self):
        """
        ✔ save the data
        """
        if self.json_save_path:
            logging.debug(f"saving data to {self.json_save_path}")
            with open(self.json_save_path, "w") as f:
                json.dump(self._data, f, indent=4)

    def __getitem__(self, key):
        """
        ✔ get item by primary key
        """
        if key not in self._data:
            raise KeyError(f"{key} not found")

        kwarg = {self.primary_key : key}

        return self.get_one(**kwarg)


    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}>"


    def __contains__(self, item: str):
        """
        ✔ check if item is in the tracker
        """
        return item in self._data

    def transform(self, replaced_uitem : UItem,
    verification_model : dict = None

    ) -> 'UTracker':
        """
        ✔ transform structure
        """

        if not verification_model:
            verification_model = {}

        primary_key, unique_index, field_keys, unique_set, verification_updates = self._parse_datafields(replaced_uitem)

        for k, v in verification_updates.items():
            if k not in verification_model:
                verification_model[k] = v

        new_tracker = UTracker(
            uitem_type=replaced_uitem,

            primary_key=primary_key,
            unique_keys=unique_index,
            field_keys=field_keys,
            verification_model = verification_model,
            unique_set=unique_set,
        )

        conflicts = []
        for item in self._objects:
            item : UItem

            data = item.to_dict()
            try:

                new_tracker.create_item(**data)
            except UniqueConflict:
                logging.error(f"failed to transform (unique key) {item}")
                conflicts.append(data)
            except ValueError:
                logging.error(f"failed to transform (primary key) {item}")
                conflicts.append(data)
                
        return new_tracker, conflicts

        
        # 
    def remove(self, *args, **kwargs):
        items  = self.get_all(**kwargs)
        items.extend(args)

        for item in items:
            
            if not isinstance(item, UItem):
                raise TypeError(f"{item} is not a UItem")

            item : UItem = self._objects.pop(self._objects.index(item))
            del self._data[item.primary_key_val]
            self._objects.remove(item)

    def _parse_datafields(self, uitemr : UItem):
        logging.debug("loading uitem type")
                # check if uitem_type is a class
        if not isinstance(uitemr, type):
            raise TypeError("uitem_type is not a class")
        

        # check if uitem_type is a subclass of UItem
        if not issubclass(uitemr, UItem):
            raise TypeError(f"{uitemr} is not a subclass of UItem")

        logging.debug("loading dataclasses")
        dataclass_fields = uitemr.__dataclass_fields__
        
        dataclass_fields = {k : v for k, v in dataclass_fields.items() if not k.startswith("_")}

        verification_updates = {}
        for k, v in dataclass_fields.items():
            v : dataclasses.Field
            if v.type in [int, float, str, bool]:
                verification_updates[k] = v.type


        #init var
        primary_key = None
        unique_index = []
        field_keys = []
        unique_set = []

        for field in dataclass_fields.values():
            if field.type == PrimaryJsonKey:
                if primary_key:
                    raise ValueError("Multiple PrimaryJsonKey found")
                primary_key = field.name

            if field.type == UniqueSet:
                unique_set.append(field.name)

            if field.type == UniqueKey or field.type == UniqueSet:
                unique_index.append(field.name)

        if not primary_key:
            raise ValueError("No PrimaryJsonKey found")

        field_keys : typing.List[str] = [field.name for field in dataclass_fields.values()]
        # field keys remove primary_json_key
        field_keys.remove(primary_key)

        return primary_key, unique_index, field_keys, unique_set, verification_updates