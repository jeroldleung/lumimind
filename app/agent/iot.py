import json
from typing import Any, Dict

import requests
from websockets.asyncio.server import ServerConnection


class IOTProvider:
    def __init__(self, url: str):
        self.url = url
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Host": "smart-api.chinafsl.com",
            "Connection": "keep-alive",
        }

    async def iot_control_lamp(self, websocket: ServerConnection, args: Dict[str, Any]) -> str:
        data = {
            "action": args["action"],
            "gatewayId": "e816564f9315",
            "param": {
                "id": args["id"],
                "config": [{"CF_OnOff": args["on"], "CF_Bright": args["bright"]}],
            },
        }
        res = requests.post(
            self.url,
            headers=self.headers,
            data=json.dumps(data),
        )
        return res.text

    async def iot_set_volume(self, websocket: ServerConnection, args: Dict[str, Any]) -> str:
        m_out = {
            "type": "iot",
            "commands": [
                {
                    "name": "Speaker",
                    "method": "SetVolume",
                    "parameters": {"volume": args["volume"]},
                }
            ],
        }
        await websocket.send(json.dumps(m_out))
        return "success"
