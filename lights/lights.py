from datetime import datetime
import requests
import json
from ..credentials import PHUE


class Light:
    HEADERS = {"Content-Type": 'application/json',
               "hue-application-key": PHUE.USERNAME.value}

    def __init__(self, id: int):
        self.id = id

    def set_light(self, on: str):
        raw = f'{{"on":{{"on": {on}}}}}'
        file = open("./tokens.json", "r")
        tokens = json.loads(file.read())
        self.HEADERS['Authorization'] = f"Bearer {tokens['access_token']}"
        response = requests.put(
            f"{PHUE.LIGHT_URL.value}/{self.id}",
            headers=self.HEADERS,
            data=raw
        )
        return response.json()
