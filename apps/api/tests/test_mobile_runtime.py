import pytest

from app.mobile import FakeMobileExecutionAdapter, MobileAction, MobileRuntimeError


def test_fake_adapter_observations_are_deterministic_and_ordered():
    runtime = FakeMobileExecutionAdapter()
    device = runtime.create_device()
    session = runtime.start_session(device.id, owner="agent-a")

    first = runtime.observe(session.id)
    second = runtime.observe(session.id)

    assert first.id == "device-0001-obs-0001"
    assert second.id == "device-0001-obs-0002"
    assert first.sequence == 1
    assert second.sequence == 2
    assert first.elements[0].index == 1
    assert first.elements[0].text == "Settings"


def test_device_lease_serializes_agent_control():
    runtime = FakeMobileExecutionAdapter()
    device = runtime.create_device()
    session = runtime.start_session(device.id, owner="agent-a")

    with pytest.raises(MobileRuntimeError, match="already leased"):
        runtime.start_session(device.id, owner="agent-b")

    runtime.end_session(session.id, park=True)
    next_session = runtime.start_session(device.id, owner="agent-b")
    assert next_session.lease_owner == "agent-b"


def test_park_and_resume_preserve_device_state():
    runtime = FakeMobileExecutionAdapter()
    device = runtime.create_device()
    session = runtime.start_session(device.id, owner="agent-a")

    runtime.execute(
        session.id,
        MobileAction(kind="launch_app", package="com.example.notes"),
    )
    runtime.set_app_data(device.id, "login", "authenticated")
    parked = runtime.end_session(session.id, park=True)

    assert parked.state == "parked"
    assert parked.app_data["foreground_package"] == "com.example.notes"
    assert parked.app_data["login"] == "authenticated"

    resumed = runtime.start_session(device.id, owner="agent-b")
    restored = runtime.get_device(device.id)
    assert restored.state == "active"
    assert restored.app_data["foreground_package"] == "com.example.notes"
    assert restored.app_data["login"] == "authenticated"
    assert resumed.lease_owner == "agent-b"


def test_human_takeover_blocks_agent_actions_then_hands_control_back():
    runtime = FakeMobileExecutionAdapter()
    device = runtime.create_device()
    session = runtime.start_session(device.id, owner="agent-a")

    takeover = runtime.begin_human_takeover(session.id)
    assert takeover.control_mode == "human"
    assert runtime.get_device(device.id).state == "human_control"

    with pytest.raises(MobileRuntimeError, match="blocked during human takeover"):
        runtime.observe(session.id)

    with pytest.raises(MobileRuntimeError, match="blocked during human takeover"):
        runtime.execute(session.id, MobileAction(kind="tap", coordinates=(10, 10)))

    returned = runtime.finish_human_takeover(session.id)
    assert returned.control_mode == "agent"
    observation = runtime.observe(session.id)
    assert observation.sequence == 1


def test_privileged_install_requires_explicit_authorization():
    runtime = FakeMobileExecutionAdapter()
    device = runtime.create_device()
    session = runtime.start_session(device.id, owner="agent-a")

    action = MobileAction(kind="install_app", package="com.example.app")
    with pytest.raises(MobileRuntimeError, match="explicit authorization"):
        runtime.execute(session.id, action)

    result = runtime.execute(
        session.id,
        action.model_copy(update={"authorized": True}),
    )
    assert result == {"status": "ok", "installed": "com.example.app"}
    assert runtime.get_device(device.id).installed_apps == ["com.example.app"]
