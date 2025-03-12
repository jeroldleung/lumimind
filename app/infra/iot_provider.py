import json
from typing import Any, Dict

import requests


class IOTProvider:
    def __init__(self, url: str):
        self.url = url

    def iot_turn_on(self, args: Dict[str, Any]) -> str:
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Host": "smart-api.chinafsl.com",
            "Connection": "keep-alive",
        }
        data = {
            "action": "device",
            "gatewayId": "e816564f9315",
            "param": {"id": "2", "config": [{"CF_OnOff": args["on"]}]},
        }
        res = requests.get(
            self.url,
            headers=headers,
            data=json.dumps(data),
        )
        return res.text
