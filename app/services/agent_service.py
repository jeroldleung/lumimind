import json

from loguru import logger
from websockets.asyncio.server import ServerConnection

from ..infra import IOTProvider, LLMProvider
from ..schemas import iot_function_schemas as iotfs
from ..utils.stream import accumulate_streaming


class AgentService:
    def __init__(self, llm_client: LLMProvider, iot_client: IOTProvider):
        self.llm_client = llm_client
        self.iot_client = iot_client
        with open("assets/agent_prompt_text.txt") as f:
            system_prompt = f.read()
        self.messages = [{"role": "system", "content": system_prompt}]

        # get all iot function schemas and registry to llm client
        ts = [getattr(iotfs, name) for name in dir(iotfs) if name.startswith("iot")]
        self.llm_client.registry_tools(ts)

    async def chat_completion(
        self, websocket: ServerConnection, user_input: str
    ) -> str:
        self.messages.append({"role": "user", "content": user_input})
        stream_msg = self.llm_client.chat_completion(self.messages)
        content, tool_calls = accumulate_streaming(stream_msg)
        self.messages.append({"role": "assistant", "content": content})

        # calling tools
        if tool_calls:
            self.messages[-1]["tool_calls"] = tool_calls
            logger.debug(tool_calls)

            for t in tool_calls:
                tool_call, function = t, t.function
                name, args = function.name, json.loads(function.arguments)
                iot_method = getattr(self.iot_client, name)
                result = await iot_method(websocket, args)
                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                }
                self.messages.append(tool_msg)

            complete_stream = self.llm_client.chat_completion(messages=self.messages)
            complete_content, _ = accumulate_streaming(complete_stream)
            self.messages.append({"role": "assistant", "content": complete_content})
            return complete_content

        return content
