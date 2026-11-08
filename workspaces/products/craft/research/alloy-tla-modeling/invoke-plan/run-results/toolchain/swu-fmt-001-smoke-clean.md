# SWU-FMT-001 Clean Smoke Receipt

Timestamp: 2026-06-16T21:18:00Z
Result: pass

## Install Surface

- Tool cache: `.formal-tools/`
- Git ignore mechanism: `.git/info/exclude`
- Java runtime: `.formal-tools/jre/current/bin/java`
- TLA+ tools jar: `.formal-tools/tla/tla2tools-1.7.4.jar`
- Alloy jar: `.formal-tools/alloy/org.alloytools.alloy.dist-6.2.0.jar`
- System install fallback: `sudo -n true` required a password, so the run used a portable Temurin JRE.

## Checksum Checks

```text
.formal-tools/downloads/OpenJDK17U-jre_x64_linux_hotspot_17.0.19_10.tar.gz: OK
.formal-tools/tla/tla2tools-1.7.4.jar: OK
6b8c1cb5bc93bedfc7c61435c4e1ab6e688a242dc702a394628d9a9801edb78d  .formal-tools/alloy/org.alloytools.alloy.dist-6.2.0.jar
```

## Command Transcript

### Java

Command:

```bash
.formal-tools/jre/current/bin/java -version
```

Result:

```text
openjdk version "17.0.19" 2026-04-21
OpenJDK Runtime Environment Temurin-17.0.19+10 (build 17.0.19+10)
OpenJDK 64-Bit Server VM Temurin-17.0.19+10 (build 17.0.19+10, mixed mode, sharing)
[exit=0]
```

### TLA+ SANY

Command:

```bash
.formal-tools/jre/current/bin/java -cp .formal-tools/tla/tla2tools-1.7.4.jar tla2sany.SANY \
  projects/domainspec-v2/research/alloy-tla-modeling/invoke-plan/run-results/toolchain/ToolchainSmoke.tla
```

Result:

```text
****** SANY2 Version 2.1 created 24 February 2014
Parsing file .../ToolchainSmoke.tla
Parsing file /tmp/Naturals.tla
Semantic processing of module Naturals
Semantic processing of module ToolchainSmoke
[exit=0]
```

### TLA+ TLC

Command:

```bash
.formal-tools/jre/current/bin/java -cp .formal-tools/tla/tla2tools-1.7.4.jar tlc2.TLC -cleanup \
  projects/domainspec-v2/research/alloy-tla-modeling/invoke-plan/run-results/toolchain/ToolchainSmoke.tla
```

Result:

```text
TLC2 Version 2.19 of 08 August 2024 (rev: 5a47802)
Model checking completed. No error has been found.
3 states generated, 2 distinct states found, 0 states left on queue.
The depth of the complete state graph search is 2.
[exit=0]
```

### Alloy Help

Command:

```bash
.formal-tools/jre/current/bin/java -jar .formal-tools/alloy/org.alloytools.alloy.dist-6.2.0.jar help
```

Result:

```text
The Alloy dispatcher
Available sub-commands:
  natives
  prefs
  solvers
  version
  gui
  commands
  exec
  ls
  lsp
[exit=0]
```

### Alloy Version

Command:

```bash
.formal-tools/jre/current/bin/java -jar .formal-tools/alloy/org.alloytools.alloy.dist-6.2.0.jar version
```

Result:

```text
6.2.0
[exit=0]
```

## Notes

- The raw transcript at `swu-fmt-001-smoke.md` includes a failed `tla2sany.SANY -help` probe. SANY does not expose a useful help flag in this jar, so this clean receipt uses a minimal parser smoke plus a finite TLC smoke.
- The smoke module and config live under `invoke-plan/run-results/toolchain/` and are evidence fixtures, not product models.
