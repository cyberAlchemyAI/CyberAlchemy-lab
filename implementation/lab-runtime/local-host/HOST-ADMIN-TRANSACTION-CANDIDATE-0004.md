# WSL host transaction candidate 0004: root-mediated instance custody

Status: **INERT DESIGN / NO HOST EFFECT / NOT SELECTED** (19 October 2026).
This is a versioned correction to [candidate 0003](HOST-ADMIN-TRANSACTION-CANDIDATE-0003.md),
which followed [candidate 0002](HOST-ADMIN-TRANSACTION-CANDIDATE-0002.md)
and its independent review. It deliberately changes the ownership proposal:
the `instances` directory is root-owned, not service-owned. No command below
has been run with privilege; no account, directory, unit, family, slot, or
issuer grant was created. The local Docker fixture is a separate runnable
product and supplies no protected host qualification.

## Why the parent must change

The T02 v2 independent review reproduced a service-UID process renaming a
just-created child under a service-owned 0700 `instances` directory and
substituting another directory before the writer's first open. `O_NOFOLLOW`
and a later inode comparison do not prevent that intermediate substitution.
The proposed correction is a **root-mediated create-and-bind protocol**:

* `/var/lib/cyberalchemy-lab/source8-v1` and its `instances` child are
  root:root **0700** on host ext4, with no ACL, bind alias, group/other access,
  inherited writable directory FD, or writable alternate mount. Only the
  administrator-owned broker may create or rename an instance entry. The
  service UID cannot traverse the host parent, even if another process obtains
  that UID. The broker creates a single fresh child using held directory FDs,
  `mkdirat` with restrictive mode and umask **at creation**, nofollow opens,
  unique name, and an exact device/inode witness; no later `chmod` may repair
  an interval of broader access. It opens each ancestor via held nofollow
  directory FDs and verifies owner, mode, filesystem and mount before the
  next create. It binds exactly one authorized child name to the current
  Root intent and held slot/epoch, and refuses a second child name, replayed
  epoch or an absent/changed slot;
  it gives the child to the dedicated service UID only after verifying its
  empty preimage. Every parent/child descriptor held by the broker has
  `FD_CLOEXEC`; the broker must prove none is inherited or passed to the
  service through an activation socket, systemd FD store, environment,
  `/proc`-reachable broker descriptor, or helper. No generated child is part
  of the preparation transaction.
* A reviewed systemd unit later bind-mounts **only that one child** into its
  private mount namespace at a fixed in-namespace target such as
  `/run/cal-source8/family`. The service sees and may write the selected child
  at this target; it cannot traverse, rename, create siblings in, or replace
  the host `instances` parent. The target's in-namespace parent must itself be
  root-owned and non-writable to the service from its first creation, so the
  service cannot rename or replace the bind target. The selected Root intent
  must bind both the host
  child path and its in-namespace mount target, plus source/target
  device/inode/mount identities. T35's versioned external-root successor must
  use that two-path contract; the disabled v8 path rules cannot be relaxed in
  place. This is a design constraint, not a selected bind mount or installed
  unit.
* The broker retains a nofollow `O_PATH` child descriptor until systemd has
  prepared the bind and the in-namespace process has checked the target. It
  records the pre-bind host child `statx`/mount identity, systemd invocation
  and source-path resolution, and a post-bind `statx`/mountinfo witness from
  inside the unit. The target must resolve to the **same selected child inode**
  on the expected underlying filesystem; host and target mount IDs may differ
  across namespaces and must be related by an explicit mount-source witness,
  not asserted numerically equal. Otherwise the service refuses before any
  family write. The handoff must specify an enforceable way to bind from the held
  inode or to exclude all capable host-side replacement during path-based
  `BindPaths` resolution. A post-bind match alone is not a continuous race
  proof. Plain `BindPaths=` plus two snapshots is therefore not selected as
  sufficient. Trusted root/broker authority and its concurrent actions must
  be accounted for explicitly.
* The service must never receive a parent FD, `CAP_DAC_OVERRIDE`,
  `CAP_SYS_ADMIN`, host mount namespace access, or a privileged helper that
  writes the parent. Its source/API snapshot would be separately bind-mounted
  read-only from a root-controlled, hash-pinned closure. The checkout and
  `/home/vlad_` must not be broadly mounted into the service.

