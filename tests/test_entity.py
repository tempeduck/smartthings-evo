"""Tests for entity updates driven by the REST coordinator."""

from __future__ import annotations

from dataclasses import dataclass
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock

from pysmartthings import Attribute, Capability, Command
from pysmartthings.models import HealthStatus
import pytest

from conftest import PACKAGE, load_component_module


class FakeEntity:
    """Minimal Home Assistant Entity implementation."""

    def __init__(self):
        self.hass = object()
        self._remove_callbacks = []
        self.write_count = 0

    async def async_added_to_hass(self):
        return None

    def async_on_remove(self, callback):
        self._remove_callbacks.append(callback)

    def async_write_ha_state(self):
        self.write_count += 1

    @property
    def available(self):
        return self._attr_available


class DeviceInfo(dict):
    """DeviceInfo mapping stand-in."""


@dataclass
class FakeFullDevice:
    """Runtime device data shared with entities."""

    device: object
    status: dict
    online: bool


@pytest.fixture
def entity_module(monkeypatch):
    """Load the entity module with lightweight Home Assistant stand-ins."""
    connected = {}

    core = ModuleType("homeassistant.core")
    core.callback = lambda function: function
    device_registry = ModuleType("homeassistant.helpers.device_registry")
    device_registry.DeviceInfo = DeviceInfo
    dispatcher = ModuleType("homeassistant.helpers.dispatcher")

    def connect(hass, signal, callback):
        connected[signal] = callback
        return lambda: connected.pop(signal, None)

    dispatcher.async_dispatcher_connect = connect
    entity = ModuleType("homeassistant.helpers.entity")
    entity.Entity = FakeEntity

    monkeypatch.setitem(sys.modules, "homeassistant", ModuleType("homeassistant"))
    monkeypatch.setitem(sys.modules, "homeassistant.core", core)
    monkeypatch.setitem(
        sys.modules, "homeassistant.helpers", ModuleType("homeassistant.helpers")
    )
    monkeypatch.setitem(
        sys.modules, "homeassistant.helpers.device_registry", device_registry
    )
    monkeypatch.setitem(sys.modules, "homeassistant.helpers.dispatcher", dispatcher)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers.entity", entity)

    package = sys.modules[PACKAGE]
    package.FullDevice = FakeFullDevice
    constants = ModuleType(f"{PACKAGE}.const")
    constants.DOMAIN = "smartthings"
    constants.MAIN = "main"
    constants.SIGNAL_SMARTTHINGS_UPDATE = "smartthings_update_{}"
    monkeypatch.setitem(sys.modules, f"{PACKAGE}.const", constants)

    module = load_component_module("entity")
    module._test_connected = connected
    return module


def _attribute(value, data=None):
    return SimpleNamespace(value=value, data=data)


def _status(value):
    return {
        "main": {
            Capability.SWITCH: {
                Attribute.SWITCH: _attribute(value),
            }
        }
    }


def _full_device(value="off", online=True):
    return FakeFullDevice(
        device=SimpleNamespace(device_id="device-1"),
        status=_status(value),
        online=online,
    )


@pytest.mark.asyncio
async def test_entity_subscribes_and_rebuilds_state(entity_module):
    full = _full_device()
    client = SimpleNamespace(execute_device_command=AsyncMock())
    entity = entity_module.SmartThingsEntity(
        client, full, {Capability.SWITCH}
    )
    entity.hass = object()
    entity.write_count = 0
    entity._remove_callbacks = []

    await entity.async_added_to_hass()
    full.status = _status("on")
    full.online = False
    entity_module._test_connected["smartthings_update_device-1"]()

    assert entity.get_attribute_value(Capability.SWITCH, Attribute.SWITCH) == "on"
    assert entity.available is False
    assert entity.write_count == 1
    assert len(entity._remove_callbacks) == 1


@pytest.mark.asyncio
async def test_entity_executes_command_for_its_component(entity_module):
    full = _full_device()
    client = SimpleNamespace(execute_device_command=AsyncMock())
    entity = entity_module.SmartThingsEntity(
        client, full, {Capability.SWITCH}, component="main"
    )

    await entity.execute_device_command(
        Capability.SWITCH, Command.ON, argument=["value"]
    )

    client.execute_device_command.assert_awaited_once_with(
        "device-1",
        Capability.SWITCH,
        Command.ON,
        "main",
        argument=["value"],
    )


def test_entity_availability_event_updates_state(entity_module):
    entity = entity_module.SmartThingsEntity(
        SimpleNamespace(), _full_device(), {Capability.SWITCH}
    )
    entity.write_count = 0

    entity._availability_handler(
        SimpleNamespace(status=HealthStatus.OFFLINE)
    )

    assert entity.available is False
    assert entity.write_count == 1
