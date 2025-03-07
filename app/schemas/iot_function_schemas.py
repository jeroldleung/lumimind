from pydantic import BaseModel, Field


class iot_turn_on(BaseModel):
    on: bool = Field(..., description="Whether to turn on the iot device")
