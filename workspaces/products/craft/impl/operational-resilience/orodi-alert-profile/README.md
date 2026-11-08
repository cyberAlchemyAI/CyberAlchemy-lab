# ORODI Alert Profile implementation

This package validates a platform-neutral ORODI alert profile and renders its
first Grafana file-provisioning artifact deterministically.

The Body War profile carries five evidence-only rules. Missing telemetry and
evaluation errors are fail-closed attention states while retaining distinct
`no_data` and `error` evidence meanings. Notification delivery is absent from
the profile. The Grafana adapter uses the existing always-muted container-
loopback sink solely to prevent external delivery in the local evaluation lab.

Run the no-effect profile suite:

```bash
./projects/domainspec-v2/impl/operational-resilience/orodi-alert-profile/test-local.sh
```

Prepare the loopback human test:

```bash
./projects/domainspec-v2/impl/operational-resilience/orodi-alert-profile/test-local.sh --operator-test
```

The second command retains the local Grafana stack for human inspection. It
does not publish or deploy externally.
