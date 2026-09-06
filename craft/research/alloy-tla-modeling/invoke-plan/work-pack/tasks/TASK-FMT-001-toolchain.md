# TASK-FMT-001: Toolchain Install And Smoke

Layer: L0
Status: completed

## Objective

Install or locate Java, TLA+ tools, and Alloy so a local executor can invoke the formal-modeling tools without committing third-party binaries.

## Source Contracts

- `../../IMPLEMENTATION-LAYERING.md`
- `../shared/context.md`
- Official TLA+ release: `https://github.com/tlaplus/tlaplus/releases/tag/v1.7.4`
- Official Alloy release: `https://github.com/AlloyTools/org.alloytools.alloy/releases/tag/v6.2.0`

## Implementation Detail

Use ignored local storage for downloads. Recommended cache root:

```text
.formal-tools/
```

If using a tracked ignore policy, add `.formal-tools/` to `.gitignore`; otherwise write it to `.git/info/exclude` and record that choice in the receipt.

Recommended WSL/Linux baseline:

```bash
sudo apt-get update
sudo apt-get install -y openjdk-17-jre-headless
mkdir -p .formal-tools/tla .formal-tools/alloy
curl -fL -o .formal-tools/tla/tla2tools-1.7.4.jar \
  https://github.com/tlaplus/tlaplus/releases/download/v1.7.4/tla2tools.jar
printf '%s  %s\n' \
  bee4a54f3ee3d4afc347c3240ec2d9e93b075104 \
  .formal-tools/tla/tla2tools-1.7.4.jar | sha1sum -c -
curl -fL -o .formal-tools/alloy/org.alloytools.alloy.dist-6.2.0.jar \
  https://github.com/AlloyTools/org.alloytools.alloy/releases/download/v6.2.0/org.alloytools.alloy.dist.jar
sha1sum .formal-tools/alloy/org.alloytools.alloy.dist-6.2.0.jar
```

Smoke commands:

```bash
java -version
java -cp .formal-tools/tla/tla2tools-1.7.4.jar tla2sany.SANY -help
java -jar .formal-tools/tla/tla2tools-1.7.4.jar -help
java -jar .formal-tools/alloy/org.alloytools.alloy.dist-6.2.0.jar help
```

If Alloy jar CLI differs, record the actual help/error output and reroute to wrapper repair rather than hiding it.

## Smallest Working Units

### SWU-FMT-001

- Goal: Make Java, TLA+ tools, and Alloy available from ignored local storage.
- Dependencies: none.
- Write scope: `.formal-tools/`; optional `.gitignore` or `.git/info/exclude`; `invoke-plan/run-results/toolchain/`.
- Done criteria: Java and both formal tools respond to help/version/smoke commands.
- Acceptance evidence: command transcript with versions/help output.
- Validation surface: commands listed above.
- Execution owner: local-fallback.
- Handoff note: Run this first; do not repair models in this SWU.
- Status: completed 2026-06-16.
- Evidence:
  - `../../run-results/toolchain/swu-fmt-001-smoke-clean.md`
  - `../../run-results/toolchain/ToolchainSmoke.tla`
  - `../../run-results/toolchain/ToolchainSmoke.cfg`
- Validation result: pass. Portable Java 17.0.19, TLA+ SANY/TLC, and Alloy 6.2.0 all ran from ignored local storage.

### SWU-FMT-002

- Goal: Record provenance and checksum policy for downloaded formal tools.
- Dependencies: SWU-FMT-001.
- Write scope: `invoke-plan/run-results/toolchain/`.
- Done criteria: receipt records URLs, release tags, date checked, TLA+ upstream sha1, and local Alloy checksum.
- Acceptance evidence: `toolchain-receipt.md` or equivalent.
- Validation surface: review receipt plus `git status --short .formal-tools/`.
- Execution owner: local-fallback.
- Handoff note: Alloy release metadata has no upstream checksum digest in the API; record local checksum honestly.
- Status: completed 2026-06-16.
- Evidence:
  - `../../run-results/toolchain/toolchain-receipt.md`
  - `../../session-evidence/20260616-swu-fmt-002-context-pack.md`
- Validation result: pass. The receipt records release URLs, checked date, upstream TLA+ SHA-1, portable JRE checksum, local Alloy checksum, and scoped git status showing `.formal-tools/` remains untracked.
