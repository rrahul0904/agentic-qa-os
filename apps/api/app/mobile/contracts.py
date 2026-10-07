from typing import Literal

from pydantic import BaseModel, Field


ControlMode = Literal["agent", "human"]
ActionKind = Literal[
    "tap",
    "type",
    "swipe",
    "launch_app",
    "key_event",
    "install_app",
]
DeviceState = Literal["stopped", "active", "parked", "human_control"]


class UIElement(BaseModel):
    index: int = Field(ge=0)
    role: str
    text: str | None = None
    bounds: tuple[int, int, int, int]


class MobileObservation(BaseModel):
    id: str
    device_id: str
    sequence: int = Field(ge=0)
    screenshot_ref: str
    elements: list[UIElement]


class MobileAction(BaseModel):
    kind: ActionKind
    element_index: int | None = Field(default=None, ge=0)
    text: str | None = None
    coordinates: tuple[int, int] | None = None
    swipe: tuple[int, int, int, int] | None = None
    package: str | None = None
    key: str | None = None
    artifact_ref: str | None = None
    authorized: bool = False


class MobileDevice(BaseModel):
    id: str
    state: DeviceState = "stopped"
    installed_apps: list[str] = []
    app_data: dict[str, str] = {}


class MobileSession(BaseModel):
    id: str
    device_id: str
    control_mode: ControlMode = "agent"
    lease_owner: str | None = None
    last_observation_id: str | None = None
