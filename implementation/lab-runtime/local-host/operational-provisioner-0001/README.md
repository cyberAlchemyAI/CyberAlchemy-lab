# Local operational provisioner 0001

This is an executable, unprivileged slice of T34. It creates a new owned store and stages a fresh per-run Reader policy from a separate private custody directory. It does not create a Project authority store, issue an operator grant, or operate on the protected Source8 family. The old `CandidateBranch` remains disposable and unchanged. A focused integration test stages a valid fresh `engineering` fixture policy and authenticates it through the actual API16 `ReaderChannel`; this does not qualify a protected Source8 policy.

`controller.py` accepts a private JSON plan with schema `lab-local-operational-provision-plan/v1`. Required fields are `store_id`, `operator_ref`, `scope_ref`, `owner_uid`, `engine_path`/`engine_sha256`, `profile_path`/`profile_sha256`, `base_head_path`/`base_head_sha256`, `store_path`, `rollback_path`, `private_key_path`/`private_key_sha256`, `custody_policy_path`/`custody_policy_sha256`, `channel_root_path`, `source_name`, and `source_expires_at`. The selected operator and scope refs must match the custody policy exactly; `store_id` is an independent local store identity. The plan must be `0600` under an owner-only `0700` directory. The store and channel directories must be new and disjoint; the store parent and retained rollback directory must already be owned by the current UID at mode `0700`. The private key and custody policy must be outside the repository, with mode `0600` and byte pins in the private plan; their parents must be owner-only `0700` directories. The channel root must be a direct or nested `/tmp` path. Plan, selected implementation, profile, base HEAD, key, and policy bytes are pinned before staging.

Run:

```sh
python3 -B implementation/lab-runtime/local-host/operational-provisioner-0001/controller.py --plan /tmp/your-private-plan.json initialize
python3 -B implementation/lab-runtime/local-host/operational-provisioner-0001/controller.py --plan /tmp/your-private-plan.json --operation-id op:your-run-001 --intent reader-session:your-work stage
python3 -B implementation/lab-runtime/local-host/operational-provisioner-0001/controller.py --plan /tmp/your-private-plan.json restart
python3 -B implementation/lab-runtime/local-host/operational-provisioner-0001/controller.py --plan /tmp/your-private-plan.json rollback
```

`stage` returns an absolute staged policy path and SHA-256. Supply a stable `--operation-id` for an exact retry after a lost CLI response; omitting it creates a fresh ID each time. The request fingerprint binds the private plan, policy bytes, and `--intent`. Repeating an active ID and identical request returns the same path and generation with `replayed: true`; changing the intent returns `OPERATION_CONFLICT`. A pending intent with no created channel can retry under the same ID only with the same request fingerprint. After restart, rollback, or a newer run, a committed old ID returns `OPERATION_RETIRED` and cannot reactivate a channel. The journal retains up to 1024 operation IDs, then refuses new ones rather than forgetting retry history. A staged policy path is not a reused Session or nonce: API16 creates each challenge nonce in process.

The controller itself checks only a subset of policy fields; the API16 constructor remains responsible for its closed schema and source controls. The focused test authenticates one fresh `engineering` fixture after staging. It creates a new `0700` run directory and `0600` policy file for each successful run. Pinned file reads and journal/policy writes loop until all bytes are read or written. `restart` and `rollback` remove only a staged file and directory whose recorded inode, digest, mode, and exact directory shape still match. If interrupted after unlink or rmdir, restart clears the exact recorded active run only when its pinned directory is empty or absent and no foreign channel entry exists. Changed or foreign bytes are preserved and refused. The owned store and retained rollback path remain. A changed or revoked custody policy blocks new staging but does not prevent invalidation of a previously staged channel. The controller never stores or restores Session RAM.

Operations take a nonblocking `flock` on the store's `0600` lock file and reload state inside the lock. A second controller gets `STORE_BUSY`; it cannot overwrite the first controller's generation. On restart, a pending operation's private run directory is removed only if it is empty or contains exactly the pinned `0600` policy bytes. A dangling symlink, changed policy, extra file, or unrelated channel entry returns `UNCERTAIN_CHANNEL_RETAINED` while retaining both the pending record and bytes. A test terminates the process immediately after `mkdir`; a new process retries the same operation ID, removes the exact empty residue, and creates a distinct fresh run. Rollback preserves an unrelated retained-store sentinel. This is process-crash recovery in disposable local roots, not power-loss durability or hostile same-UID isolation. The focused suite also runs two distinct owned-store rehearsals in fresh CLI processes with separate private roots, principals, keys, policy bytes, and store IDs; both use the same test UID and synthetic policy. Do not count original T34 complete until protected Source8 policy integration and separately authorized custody/owner qualification pass.

Focused checks:

```sh
python3 -B -m unittest -q implementation/lab-runtime/local-host/operational-provisioner-0001/test_controller.py
python3 -O -B -m unittest -q implementation/lab-runtime/local-host/operational-provisioner-0001/test_controller.py
```

The tests use disposable `/tmp` inputs and test-only bytes. No credential, policy, or local store path is checked into Git.
