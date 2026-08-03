# Home Assistant Live Test Preflight and Rollback Plan

Date prepared: 2026-07-30
Status: Prepared only; no live-system action has been taken.

## Phase A findings

Read-only discovery completed on 2026-07-30:

- Installation type: Home Assistant OS
- Machine type: `qemux86-64`
- Home Assistant Core: `2026.7.4`
- Required minimum: `2026.6.0`
- Core state: running, not in safe mode
- HACS: loaded with one enabled config entry
- Existing SmartThings integration: loaded
- Existing SmartThings config entries: one enabled entry titled `Home`
- Existing entry source: DHCP
- Existing entry version: 3, minor version 3
- Available backup: protected and compressed automatic partial backup created
  on 2026-07-30; its content includes Home Assistant configuration
- Existing `/config/custom_components` directory: present
- Existing `/config/custom_components/smartthings` override: absent
- HACS: no `smartthings-evo` or equivalent SmartThings integration repository
  is registered or installed
- HAOS backup creation command is available through `ha backups new`; restore
  is available through `ha backups restore <slug> --homeassistant`, with a
  password argument when required by the selected backup

Phase A result: version and backup prerequisites pass, but installation is
currently a **no-go without an explicit migration/rollback review**.

The custom integration uses the same `smartthings` domain as Home Assistant's
built-in integration. After installation and restart, it will replace the code
used to load the existing entry rather than create an independently coexisting
integration. Its migration from minor version 3 to 4 removes an incompatible
old token and forces Samsung-account reauthentication. The existing entry,
devices, and entity registry therefore need to be treated as migration state,
not as a parallel installation.

The filesystem/HACS inspection found no pre-existing custom override to
preserve. The proposed installation target is therefore a new
`/config/custom_components/smartthings` directory sourced from the reviewed
local commit, followed by one supported Home Assistant restart. Rollback is to
remove only that newly added directory and restore the pre-install Home
Assistant backup if the config-entry migration or registry changes must be
reversed.

## Objective

Validate `smartthings-evo` in Robert's Home Assistant environment while
protecting the existing Home Assistant configuration, the built-in SmartThings
integration, and Samsung authentication material.

The first live step is intentionally read-only: identify the Home Assistant
instance and retrieve its version. Installation, integration reloads, Home
Assistant restarts, extension loading, and Samsung authentication are separate
approval boundaries.

## Current evidence

- The integration requires Home Assistant `2026.6.0` or newer.
- Local `main` contains two test commits beyond the fork:
  - `889d8d5` — authentication, token, and coordinator tests
  - `f2174f5` — config-flow and entity tests
- The isolated unit suite passes 32 tests.
- Compilation, JSON validation, HACS validation, and hassfest pass.
- No live Home Assistant or Samsung operation has been performed.

## Sensitive-data rules

Never record or expose:

- Samsung usernames or passwords
- Home Assistant credentials or API tokens
- OAuth callback URLs
- Authorization codes
- Access or refresh tokens
- Config-entry storage contents
- Unsanitized diagnostic exports

Logs used for debugging must be reviewed and sanitized before being placed in
the repository, an issue, or chat.

## Phase A: Read-only environment discovery

This phase requires approval before connecting to the Home Assistant system.
It must not install, copy, reload, restart, authenticate, or alter anything.

Collect only:

1. Home Assistant installation type
2. Home Assistant Core version
3. Whether the built-in `smartthings` integration is loaded
4. Whether a SmartThings config entry already exists
5. Whether HACS is installed
6. The supported backup mechanism for this installation type
7. The supported custom-component installation path

Success gate:

- Home Assistant is at least `2026.6.0`.
- The installation and rollback mechanisms are known.
- The existing SmartThings state is understood.

Stop conditions:

- Home Assistant is older than `2026.6.0`.
- The instance cannot be backed up.
- The existing integration state cannot be inspected safely.
- Obtaining the information would require exposing credentials or tokens.

## Phase B: Backup and rollback preparation

This phase changes backup state and requires a separate review before running.

Before copying integration files:

1. Create a Home Assistant backup using the instance's supported mechanism.
2. Record the backup name and timestamp, but not private backup contents.
3. Confirm the backup reports successful completion.
4. Record whether the built-in SmartThings integration is configured.
5. Export only a non-sensitive entity inventory if comparison is needed.
6. Confirm filesystem access to the Home Assistant configuration directory.
7. Identify the exact existing `custom_components/smartthings` target, if any.

Rollback procedure:

1. Stop testing and avoid further authentication attempts.
2. Remove only the test custom component using the same installation mechanism
   used to add it.
3. Restore the previous custom-component directory if one existed.
4. Restore the Home Assistant backup if config-entry or registry state changed
   and cannot be cleanly reverted.
5. Start or restart Home Assistant only through its supported mechanism.
6. Confirm the pre-test integrations and representative entities recover.

The exact commands must be filled in only after the installation type and
management interface are known. Do not invent generic container, SSH, or
service commands.

## Phase C: Installation review

Installation is a live mutation and requires explicit approval after presenting
the resolved source, destination, and restart/reload action.

Pre-install review must state:

- Source commit to install
- Exact source directory
- Exact destination directory
- Whether the destination already exists
- Whether HACS or manual installation will be used
- Whether the built-in integration will remain enabled
- Whether a config-entry reload or full restart is required
- Expected outage or entity duplication risk
- Exact rollback action

Initial recommendation:

- Prefer an installation method that preserves a clear rollback path.
- Do not delete or overwrite an existing custom component without first
  identifying and preserving it.
