from pydantic import BaseModel, Field


class iot_turn_on(BaseModel):
    on: bool = Field(..., description="Whether to turn on the iot device")
    brightness: int = Field(..., description="Brightness of the lamp, from 0 to 100")
