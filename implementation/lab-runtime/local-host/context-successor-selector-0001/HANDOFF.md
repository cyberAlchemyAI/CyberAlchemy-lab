# Context successor selection handoff

This package is a **pure selection and projection candidate**, not a Context delivery. `execute_context()` always refuses. It reads no protected Source body and installs no role files. It was tested with synthetic effect reviews; those tests do not represent a reviewed real Source, Reader, or Mapper run.

## Selection contract

`adapter.select()` replays the frozen Mapper selector over fresh Source and Reader inputs. It requires the exact dynamically selected Mapper source manifest, a 54-file package manifest representing the native 55-leaf closure including the manifest itself, a PASS/no-retry Mapper terminal bound to the package digest, external OS exit 0, and an independently authored Mapper effect review whose **outside-supplied SHA-256** binds all five Source/Reader/Mapper digests, terminal, and exit evidence. The outside pin must come from a separate reviewer, not from this selector or the effect controller.

It projects the five original `api-v25` bridge, selection, protocol, profile, and source-manifest files and seven original Context role/policy/evidence files into memory. Context base, generation, build, API source selection, API bridge, API profile, and Reader implementation evidence receive fresh same-family paths and digest bindings. `control.py` and `build.py` use the later reviewed JIT-guarded projections, with the Context authorization path rooted under the selected Source role. All five Context Python files retain the original `_t35_effect_refused()` guard. No Context source manifest or effect release is produced.

Run `python3 -m unittest -v test_adapter.py` and `python3 -O -m unittest -v test_adapter.py` from this directory. The tests use synthetic manifests and reviews to exercise selection and refusal only.

## Remaining original-role path

1. Independently review the corrected Source stage's one-shot effect and supply its actual package digest and external review pin. The stage umask correction changed `context-successor-stage-0001/freeze.json`, while the selected public `context-successor-recovery-0001/freeze.json` and Source manifest remained stable. These Reader, Mapper, and Context selectors pin the public recovery profile, not the stage freeze, so the correction alone does **not** invalidate their pins. The independent Source effect review must still verify the corrected release bytes and actual terminal. The absolute Source period remains a separate currentness condition; it expires at 2026-10-21 15:00 UTC.
2. Release and independently review a fresh Reader cold-open bound to that Source package. Select its actual public manifest and private receipt through the Reader/Mapper predecessor selectors.
3. Adapt the frozen Mapper native verifier to the fresh family without weakening its 55-leaf and byte-parity checks, release Mapper once, and independently review its actual package and terminal. This selector can then consume its external review.
4. Design an independently reviewed Context release with a current host-policy/Context issuer, exclusive service custody, a durable output root, a private JIT root, and expiry validation. The selected JIT build still contains an old `/tmp/cal-context-jit-private-20261020-0001` literal behind its effect refusal. Replace and review it as part of release, not by assuming this projection enables it.
5. Only after the Context release and its actual output pass independent review should an API service or current Context delivery claim be made. This package claims only in-memory projection of original role bytes.

The predecessor Context stage and JIT files are SHA-pinned. This package does not modify them or any frozen Source, Reader, or Mapper package.
