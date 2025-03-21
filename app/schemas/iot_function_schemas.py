from typing import Literal

from pydantic import BaseModel, Field


class iot_control_lamp(BaseModel):
    action: Literal["device", "group"] = Field(
        ...,
        description="""
        device for control a single device,
        group for control all devices""",
    )
    id: Literal["0", "2", "4", "6", "5"] = Field(
        ...,
        description="""
        0 is for all,
        2 is living room,
        4 is kitchen,
        5 is bedroom,
        6 is wash room""",
    )
    on: bool | None = Field(..., description="Whether to turn on the device")
    bright: int | None = Field(..., description="Brightness of the lamp, from 0 to 100")


class iot_set_volume(BaseModel):
    volume: int = Field(..., description="Your speaking volume, from 0 to 100")
