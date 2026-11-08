# T25 local candidate package slice

`package.py` builds a deterministic disposable ZIP, replays it in clean temporary roots, and prints [RESULT.json](RESULT.json). The exact [INVENTORY.json](INVENTORY.json) lists every original member ID and addition path/hash/kind. The archive is not retained in the repository. It embeds the existing exact original-public-input archive (363 original member IDs, 681 public files) and 799 selected additions:

- 779 Docker fixture workspace files: 698 selected materials, three runtime files and 78 name-only empty placeholders. The owner-only registry is staged from its byte-identical selected public postimage.
- Four Docker build inputs, the selected package manifest and release pin, the package builder, and the deterministic `.dockerignore`.
- Twelve pinned API40 composite controls, entrypoints, and prior run receipts.

Every selected body is rehashed before packaging. The original bundle and account programs are hash-pinned, checked for linked ancestors, and executed from their verified bytes; the bundle's `account` import is bound to the selected account program. Replay rejects missing or changed entries, changed original archive, escaped paths, duplicate JSON keys, noncanonical ZIP bytes, and a manifest that claims completion. Extraction writes into an existing empty directory and runs the fixture context verifier on the extracted files. Thirteen tests pass both normally and with `python3 -O -B`, including changed-code, ambient-module, linked-ancestor and import-window source-swap refusals.

Run from the repository root:

```sh
python3 -B implementation/lab-runtime/local-host/t25-local-candidate-0001/package.py
python3 -B implementation/lab-runtime/local-host/t25-local-candidate-0001/package.py --inventory
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t25-local-candidate-0001 -p 'test_package.py' -q
```

To get the verified, standalone **Docker fixture context**, create an empty directory and run `package.py --extract /path/to/empty-directory`. The context is under `fixture/`. From that directory, run `docker compose -f fixture/compose.yaml build --no-cache lab-fixture`, then `docker compose -f fixture/compose.yaml run --rm --no-deps --pull never chain-fixture` and the corresponding `lab-fixture` run. Use a unique `LAB_LOCAL_IMAGE` tag for the run, and remove that tag afterward. A [separate T30 smoke](../t30-candidate-rehearsal-0001/RUN-DOCKER-0001.json) has now built and run both journeys from this exact archive's clean extraction; [independent review](../working/t30-candidate-rehearsal-independent-review-0001/REVIEW-0003.md) accepted that bounded fixture result.

**T25 remains open.** The original 363 member dispositions are not complete. The twelve API40 files are selected controls, not its runnable full closure: the profile names 33,424 selected files, including 857 absolute WSL host paths, and the installed ABI/loader and fresh private branch credentials are not captured in this archive. No API40 Docker smoke, installed API40 product replay, protected Source8 effect, original owner decision, or release effect is claimed. The fixture package is the runnable local Docker product slice; the API40 composite remains a separately proven WSL host CLI until its portable closure is designed and tested.
