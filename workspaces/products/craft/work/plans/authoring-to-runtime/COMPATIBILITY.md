# Application and historical SFOL compatibility

Status: S05 bounded compatibility implementation. Authority effect: none.

| Authored selection | Parser result | Diagnostic | Behavior |
| --- | --- | --- | --- |
| `profile application-v1` | Target typed application source | None for compatibility | Never enters inline SFOL compatibility; not yet an executable CLI build. |
| `profile legacy-sfol-v1` | Existing legacy carrier | `ALCH_LEGACY_COMPATIBILITY` | Explicit historical semantics; no migration. |
| No source profile, including `logic sfol-v1` | Existing legacy carrier | `ALCH_LEGACY_DEFAULT` | Historical default retained to preserve existing CLI/API behavior. |
| Both source profiles or duplicate source profile | Rejected | `ALCH_PROFILE_CONFLICT` | No precedence or fallback. |
| Unknown source profile | Rejected | `ALCH_PROFILE_UNSUPPORTED` | No fallback. |
| FormalClaim without target profile | Rejected | `ALCH_PROFILE_REQUIRED` | Never parsed as legacy inline logic. |
| Target source plus `logic sfol-v1` | Rejected | `ALCH_PROFILE_CONFLICT` | No mixed proposition language. |

`ParsedDomainSource` exposes `source_profile`, `profile_selection` and
`diagnostics` outside `carrier`. Consequently selection metadata does not
change historical carrier bytes, generated behavior or digest inputs.
Appending an explicit compatibility declaration preserves existing source-line
references and produces identical compilation output in the parity test.
Moving declarations naturally changes source-line trace references.

The local compatibility CLI still requires its existing `--backend local-compat`
for check/build. It prints compatibility diagnostics to stderr; the JSON stdout
receipt remains unchanged. Library parsing performs no logging and returns
diagnostics to its caller. The existing DomainSpec backend selection/default is
unchanged; source profile and code-generation backend are distinct selections.
Other profile-specific prototypes are not relabeled or silently migrated. C01
classifies them in the closed profile architecture as bounded capability
adapters or optional packages; they do not become competing product grammars.

This is an explicit compatibility boundary, not removal of historical input
support. Forcing every existing unprofiled source to add a declaration would
change the agreed historical behavior and is not done. I07 owns the public
target application build. The C01 profile architecture and compatibility matrix
are recorded in [PROFILE-ARCHITECTURE.md](PROFILE-ARCHITECTURE.md).

Tests: parser compatibility matrix and exact compiled-output parity,
FormalClaim mixed-profile rejection, existing source/container tests, and
CLI checks for both compatibility modes and target rejection by local-compat.
