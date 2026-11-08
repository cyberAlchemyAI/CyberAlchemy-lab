# ISB-09 implementation plan

Owner approved the [structural model](STRUCTURAL-MODEL-APPROVAL.json) and requested
“plan and implement”. This local successor carries no governance admission.
All five steps are complete as a local candidate; see [implementation evidence](evidence.json).

1. Bind the existing Auth Foundation HTTPS verifier and authorization service.
   Add a separate trusted tenant bridge; preserve frozen authentication candidates.
2. Add a closed DomainSpec service-security contract and Alch declarations for
   explicit public/protected routes. Author permission tuples in Alch.
3. Require trusted request preparation in protected generated services. Filter
   discovery and automatic selection using current exact grants; authorize the
   selected model immediately before dispatch. Keep health public.
4. Bind custody to tenant + issuer + subject + kind. Reauthorize saved model and
   strategy before replay. Never cache an authorization acceptance.
5. Test signed-token validation, current membership/session/role/grant rejection,
   isolation, discovery, invocation/stream and replay. Run previous regressions,
   preserve ISB-08 evidence, and synchronize paired plans/Craft.

Construction chain: existing Define-backed service meanings and owner-approved
security distinctions → typed contract → authored source → generated service →
trusted Auth Foundation port → exact local tests. No ontology-runtime selectors
are required. Policy data is operator-managed and read afresh; deployment and
credential provisioning are outside this implementation.

## Open Questions

Production issuer/audience/client configuration, persistent sessions, and live
Keycloak deployment remain owned by Auth Foundation. This candidate reuses its
fixed HTTPS test token profile and supports bearer API callers (human or service).
Tenant hierarchy, delegation and shared replay remain excluded by the approval.
