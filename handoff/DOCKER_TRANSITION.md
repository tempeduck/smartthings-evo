# Docker transition note

## Status and recommendation

No production Docker transition is recommended. This is a HACS custom integration
and browser-extension helper whose runtime belongs inside Home Assistant and the
user's browser.

Continue using containers only for disposable validation such as hassfest. Do not
create a separate persistent integration container: it would not participate in
Home Assistant's config entries, entity lifecycle, or HACS update model.

Samsung callbacks, access tokens, refresh tokens, and diagnostic data must never be
included in container build contexts or validation artifacts.
