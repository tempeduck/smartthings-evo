# SmartThings Evo Readiness Assessment and Roadmap

Date: 2026-07-30

## Executive summary

The `tempeduck/smartthings-evo` fork is synchronized with upstream and passes
the available static validation. It is ready for controlled testing, but it
cannot yet be described as fully working or production-proven.

The remaining uncertainty is operational: the integration has not been
installed in Robert's Home Assistant environment, authenticated against
Samsung, or exercised against live SmartThings devices. There is also no
committed automated test suite.

One limitation is already known: button presses and other momentary events
that require SmartThings push subscriptions are unavailable. This integration
uses REST polling every 30 seconds because the Samsung mobile authentication
method does not grant the installed-app/SSE permissions used for push updates.

## Repository status

- Personal fork: `tempeduck/smartthings-evo`
- Original repository: `crash0verride11/smartthings-evo`
- Branch: `main`
- Reviewed commit: `16548af075390ff964940c30c5964b2e488f798b`
- Local, `origin/main`, and `upstream/main` point to the same commit.
- Fork divergence from upstream is zero commits in either direction.
- The fork has no GitHub Actions runs because its workflows have not been
  enabled or run.
- Upstream HACS and hassfest Actions pass on the reviewed commit.
- Upstream's published release is `2026.7.1`.
- The integration declares Home Assistant `2026.6.0` as its minimum version.

## Validation completed

The following non-live checks pass:

- Python compilation for `custom_components/smartthings`
- JSON parsing for the integration manifest
- JSON parsing for integration strings and English translations
- JSON parsing for the browser-extension manifest
- Local hassfest:
  - 1 valid integration
  - 0 invalid integrations
  - One expected warning because the `smartthings` domain collides with Home
    Assistant's built-in integration
- Upstream HACS validation on the reviewed commit
- Upstream hassfest validation on the reviewed commit
- Static review of the pinned `pysmartthings==4.0.1` token-refresh contract

## Validation not completed

None of the following has been demonstrated in Robert's environment:

- Installation through HACS or manual custom-component installation
- Coexistence with, replacement of, or migration from Home Assistant's
  built-in SmartThings integration
- Loading the unpacked Chrome or Edge extension
- Manual Samsung authentication
- Automatic extension-assisted authentication
- Successful creation of a Home Assistant config entry
- SmartThings location, room, scene, and device discovery
- Entity creation across supported platforms
- Device-state polling
- Safe device command execution
- Access-token refresh
- Refresh-token persistence
- Config-entry reload
- Home Assistant restart persistence
- Network outage recovery
- Reauthentication after token revocation
- Device addition or removal after initial setup
- API request volume with Robert's actual device count
- Long-running stability

## Known functional limitations

### No push events

The Samsung mobile authentication flow does not provide the installed-app/SSE
permissions required by `pysmartthings` for realtime subscriptions. The
integration polls device status and health over REST every 30 seconds.

Consequences include:

- Button-press events are not expected to arrive.
- Other momentary events may be missed.
- State updates can lag by up to the polling interval plus API latency.
- API traffic increases with the number of devices because status and health
  are fetched per device.

The repository currently retains event-related entities and listener code even
though those listeners do not receive events under the polling model. It may
be clearer to suppress entities that cannot function.

### Undocumented Samsung authentication

Authentication imitates Samsung's mobile application and depends on
undocumented endpoints, client identifiers, encryption behavior, and
authorization policy. Samsung can change these without notice.

### Private Home Assistant API

The automatic flow uses Home Assistant's private `_encode_jwt` helper. Private
APIs can change without the compatibility guarantees of public APIs.

### Browser-extension dependency

The Chrome/Edge Manifest V3 extension:

- Must currently be loaded unpacked.
- Is tied to its local folder location.
- Has not been published through an extension store.
- Must intercept a custom `sasdk://` callback.
- Has not been tested in Robert's browsers.

### Missing automated tests

HACS and hassfest validate packaging and conformance. They do not prove
authentication, token refresh, polling, entity behavior, or live API
compatibility.

