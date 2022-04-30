import json
import typing
import os
import datetime
import inspect

def parse_json(data : typing.Union[dict, list, str]) -> dict:
    """
    parse input data to dict
    checks if data is valid json path or json data
    """
    if isinstance(data, (dict, list)):
        return data
    elif isinstance(data, str) and os.path.exists(data):
        with open(data, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return None
    elif isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None
        
def create_timestamp() -> int:
    """
    creates a unix timestamp
    """
    now = datetime.datetime.now()
    # convert now to unix timestamp milliseconds
    unix_timestamp = int(now.timestamp() * 1000)
    return unix_timestamp

def is_jsonable(x):
    """
    checks if a value is jsonable
    """
    try:
        json.dumps(x)
        return True
    except:
        return False

def get_calling_method_name() -> str:
    """ 
    returns the name of the calling method

    Returns:
        str: name of the calling method
    """
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    calling_method_name = calframe[1][3]
    return calling_method_name

def parse_dimension_string(dimension_string : str) -> list:
    """
    parses a dimension string [int]xint to x,y
    """
    dimension_string = dimension_string.lower()

    if "x" not in dimension_string:
        return None

    splits = dimension_string.split("x")
    if len(splits) != 2:
        return None
    
    try:
        x = int(splits[0])
        y = int(splits[1])
        return x, y
    except ValueError:
        return None