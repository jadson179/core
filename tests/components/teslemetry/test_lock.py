"""Test the Teslemetry lock platform."""

from unittest.mock import patch

import pytest
from syrupy.assertion import SnapshotAssertion

from homeassistant.components.lock import (
    DOMAIN as LOCK_DOMAIN,
    SERVICE_LOCK,
    SERVICE_UNLOCK,
    LockState,
)
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er

from . import assert_entities, setup_platform
from .const import COMMAND_OK


async def test_lock(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
) -> None:
    """Tests that the lock entities are correct."""

    entry = await setup_platform(hass, [Platform.LOCK])
    assert_entities(hass, entry.entry_id, entity_registry, snapshot)


async def test_lock_services(
    hass: HomeAssistant,
) -> None:
    """Tests that the lock services work."""

    await setup_platform(hass, [Platform.LOCK])

    entity_id = "lock.test_lock"

    with patch(
        "homeassistant.components.teslemetry.VehicleSpecific.door_lock",
        return_value=COMMAND_OK,
    ) as call:
        await hass.services.async_call(
            LOCK_DOMAIN,
            SERVICE_LOCK,
            {ATTR_ENTITY_ID: entity_id},
            blocking=True,
        )
        state = hass.states.get(entity_id)
        assert state.state == LockState.LOCKED
        call.assert_called_once()

    with patch(
        "homeassistant.components.teslemetry.VehicleSpecific.door_unlock",
        return_value=COMMAND_OK,
    ) as call:
        await hass.services.async_call(
            LOCK_DOMAIN,
            SERVICE_UNLOCK,
            {ATTR_ENTITY_ID: entity_id},
            blocking=True,
        )
        state = hass.states.get(entity_id)
        assert state.state == LockState.UNLOCKED
        call.assert_called_once()

    entity_id = "lock.test_charge_cable_lock"

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            LOCK_DOMAIN,
            SERVICE_LOCK,
            {ATTR_ENTITY_ID: entity_id},
            blocking=True,
        )

    with patch(
        "homeassistant.components.teslemetry.VehicleSpecific.charge_port_door_open",
        return_value=COMMAND_OK,
    ) as call:
        await hass.services.async_call(
            LOCK_DOMAIN,
            SERVICE_UNLOCK,
            {ATTR_ENTITY_ID: entity_id},
            blocking=True,
        )
        state = hass.states.get(entity_id)
        assert state.state == LockState.UNLOCKED
        call.assert_called_once()
