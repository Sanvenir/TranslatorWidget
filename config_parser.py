import json


class Configuration(object):
    def __init__(self, path="./config.json"):
        super().__init__()
        self.json = None
        with open(path, "r") as fin:
            self.json = json.load(fin)

    def __getattr__(self, item):
        return self.json.get(item)