This removes the specific parent-entry rename power from an ordinary
same-UID actor. It does **not** prove that same-UID actors cannot alter the
inside of the child: `/proc/<service-pid>/root` or `/proc/<pid>/fd` may expose
the private mount; a same-UID process in the service tree already sees it; a
privileged administrator can bypass discretionary permissions. WSL `/proc` is
currently mounted without `hidepid`, and Yama `ptrace_scope` is 1; neither
observation is a tested denial of these proc-mediated routes. A separately
reviewed process-dumpability/proc, credential, and mount-namespace mechanism
must close those routes and pass an actual same-UID adversarial test. The
trusted root administrator/broker remains within the authority boundary.
In a harmless same-UID child check, this user could `stat` that child's
`/proc/<pid>/root` and `fd` directories; no private-mount access was tested.

## Exact preparation slices and host preimages

The following slices are separately selectable; a later slice cannot turn an
earlier proposal into activation proof. Each requires a fresh exact preimage,
retained transcript, and independent approval. The candidate UID/GID is
`20001:20001` **only if** fresh passwd/group, NSS, process, file, container UID
mapping, and allocation checks confirm uniqueness. A collision requires a new
numbered candidate; it is not resolved by auto-allocation.

| Slice | Proposed effect | Required preimage and permitted postimage | Stop / rollback |
| --- | --- | --- | --- |
| A: account | Administrator creates locked non-login `cal-source8` group GID 20001 and account UID 20001, primary group 20001, no supplementary groups, no home, no subordinate UID/GID allocation. | Exact existing `/etc/{group,gshadow,passwd,shadow,subuid,subgid}` hashes and named/numeric entries, account tool binaries/digests, `login.defs` and default configuration, process/UID map census, and relevant lock/backup/log paths. The only desired persistent semantic delta is one group and one user; changes to other entries or subid ranges refuse. | On partial group-only creation, remove only the exact unused group after rechecking dependencies. Never copy old `/etc` files over concurrent host changes. If an unexpected tool write occurs, stop before another step and revise the manifest from the retained pre/post trace. |
| B: storage | Administrator creates `/var/lib/cyberalchemy-lab` root:root 0755, `/var/lib/cyberalchemy-lab/source8-v1` root:root 0700, `instances` root:root 0700, and `custody`/`retained` root:root 0700, using held nofollow ancestor FDs, explicit restrictive creation modes and umask. | All **five** new paths must be absent, no symlink or mount alias in the chain, `/var` and `/var/lib` root:root 0755 on the expected ext4 filesystem, and no ACL granting write or traverse. No instance child or family exists; no create-then-chmod exposure is permitted. | Remove only empty paths proved created by this slice, in reverse order, after retention review. Preserve any child, record, or new dependency. No recursive deletion. |
| C: inactive unit and snapshot | **Unselected.** Install exact reviewed snapshot, broker, unit bytes, and `daemon-reload`, without enable/start. | Requires executable and closure hashes, exact snapshot path and byte inventory, mount source/target, complete systemd settings and drop-ins, cgroup delegation/limits, account and proc isolation, broker API, record destinations and rollback manifest. None are currently selected. | Do not install a placeholder unit or broad mount. A missing value is a hard stop to this slice. |
| D: installed adversarial probe | **Unselected separate effect transaction.** Root broker creates one disposable child, service starts under reviewed unit, and independent hostile actors try replacement and mutation during the held create-to-open interval. | Requires exact child, probe scripts, process identities, mount/cgroup paths, journal/evidence destinations, slot receipt, negative oracle and retention policy. Include UID 1000 and deliberately controlled same-UID outsider and process-tree cases. | If any actor can reach/replace/mutate the child, quarantine and retain all evidence, stop unit and preserve held-slot disposition. Never promote to protected signing. |

