# Independent observed margin adapter review

FLAG: three static integration findings remain. No original runtime or substitution experiment was executed.

## MA01 P1

Original period binding uses ref+sha256; selected adapter capture binding requires path+sha256. Direct dictionary equality always rejects a valid original parent period. Original protocol.binding returns exactly ref+sha256; ReaderChannel validates control.period_binding against that shape. Margin config_check and capture_binding require path+sha256.

Correction: Compare original period binding to an explicitly normalized closed ref binding constructed from independently selected path+sha256, preserving original schemas and exact locator/hash checks.

## MA02 P1

New margin helper live callable and constant selection is incomplete. before_claim alone is held; new capture/kernel/adapter helper bodies and kernel CHECKPOINTS/REMAINING are not independently validated. software checks selected original API callbacks, then only presence of new helper files. K.decide, K.instant, K.require and C.capture execute without code-record checks; K.CHECKPOINTS controls an early successful return. Frozen RuntimeBinding does not freeze these module globals.

Correction: Retain independent externally held selections for the actual captured new helper modules, their executed function code/context/defaults/closure bindings and required constants, checked by a separately selected caller before executing the new gate and at its required exit boundary. Keep fresh source-byte guards.

## MA03 P2

Assessment journal reader can acquire the already-held assessor Vault lock again. Vault.claim holds its exclusive lock before gate. Original completed_candidate_application falls back to host.vault when application_journal_scope is None; otherwise ApplicationJournal locks the selected root. Original schema permits None and no adapter constraint prevents selecting host.vault.root. The additional completed-candidate read is unconditional even if original preflight resolved an admitted application without this read.

Correction: Before delegation under Vault.claim, require a nonnull independently selected application_journal_scope with canonical root distinct from the assessor Vault root (and verify selected input ownership); fail before calling original assessment preflight/completed-candidate reader when the distinct journal cannot be established. Preserve original readers and retries.

The fresh gate placement, original retries/recovery, separate actual assessment attachment, protected mode selection, final real-clock ordering, complete-tail arithmetic and strict equality refusal are coherent in the reviewed source. 157 metadata bindings and supplied manifest/handoff identities passed; 8 staged Python files compiled without execution. Entire original Vault.claim AST is recovered by removing only the added gate; all original Service methods other than constructor and _call remain unchanged. Selected current metadata references are acyclic.

Existing author records report 50 pure controls, not native/runtime or empirical qualification. The null policy and unresolved runtime selection remain unqualified. New Source helper/family, complete source/profile/code closure, actual assembly, measured full-tail/load/overhead/uncertainty, and all original whole-learning/security/recovery gates remain pending. T03 stays open.

Only this own report directory was written; no frozen or shared source/status changes. Machine-readable detail is in review.json.