## Recommended work plan

### Phase 1: Build a non-live automated test foundation

Add focused tests before modifying behavior or installing the integration.

Priority test areas:

1. Samsung authentication utilities
   - PKCE verifier and challenge generation
   - Service-parameter construction
   - Callback parsing
   - Encrypted-state validation
   - Encrypted-code handling
   - Missing and malformed callback fields
   - Samsung error responses

2. Token management
   - Token normalization
   - Expiration calculation
   - Preservation of refresh tokens omitted from refresh responses
   - Preservation of Samsung user and regional-host information
   - Refresh before expiry
   - Persistence after refresh
   - Revoked or missing refresh tokens
   - Concurrent requests near token expiry

3. Config flow
   - Manual authentication success and failure
   - Automatic authentication success and failure
   - Missing Home Assistant Cloud/default configuration
   - No SmartThings locations
   - Connection failures
   - Duplicate configuration
   - Reauthentication and account mismatch
   - Flow-state loss between browser steps

4. Polling coordinator
   - Successful status and health refresh
   - Partial device failure
   - Authentication failure
   - Connection timeout
   - Offline devices
   - Bluetooth tracker handling
   - Dispatcher notification behavior
   - Removal or mutation of devices during polling

5. Entity behavior
   - Entity state refresh after coordinator updates
   - Availability transitions
   - Safe device commands
   - Entities with missing components or capabilities

These tests should use mocked HTTP and Home Assistant fixtures. They must not
contain real callback URLs, authorization codes, tokens, credentials, device
identifiers, or diagnostic exports.

### Phase 2: Prepare a reviewed live-installation plan

Installing or reloading the integration crosses into a live system and should
only occur after reviewing the exact action.

Before installation:

1. Confirm the Home Assistant version is at least `2026.6.0`.
2. Identify whether the built-in SmartThings integration is installed.
3. Decide whether the two integrations can coexist safely or whether the
   existing entry must be disabled.
4. Back up Home Assistant configuration and config-entry state.
5. Document the rollback procedure.
6. Identify the exact custom-components installation path.
7. Confirm whether a full restart or config-entry reload will be required.
8. Select one or two low-risk devices for command testing.
9. Decide what sanitized logging can be enabled.

No callback URL, authorization code, access token, refresh token, Samsung
credential, Home Assistant credential, or diagnostic export should be pasted
into chat, committed, or included in reports.

### Phase 3: Test manual authentication first

The manual flow should be tested before the more complicated automatic
handoff.

Success criteria:

1. The unpacked extension loads without errors.
2. Samsung login opens from the Home Assistant config flow.
3. The extension captures the `sasdk://` callback.
4. The callback can be supplied to the manual form.
5. Home Assistant exchanges the authorization code successfully.
6. A config entry is created.
7. The intended SmartThings location is selected.
8. Tokens are stored only in Home Assistant config-entry storage.
9. Logs and browser-visible errors do not expose sensitive callback data.

If the flow fails, collect only sanitized error class, status, stage, and
timestamps. Do not retain the complete callback or token response.

### Phase 4: Test initial setup and normal operation

After authentication:

1. Confirm rooms, scenes, devices, and entities are discovered.
2. Compare discovered entities with the SmartThings application.
3. Record unsupported or incorrectly mapped capabilities.
4. Confirm read-only sensor state updates.
5. Execute commands only against selected low-risk devices.
6. Confirm command results appear after the next polling cycle.
7. Confirm offline devices become unavailable.
8. Confirm one failing device does not permanently disrupt all polling.
9. Observe logs for authentication, parsing, timeout, and rate-limit errors.

### Phase 5: Measure polling behavior

The coordinator currently performs status and health requests for each
non-tracker device every 30 seconds.

Measure:

- Number of SmartThings devices
- Requests per polling cycle
- Average and worst polling duration
- API errors and rate limits
- Home Assistant CPU and memory impact
- Time from a device change to the corresponding Home Assistant update

