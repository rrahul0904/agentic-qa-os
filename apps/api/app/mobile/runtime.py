from __future__ import annotations

from dataclasses import dataclass

from .contracts import MobileAction, MobileDevice, MobileObservation, MobileSession, UIElement


class MobileRuntimeError(RuntimeError):
    pass


@dataclass(frozen=True)
class DeviceLease:
    device_id: str
    owner: str
    token: str


class DeviceLeaseManager:
    """In-memory lease primitive used to prove per-device serialization semantics."""

    def __init__(self) -> None:
        self._leases: dict[str, DeviceLease] = {}
        self._counter = 0

    def acquire(self, device_id: str, owner: str) -> DeviceLease:
        current = self._leases.get(device_id)
        if current is not None:
            raise MobileRuntimeError(
                f"device {device_id} is already leased by {current.owner}"
            )
        self._counter += 1
        lease = DeviceLease(
            device_id=device_id,
            owner=owner,
            token=f"lease-{self._counter:04d}",
        )
        self._leases[device_id] = lease
        return lease

    def release(self, token: str) -> None:
        for device_id, lease in list(self._leases.items()):
            if lease.token == token:
                del self._leases[device_id]
                return
        raise MobileRuntimeError("unknown lease token")

    def owner_for(self, device_id: str) -> str | None:
        lease = self._leases.get(device_id)
        return lease.owner if lease else None


class FakeMobileExecutionAdapter:
    """Deterministic, provider-neutral adapter for contract and lifecycle tests.

    This intentionally does not claim ADB, emulator, physical-device, or hosted-cloud
    support. It exists to lock down the behavior boundary before a real adapter is added.
    """

    def __init__(self) -> None:
        self.devices: dict[str, MobileDevice] = {}
        self.sessions: dict[str, MobileSession] = {}
        self.leases = DeviceLeaseManager()
        self._device_counter = 0
        self._session_counter = 0
        self._observation_counter: dict[str, int] = {}

    def create_device(self) -> MobileDevice:
        self._device_counter += 1
        device = MobileDevice(id=f"device-{self._device_counter:04d}")
        self.devices[device.id] = device
        return device.model_copy(deep=True)

    def start_session(self, device_id: str, owner: str) -> MobileSession:
        device = self._device(device_id)
        if device.state == "human_control":
            raise MobileRuntimeError("human takeover is active")
        if device.state == "parked":
            device.state = "active"
        elif device.state == "stopped":
            device.state = "active"

        lease = self.leases.acquire(device_id, owner)
        self._session_counter += 1
        session = MobileSession(
            id=f"session-{self._session_counter:04d}",
            device_id=device_id,
            control_mode="agent",
            lease_owner=lease.owner,
        )
        self.sessions[session.id] = session
        return session.model_copy(deep=True)

    def end_session(self, session_id: str, *, park: bool = True) -> MobileDevice:
        session = self._session(session_id)
        device = self._device(session.device_id)
        if session.control_mode != "agent":
            raise MobileRuntimeError("cannot end an agent session during human takeover")

        lease = self._lease_for_device(device.id)
        self.leases.release(lease.token)
        del self.sessions[session_id]
        device.state = "parked" if park else "stopped"
        return device.model_copy(deep=True)

    def observe(self, session_id: str) -> MobileObservation:
        session = self._agent_session(session_id)
        device = self._device(session.device_id)
        if device.state != "active":
            raise MobileRuntimeError(f"device is not active: {device.state}")

        sequence = self._observation_counter.get(device.id, 0) + 1
        self._observation_counter[device.id] = sequence
        observation = MobileObservation(
            id=f"{device.id}-obs-{sequence:04d}",
            device_id=device.id,
            sequence=sequence,
            screenshot_ref=f"memory://{device.id}/screens/{sequence:04d}.png",
            elements=[
                UIElement(
                    index=1,
                    role="button",
                    text="Settings",
                    bounds=(20, 40, 220, 120),
                ),
                UIElement(
                    index=2,
                    role="text",
                    text=f"state:{device.state}",
                    bounds=(20, 140, 420, 220),
                ),
            ],
        )
        session.last_observation_id = observation.id
        return observation

    def execute(self, session_id: str, action: MobileAction) -> dict[str, str]:
        session = self._agent_session(session_id)
        device = self._device(session.device_id)
        if device.state != "active":
            raise MobileRuntimeError(f"device is not active: {device.state}")

        if action.kind == "install_app":
            if not action.authorized:
                raise MobileRuntimeError("install_app requires explicit authorization")
            if not action.package:
                raise MobileRuntimeError("install_app requires package")
            if action.package not in device.installed_apps:
                device.installed_apps.append(action.package)
            return {"status": "ok", "installed": action.package}

        if action.kind == "launch_app":
            if not action.package:
                raise MobileRuntimeError("launch_app requires package")
            device.app_data["foreground_package"] = action.package
            return {"status": "ok", "foreground_package": action.package}

        if action.kind == "type" and action.text is not None:
            device.app_data["last_typed_text"] = action.text

        return {"status": "ok", "action": action.kind}

    def begin_human_takeover(self, session_id: str) -> MobileSession:
        session = self._session(session_id)
        device = self._device(session.device_id)
        if device.state != "active" or session.control_mode != "agent":
            raise MobileRuntimeError("device is not available for human takeover")
        session.control_mode = "human"
        device.state = "human_control"
        return session.model_copy(deep=True)

    def finish_human_takeover(self, session_id: str) -> MobileSession:
        session = self._session(session_id)
        device = self._device(session.device_id)
        if session.control_mode != "human" or device.state != "human_control":
            raise MobileRuntimeError("human takeover is not active")
        session.control_mode = "agent"
        device.state = "active"
        return session.model_copy(deep=True)

    def set_app_data(self, device_id: str, key: str, value: str) -> None:
        self._device(device_id).app_data[key] = value

    def get_device(self, device_id: str) -> MobileDevice:
        return self._device(device_id).model_copy(deep=True)

    def _device(self, device_id: str) -> MobileDevice:
        try:
            return self.devices[device_id]
        except KeyError as exc:
            raise MobileRuntimeError(f"unknown device {device_id}") from exc

    def _session(self, session_id: str) -> MobileSession:
        try:
            return self.sessions[session_id]
        except KeyError as exc:
            raise MobileRuntimeError(f"unknown session {session_id}") from exc

    def _agent_session(self, session_id: str) -> MobileSession:
        session = self._session(session_id)
        if session.control_mode != "agent":
            raise MobileRuntimeError("agent actions are blocked during human takeover")
        return session

    def _lease_for_device(self, device_id: str) -> DeviceLease:
        for lease in self.leases._leases.values():
            if lease.device_id == device_id:
                return lease
        raise MobileRuntimeError(f"device {device_id} has no active lease")
