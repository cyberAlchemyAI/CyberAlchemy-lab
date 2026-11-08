# vLLM configuration and engine binding construction

Status: owner-directed candidate construction. Raw authorization: “plan and do this”.
Authority effect: none. Construction follows CAV2-D65 and the existing accepted
local pattern and workspace product chain; it does not amend their acceptance.

Product frontier: configure a vLLM connection, discover the exact served model,
check its tokenizer, run the accepted Alch/DomainSpec public service with a bounded
vLLM wire translator, and own tunnel/listener cleanup. Native framing translates
vLLM JSON/SSE to the existing generated mappings; selection, public API, custody
and stream lifecycle remain the accepted Alch/DomainSpec composition.

Runnable work: closed private configuration; SSH discovery and forwarding;
bounded JSON/SSE translation; configure/check/start commands; local real-HTTP
regressions and revised product manifest/evidence. Done requires successful
configuration-to-service integration and failure/cleanup tests, followed by the
existing regression matrix. Previous candidates and receipts remain historical.

Operational lane: the operator owns SSH access and trusted host keys, the remote
model and its availability, any engine bearer secret, and changes to a dynamic
address. These block only live instance checks. No installation, restart, Caddy
change, model download, public hosting or deployment is part of construction.
No ontology records/selectors are required. SSH discovery is read-only, bounded to
listening TCP ports on the explicitly configured instance and GET /v1/models.

## Open Questions

Live instance reachability and the actual served model identifier are observations
to obtain through setup. Remote credentials stay with the operator. The current
service deadline remains at most 30 seconds; larger budgets require a separately
validated composition after measuring the real model. See README.md for protocol
and operational limitations.
