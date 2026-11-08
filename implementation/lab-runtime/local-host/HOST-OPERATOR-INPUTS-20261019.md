# WSL operator inputs, 19 October 2026

The operator identified `vlad_` as the WSL host administrator and Vlad as the
protected Source8/reader/mapper/Context custodian. The operator reported that
`sudo -v` succeeded in their own terminal. This is an accountable-person
reference, not a host deployment approval, issuer enrollment, or proof that a
protected current family exists.

Read-only checks in the Codex process still show UID/GID `1000:1000`, membership
in `sudo`, a running systemd, and `sudo -n true` requiring interactive
authentication. `cal-source8` has no passwd/group entry, numeric UID/GID 20001
have no entry, and the proposed `/var/lib/cyberalchemy-lab/source8-v1` root
does not exist. The current process is in `/init.scope`; no dedicated service
cgroup has been selected or installed. Recheck these preimages before any
administrator action.

The administrator can prepare the host without sharing a password: choose the
service UID/GID, root and ancestor owners/modes, exact systemd unit and
delegated cgroup, mount namespace, allowed writers, capacities, rollback owner,
and an exclusive write manifest. The user should run privileged commands only
after that manifest is reviewed and selected; the current Codex terminal cannot
reuse the operator's `sudo` authentication. The current protected family path
and issuer manifest references remain to be supplied by the custodian, as
references only, without keys or private contents.

The Docker Compose fixture is already runnable locally, but its process runs
as checkout UID 1000 and its private fixture data does not satisfy G01 or G02.
No host account, directory, service, cgroup or protected family was created by
this note.
