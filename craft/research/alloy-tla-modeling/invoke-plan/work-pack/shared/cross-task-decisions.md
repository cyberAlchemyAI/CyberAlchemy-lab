# Cross-Task Decisions

Status: pass

| Decision ID | Decision | Rationale | Owner |
| --- | --- | --- | --- |
| D-FMT-001 | Use pinned stable releases for first surface. | Avoid drifting under changing latest/pre-release behavior while examples are unvalidated. | invoke plan |
| D-FMT-002 | Keep tool binaries out of git. | Prevent large third-party binaries and license/provenance ambiguity in the research folder. | invoke plan |
| D-FMT-003 | Start TLA+ with safety checks, not liveness. | TLA+ v1.7.4 release notes mention a liveness multi-worker fix; current saga model first needs safety syntax/semantics. | invoke plan |
| D-FMT-004 | Execute one SWU at a time. | Toolchain install, wrapper scripts, model validation, and fixture design have different failure modes. | invoke plan |
| D-FMT-005 | Do not mutate DomainSpec canonical definitions. | The tower is research-local and the `orchestrates` issue remains governance residue. | invoke plan |