Slice A's proposed account-tool invocation is `groupadd --gid 20001
cal-source8`, followed only after verification by `useradd --uid 20001 --gid
cal-source8 --no-create-home --no-user-group --home-dir /nonexistent --shell
/usr/sbin/nologin --password '!' cal-source8`. These are **candidate
arguments**, not an executable instruction: on this host `useradd` has no
`--no-log-init` option, and the selected normal-user invocation may allocate
`/etc/subuid` and `/etc/subgid` or initialize `/var/log/lastlog` and
`/var/log/faillog`. `groupadd` and `useradd` may create `.lock`, `-` backup,
cache, journal, and audit records. The exact binary-specific predicted write
set and a method to suppress or retain each side effect must be independently
selected **before** Slice A. The account must remain locked; `!` is a lock
marker, not a password to share. No `sudo`, `groupadd`, or `useradd` has run.

The current read-only observation is `vlad_` UID/GID 1000 in `sudo`, no
`cal-source8` or 20001 passwd/group entry, no proposed storage or unit path,
root:root 0755 `/var`, `/var/lib`, and `/etc/systemd/system`, `/var/lib` on
`/dev/sdd` ext4, systemd running, and unified cgroup v2 with `nsdelegate`.
It does not establish absence of ACLs, alternate mounts, inherited FDs, or
future credentials. The administrator reports `sudo -v` in their terminal;
this agent has no reusable privileged session.

## Unit and broker policy to bind before Slice C

The exact candidate service name remains
`/etc/systemd/system/cal-source8-writer@.service`, but **there is no selected
unit body or `ExecStart`**. A concrete unit cannot be bound until the T35
successor's executable and source/API snapshot are selected. Its reviewed
body must specify and verify:

1. An instance identifier grammar closed to traversal/escaping; mapping to
   one root-created host child and one private target. `%i` expansion and
   systemd escaping are checked against the exact Root intent. A root-owned
   broker creates the child; the service never performs parent `mkdirat`.
   The broker-to-systemd protocol must bind the **held child**, not merely a
   later pathname, and measure pre/post mount identity and the interval. If
   the selected systemd mechanism cannot do this or cannot exclude every
   capable root-side replacement during path resolution, Slice C remains
   unselected. The broker API must consume one selected Root intent and one
   continuously held slot/epoch, reject alternate names and replay, and
   preserve its terminal outcome before another attempt.
2. `User=cal-source8`, `Group=cal-source8`, no supplementary groups,
   `NoNewPrivileges=yes`, empty `CapabilityBoundingSet` and
   `AmbientCapabilities`, `ProtectSystem=strict`, no writable checkout/home,
   and exactly one read-write family bind. Restrict mount/user namespace
   creation and privileged system calls after systemd sets up the mount. The
   unit, drop-ins and effective `systemctl show` properties must be recorded;
   the unit file alone is insufficient. There must be no inherited parent or
   child descriptor, FD store entry, activation socket, or proc-mediated
   broker FD access in the service's effective process state.
3. A pinned read-only snapshot of the exact executable/import closure and
   issuer public verification material, with source and writable family mounts
   disjoint. All paths, mount IDs, owners/modes, ACLs and inherited FDs must be
   enumerated from inside and outside the service namespace. There is no
   selected protected Source8 family to bind yet.
4. Finite CPU, memory, task and wall-time limits measured against the actual
   source/reader/mapper/Context construction, plus explicit `KillMode`, stop
   timeout, cgroup kill/reap and terminal trace. `Delegate=yes` is not assumed:
   use it only if the actual supervisor needs nested cgroup control, with a
   separate proof that delegation does not widen write authority. `TasksMax`
   is a resource limit, not a sole-writer proof.
5. A per-attempt root-controlled custody record binding host and namespace
   child inode, selected binary/closure, UID/GID, unit invocation ID, cgroup,
   mount namespace, held slot OFD, period, start/end and cleanup. The broker
   must preserve indeterminate attempts; the service cannot edit custody or
   retained records. The owner/reviewer must remeasure continuity at every
   pre-effect boundary and after all descendants terminate.

The proc/FD route requires special attention. The private bind target alone
is not a security boundary against a peer with the same UID and proc access.
The installed negative oracle must show that a controlled same-UID process
outside the service cannot reach `/proc/<pid>/root`, `/proc/<pid>/fd`, the
root-held source path, or an alias and cannot alter a child leaf while the
writer is paused. It must also show that a second holder inside the unit is
absent or explicitly constrained. If those conditions cannot be enforced,
the sole-writer claim stays NO-GO even if a UID 1000 rename attempt fails.

## Remaining inputs and acceptance boundary

The host administrator must select the account-tool effect trace, exact
broker and service bytes, immutable snapshot closure, unit/cgroup/mount/proc
policy, ACL and alias census, finite limits, and rollback owner. The runtime
owner must provide attributable historical a/b release and detached-descendant
disposition plus a continuously held slot. Vlad, as named custodian, must
identify the current protected source family locator and reader, mapper, and
Context issuer/grant manifests, period and permitted access route. **Do not
paste keys or private source into chat or this repository.** A current family
may need to be constructed; its existence is not assumed from the name
“Source8.” A distinct reviewer must accept the exact installed boundary and
the hostile same-UID oracle before any protected effect, G01/G02 claim, or
T02/T35 completion.

No part of this candidate authorizes host mutation or changes the original
T02 v2 review. The earlier service-owned-parent proposal remains historical
counterevidence; this revised root-owned proposal is not yet implemented or
tested on the host. **No installed denial, sole-writer property, or G01/G02
qualification is claimed.**
