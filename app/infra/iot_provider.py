import json

import requests


class IOTProvider:
    def __init__(self, url: str):
        self.url = url

    def iot_turn_on(self, on: bool) -> str:
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Host": "smart-api.chinafsl.com",
            "Connection": "keep-alive",
        }
        data = {
            "action": "device",
            "gatewayId": "e816564f9315",
            "param": {"id": "2", "config": [{"CF_OnOff": on}]},
        }
        res = requests.get(
            self.url,
            headers=headers,
            data=json.dumps(data),
        )
        return res.text
