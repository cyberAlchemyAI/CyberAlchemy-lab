# Independent review — local Docker fixture, 19 October 2026

**Disposition: PASS for the disposable local Work fixture only.** This is not
LC-U03-02/LC-U05-03 acceptance, G01/G02 satisfaction, host qualification,
NamespaceActivation, or permission to admit/release the composite runtime.

I reviewed these exact current files (SHA-256):

| File | SHA-256 |
| --- | --- |
| `Dockerfile` | `c51a6e8f82b54f31c1c535741f6e7de007b20f9f7e23f3f10d81b50d6833930b` |
| `compose.yaml` | `44f45b4bb9305705b11908f2bb4db85712e3ef463539271da4ee7b53a6fc27cc` |
| `README.md` | `398e4390a90a7aa60124c9f7a56bd7095e91e9906bbf8d02e3b104fe01363dec` |
| `WSL-HOST-INVENTORY.md` | `cbb4f0de06bda8860023b25197e2276ebd76b473ce3808852d9148ce52144a22` |
| `HOST-SETUP-PROPOSAL.md` | `91419e7101590f22636ee4d22ef6f007e7346e704eaecf041d85a27acb04fdf6` |
| `docker-run-0001.txt` | `63c44f7522f583f41c284ef0d762a2a6aeaaa01bd7e77fb528ae0149bec4e867` |

`docker compose -f implementation/lab-runtime/local-host/compose.yaml config`
exited 0 in the independent review. It resolves the build context to
`implementation/lab-runtime/local-host`, the checkout bind to `/workspace`
read-only, and the fixture process to UID/GID 1000:1000. Compose declares
`network_mode: none`, `read_only: true`, all Linux capabilities dropped,
`no-new-privileges`, no published port or persistent volume, and a private
`/tmp` tmpfs. The built image exists as
`sha256:e914bfa0ab88a0ac0306ff0adb487adf6e8a37bb431c3a1dd259b9a05e49283a`;
its image-level user is 20001:20001, overridden by this Compose fixture.
The Docker build context does not copy the checkout into the image.

The coordinator's captured [run](docker-run-0001.txt) records the exact README
command exiting 0, the local Work journey passing, and no matching Compose
containers remaining. I did not repeat that slow full journey. The first run
as UID 20001 failed because `authority/definitions/registry.json` is owner-only
mode 0600; switching the fixture process to the checkout owner's UID resolved
that read without changing host file modes or copying source bytes into the
image. I independently confirmed the current owner UID/GID 1000:1000, the
registry mode 0600, and the read-only Compose resolution.

The process can read **every checkout file available to that owner**, including
other owner-only files, because the whole repository is mounted. The container
is therefore not a secret-isolation boundary. Network isolation and the lack
of a persistent volume limit its effects, but do not prove that all dependency
code ignores unrelated private bytes. The local launcher writes its disposable
fixture key and store under `/tmp`, then removes them on successful completion;
its reported result has no repository admission or external effect.

The WSL inventory records a possible host but does not select an exclusive
service account, delegated cgroup, capable-peer exclusion, protected source
family, issuer, or rollback/write envelope. `sudo -n true` requires interactive
authentication, and no host account or cgroup mutation was attempted. Actual
host and protected-input oracles remain unrun. The earlier `cal-source8` and
external `/var/lib/cyberalchemy-lab/source8-v1` proposal has an inactive
NO-GO verdict; its account, tree, and unit are absent on this host.

I also checked the [host setup proposal](HOST-SETUP-PROPOSAL.md) against the
reviewed inactive T02 `cal-source8`/external-root proposal and this host's
current read-only preimages. It correctly leaves numeric UID, installed unit,
write manifest, owner release, exclusive writer proof, and protected issuers
unselected. It authorizes no administrator command or activation. Its route is
reviewable as a draft; it cannot serve as an actual host receipt.
