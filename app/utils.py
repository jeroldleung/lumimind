from .schemas import MessageFromClient, MessageToClient, MessageType


def message_to_client(msg: MessageToClient) -> str:
    if msg.type == MessageType.HELLO:
        return msg.model_dump_json(exclude_none=True)
    else:
        return msg.model_dump_json(exclude_none=True, exclude_defaults=True)


def message_from_client(msg: str) -> MessageFromClient:
    return MessageFromClient.model_validate_json(msg)
