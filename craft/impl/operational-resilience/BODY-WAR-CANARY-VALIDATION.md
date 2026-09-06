# Body War Canary Validation

Run the no-effect repository suite from the repository root:

```bash
bash projects/domainspec-v2/impl/operational-resilience/body-war-canary-test-all.sh
```

The script fails at the first nonzero command and performs only:

- TypeScript typechecking and Node tests for snapshot projection, gateway
  state/routing, bounded telemetry, and pure server handlers;
- Python standard-library tests for scheduling, evaluation, recovery, rollback,
  independent observation, evidence packaging, and tabletop coverage;
- closed-contract/provenance checks and static infrastructure checks.

It never invokes Docker, Compose, a package manager, a network client, a live
listener, a workload, a fault, rollback actuation, or deployment. A passing
suite establishes repository-local implementation behavior only. Live
compatibility, service health, telemetry, rollback, restoration, teardown, and
evidence remain commissioning evidence.

After the two local images are built, verify local-test readiness without
starting any service:

```bash
bash projects/domainspec-v2/impl/operational-resilience/body-war-canary-local-test.sh --preflight
```

This additionally proves that the exact images exist as `linux/amd64`, the
pinned Prometheus image is cached, all five loopback ports are free, the
reserved Compose project is absent, the Compose model normalizes, and the
strengthened static runtime contract passes. `LOCAL_TEST_READY=true` means the
human test can be requested; it is not a commissioning or deployment result.

The effectful `--human-test` mode remains a separate human decision. It starts
one unique local Compose project, exercises stable/candidate routing,
candidate-only failure, rollback, restoration probes, and Prometheus readiness,
then captures Compose state and service logs, performs exact trap-based cleanup,
and retains the run-local evidence directory. A failed phase is recorded before
teardown so a refused endpoint cannot erase the originating container error.
