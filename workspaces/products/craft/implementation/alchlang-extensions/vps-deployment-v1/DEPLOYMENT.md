# Alch VPS deployment

Status: deployed and verified. See execution.json for the exact image and live receipts.
Public destination: https://alch.cyberalchemylab.com on root@187.77.248.154.

## Product construction

Release image: `sha256:e9100820a45036f3541e327146a3c11eed87ad2fb688bcbbc5dfbbd4c663750f`.
The previous application manifest is historical: compiler dependencies changed.
`payload-manifest.json` freezes 467 current files; every hash was verified inside
this image. `release-test.json` and `evidence/local-*.json` record the new release's
build, invoke, event delivery, lifecycle, and container replacement tests.
No claim is made that the earlier 45-case suite was rerun on these changed bytes.
Construction DAG: freeze dependency closure → package image → isolated build and
lifecycle test → container replacement persistence test → exact image rollout.
All construction steps for this bounded deployment have passed locally.

## Operational support

VPS operator owns /srv/alch-host, the dedicated /etc/apparmor.d/alch-host profile,
and the Alch container/router. DNS owner has added the subdomain A record.
The user explicitly requested deployment of this service. Original preflight and
envelope records describe the earlier preparation epoch; execution.json records actual effects and live validation for this release.
KEP, orchestrator, apex DNS and global kernel settings are outside scope.

State directories /srv/alch-host/data and /srv/alch-host/runtime persist across
container replacement. The second directory holds function generation state and
must not be treated as disposable temporary storage. Both belong to uid 10001.
The target OCI manifest is `sha256:ca2bb02237dbdafe15a00a3e4083327eef917948bc99504451250f0cc9185c12`; its config digest is the local image ID above.
The application uses a read-only container root, no capabilities, no privilege
escalation, no Docker socket, and per-container namespace permissions.

## Access and rollback

HTTPS exposes a public health endpoint and bearer-authenticated /v1/projects API.
The operator token is stored locally outside the repository at
/home/vrondelli/.config/alch-host/alch.cyberalchemylab.com.token (mode 0600).
Only its SHA-256 hash is installed in /srv/alch-host/operator.json.
The current policy is bounded to OrderService, place-order, record-order, and
orders-local. This deployment does not enable arbitrary tenant policies.

Rollback removes only the Alch service/route with docker compose down for project
alch-host using its release compose file. Retain both state directories and the
operator configuration. No KEP/orchestrator rollback is authorized.

## Operator commands

On the VPS, use `/srv/alch-host/releases/e9100820a450`:

```sh
docker compose -p alch-host --env-file release.env -f compose.yaml ps
docker compose -p alch-host --env-file release.env -f compose.yaml logs --tail 100
```

The `staging.yaml` override disables public routing and was used for preactivation
testing. Do not include it in normal startup. The `deployment-smoke` project and
its single sample order remain as deployment evidence; the function is accepting.

## Open Questions

Target isolation, HTTPS, authentication and live persistence checks passed.
Broader tenant policies, tenant credential management and client UX are future work.
