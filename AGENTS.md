# Agent Guidance

## Read first

Read `CLAUDE.md` for the project architecture, authentication flow, and current
constraints. Read `handoff/ACTIVE.md` for current state. The shared private
Codex guidance in `~/.codex/AGENTS.md` supplies cross-project safety rules.

Before changing files, inspect `git status`, recent history, and both Git
remotes. Preserve the relationship between the personal fork (`origin`) and
the original project (`upstream`).

## Project workflow

- This is a HACS custom integration derived from Home Assistant Core's
  SmartThings integration.
- Integration code is under `custom_components/smartthings/`; the required
  Chrome/Edge OAuth helper is under `chrome-extension/`.
- The Samsung OAuth callback and stored token are sensitive. Never place
  callback URLs, authorization codes, access tokens, refresh tokens, Samsung
  credentials, Home Assistant credentials, or diagnostic exports in the
  repository or handoff.
- Preserve Home Assistant compatibility and the polling model unless a change
  is deliberately scoped and tested.
- Validate Python and JSON locally, then use the repository's HACS and hassfest
  workflows when relevant. Do not claim Home Assistant runtime validation
  unless the integration was actually installed and exercised.
- Installing the integration, loading the browser extension, authenticating
  with Samsung, or restarting/reloading Home Assistant crosses into live
  systems and requires an explicit review of the intended action first.
- Do not commit, push, publish a release, or open an upstream pull request
  unless the user asks.

## Handoff

After meaningful work, update `handoff/ACTIVE.md` with current state,
validation performed, open work, and operational risks. Keep durable
architecture and setup facts in `CLAUDE.md`.
