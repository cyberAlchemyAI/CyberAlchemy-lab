# T25 public runtime installer prototype, v3

`install.py` composes two already selected public artifacts into one clean, owned WSL directory: the deterministic T25 candidate archive (363 historical member IDs, 681 public files and 799 local additions) and the retained seven-file API40 `lab.status` **dependency guard** archive. It pins the historical 363-ID reconciliation separately. The candidate's extracted Docker fixture context and the status guard sit under `runtime/candidate/` and `runtime/status/`. It copies no protected Source/issuer contents or mutable authority state.

The installer checks selected builder and archive hashes before effect, validates both archive member sets, verifies the extracted Docker fixture context, runs the installed status guard in isolated Python, records every installed file digest, and publishes the staged directory as `runtime/`. A cold replay compares the entire canonical manifest, including its exact key set, to a manifest reconstructed from the selected archive bytes. It rejects changed, missing or extra claims and files before executing the status guard again. The guard reports seven matched prerequisites and expressly says the original API Service was not executed. A partial stage is removed after a normal failure. The caller supplies an existing absolute, empty, owned mode-0700 directory with no symlink in its ancestry; other roots are refused before staging. The published `runtime/` directory is mode 0700 and its manifest is mode 0600. Cold replay rechecks those modes, owners, and the root's current mode and ancestry, so a post-install privacy change cannot return PASS.

Twelve small focused tests passed in normal and optimized Python. They exercise a tiny candidate archive plus the actual pinned status-guard slice: positive install/cold replay, changed candidate and guard archive refusal before effect, changed installed byte refusal, forged and extra-claim manifest refusal, dirty, linked-ancestor and mode-0777 root refusal before staging, and post-install changes to root, runtime, and manifest modes. The full 27.6 MB candidate installation and Docker run have **not** been performed for this new installer while other long native runs load the host. The earlier T30 clean-archive Docker smoke remains separate evidence for its fixture slice.

When the host has capacity, the bounded live check is:

```sh
mkdir -m 700 /home/vlad_/.local/cal-t25-runtime-check
python3 -B implementation/lab-runtime/local-host/t25-runtime-installer-0003/install.py install /home/vlad_/.local/cal-t25-runtime-check
python3 -B implementation/lab-runtime/local-host/t25-runtime-installer-0003/install.py replay /home/vlad_/.local/cal-t25-runtime-check
```

The installed Docker fixture context is `runtime/candidate/fixture/`; its existing `run-local-product.sh` is the isolated fixture replay path. A clean Docker run of this new installation is still required before T25 can advance. The seven-file guard is not the original `lab.status` Service: 201 of its 207 source-guard rows are omitted. The API45 revision-2 preflight selects 5,250 source/schema execution files, including 625 absolute host dependencies and 333 live authority paths, and is not a complete transitive closure. The existing local Docker image uses Python 3.12.15 while the selected WSL Python dependency set includes Python 3.14. The integrated API needs a portable code/data/ABI recut and a clean installed Docker replay; this prototype makes no full API, original owner, protected Source8, admission, or release claim. T25 remains open.

The entry checks do not prove freedom from concurrent path replacement by another host process. The caller still needs exclusive control of the destination while installing.
