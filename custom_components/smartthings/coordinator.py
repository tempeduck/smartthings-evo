"""REST polling coordinator for SmartThings.

The Samsung-account (OSP) token has no ``installed_app_id`` / ``sse`` scope, so the realtime
websocket subscription isn't available. Instead we poll each device's status on an interval
and device health less frequently, update the shared ``FullDevice`` objects in place, and
notify entities via a per-device dispatcher signal (entities keep the references they were
built with, so no coordinator plumbing is needed in the ~18 platform files).
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
import logging
import time
from typing import TYPE_CHECKING

from pysmartthings import (
    Category,
    ComponentStatus,
    SmartThings,
    SmartThingsAuthenticationFailedError,
    SmartThingsConnectionError,
)
from pysmartthings.models import HealthStatus

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    HEALTH_SCAN_INTERVAL,
    MAIN,
    SIGNAL_SMARTTHINGS_UPDATE,
)

if TYPE_CHECKING:
    from . import FullDevice, SmartThingsConfigEntry

_LOGGER = logging.getLogger(__name__)


class SmartThingsCoordinator(DataUpdateCoordinator[dict[str, "FullDevice"]]):
    """Polls SmartThings device status/health over REST and updates entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: SmartThingsConfigEntry,
        client: SmartThings,
        devices: dict[str, FullDevice],
        process_status: Callable[[dict[str, ComponentStatus]], dict[str, ComponentStatus]],
    ) -> None:
        """Initialise the coordinator with the already-discovered devices."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client
        self.devices = devices
        self._process_status = process_status
        self._last_health_check: dict[str, float] = {}
        # We already have the initial status from setup; seed it so the first scheduled poll
        # is a refresh, not a cold start.
        self.data = devices

    async def _async_update_data(self) -> dict[str, FullDevice]:
        """Refresh status + health for every known device, in place."""
        started = time.monotonic()
        requests = 0
        failed_devices = 0
        trackers_skipped = 0

        try:
            for device_id, full in self.devices.items():
                main = full.device.components.get(MAIN)
                is_tracker = (
                    main is not None
                    and main.manufacturer_category is Category.BLUETOOTH_TRACKER
                )
                try:
                    if is_tracker:
                        # Trackers expose no queryable status; treat as online (matches setup).
                        full.online = True
                        trackers_skipped += 1
                    else:
                        requests += 1
                        full.status = self._process_status(
                            await self.client.get_device_status(device_id)
                        )
                        now = time.monotonic()
                        last_health_check = self._last_health_check.get(device_id)
                        if (
                            last_health_check is None
                            or now - last_health_check >= HEALTH_SCAN_INTERVAL
                        ):
                            requests += 1
                            health = await self.client.get_device_health(device_id)
                            self._last_health_check[device_id] = now
                            full.online = health.state == HealthStatus.ONLINE
                except SmartThingsAuthenticationFailedError as err:
                    failed_devices += 1
                    raise ConfigEntryAuthFailed from err
                except SmartThingsConnectionError as err:
                    failed_devices += 1
                    raise UpdateFailed(err) from err

                async_dispatcher_send(
                    self.hass, SIGNAL_SMARTTHINGS_UPDATE.format(device_id)
                )
            return self.devices
        finally:
            _LOGGER.debug(
                "SmartThings poll completed: %d device(s), %d request(s), "
                "%.2f seconds, %d failed device(s), %d tracker(s) skipped",
                len(self.devices),
                requests,
                time.monotonic() - started,
                failed_devices,
                trackers_skipped,
            )
