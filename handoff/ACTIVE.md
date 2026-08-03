# Active Handoff

The full readiness assessment and test roadmap is in
`handoff/READINESS_ROADMAP.md`.
The reviewed live-system preflight and rollback plan is in
`handoff/LIVE_INSTALL_PLAN.md`.

## Current state

- Forked `crash0verride11/smartthings-evo` to
  `tempeduck/smartthings-evo`.
- Cloned the fork at `~/projects/smartthings-evo`.
- `origin` points to the personal fork and `upstream` points to the original.
- Local `main` matches upstream commit `16548af` before workspace scaffolding.
- Added workspace guidance, project context, tests, and validation handoffs.
  Local changes have been committed but not pushed.
- Completed the initial non-live automated test foundation. The repository now
  has isolated pytest coverage for Samsung authentication/token management,
  configuration-flow state transitions, REST polling, and base entity update
  and command behavior, plus a GitHub Actions test workflow.
- Callback validation now rejects missing or mismatched Samsung callback state,
  and token refreshes are serialized to prevent duplicate concurrent refresh
  requests.

## Validation

- Python compilation completed successfully with `python3 -m compileall`.
- Integration, translation, extension, and HACS manifest JSON parsed
  successfully.
- Current hassfest completed with 1 valid integration and 0 invalid
  integrations. Its only warning is expected for this project: the
  `smartthings` domain collides with Home Assistant's built-in integration.
- Review on 2026-07-30 confirmed `origin/main`, `upstream/main`, and local
  `main` all point to `16548af` with zero fork divergence.
- The upstream HACS and hassfest GitHub Actions are passing on `16548af`;
  the personal fork has no Actions runs because workflows have not been
  enabled/run there.
- Static review of `pysmartthings==4.0.1` confirmed its
  `refresh_token_function` callback is invoked before API requests and accepts
  the access-token string returned by `SamsungTokenManager`.
- The isolated unit suite passes: 32 tests.
- The HACS GitHub Action has not been run against the unpushed local
  scaffolding.
- Disposable end-to-end validation has now exercised a real Samsung login and
  live SmartThings API access without changing production Home Assistant.
- A disposable Home Assistant Core `2026.7.4` container is running on the
  development VM as `smartthings-evo-ha-20260730`, bound to the development
  VM's LAN address at `10.10.1.19:18123`. Its isolated configuration is under
  `/tmp/smartthings-evo-ha-20260730/config`; it contains a copy of the current
  custom integration and no production config, tokens, entries, or devices.
- The disposable instance reached onboarding and recognized the custom
  `smartthings` integration without import, manifest, or dependency errors.
  The only integration-related log message was Home Assistant's standard
  warning that a custom integration is not tested by Home Assistant.
- Disposable-runtime config-flow validation passed: after isolated onboarding,
  Home Assistant Core `2026.7.4` exposed the custom integration through its real
  config-flow API and returned the expected `pick_method` menu with automatic
  and manual Samsung authentication choices.
- Disposable-runtime migration validation passed using synthetic data: a
  SmartThings version-3/minor-3 entry was migrated to minor version 4, its
  synthetic incompatible legacy token was removed, and Home Assistant moved
  the entry to an authentication-required setup error. No production entry or
  token was copied.
- Disposable end-to-end manual authentication passed on 2026-08-03 using
  Chrome with the unpacked extension: Samsung login, callback capture, manual
  callback submission, token exchange, config-entry creation, and location and
  device discovery all succeeded. Callback and token values were never placed
  in the repository or chat.
- The disposable SmartThings entry loaded successfully and registered 69
  enabled entities across binary sensor, button, light, media player, number,
  select, sensor, and switch platforms. The expected devices were present.
- Inbound REST polling was demonstrated by turning on a low-risk oven light in
  SmartThings and observing Home Assistant update to `on` within the polling
  path. Outbound command execution was demonstrated by turning the same light
  off in Home Assistant and confirming it turned off physically.
- No authentication, command, connection, polling, or rate-limit errors were
  logged. `pysmartthings` emitted nonfatal warnings for several unknown private
  Samsung capability names.
- Disposable config-entry reload passed without requiring a Home Assistant
  restart. The entry returned to `loaded` with no integration errors.
- Disposable container restart persistence passed: Home Assistant returned to
  `RUNNING`, the stored Samsung-authenticated SmartThings entry loaded without
  reauthentication, and all 69 registered entities remained present.
- Forced token-refresh validation passed in the disposable instance: after
  changing only the stored access-token expiry timestamp to expired and
  restarting, both access and refresh tokens rotated, a fresh approximately
  24-hour access lifetime was persisted, and the entry loaded without 2FA or
  interactive reauthentication. Token values were not output or recorded.
- Phase A live-system discovery was completed read-only on 2026-07-30:
  Home Assistant OS is running Core `2026.7.4`, HACS is loaded, and a protected
  automatic backup includes Home Assistant configuration.
- One enabled built-in SmartThings entry (`Home`, source DHCP) exists at version
  3/minor version 3. Installing this same-domain custom integration will replace
  the code loading that entry; its minor-version-4 migration deliberately drops
  the incompatible old token and forces Samsung-account reauthentication.

## Open work

1. Add deeper setup-entry and platform-specific entity tests as defects or
   compatibility work identify high-value cases.
2. Continue longer-running polling stability observation in the disposable
   instance.
3. Review and approve backup creation and the exact installation/migration
   actions before changing the live Home Assistant instance.
4. Exercise automatic authentication and capture sanitized failure details if
   the known callback-tab HTTP 500 appears.

## Risks

- The project depends on undocumented Samsung mobile authentication behavior.
- OAuth callbacks and token data are secrets and must not be copied into this
  file, issues, commits, or chat.
- Polling replaces push updates, and button events are not available through
  the polling path.
- Manual authentication, discovery, commands, polling, config-entry reload,
  restart persistence, and forced token refresh are verified in the disposable
  environment. Multi-day stability remains unverified.
- Installation will migrate the existing same-domain built-in SmartThings entry
  and force reauthentication; it is not an independent coexistence test.
- Production installation and authentication have not been performed.
- The disposable container is temporary and exposed to the home LAN. Remove the
  `smartthings-evo-ha-20260730` container and its explicit `/tmp` directory when
  testing is complete.
