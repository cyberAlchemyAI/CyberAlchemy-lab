# Live Auth Foundation inference rehearsal

Product frontier: ISB-09 passed local signed-token and Rust authorization tests.
This successor closes the real HTTPS issuer/JWKS/introspection integration gap
for autonomous service API callers using the approved flat tenant model.

1. Build the unchanged protected Alch service and locked tenant bridge.
2. Obtain an access token from the existing local AF service client over verified
   TLS. Keep credentials and token in memory; never write them to evidence.
3. Create an owner-only disposable policy with the verified service identity,
   exact current session and two tenant memberships. Start a numeric-loopback
   provider fixture and inference listener.
4. Check anonymous denial, discovery, JSON, SSE, replay, tenant isolation and
   current model/session revocation. Restore only the disposable policy as needed.
5. Close listeners, remove temporary files, and record source-bound results.

Construction chain: approved structural definitions → ISB-09 typed/authored
candidate → unchanged generated product → live dependency witness. No ontology
selectors, governance admission, production deployment or issuer administration.

Operational support: the local AF operator owns the existing HTTPS stack,
credentials and CA trust; these are exact prerequisites for this live test.
The runner owns temporary policy/provider/listener cleanup. No running containers,
existing grants, realm settings or frozen candidate bytes are changed.

## Open Questions

Browser login-to-inference handoff, automatic session enrollment, production
issuer/audience selection, durable custody and external TLS remain separate work.
The current session registry is explicitly operator-managed. Issued test access
tokens expire under the existing five-minute profile; this rehearsal does not
change client state or revoke another session.
