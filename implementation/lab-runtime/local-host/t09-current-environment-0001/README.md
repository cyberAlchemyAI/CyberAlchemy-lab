# Current composite environment check

Run `python3 -B implementation/lab-runtime/local-host/t09-current-environment-0001/verify.py` from the repository root. The check binds the API39 source/profile, its selected composite SDK, the task-local jsonschema 4.19.2 overlay, and the sealed 1,010-file installation. It checks selected SDK/overlay member bytes and sizes and installed member bytes and modes, executes the installed Python through its selected ELF loader and ABI libraries, verifies the API source guard in that interpreter, then rereads the public selections and complete installation. It refuses an unsupported requested environment, a missing overlay, changed input bytes, or an equal-byte symlinked ancestor.

The check establishes only the API39 fixture environment on this WSL host. The historical R02 seven-field environment contract, original full protected proof, current T08 host binding, composite Action dispatch, upgrades, rollback and protected deployment are separate unfulfilled T09/T06 obligations. The executable check has no authority effect.

Focused tests: `python3 -B -m unittest implementation/lab-runtime/local-host/t09-current-environment-0001/test_verify.py` and the same command with `-O -B`.
