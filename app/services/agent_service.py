import json

import app.schemas.iot_function_schemas as iotfs
from app.infra import IOTProvider, LLMProvider


class AgentService:
    def __init__(self, llm_client: LLMProvider, iot_client: IOTProvider):
        self.llm_client = llm_client
        self.iot_client = iot_client
        self.messages = [{"role": "system", "content": "You are a helpful assistant."}]

        # get all iot function schemas and registry to llm client
        ts = [getattr(iotfs, name) for name in dir(iotfs) if name.startswith("iot")]
        self.llm_client.registry_tools(ts)

    def chat_completion(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        msg = self.llm_client.chat_completion(self.messages)
        self.messages.append(msg)

        if len(msg.tool_calls) > 0:
            tool_call, function = msg.tool_calls[0], msg.tool_calls[0].function
            name, args = function.name, json.loads(function.arguments)
            iot_method = getattr(self.iot_client, name)
            result = iot_method(args)
            tool_msg = {"role": "tool", "tool_call_id": tool_call.id, "content": result}
            self.messages.append(tool_msg)
            complete_tool_call = self.llm_client.chat_completion(messages=self.messages)
            self.messages.append(complete_tool_call)
            return complete_tool_call.content

        return msg.content