If polling approaches the interval duration or triggers rate limits, consider:

- Bounded concurrency
- A longer configurable interval
- Backoff after failures
- Retaining successful device results when one device fails
- Separating health polling from more frequent status polling

### Phase 6: Test automatic authentication

After manual authentication succeeds, test the complete automatic path:

1. Home Assistant generates the routing state.
2. The sentinel URL is intercepted before network navigation.
3. The extension stores the pending flow.
4. Samsung login completes.
5. The extension captures the `sasdk://` callback.
6. The extension forwards the encrypted code and Home Assistant routing state
   through `my.home-assistant.io`.
7. Home Assistant resumes the correct config flow.
8. The token exchange succeeds.
9. The config entry is created without an unexplained HTTP 500 page.

Test Chrome and Edge separately if both are intended to be supported.

The known HTTP 500 tab should be investigated even if Home Assistant finishes
the flow. A successful entry accompanied by an error page is confusing and
may hide a race or exception.

### Phase 7: Test lifecycle and recovery

Production readiness requires more than one successful login.

Test:

1. Config-entry reload
2. Home Assistant restart
3. Access-token expiry and refresh
4. Persistence of the refreshed token across restart
5. Temporary loss of internet access
6. Temporary SmartThings API failure
7. Token revocation and reauthentication
8. Samsung password or account-security changes
9. Addition of a new SmartThings device
10. Removal of an existing SmartThings device
11. Location changes
12. Extension removal after authentication
13. Continuous operation for several days

### Phase 8: Clarify the supported feature surface

Update user-facing documentation with an explicit matrix:

| Feature | Expected status |
| --- | --- |
| Samsung account authentication | Requires live validation |
| Device and entity discovery | Requires live validation |
| REST-polled state | Implemented; requires live validation |
| Device commands | Implemented; requires live validation |
| Token refresh | Implemented; requires lifecycle validation |
| Push state updates | Unsupported |
| Button-press events | Unsupported |
| Other momentary events | Potentially unavailable |
| Chrome extension | Implemented; requires browser validation |
| Edge extension | Intended; requires browser validation |

Consider removing or disabling event entities that cannot update under the
polling model. At minimum, make their limitation prominent.

### Phase 9: Establish fork CI and publish evidence

After adding tests:

1. Enable GitHub Actions on the personal fork.
2. Run HACS and hassfest on the fork.
3. Add the automated test workflow.
4. Record a sanitized Home Assistant compatibility matrix.
5. Document which devices and entity platforms were exercised.
6. Commit and push only when Robert explicitly requests it.
7. Decide separately whether any focused fixes should be proposed upstream.

## Proposed definition of ready

The fork can reasonably be called ready for regular use when:

- HACS, hassfest, compilation, JSON checks, and automated tests pass.
- Manual authentication succeeds.
- Automatic authentication either succeeds cleanly or is explicitly marked
  experimental.
- Initial discovery succeeds against a representative account.
- Common read-only entities update through polling.
- Selected low-risk commands succeed.
- Access-token refresh is demonstrated.
- Reload and restart persistence are demonstrated.
- Network failures recover without manual repair.
- Token revocation initiates a usable reauthentication flow.
- Polling remains within acceptable API and performance limits.
- Unsupported push events are clearly documented.
- No sensitive authentication material appears in logs or reports.

## Immediate next actions

The highest-value next sequence is:

1. Add the non-live authentication, token, config-flow, and coordinator tests.
2. Produce the exact live-installation and rollback checklist for Robert's
   Home Assistant environment.
3. Review that checklist before touching the live system.
4. Run manual authentication and basic discovery.
5. Test polling and selected low-risk commands.
6. Test automatic authentication and the known HTTP 500 behavior.
7. Exercise refresh, reload, restart, outage, and reauthentication scenarios.
8. Convert findings into targeted fixes and documentation updates.

Until those steps are complete, the correct status is:

> Static validation passes and the design is plausible, but end-to-end
> functionality and operational reliability remain unverified.
