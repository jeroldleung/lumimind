import json
from typing import Any, Dict

import requests
from loguru import logger


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
            "action": args["action"],
            "gatewayId": "e816564f9315",
            "param": {
                "id": args["id"],
                "config": [{"CF_OnOff": args["on"], "CF_Bright": args["brightness"]}],
            },
        }
        logger.debug(data)
        res = requests.post(
            self.url,
            headers=headers,
            data=json.dumps(data),
        )
        return res.text
