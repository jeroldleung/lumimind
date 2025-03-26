import json
from typing import List

from loguru import logger
from openai.types.chat import ChatCompletionMessageToolCall
from websockets.asyncio.server import ServerConnection

from app.infra.iot_provider import IOTProvider
from app.infra.llm_provider import LLMProvider
from app.schemas import iot_function_schemas as iotfs


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

    async def recur_tool_call(
        self,
        websocket: ServerConnection,
        tool_calls: List[ChatCompletionMessageToolCall],
    ) -> str:
        self.messages.append({"role": "assistant", "tool_calls": tool_calls})
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

        complete = self.llm_client.chat_completion(messages=self.messages)
        if complete.choices[0].message.content:
            return complete.choices[0].message.content
        else:
            return await self.recur_tool_call(websocket, complete.choices[0].message.tool_calls)

    async def chat_completion(self, websocket: ServerConnection, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        res_msg = self.llm_client.chat_completion(self.messages)
        content = res_msg.choices[0].message.content
        tool_calls = res_msg.choices[0].message.tool_calls

        # calling tools
        if tool_calls:
            complete_content = await self.recur_tool_call(websocket, tool_calls)
            self.messages.append({"role": "assistant", "content": complete_content})
            return complete_content

        self.messages.append({"role": "assistant", "content": content})
        return content