- Preserve the existing SmartThings config entry and registry state. Do not
  delete and recreate the entry for the first test.
- Expect the existing version 3/minor 3 entry to migrate to minor version 4 and
  require Samsung-account reauthentication when the custom component loads.
- Establish whether restoring the Home Assistant backup is sufficient to
  reverse the config-entry migration, and preserve a copy of the pre-test
  custom-component state if one exists.
- Treat the domain collision as a replacement/migration test, not coexistence.

## Phase D: Home Assistant load test

After installation approval:

1. Load or restart Home Assistant using its supported mechanism.
2. Confirm Home Assistant becomes healthy.
3. Inspect only sanitized logs for import, manifest, dependency, and setup
   errors.
4. Confirm `smartthings-evo` appears in the integration setup interface.
5. Do not begin Samsung authentication during this phase.

Success gate:

- Home Assistant loads normally.
- No import or dependency error occurs.
- Existing integrations and representative entities remain healthy.
- The custom integration is selectable.

Rollback immediately if Home Assistant fails to start or an existing critical
integration is disrupted.

## Phase E: Browser-extension test

Loading the unpacked extension is a live browser change and should be reviewed
before action.

Review:

- Browser and version
- Exact extension source directory
- Requested permissions
- Existing similarly named extensions
- How the unpacked extension will be removed

The extension requests navigation, tabs, storage, cookies, and scoped host
access. Confirm its permissions match `chrome-extension/manifest.json`.

Initial test:

1. Load the extension unpacked from the reviewed folder.
2. Confirm its service worker loads without errors.
3. Open its popup.
4. Do not enter a Home Assistant target or authenticate yet.
5. Confirm it can be removed cleanly.

## Phase F: Manual Samsung authentication

Manual authentication is preferred for the first attempt because it has fewer
handoff components than the automatic path.

Before beginning:

- Select a short test window.
- Ensure no callback or token logging is enabled.
- Keep the Home Assistant log view available.
- Confirm the extension is loaded.
- Confirm rollback remains available.

Test:

1. Start the `smartthings-evo` config flow.
2. Select manual authentication.
3. Open the Samsung login URL.
4. Authenticate directly with Samsung; credentials must never be shared with
   the agent or written to the repository.
5. Allow the extension to capture the `sasdk://` callback.
6. Paste the callback only into the Home Assistant form.
7. Do not paste it into chat, logs, notes, or files.
8. Confirm a config entry is created.
9. Confirm the intended location is selected.
10. Review sanitized logs for errors.

Success gate:

- Token exchange succeeds.
- The config entry loads.
- The callback and tokens remain secret.

## Phase G: Discovery and low-risk operation

Before sending commands, choose one or two explicitly safe devices. Avoid locks,
doors, alarms, ovens, HVAC equipment, water valves, or other safety-relevant
devices for initial command testing.

Validate:

1. Rooms, scenes, devices, and entities are discovered.
2. Entity availability matches SmartThings.
3. Read-only sensor states are plausible.
4. State changes arrive within the expected polling delay.
5. One explicitly selected low-risk command succeeds.
6. The resulting state returns through polling.
7. Offline-device handling works.
8. Logs show no persistent authentication, rate-limit, or parsing errors.

Known expected limitation:

- Button-press and other push-only events will not work.

## Phase H: Persistence and recovery

Each action below needs review because it affects live runtime state:

1. Reload the config entry.
2. Restart Home Assistant.
3. Confirm entities return after restart.
4. Observe a normal access-token refresh.
5. Confirm the refreshed token survives restart without exposing it.
6. Test a brief network interruption.
7. Confirm polling recovers.
8. Revoke authentication only after separately reviewing the reauthentication
   and recovery path.

## Phase I: Automatic authentication

Attempt only after manual authentication works:

1. Start a fresh config flow.
2. Select automatic authentication.
3. Confirm the extension intercepts the sentinel URL.
4. Complete Samsung login.
5. Confirm routing through `my.home-assistant.io`.
6. Confirm Home Assistant resumes the correct flow.
7. Record sanitized information about any HTTP 500 page.

Do not capture the complete browser URL or query parameters in screenshots or
reports.

## Evidence to record

Safe evidence:

- Home Assistant version
- Installation type
- Browser name and version
- Source commit
- Test timestamps
- Pass/fail by scenario
- Sanitized exception class and stage
- Entity platform counts without personal names or identifiers
- Poll interval and approximate update latency

Unsafe evidence:

- Raw callbacks
- Tokens
- Credentials
- Config-entry JSON
- Full diagnostic downloads
- Screenshots containing sensitive URLs or account information

## Immediate approval boundary

Phase A is complete. The next proposed action is the non-mutating portion of
Phase B/C, which is now complete:

> Inspect the Home Assistant custom-component directory, HACS repository state,
> and supported backup/restore commands; resolve the exact source, destination,
> migration behavior, and rollback procedure.

No backup creation, installation, file copy, reload, restart,
browser-extension change, Samsung login, or token access is included in that
inspection. Those mutations remain separate approval boundaries.

The next mutation requiring approval is:

1. Create and verify a fresh pre-install HAOS backup.
2. Copy the reviewed local `custom_components/smartthings` directory to the
   previously absent production target.
3. Restart Home Assistant once through its supported HAOS command.
4. Confirm the existing entry migrates to minor version 4 and requests
   reauthentication.
5. Complete Samsung reauthentication in Robert's browser.

If startup or migration fails, remove only the new custom-component directory;
restore the fresh backup when reverting config-entry or registry state is
necessary.
