import json


class Message:
    @staticmethod
    def build_hello(**args) -> str:
        msg = {"type": "hello", "transport": "websocket"}

        if "sample_rate" in args:
            msg["sample_rate"] = args["sample_rate"]

        return json.dumps(msg)

    @staticmethod
    def build_tts(**args) -> str:
        msg = {"type": "tts"}

        if "state" in args:
            msg["state"] = args["state"]
        if "text" in args:
            msg["text"] = args["text"]

        return json.dumps(msg)
