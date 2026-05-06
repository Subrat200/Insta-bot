import json
import os

class Database:
    def __init__(self):
        self.file = "data.json"
        if not os.path.exists(self.file):
            self._save({})

    def _load(self):
        with open(self.file, "r") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.file, "w") as f:
            json.dump(data, f)

    def add_user(self, user_id, name):
        data = self._load()
        data[str(user_id)] = {"name": name}
        self._save(data)
