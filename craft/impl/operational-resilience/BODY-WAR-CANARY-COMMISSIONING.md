# Body War Canary Commissioning Gate

The repository implementation and its two local images may be prepared without
commissioning the lab. Image preparation is not authority to start services,
probe them, run load, activate faults, roll back, or claim deployment.

Verify readiness without runtime effects from the repository root:

```bash
bash projects/domainspec-v2/impl/operational-resilience/body-war-canary-local-test.sh --preflight
```

The preflight requires the exact local Body War and gateway images plus the
pinned Prometheus image. It checks Docker, Compose, image platform, free
loopback ports, absent project resources, Compose normalization, and static
runtime wiring. It never creates a token, starts Compose, or runs the test.

A later explicit human-test decision may run:

```bash
bash projects/domainspec-v2/impl/operational-resilience/body-war-canary-local-test.sh --human-test
```

That decision must freshly bind:

- the current 60-path implementation manifest and full-suite receipt;
- Body War stable/candidate image equality and exact cached image ID;
- gateway and Prometheus image/platform digests;
- Docker Engine, Compose, and `linux/amd64` compatibility;
- the five loopback ports and absence of matching pre-existing resources;
- CPU, memory, PID, tmpfs, retention, run-time, request, and evidence limits;
- a mode-0600 run-local control-token path and digest-only receipt handling;
- an exact recovery-ledger and evidence-output root;
- permission for Compose/network effects, synthetic workload, candidate-only
  faults, rollback, exact cleanup, and no other effect.

The runtime must stop on drift, unknown resources, public binds, credentials,
remote endpoints, real Strava, Postgres, Traefik, DNS, persistent volumes, or
any failure to reconcile the exact project. No broad prune is permitted.

The runner uses a unique Compose project, a project-scoped bridge with explicit
loopback-only published ports, a run-local mode-0600 token, and a trap that
captures Compose state and service logs before executing only
`down --volumes --remove-orphans` against that exact project. The gateway token
file is mounted directly into its image-owned `/run/orodi` directory so no
tmpfs can shadow the evidence-bound file. The runner never records the token,
prunes Docker, or removes unrelated resources.

Successful commissioning still produces only a runtime-derived offline ORODI
snapshot with `runtime_admission: denied` and `authority_effect: none`. It does
not authorize deployment, release, production use, or ontology promotion.
