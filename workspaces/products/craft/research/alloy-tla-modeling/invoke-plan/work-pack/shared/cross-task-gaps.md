# Cross-Task Gaps

Status: active

| Gap ID | Gap | Affects | Resolution Route |
| --- | --- | --- | --- |
| G-FMT-001 | No Java runtime on PATH. | SWU-FMT-001 and all formal checks. | Install OpenJDK 17 or supply Java 11+ path. |
| G-FMT-002 | Alloy upstream release metadata lacks checksum digest. | SWU-FMT-002. | Capture URL, release tag, and local checksum. |
| G-FMT-003 | Existing examples may require syntax repair. | SWU-FMT-005, SWU-FMT-006. | Treat parse/check failure as valid receipt and perform repair in a follow-up SWU. |
| G-FMT-004 | Fixture generator design is not yet chosen. | SWU-FMT-007. | Start with fixture schema before generator code. |
