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
- Added workspace guidance and project context; nothing has been committed or
  pushed.
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
- No Home Assistant installation, Samsung login, browser-extension load, or
  live API test has been performed.

## Open work

1. Add deeper setup-entry and platform-specific entity tests as defects or
   compatibility work identify high-value cases.
2. Obtain approval for Phase A of `handoff/LIVE_INSTALL_PLAN.md`, then confirm
   Robert's Home Assistant version meets the declared `2026.6.0` minimum and
   identify the installation/backup mechanisms.
3. Resolve the exact installation and rollback actions before touching the
   live Home Assistant instance.
4. Load the unpacked extension and test manual authentication first.
5. Exercise automatic authentication and capture sanitized failure details if
   the known callback-tab HTTP 500 appears.

## Risks

- The project depends on undocumented Samsung mobile authentication behavior.
- OAuth callbacks and token data are secrets and must not be copied into this
  file, issues, commits, or chat.
- Polling replaces push updates, and button events are not available through
  the polling path.
- Static and CI validation do not establish end-to-end functionality; current
  operational readiness remains unverified until authentication, initial
  discovery, commands, polling, token refresh, reload, and restart persistence
  are exercised in Home Assistant.
- Live installation and authentication have not yet been validated.
