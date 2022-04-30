import logging
import os
import typing
import json
import PIL
from PIL import Image
from PIL.Image import Image as PILImage
import requests
import io
# ANCHOR load methods
def load_file(path : str, **kwargs) -> str:
    with open(path, "r") as file:
        return file.readlines()

def save_file(obj, path : str, **kwargs):
    with open(path, "w") as file:
        file.write(obj)

def load_json(path : str, **kwargs) -> str:
    with open(path, "r") as file:
        return json.load(file)

def save_json(obj, path : str, **kwargs):
    with open(path, "w") as file:
        json.dump(obj, file)

def fetch_web_img(link : str, **kwargs) -> PILImage:
    if link is None:
        return
    res = requests.get(link)
    if res is None or res.content is None:
        return
    return Image.open(io.BytesIO(res.content))

def save_web_img(obj, path : str, **kwargs):
    if isinstance(obj, PILImage):
        obj.save(path)
        return
    if obj is None:
        return
    with open(path, "wb") as file:
        file.write(obj)

def load_web_img(path : str, **kwargs) -> PILImage:
    return Image.open(path)

class FolderCacher:
    class _CACHE_FLAG_: pass
    class CONSTANT_CACHE(_CACHE_FLAG_): pass
    class HOLDING_CACHE(_CACHE_FLAG_): pass

    def __init__(self, path : str, create_if_null : bool = True, extension : str =None) -> None:
        if create_if_null and not os.path.exists(path):
            os.mkdir(path)
        elif not os.path.exists(path):
            raise FileNotFoundError(path)

        self._constant_cache = {}
        self._holding_queue = {}
        self._counting_index = {}
        
        self.method_fetch = None
        self.method_load = None
        self.method_save = None

        self.MAX_HOLDING_QUEUE_SIZE = 30
        self.MAX_CONSTANT_CACHE_SIZE = 30
        self.MIN_REQ_TO_PLACE_CONSTANT = 10

        self.GLOBAL_EXTENSION = extension
        self.PATH = path

        # list path
        files = os.listdir(path)
        for file in files:
            # split extension
            file_name, extension = os.path.splitext(file)
            extension = extension[1:]
            if extension != self.GLOBAL_EXTENSION and self.GLOBAL_EXTENSION is not None:
                continue
            if self.GLOBAL_EXTENSION is None:
                self._counting_index_action(file)
            else:
                self._counting_index_action(file_name)
    
    def __contains__(self, name) -> bool:
        if isinstance(name, str):
            return name in self._counting_index
        if isinstance(name, typing.Iterable) and len(name) == 2 and name[0] in self._counting_index:
            if name[1] == FolderCacher.CONSTANT_CACHE:
                return name[0] in self._constant_cache
            if name[1] == FolderCacher.HOLDING_CACHE:
                return name[0] in self._holding_queue
        
        raise TypeError(f"{name} is not a valid key to check contains")
            

    def _get_from_cache(self, key : str):
        if key not in self._counting_index:
            raise KeyError(f"{key} not in index")
        
        if key in self._constant_cache:
            self._counting_index_action(key)
            return self._constant_cache[key]
        if key in self._holding_queue:
            self._counting_index_action(key)
            return self._holding_queue[key]
        return None

    def _counting_index_action(self, key : str):
        if key not in self._counting_index:
            self._counting_index[key] = 0
        else:
            self._counting_index[key] += 1
    
    def _get_lowest_count_in_holding_cache(self, target_dict :typing.Dict[str, typing.Any]) -> str:
        if len(target_dict) == 0:
            return None, None
    
        lowest = None
        for key in target_dict:
            if lowest is None:
                lowest = key
                continue
            if self._counting_index[key] < self._counting_index[lowest]:
                lowest = key

        if lowest is None:
            return None, 0

        return lowest, self._counting_index[lowest]


    def _place_cache(self, key : str, obj : object):
        # constant cache maintain
        lowest = None
        while len(self._constant_cache) > self.MAX_CONSTANT_CACHE_SIZE:
            # get the lowest on counting index
            lowest, lowest_count = self._get_lowest_count_in_holding_cache(self._constant_cache)
            lowest_v = self._constant_cache.pop(lowest)
            # add lowest 
            self._holding_queue[lowest] = lowest_v

        # holding queue once over limit, just pop the oldest one
        while len(self._holding_queue) > self.MAX_HOLDING_QUEUE_SIZE:
            self._holding_queue.popitem()

        if key in self._constant_cache:
            return

        if key in self._holding_queue and self._counting_index[key] >= self.MIN_REQ_TO_PLACE_CONSTANT:
            self._holding_queue.pop(key)
            self._constant_cache[key] = obj
            return

        if key not in self._holding_queue:
            self._holding_queue[key] = obj

    def save(self, key : str,obj=None, **kwargs):
        key = str(key)
        if key in self._counting_index:
            logging.info(f"{key} already exist in cache")

        if self.method_fetch is None:
            logging.info("No method to fetch")
            return None

        if obj is None and self.method_fetch is not None:
            logging.info(f"obj is None, attempting to fetch")
            obj = self.method_fetch(**kwargs)
            
        if obj is None:
            return None
        
        if self.method_save is None:
            logging.info("No method to save")
            return obj

        path = os.path.join(self.PATH, key)
        if self.GLOBAL_EXTENSION is not None:
            path += f".{self.GLOBAL_EXTENSION}"

        self.method_save(obj=obj, path=path, **kwargs)

        self._counting_index_action(key)
        self._place_cache(key, obj)
        return obj


    def load(self, key : str, **kwargs):
        key = str(key)
        if (cache:=self._get_from_cache(key)) is not None:
            self._place_cache(key, cache)
            return cache

        if key not in self._counting_index:
            logging.info(f"{key} not in index")
            return None

        if self.method_load is None:
            logging.info("No method to load")
            return None

        file_path = os.path.join(self.PATH, f"{key}")
        if self.GLOBAL_EXTENSION is not None:
            file_path += "."
            file_path += self.GLOBAL_EXTENSION

        obj = self.method_load(path=file_path,**kwargs)
        if obj is None:
            logging.info(f"{key} load returned None")
            return None

        self._counting_index_action(key)
        self._place_cache(key, obj)
        return obj

    def get_path(self, key : str):
        path=  os.path.join(self.PATH, key)
        if self.GLOBAL_EXTENSION is not None:
            path += f".{self.GLOBAL_EXTENSION}"
        return path

    def remove_folder(self):
        if os.path.exists(self.PATH):
            os.rmdir(self.PATH)
    
    @staticmethod
    def make_pilimage_cache(path : str, create_if_null : bool = True, extension : str =None) -> 'FolderCacher':
        cache = FolderCacher(path, create_if_null, extension)
        cache.method_load = lambda **kwargs: PIL.Image.open(kwargs['path'])
        cache.method_save = lambda **kwargs: kwargs['obj'].save(kwargs['path'])
        return cache

    @staticmethod
    def make_webimg_cache(path : str, create_if_null : bool = True, extension : str ='png') -> 'FolderCacher':
        cache = FolderCacher(path, create_if_null, extension)
        cache.method_load = load_web_img
        cache.method_save = save_web_img
        cache.method_fetch = fetch_web_img

        return cache