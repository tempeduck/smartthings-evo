# smartthings-evo
SmartThings is 'evolving' their developer API by charging for access starting in October. smartthings-evo is a copy of the ha-core smartthings component, refactored to mirror the authentication flow of the android mobile app, requiring a browser extension to capture the sasdk:// redirect uri and finish authorization.

## Push vs Polling
The REST auth is not capable of subscribing to push updates and the integration now polls the REST api every 30s.

# Authentication

> [!IMPORTANT]
> A browser extension is required to successfully authenticate with SmartThings (capture the sasdk:// uri). Do not skip this step!

SmartThings mobile uses a custom PKCE OAuth authentication which blocks automated logins. Authentication requires a browser-based OAuth flow using a browser extension to capture the mobile app redirect URI.

## Setup

   ### chrome-extension
   > The chrome extension is tied to the folder location on your computer and may disappear if you move the folder.
   - Download the project 
   - Extract the zip file and locate `./chrome-extension/`
   - Open Google Chrome and navigate to `chrome://extensions/` or Edge `edge://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the extracted `chrome-extension` folder
   - Start the the automated authentication flow in the integration
   - After logging in to Samsung the redirect should be captured and re-written to my-homeassistant.io
   - Proceed with the `Link to Home Assistant` process

   ### Known Issue
   - A tab loads a 500 internal server error but authentication proceeds in HA

#### original codeowner
thanks to joostlek for handling the integration thus far
