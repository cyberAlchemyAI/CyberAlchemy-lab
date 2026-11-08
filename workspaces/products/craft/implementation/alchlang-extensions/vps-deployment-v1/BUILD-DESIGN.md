# Self-contained VPS release prototype

Runtime release: the lifecycle application plus the newly frozen current compiler and RWO
files, pinned Node/Rust binaries and offline crates in a private image. Workstation
paths exist only inside the image. Persistent registry and /tmp volumes retain
function generations. A small gateway forwards HTTPS ingress to the loopback API.

Construction DAG: dependency closure -> image -> isolated build/invoke/lifecycle
and persistence smoke -> image identity -> rollout. Construction is runnable now.
Operational support: Alch-only VPS paths/volumes/router (VPS operator), DNS (user,
completed), owner deployment instruction (current user turn). KEP/orchestrator and
global kernel policy remain protected. No stage depends on unrelated maintenance.

Container boundary: uid 10001, no capabilities, no privilege escalation, read-only
root, private state, no Docker socket or host credentials. Bubblewrap requires
nested user/mount namespaces; scope its AppArmor profile to Alch on Ubuntu and
use container-specific seccomp and systempaths settings. Docker masked proc
paths otherwise prevent Bubblewrap from creating a private proc mount. This does not change host sysctls.

## Open Questions

Target isolation and persistent-state smoke tests must pass before ingress is
activated. The application remains the bounded semantic-host-v1 service.
