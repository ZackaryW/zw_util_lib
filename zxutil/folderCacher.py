
import os
import shutil
from PIL import Image
import json


# ANCHOR load methods
def load_json(file_path : str, **kwargs) -> str:
    with open(file_path, "r") as file:
        return json.load(file)

def load_file(file_path : str, **kwargs) -> str:
    with open(file_path, "r") as file:
        return file.readlines()

def load_image(file_path : str, **kwargs) -> str:
    return Image.open(file_path)

def save_file(raw, file_path : str, **kwargs):
    with open(file_path, "w") as file:
        file.write(raw)

def save_image(raw, file_path : str, **kwargs):
    raw : Image
    raw.save(file_path)

def save_json(raw, file_path : str, **kwargs):
    with open(file_path, "w") as file:
        json.dump(raw, file)

class FolderCacher:
    """
    a very primitive way to cache files

    """
    def __init__(self, path : str, create: bool = False) -> None:
        if create and not os.path.exists(path):
            os.mkdir(path)

        if not os.path.exists(path):
            raise FileNotFoundError(path)

        self.most_frequent_files = {} 
        self.minimum_needed_to_cache = 10
        self.maximum_cache_size = 30
        self.holding_queue = {}
        self.holding_queue_size = 5
        self.file_load_method = load_file
        self.file_save_method = save_file

        self.count_index = {}
        self.path = path
        # walk path
        files = os.listdir(path)
        for file in files:
            self.count_index[file] = 0, os.path.join(path, file)


    def __contains__(self, file_name : str) -> bool:
        return file_name in self.count_index
    
    def _trigger_count(self, file_name : str, save :bool = False) -> None:
        if save and file_name not in self.count_index:
            self.count_index[file_name] = list([0, None])

        elif file_name not in self.count_index:
            return
        self.count_index[file_name][0] += 1
    
    def _get_holding_queue(self, file_name : str) -> str:
        if file_name not in self.holding_queue:
            return None
        return self.holding_queue[file_name]

    def _get_frequenct(self, file_name : str) -> int:
        if file_name not in self.count_index:
            return None
        return self.most_frequent_files[file_name]

    def _place_holding_queue(self, item, file_name : str):
        while len(self.holding_queue) >= self.holding_queue_size:
            # pop first 
            key = self.holding_queue.popitem()
        self.holding_queue[file_name] = item
    
    def _handle_frequent_files(self, loaded, file_name :str):
        if self.count_index[file_name][0] < self.minimum_needed_to_cache:
            return
        
        if len(self.most_frequent_files) < self.maximum_cache_size:
            self.most_frequent_files[file_name] = loaded
            return


        current_min_key = file_name
        current_min_count = self.count_index[file_name][0]
        for k, v in self.most_frequent_files:
            if self.count_index[k][0] < current_min_count:
                current_min_key = k
                current_min_count = self.count_index[k][0]
            
        if current_min_key == file_name:
            return
        
        self.most_frequent_files[file_name] = loaded
        del self.most_frequent_files[current_min_key]


    def load(self, file_name : str, **kwargs):
        file_name = str(file_name)
        self._trigger_count(file_name)
        if (holding:= self._get_holding_queue(file_name)) is not None:
            return holding
        if (item := self._get_frequenct(file_name)) is not None:
            return item  

        file_path = self.count_index[file_name][1]
        loaded = self.file_load_method(file_path, **kwargs)
        self._place_holding_queue(loaded, file_name)
        self._handle_frequent_files(loaded, file_name)

        return loaded
        

    def save(self, raw, file_name : str, extension : str=None, overwrite : bool = False,**kwargs):
        file_name = str(file_name)
        self._trigger_count(file_name, save=True)
        complete_save_path = os.path.join(self.path, file_name)
        if extension is not None:
            complete_save_path = complete_save_path + "." + extension
        self._place_holding_queue(raw, file_name, **kwargs)
        if os.path.exists(complete_save_path) and not overwrite:
            return
        self.count_index[file_name][1] = complete_save_path
        self.file_save_method(raw, complete_save_path)

    def remove_path(self):
        shutil.rmtree(self.path)


    
    # ANCHOR class

    @classmethod
    def image_cacher(cls, path : str, create :bool = False) -> 'FolderCacher':
        cacher = FolderCacher(path, create)
        cacher.file_load_method = load_image
        cacher.file_save_method = save_image
        return cacher

