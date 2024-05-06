import requests
from ..credentials import GOVEE


class Heater:
    HEADERS = {"Content-Type": 'application/json',
               "Govee-API-Key": GOVEE.GOVEE_API_KEY.value}

    def set_heater(self, on: str):
        raw = f'{{"device": "{GOVEE.HEATER_MAC_ADDRESS.value}", "model": "H7131", "cmd": {{"name": "turn", "value": "{"on" if on == "true" else "off"}"}}}}'
        print(raw)
        response = requests.put(GOVEE.URL.value,
                                headers=self.HEADERS,
                                data=raw
                                )
        return response.json()
