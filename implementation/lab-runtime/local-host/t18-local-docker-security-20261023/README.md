# T18 local Docker isolation observation

`RESULT.json` records a live `docker inspect` of the disposable `lab-fixture`
container during the 23 October 2026 `run-local-product.sh` run. The exact
selected settings passed: UID/GID `20001:20001`, read-only root filesystem,
no network, all capabilities dropped, no-new-privileges, 64 process limit,
1 GiB memory limit, one CPU, and a bounded `/tmp` tmpfs. The receipt retains
the container and image IDs, observed settings, expected settings, UTC time,
and a no-replace result. SHA-256 of `RESULT.json` is
`de50a54a2ac1270ceabf1fb740ff5c2bbb5382df21e800ec10380402d5dce95c`.

This is an observed local Docker configuration. It does not exercise the
integrated API Service/Vault, prove all 34 operations, or complete T18's
authentication, hostile-input and recovery matrix.
