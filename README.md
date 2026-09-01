# SmartThings Evo

SmartThings Evo is a Home Assistant custom integration for controlling
SmartThings devices through Samsung-account authentication. It is intended for
users who need an alternative to the SmartThings developer OAuth flow.

It discovers SmartThings locations, rooms, scenes, devices, and supported
entities, and supports device state updates and commands through the
SmartThings REST API.

## Push vs Polling
This login method can't subscribe to push updates, so the integration polls
device state over the REST API every 30 seconds. Device connectivity health is
checked every 5 minutes to reduce API traffic. Button presses and other
momentary events that require push subscriptions are unavailable.

## Important limitations

- This is an independent custom integration, not an official Home Assistant
  integration.
- It uses Samsung's undocumented mobile-app authentication behavior, which may
  change without notice.
- Automatic browser-assisted authentication is experimental and still needs
  wider validation. Manual authentication is the dependable production path.

## Requirements

- Home Assistant 2026.6.0 or newer
- A SmartThings account and at least one SmartThings location
- Chrome or Edge for authentication, with the OAuth Helper extension loaded
  unpacked

## Installation through HACS

This repository is not currently in the default HACS catalog. Add it as a
custom repository:

1. Open HACS and select **Integrations**.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add `https://github.com/tempeduck/smartthings-evo` as an **Integration**.
4. Install SmartThings Evo and restart Home Assistant when requested.

This integration uses the same `smartthings` domain as Home Assistant's
built-in integration. Installing it replaces the code used by an existing
built-in SmartThings entry and may require Samsung-account reauthentication.

## Browser helper

Download the [SmartThings OAuth Helper ZIP](https://github.com/tempeduck/smartthings-evo/releases/download/v2026.7.1/smartthings-evo-chrome-extension-v0.1.0.zip),
extract it, and load the `chrome-extension` folder as an unpacked extension:

1. Open `chrome://extensions/` in Chrome or `edge://extensions/` in Edge.
2. Enable **Developer mode**.
3. Select **Load unpacked** and choose the extracted `chrome-extension` folder.

The extension is tied to its local folder. Reload it after updating the files.

## Authentication

> [!IMPORTANT]
> A browser extension is required to authenticate with SmartThings. Do not
> paste callback URLs, authorization codes, or tokens into issues or support
> requests.

### Manual authentication — recommended

Start the SmartThings config flow in Home Assistant and choose **Manual (copy
the callback URL myself)**. Complete Samsung login in the browser helper, copy
the captured callback into Home Assistant, and finish setup promptly. Callback
values expire quickly.

### Automatic authentication — experimental

The automatic flow uses the extension to intercept the Samsung callback and send
it back to Home Assistant without copy/paste. Choose **Automatic (SmartThings
OAuth Helper extension)** in the config flow. Home Assistant Cloud must be
enabled for this path.

A cosmetic HTTP 500 tab may remain open after authentication even when the
original Home Assistant flow succeeds; it can be closed. If automatic
authentication fails, use the manual flow.

## Verification

After setup, confirm that the intended location and devices appear. Allow one
polling interval and verify that state updates in Home Assistant. Test commands
only on low-risk devices.

## Support and privacy

When reporting a problem, include the Home Assistant version, integration
version, affected device type, approximate time, and a sanitized error message.
Never include Samsung credentials, callback URLs, authorization codes, access
tokens, refresh tokens, Home Assistant credentials, or diagnostic exports.

Track automatic-authentication work in [issue #2](https://github.com/tempeduck/smartthings-evo/issues/2).

## Development

The project is validated with Python compilation, JSON parsing, hassfest, HACS,
and isolated pytest coverage. The current production installation uses
SmartThings Evo 2026.7.1.

## Credits

The integration is derived from Home Assistant Core's SmartThings integration.
Thanks to joostlek for handling the original integration.
