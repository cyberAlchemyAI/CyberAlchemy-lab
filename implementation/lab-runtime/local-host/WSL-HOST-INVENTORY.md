# WSL host candidate inventory — 19 October 2026

This is a read-only observation for preparing the original Lab runtime host
selection. It is not a NamespaceActivation, deployment approval, or host oracle.

| Item | Observed on this WSL host |
| --- | --- |
| Kernel | Linux 6.18.33.2-microsoft-standard-WSL2 |
| Current process | UID/GID 1000:1000, no effective Linux capabilities, cgroup `/init.scope` |
| cgroup | unified cgroup v2 mounted `rw` with `nsdelegate`; `/sys/fs/cgroup` is root-owned mode 0555 |
| systemd | running; `user@1000.service` reports `Delegate=yes` |
| Checkout | ext4; `/home/vlad_/projects/CyberAlchemy-lab` owner 1000:1000 |
| Proposed UID 20001 | no passwd entry currently; not created or reserved |
| Earlier T02 host proposal | `cal-source8` account, `/var/lib/cyberalchemy-lab/source8-v1/instances` parent; account, tree and unit are absent now |
| Noninteractive host administration | `sudo -n true` requires interactive authentication; no host account or cgroup changes were attempted |
| Docker | 29.8.1, cgroup v2, local daemon reachable |

No dedicated host service account, selected exclusive cgroup subtree,
independent worker/alias exclusion proof, durable start/terminal control
custody, or protected source family was established by this inventory. The
Docker fixture uses the checkout owner's UID and has no host deployment
authority.

The prior [T02 namespace design](../../../docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/fresh-family-exclusive-namespace-design-independent-review-0002/review.json)
proposes `cal-source8` and an external `/var/lib/cyberalchemy-lab/source8-v1`
root, but its independent verdict is bounded inactive NO-GO. It also requires
a coherent external-path T35 code successor and a proof that no other holder of
the service UID can swap the selected directory. This inventory does not
install or endorse that proposal.

Before any host mutation, the WSL administrator and runtime owner must choose
the exact service account/UID, root and ancestor paths, delegated cgroup,
namespace identities, mount/ACL/confinement policy, worker and capable-peer
exclusion, control-store custody, resource limits, rollback owner, and complete
absolute-path write manifest. The protected-input custodian must separately
select current source/reader/mapper/Context issuers, grants, periods and
historical-family disposition. These selections need independent review
before LC-U03-02 or LC-U05-03 can run their actual oracles. Do not paste keys
or protected bodies into this repository or chat.
