# Context dependency review

Status: inspected design proposal. No runtime selection changed.

## Observed source selection

The frozen Context5 source contains 11,165 files and 1,187,416,595 bytes. Its
`base.preflight` reads and hashes this complete set on every invocation, then
checks the environment, mapper and mapped package, and API profile independently.
The measured byte-verification component takes approximately 8–12 seconds per
pass on this host. This component measurement does not explain the complete
duration of an API call by itself.

The API25 qualification source contains 10,133 files. Its runtime protocol
separately declares 790 schema inputs and 30 profile files. Its `Schemas.guard`
actually verifies these declarations. The mapper source contains 1,024 files;
the source producer contains 752. These sets overlap and cannot be added to
obtain an exact execution dependency count.

The current complete qualification selection includes historical receipts,
earlier source packages and test implementations. Their byte integrity matters
for reproducing qualification. Membership in this historical selection alone
does not show that a file supplies a particular runtime computation.

## Proposed separation

1. Preserve the complete qualification manifest and all historical observations.
2. Declare an independently pinned execution manifest containing every selected
   implementation, imported loader, configuration, protocol/schema resource,
   original source/package input, native executable and generated-carrier fixture.
3. Give every execution row an explicit use and selecting parent. Require a
   complete dependency walk and actual import/read observations before claiming
   this selection is complete. A smaller count is not proof of completeness.
4. Verify all selected execution bytes at their declared boundaries. Preserve
   environment identity, original signed source and branch/cut selection,
   native mapper/package identity and original API/schema identity checks.
5. Continue checking actual current policy bytes, owner/mode, operation grants,
   revocation, real clock, deadlines, Session lifetime and disposal independently.
   An execution manifest supplies no permission or governing authority.
6. Requalify an immutable Context successor with all original 50 checks and the
   independent audit, then the affected full API suites and real lifecycle.

An execution selection must fail closed on an unselected dependency. It must not
turn a historic PASS receipt, file metadata or a reused verification stamp into
current permission or current byte verification. Dynamic schema references,
deferred imports and data-selected paths remain explicit obligations.

## Immediate disposition

The descriptor helper's actual 17 cases and full dependency comparison are
sealed. Its measured component ratio is 1.227 and each pass uses 2,419 directory
descriptors. This modest result does not justify claiming a complete latency
repair or changing Context5's frozen semantics.

Finish the current helper's complete 22-case run before freezing the authored
Session boundary successor. Preserve the running API146, export134 and review11
results. Inspect their actual saved outcomes before changing affected paths.
The execution manifest proposal needs further dependency evidence; no Context6
selection or runtime qualification has been produced here.

Authority effect: none. Final owner checkpoint remains R08 after complete S02.
