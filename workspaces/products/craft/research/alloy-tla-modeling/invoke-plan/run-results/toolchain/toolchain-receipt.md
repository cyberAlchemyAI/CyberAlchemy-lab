# Formal Toolchain Provenance Receipt

Timestamp: 2026-06-16T21:22:00Z
Result: pass

## Policy

- Downloaded third-party artifacts live under `.formal-tools/`.
- `.formal-tools/` is excluded through `.git/info/exclude`, not a tracked `.gitignore` change.
- Toolchain receipts are tracked under `projects/domainspec-v2/research/alloy-tla-modeling/invoke-plan/run-results/toolchain/`.
- Upstream checksums are recorded only when the upstream release provides one. Local checksums are labeled local-only.

## Artifacts

| Tool | Version/Tag | Source URL | Local Path | Size | Upstream Checksum | Local Checksum |
| --- | --- | --- | --- | --- | --- | --- |
| Temurin JRE | `jdk-17.0.19+10` | `https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.19%2B10/OpenJDK17U-jre_x64_linux_hotspot_17.0.19_10.tar.gz` | `.formal-tools/downloads/OpenJDK17U-jre_x64_linux_hotspot_17.0.19_10.tar.gz` | 46671975 bytes | SHA-256 `adb5a2364baa51de1ef91bb9911f5a61d24b045fe1d6647cb8050272a3a8ee75` | SHA-1 `1938d09f54b1ed429901fb6b04c9ad21ed552bef`; SHA-256 `adb5a2364baa51de1ef91bb9911f5a61d24b045fe1d6647cb8050272a3a8ee75` |
| TLA+ tools | `v1.7.4` | `https://github.com/tlaplus/tlaplus/releases/download/v1.7.4/tla2tools.jar` | `.formal-tools/tla/tla2tools-1.7.4.jar` | 2274532 bytes | SHA-1 `bee4a54f3ee3d4afc347c3240ec2d9e93b075104` | SHA-1 `bee4a54f3ee3d4afc347c3240ec2d9e93b075104`; SHA-256 `936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88` |
| Alloy | `v6.2.0` | `https://github.com/AlloyTools/org.alloytools.alloy/releases/download/v6.2.0/org.alloytools.alloy.dist.jar` | `.formal-tools/alloy/org.alloytools.alloy.dist-6.2.0.jar` | 21062377 bytes | none found in release metadata checked for this work-pack | SHA-1 `fa67c6db2ce61955b1b373094d8841cc639f0570`; SHA-256 `6b8c1cb5bc93bedfc7c61435c4e1ab6e688a242dc702a394628d9a9801edb78d` |

## Validation Transcript

```bash
sha1sum .formal-tools/tla/tla2tools-1.7.4.jar \
  .formal-tools/alloy/org.alloytools.alloy.dist-6.2.0.jar \
  .formal-tools/downloads/OpenJDK17U-jre_x64_linux_hotspot_17.0.19_10.tar.gz
```

```text
bee4a54f3ee3d4afc347c3240ec2d9e93b075104  .formal-tools/tla/tla2tools-1.7.4.jar
fa67c6db2ce61955b1b373094d8841cc639f0570  .formal-tools/alloy/org.alloytools.alloy.dist-6.2.0.jar
1938d09f54b1ed429901fb6b04c9ad21ed552bef  .formal-tools/downloads/OpenJDK17U-jre_x64_linux_hotspot_17.0.19_10.tar.gz
```

```bash
sha256sum .formal-tools/tla/tla2tools-1.7.4.jar \
  .formal-tools/alloy/org.alloytools.alloy.dist-6.2.0.jar \
  .formal-tools/downloads/OpenJDK17U-jre_x64_linux_hotspot_17.0.19_10.tar.gz
```

```text
936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88  .formal-tools/tla/tla2tools-1.7.4.jar
6b8c1cb5bc93bedfc7c61435c4e1ab6e688a242dc702a394628d9a9801edb78d  .formal-tools/alloy/org.alloytools.alloy.dist-6.2.0.jar
adb5a2364baa51de1ef91bb9911f5a61d24b045fe1d6647cb8050272a3a8ee75  .formal-tools/downloads/OpenJDK17U-jre_x64_linux_hotspot_17.0.19_10.tar.gz
```

```bash
git status --short .formal-tools projects/domainspec-v2/research/alloy-tla-modeling/invoke-plan/run-results/toolchain
```

```text
?? projects/domainspec-v2/research/alloy-tla-modeling/invoke-plan/run-results/toolchain/
```

Interpretation: `.formal-tools/` remains untracked; only receipt files are visible to git.
