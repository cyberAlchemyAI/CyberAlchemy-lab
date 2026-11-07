# Preparing a stable distribution

One Python distribution serves all consumers. Its current CLI publication adapter is qualified on the recorded Linux x86_64/WSL2 host; other operating systems require adapter implementation and native qualification, not separate Define product versions.

## Reproduce qualification

1. Build the wheel and source archive from reviewed source after the explicit `seal.py` packaging step.
2. Copy both archives outside the Lab repository.
3. Create clean virtual environments for the supported interpreter versions, install the wheel, and run `python -m pip check`.
4. Extract the source archive outside the repository and run `python -I -m unittest discover -s EXTRACTED/tests -v` using each installed environment.
5. Run the documented CLI workflow and compare every reconstructed byte. Run JSON/Python parity, resource drift and the repository-denied workflow.
6. Install from the source archive separately, then repeat the same suite against that installation.
7. Record archive hashes, dependency versions, test logs, installed locations and source preservation checks. A rebuilt artifact must match the artifact selected by the final qualification run.

`qualified-constraints.txt` pins the dependency cohort observed in this release qualification. It is a reproducibility aid for the recorded Linux matrix, not a security attestation or an assertion that every possible dependency combination has been tested.

## Remaining publication decisions

- Apache-2.0 has been selected for this standalone distribution. Keep LICENSE, NOTICE and `License-Expression: Apache-2.0` in the final archives; dependency distributions retain their own license files.
- Select the stable version and publication destination; apply the version-only change and qualify the final artifact.
- Approve tagging/publication of those exact bytes. Test success does not publish, admit or adopt anything automatically.

Native Lab v3 review/admission and hosted HTTP/MCP deployment remain separate integration work. They are outside this standalone release's behavior contract.
