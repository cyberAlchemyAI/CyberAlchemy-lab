# T30 disposable local candidate import rehearsal

`rehearse.py` selects the exact T25 candidate archive and hash-pinned T26 decision-state and T27 importer code. In a new private temporary root it verifies that an undecided import changes nothing, applies an explicitly **fixture-only** approval to the whole exact archive, commits through the local atomic importer, checks idempotent retry and changed-byte refusal, then starts a fresh isolated Python process that reopens the committed `HEAD` and replays all candidate bytes. The parent passes its captured runner bytes to a child bootstrap that verifies their digest before executing them; a changed-code side-effect test refuses before execution. It also extracts the archive into a fresh empty root and runs T25's selected fixture-context verifier. An unrelated sentinel stays unchanged; the temporary root is removed after the run.

[RESULT.json](RESULT.json) records the 27,595,742-byte archive's SHA-256, the initial and committed local `HEAD` hashes, and the fresh-process replay of 799 additions. The local fixture decision is not a repository-owner Decision.

`run_docker.py` extracts that exact archive into a fresh private root, builds a unique Docker image from its fixture context, and executes both the Source→Reader→Mapper→Context and Work journeys. [RUN-DOCKER-0003.json](RUN-DOCKER-0003.json) records exit 0 and the required PASS marker for both. Its before/after inventory found no selected containers, volumes, networks or image, and the temporary root was removed. The [independent third-smoke review](../working/t30-candidate-docker-independent-review-0004/REVIEW.md) verified the receipt, marker refusal test and selected-resource cleanup. The earlier [RUN-DOCKER-0001.json](RUN-DOCKER-0001.json) remains the historical receipt pinned by candidate release status 0001. The candidate does not contain the full API40 installed closure, so this is not a T30 engineering release.

[RELEASE-STATUS-0001.json](RELEASE-STATUS-0001.json) pins the candidate, local import, Docker smoke and review receipts. It records `candidate-not-released` with portable API40, all-checks, restore, original-member, human-pilot, protected-source, owner/admission and canonical publication clauses explicitly unfulfilled.
`verify_release_status.py` cold-rehashes the exact selected references and refuses changed status flags, substituted evidence, linked status files, a released claim, or a smoke receipt without both journeys and selected cleanup. Four normal and optimized tests pass; the [independent review](../working/t30-release-status-independent-review-0001/REVIEW-0002.md) confirmed the bounded verifier. Release status 0001 pins the original Docker receipt; the third run and its review are newer, separate evidence.

Run from the repository root:

```sh
python3 -B implementation/lab-runtime/local-host/t30-candidate-rehearsal-0001/rehearse.py
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t30-candidate-rehearsal-0001 -p test_rehearse.py -q
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t30-candidate-rehearsal-0001 -p test_rehearse.py -q
python3 -B implementation/lab-runtime/local-host/t30-candidate-rehearsal-0001/run_docker.py
python3 -B implementation/lab-runtime/local-host/t30-candidate-rehearsal-0001/verify_release_status.py
```
