from typing import Generator, List, Tuple

from openai.types.chat import ChatCompletionChunk


def accumulate_streaming(stream: List[ChatCompletionChunk]) -> Tuple[str, List]:
    text_res, final_tool_calls = "", {}
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            text_res += chunk.choices[0].delta.content
        for tool_call in chunk.choices[0].delta.tool_calls or []:
            index = tool_call.index
            if index not in final_tool_calls:
                final_tool_calls[index] = tool_call
                continue
            args = tool_call.function.arguments
            if args is not None:
                final_tool_calls[index].function.arguments += args
    return text_res, list(final_tool_calls.values())


def stream_content(content: str) -> Generator[str, None, None]:
    for w in content.split():
        yield w
