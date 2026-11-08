# Host lifecycle product and business prototype

Tenant owners inspect health with read scope, then submit an explicit fenced drain,
resume or restart request using lifecycle scope. The business result is recovery
without access to server credentials or business payloads. A request locator lets
the owner resolve a lost HTTP response. Drain failure retains a closed gate and a
visible reason; successful restart preserves selected code and durable business data.

The product exposes a fast 202 acceptance and GET-only polling. A single bounded
lifecycle worker holds a per-function guard during effects. Status reads do not take
that guard and never launch. Build work retains its separate thread/connection.
Activation and invocation use the same guard and reject outstanding lifecycle work.

Fresh registry roots only. New operator configuration explicitly grants lifecycle;
predecessor permissions are not broadened. Parent-death signaling and the existing
storage owner lock prevent unverified process replacement during crash recovery.

## Open Questions

See PLAN.md#open-questions. Product review is separate from operational deployment.
