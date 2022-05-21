# WARNING! NOT TESTED!!!

import json
import os

class Database:
	"""docstring for Database"""
	def __init__(self, file=db.csv):
		self.file = file
		self._data = []   # type: Dict[Tuple[str, Tuple[str, bool, Optional[int]]]]
		# format: Dict[url: (title, is_hrum, hrum_num)]
	
	def load(self):
		if not os.path.exists(self.file):
			self.save()
        with open(self.file) as f:
            self._data = json.load(f)

    def save(self):
    	with open(self.file, 'w') as f:
                json.dump(self._data, f)
    
    def update(self, url: str, title: str, is_hrum: bool, hrum_num=None):
    	self._data[url] = [url, title, hrum_num]

    def get(self, url: str):
    	return self._data.get(url)

    def get_hrums(self) -> Tuple[str, str, bool, int]:
    	for i in self._data:
            if self._data[i][1]:
            	yield [i, *data[i]]
    
    def find_hrum(self, issue: int):
    	for i in self.get_hrums():
             if i[3] == issue:
             	return i
