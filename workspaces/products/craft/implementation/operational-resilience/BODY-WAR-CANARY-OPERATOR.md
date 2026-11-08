# ORODI Body War canary operator interface

The local operator interface is a read-only Grafana dashboard backed by the
existing Prometheus gateway metrics and bounded operational events delivered by
Grafana Alloy to Loki. Every host-published endpoint is loopback-only, and all
telemetry storage is ephemeral.

Grafana also evaluates five provisioned local rules: telemetry unavailable,
unsafe candidate routing, candidate degradation, stable degradation, and
incomplete rollback restoration. Rule state is visible in the dashboard as
normal, pending, firing, no-data, or error. Missing data and evaluator errors
are not treated as healthy. No external contact point, credential, email
destination, or automated control action is configured. Each rule is bound to
an always-active local mute interval. Grafana's required receiver binding points
to an inert `127.0.0.1:9` sink inside its own container, so it cannot become an
external delivery path even if the mute boundary regresses.

Run `./body-war-canary-local-test.sh --operator-test` after the pinned local
images and gateway image are present. The runner completes the 90/10 baseline,
candidate-only fault, rollback-restoration, Prometheus-query, Loki-event, and
dashboard-provisioning machine gates before leaving Grafana live at
`http://127.0.0.1:13000/d/orodi-body-war-canary/orodi-body-war-canary` for the
terminal human visual validation.

The dashboard and alert evaluator deliberately contain no control token or control endpoint and
cannot deploy, roll back, admit, accept, promote, publish, or release anything.
An alert may request human attention but cannot initiate rollback. Notification
delivery is a separate credentialed external effect and is not part of this
local implementation. Missing telemetry remains missing. The runner prints an exact cleanup command;
cleanup removes the temporary containers, network, token, and ephemeral data.
