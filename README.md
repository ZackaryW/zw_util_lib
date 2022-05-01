# zw_util_lib
a misc collection of primitive classes primarily intended for personal generic use (does not rely on any library except built in)

> DISCLAIMER: all code in this repo should not be used in a production environment

# Folder Structure
|folder         | notes|
|-----          |-----|
zxutil          | for stable releases
zxdeprecated    | |
zxdev           | experimental

# Components
## FUNCS 
a module of just functions, all functions use built in python modules only

### base (`__init__.py`)

```py
parse_json(data : typing.Union[dict, list, str]) -> dict

create_timestamp() -> int

is_jsonable(x) -> bool

get_calling_method_name()

parse_dimension_string(dimension_string : str)
```

### img
```py
combine_linear_image(dimension :str,*args)
```

## umodel
a hacked dataclass that has some validation features that worked as a sql trigger
it exploits typing.Union in which it can take callables

### Features
1. it seamlessly converts to a key : value json structure
2. all input on assignment will be casted to the specified type
3. if a callable is defined in typing.Union (as seen below in uid), it will run a validation
4. if `UnqiueKey` or `UIterableUniqueKey` is assigned to the variable, it will check unique of all the instances of the same type

> IMPORTANT: primary key of the same type are singletons

```py
# init
UID_MUST_BE_AT_LEAST_7 = lambda x : len(str(x)) == 7

@dataclass
class someclass(UItem):
    uid : typing.Union[int, UPrimaryKey, UID_MUST_BE_AT_LEAST_7]
    name : typing.Union[str, UniqueKey]
    age : typing.Union[int, UKey]
    address : typing.Union[str, UKey]
    phone : typing.Union[int, UniqueKey]
    email : typing.Union[str, UniqueKey]
```

### function in typing.Union behavior
1. if the function returns a bool, will throw `U_ValidationError` on false
2. if the function returns None, do nothing (v3.0.17, otherwise `3`)
3. for anything else, it will be assigned directly to the function

### Whats behind
* `UItem` class has a metaclass of `UTracker`
* On init of an instance, `UTracker` first generates a `UTrackerStats` object and stored in _analyzed (can be accessed via the get_stats() cls method)
* `UTrackerStats` validates the model (ex: such as no two primary key defined)
* `UTracker` init the instance and stores it in _instances


## Bridge
a simple container class intended for inter module global variables
it mirrors with a defined json file
### Use
* any variable starts with no `_` prefix will be synced with a json file it mirrors

## classConfig
(n/a) 

## CondField / Condlex (`cond.py`)
a condition checker class
```py
# assumes x as the value to be checked
# value == x
value : Any                 
# check each func, func(x) not returning False or raise exceptions
funcs : list[funcs]
# if chained func, func2(func1(x))
chained_funcs : bool
# check against type
typ : typing.Type
# range
range : list, set, tuple
min : int
max : int
min_inclusive : bool 
max_inclusive : bool 
# iterable checks
min_len : int
max_len : int
```

please refer to tests/test_cond.py for example


## FolderCacher
a simple io based deduper

it is only intended to replace redis when its a single extension, single folder with not over 2000 entries. 

It does not watch over folder changes constantly

`load()` function will first check if file already loaded, and returns the in memory instance

`save()` function first check if the file already exists, if not it will attempt to fetch using `fetch_method`

when a file is loaded, the file will be placed in `holding_queue`, `holding_queue` will keep at a constant size (`MAX_HOLDING_QUEUE_SIZE`) and follows a queue structure

if a file load count has exceeded `MIN_REQ_TO_PLACE_CONSTANT`, it will be placed into `constant_cache` (limited by `MAX_CONSTANT_CACHE_SIZE`)

## OnChangeDict 
(n/a)