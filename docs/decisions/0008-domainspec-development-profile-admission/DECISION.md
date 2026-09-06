# DomainSpec Development Profile Admission

Decision: `CAL-DPADM-0008`

Question: `G-W4-PROFILE-ADMISSION`

Selected option: `DPADM-1`

Status: `selected`; bounded admission: `admitted`

Decision source: explicit user selection

Decision time: `2026-09-01T17:55:57Z`

## Decision

Admit the exact `ontology-lifecycle-development@0.1` profile epoch for the
CyberAlchemy Lab ontology-lifecycle D65 construction chain and reevaluate
`G-W4` against that immutable epoch.

The admission is separate from the candidate files' `release_admission`
fields. Those remain `not-granted` because this decision is not a public
DomainSpec profile or language release.

## Exact epoch

| Artifact | SHA-256 |
| --- | --- |
| `development-profile-source.json` | `7b6efdd12929763a65a97d1bc480bd6a771a3b6c75e62eacf23297b7f25162f6` |
| `development-profile.json` | `677a20c96ddf9ced1ad0732f8819e1c0806307b171b5837b0d750beeeb0d27e3` |
| `project.json` | `c6150db38723a5ea938b29473aa6da945494083aa7534429c502b0047ecae7b6` |
| DomainSpec kinds registry binding | `bc800afdca36fa701a13ec611e7ee0ef928a4c8d259d48dfac2880a3cc8cbbc4` |
| `relationship-registry.json` | `a349ed6238491e6eccb17db818e315f9b3178de6cc1c0eeb6ab70d8f409fba79` |
| compiled graph | `3fd9db1221b1cfdcd0ad780e5f435923da0e851120ff9b3de6e8310ac2023c3c` |
| compiled source set | `89fa3657f2c48bf50fa569519728a217d37d7c265295b870270dda8900fbc04a` |
| event-sourcing contract | `a0ed7e047bdd0044d069e810f851c5d0807cfb874bd9f1a7c7425df4fdff046d` |
| W3 receipt | `cf7230c5b34c7d4cc4baca98be4f5e7563819d51425e7258f5b2073794ef130c` |
| pre-admission W4 gate snapshot | `7dedb1afe7c1d1c6529ffe82aa30dba17cf4300c248e5efe215e578f13f1d013` |

The Decision Gate request digest is
`ee63846d053acf54bb03838c8f2ab54cfabab00be787d8e53bbc0cd72f4b8b30`.
The prefilter was reproduced before this record was written.

## Effect and boundary

This decision resolves the profile-admission owner gate. It permits a fresh
`G-W4` evaluation. A passing evaluation may make W5 runtime construction
ready.

It does not:

- edit or grant either `release_admission` field;
- release a DomainSpec profile or language;
- make `G-W4` pass without reevaluation;
- implement, accept, or prove conformance of the runtime; or
- authorize publication, deployment, migration, cutover, or external effects.
