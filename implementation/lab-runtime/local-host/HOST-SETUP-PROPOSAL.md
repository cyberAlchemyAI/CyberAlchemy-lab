# Proposed WSL host setup for original runtime qualification

Status: **draft, no host mutation authorized or performed**. The selected WSL
host is observable, but G01/G02 and LC-U03-02/LC-U05-03 are not satisfied by
the Docker fixture. This proposal uses the existing independently reviewed
inactive T02 choice of account name `cal-source8` and external root
`/var/lib/cyberalchemy-lab/source8-v1`; it does not adopt that proposal or
choose a numeric host UID.

Current preimages, read on 19 October 2026: `getent passwd cal-source8` returns
no entry; `/var/lib/cyberalchemy-lab`, its `source8-v1` child and `instances`
child are absent; no `cal-source8*` systemd unit is listed. The filesystem is
ext4 on `/dev/sdd`; cgroup v2 is mounted with `nsdelegate`. The current Codex
process is UID 1000 in `/init.scope`, with no effective capabilities. `sudo -n`
requires interactive authentication. Recheck all preimages immediately before
any administrator action.

The administrator's concrete next preparation is to select an unused numeric
UID/GID for `cal-source8`, the exact root-owned ancestor modes, the
service-owned `instances` mode 0700, a delegated cgroup and systemd unit, all
allowed writers and mount/ACL aliases, resource limits, restart and rollback
owners, and a complete absolute-path write manifest. The qualified supervisor
must bind those exact identities and prove that a second same-UID process
cannot swap a selected instance between creation and open. An account name,
Docker container, unit label or `Delegate=yes` alone does not prove sole
writer custody.

The code path also needs the reviewed external-root T35 successor: current v8
checks are repository-relative and activation is hard-disabled. An actual
protected run additionally needs the independently supplied current source
family, historical a/b release and nonoverlap, reader/mapper/Context signers,
grants, periods and permitted protected locator. The existing U03-02/U05-03
construction reviews list the exact host and protected oracles to run after
these inputs exist.

Before acting, the administrator and independent reviewer should bind an
exact write manifest with each destination's preimage/absence, intended
owner/mode, command/effect, credential issuer, rollback dependency and expiry.
Only then should the administrator create the host account and directories and
install a selected service. This draft deliberately contains no `sudo`
execution script: the numeric UID, service unit and exact rollback envelope are
not yet selected. Do not use Docker daemon access to bypass the host
administrator's authentication or the G01 review.
