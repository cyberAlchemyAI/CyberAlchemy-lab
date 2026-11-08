# T29 local installed-operation continuity

`continuity.py` stages the exact T07 Docker fixture inputs into an owned temporary installation, verifies all installed context files, and uses 15 fresh Python processes for a signed local Work admission, cold replay, bounded Session, and generation rollback. These processes use the WSL host Python interpreter against the installed fixture bytes; this run does not start the Docker image. The stage child compiles the selected builder bytes passed on stdin. The local signer and state exist only in the temporary root.

The Session is substantive bounded consumption: it opens against the exact committed Work version, constructs a source-backed Context/ontology packet, returns it through the installed CLI's `--context-only` route, and closes. The runner reads that packet and checks its Work input reference, signed HEAD/source epoch, Project State, 120-second lease, no durable memory and no authority effect. It does not execute a subsequent action or lesson, and it does not preserve the private packet.

Rollback restores a cold-verified genesis generation while retaining the signed candidate generation until both are independently replayed. A foreign sentinel outside the owned generations survives. Both generations and the technical private key are then removed with the owned temporary root. This is a local deployment-generation rollback, not erasure or reversal of a signed transaction in the candidate generation; it is not a crash-atomic cutover protocol.

[RUN-0002.json](RUN-0002.json) is the selected actual PASS. `RUN-0001.json` is a prior diagnostic after a launch repair and before the final lease/claim assertions. `local_t29_check_passed:true` applies to this installed T07 fixture exercise. In this receipt, `task_complete:false` has the **original T29 admitted-operation scope** and means exactly `original_scope_complete:false`: the actual authorized operation, Work satisfaction, workflow/lesson outcome, ontology/import adoption and original A03/C13/W09/O07/R04 clauses remain unassessed. The run also does not install the full API40 composite or prove protected Source8 operation.

Run from the repository root:

```sh
python3 -B implementation/lab-runtime/local-host/t29-installed-continuity-0001/continuity.py
python3 -B implementation/lab-runtime/local-host/t29-installed-continuity-0001/verify.py
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t29-installed-continuity-0001 -p 'test_continuity.py' -q
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t29-installed-continuity-0001 -p 'test_continuity.py' -q
```

`verify.py` cold-pins the final runner and receipt and refuses a changed receipt hash. The focused tests also refuse changed or linked selected files and altered Session Work, HEAD, source epoch, Project State, lease, memory or closure claims. No repository authority, historical source, or frozen predecessor file is written.
