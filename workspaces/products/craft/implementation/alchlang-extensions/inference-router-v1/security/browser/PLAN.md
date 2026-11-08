# Browser handoff and enrollment plan

Owner requested “plan and implement” after the live service-client rehearsal.
The approved structural model still owns principal, membership, roles and exact
tenant permissions. This is a local successor, with no governance admission.

Product construction:
1. Add an Auth Foundation consumer adapter using its existing OIDC library,
   verifier, online status check and session rules. Keep bearer tokens server-side.
2. Enroll verified sessions automatically only for known enabled principals with
   operator-defined `enrollment_roles`. Membership/grants are never created by login.
3. Bind cookie requests to the existing generated inference handler. Require
   same-origin and session CSRF proof for inference writes and logout. Bearer API
   callers use the same current authorization/enrollment path without cookies.
4. Test callback consumption, CSRF, expiry, revocation, in-flight logout and
   enrollment capacity/races. Preserve predecessor sources and evidence.

Construction chain: approved Define-backed security model → typed predecessor
ports and new trusted enrollment/session state → authored inference candidate →
consumer binding → current tests. No ontology selectors are required.

Operational support: Auth Foundation owns HTTPS origin/client registration and
issuer availability. Existing callback registration uses localhost:13443, already
occupied by the frozen AF application/proxy; this construction does not replace
that running app or alter its registrations. Live browser cutover is an explicit
operational follow-up, not a prerequisite for the independent candidate tests.

## Open Questions

Persistent or cross-instance sessions/revocation, external TLS/origin selection,
silent token renewal and issuer-wide logout remain later work. This baseline
uses token-bounded sessions and fresh login on expiry. Local logout revokes the
application session and its enrolled token, not other issuer sessions.
