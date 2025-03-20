from typing import Literal

from pydantic import BaseModel, Field


class iot_turn_on(BaseModel):
    action: Literal["device", "group"] = Field(
        ...,
        description="device when control a single device, group when control all devices",
    )
    id: Literal["0", "2", "4", "6", "5"] = Field(
        ...,
        description="0 is for all, 2 is living room, 4 is kitchen, 5 is bedroom, 6 is wash room",
    )
    on: bool | None = Field(..., description="Whether to turn on the iot device")
    brightness: int | None = Field(
        ..., description="Brightness of the lamp, from 0 to 100"
    )
