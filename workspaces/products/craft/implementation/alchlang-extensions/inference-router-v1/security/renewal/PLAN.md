# Bounded browser token renewal

Product construction follows the approved structural model and Auth Foundation
session policy → renewal binding contract → existing compiled inference security
and native browser adapter → current lifecycle and regression tests. No ontology
record/selector dependency or authority promotion is introduced.

A renewable session carries its trusted issuer/subject/kind/client identity,
issuer session ID, authentication time, original absolute deadline and last
activity. OIDC code + state + nonce + PKCE remains the authentication protocol.
Renewal requests use prompt=none and the established subject as login_hint. No
refresh token or ID token is retained or returned. Verified callback claims must
retain the exact identity, issuer session and authentication time, with a new
access-token identifier. Current policy enrollment still selects memberships and
roles; renewal never copies grants or trusts browser authority fields.

POST /renew requires the current cookie, exact Origin and CSRF header. It returns
an authorization URL and login transaction cookie. The browser navigates that URL;
the API never retries inference automatically. Expired access tokens cannot reach
inference: cookie clients receive 409 RENEWAL_REQUIRED while their application
session is still within its idle/absolute bounds. /session can expose renewal
metadata (no tenant catalog when the token is expired), not authorization.

Renewal atomically replaces the session and revokes the old token. It preserves
the original absolute deadline and current last activity, so background renewal
cannot extend idle time. Logout, expiry and competing replacement win against
late callbacks. Unknown legacy sessions without verified renewal metadata retain
their original token-bounded behavior. In-flight login transactions stay ephemeral.

Runnable work: implement the binding, browser/API flow and SQLite race tests;
then publish local evidence in paired Craft plans. No construction blocker.
Operational support: operator-owned key custody, backup policy, production
origins, multi-host storage and deployment affect no current construction stage
and remain deferred. No existing issuer configuration or running host is changed.

## Open Questions

The real issuer/browser renewal rehearsal passed seven checks with browser-local
application interception; current direct-TLS tests remain separate.
Production key operations, multi-host login affinity, issuer-wide logout and
durable inference custody remain separate decisions. Silent SSO failure requires
fresh sign-in; no automatic downgrade to interactive login or inference replay.
The existing token-revocation port revokes a token; local browser logout removes
the application session. Already-returned streams retain their existing behavior.
