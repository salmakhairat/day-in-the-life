import requests
import json
import os

class TenorClient():
    def __init__(self):
        self.api_key = "0QVQ7DLHDJHP"
        self.lmt = 1

    def search(self, search_term):
        r = requests.get("https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (search_term, self.api_key, self.lmt))
        if r.status_code == 200:
            result = json.loads(r.content)["results"]
            return result
        else:
            return None

    def get_url(self, info):
        info = str(info[0])
        info = info[info.find("'id':"):]
        info = info[:info.find(",")]
        info = info[7:]
        info = info[:-1]
        return info