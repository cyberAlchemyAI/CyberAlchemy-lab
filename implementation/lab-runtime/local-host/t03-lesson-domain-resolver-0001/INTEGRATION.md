# Exact local Lesson Application reference resolver candidate

Status: source and focused tests ready for independent review; **not selected by API75 or the installed final0003 product**.

## Observed need

The retained final0003 later Session failed its positive `lesson.apply` call. The exact postclaim API error is `conflict` with `retry_policy: no-retry`. Its validation report passed source/target/schema/core, typed connection, and private boundary checks, but returned `not-evaluable` for `remaining-domain-reference-*`: API75 has no full domain resolver for `cal.artifact-type.lesson-application/v1`. `operation.inspect` records `posture: failed`, `retry_allowed: false`, and `reconciliation_required: false`. The attempt has allocated, claim, and terminal result journal originals. The original private Session was disposed with memory and selection erasure.

The separate fallback margin diagnostic ran after the terminal journal existed and then asserted that the journal was empty. Its failure is secondary and does not change the primary resolver finding.

Cold evidence: `/home/vlad_/.local/share/cyberalchemy-lab/t03-installed-learning-evidence-20261026-0001/LATER-FAILED-COLD-READBACK-0001.json` (SHA-256 `21d3da934810472943b82b80cec0f2b121eeb0780b033fbda3ff384ca6736311`). The private originals remain under `/tmp/cal-T03-retained-application-mcpu03eo/workspace`.

## Successor integration

1. Copy `lesson_application_references.py` into the next common API successor package under that exact filename. Select its bytes in the successor Source manifest and profile.
2. In the successor `WorkflowCandidateHandlers.__init__(host)`, after `super().__init__(host)`, construct `LessonApplicationReferences(host)` and assign it to `self.resolution_references` only when `host.channel.policy['schema_version'] == 'lab-local-lesson-application-policy/v2-candidate'`. The existing `CandidateHandlers.validate` hook invokes `supports(target, message)` and `resolve(target, message, post)` before generic carrier fallback. All other carriers and unsupported application states remain not-evaluable.
3. Rebuild the successor source/profile, final package, archive, and fresh installation. Do not edit API75, final0003 installed files, the failed journal, or the failed idempotency key. Use a fresh Session, workspace, and key for the later application test.
4. Verify the native `lesson.apply` result and `operation.inspect`, then independent `lesson.assess` after parent close, then a fresh consumer Session. A recorded positive result is required before considering the T03 sequence complete.

The resolver handles only an admitted current signed Operational Lesson selected in an actual live parent Session, with a bound selected applicability witness, matching instruction, same source cut/scope/owner, one exact relation and evidence reference, and no conflicts, overrides, successors, or external Tool action. It verifies the prospective candidate original bytes, the exact proposal selected by the application routing, and selected resolver source bytes. That proposal check also closes direct `change.validate` calls under the application grant. It produces reference evidence and no authority or admission effect.

## Standalone `change.validate` invariant sweep

The application policy also permits direct `change.validate`, so the resolver must make a PASS independent of the `lesson.apply` preparation method. Compared against the selected v8 `preparation.py` constructor, `live`, and `preflight`:

| v8 invariant | Resolver closure or delegated guard |
| --- | --- |
| Exact selected Service, parent operator grant, selected host/API Source, current schemas and workspace | `SessionAttachment.material_guard()`, current source projection check, policy guard, and explicit selected resolver and method manifest membership |
| Independent application policy and selected routing/method/authorization bytes | `policy_guard()`, original routing read, closed routing shape, method equality and selected original, exact development authorization binding |
| Actual live Source8 parent resource, grant identities, active Session, same source cut/Assignment/Principal, and actual selected Lesson output | `SessionAttachment.material_guard()` at entry and exit, plus exact expected Session/cut/Assignment/owner comparisons in `validate_selected` |
| Selected instruction, applicability, no veto, unexpired one-Lesson selection, no unresolved conflict/override | Exact selected parent originals, one selected item, instruction/assignment/cut/scope checks, empty conflict/override and successor references |
| Signed current Lesson and original bytes/header, scope, relation and evidence refs | Current exact subject, byte SHA/header equality, signed body scope, exact three reference selectors |
| Declared action bounds within live delegated operations | Resource lifetime lock, material guard and subset check against `resource.bridge.permission().operations` |
| Exact selected ChangeProposal and candidate original, no extra authority or Tool action | Routing `proposal_binding` original equals incoming message, exact target content original, candidate state/effect checks; resolver does not dispatch or admit |

`lesson.apply` alone still performs the full preparation preflight, including request Actor/key and a second live check. The generic `change.validate` preflight handles its own Actor/key and schema. The resolver above supplies the missing domain-specific closure for the direct validation path.

## Focused checks

Run `python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t03-lesson-domain-resolver-0001 -p 'test_*.py' -v`. The 18 tests cover exact resolution, foreign Session/Assignment/Lesson/cut/scope/owner/applicability/evidence/relation, veto/ambiguous selection, selected method/authorization/action bounds, duplicate target, changed original bytes, and unrelated carriers/policies remaining unsupported. They are source-level checks; actual native success awaits successor selection and execution.
