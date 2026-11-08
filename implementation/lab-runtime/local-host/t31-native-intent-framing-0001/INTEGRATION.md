# Current intent-framing originals for T31

This candidate supplies exactly the two `intent-framing` transitions in the
existing workflow definition. `intent_bundle.py` reads six originals from one
current signed Source cut: Intent, Work, Goal, CoordinationContext, Project, and
the Goal/Project relation. It uses the same `frame.construct` inputs as the
current workflow fixture to produce a private IntentResolution. The second
transition returns the original current Source Work bytes unchanged. The
private bundle retains all six input originals, the generated resolution,
exact file hashes, source/profile/cut, actor/run, and an authority-none receipt.
Cold consumption also exposes the six verified original `(header, bytes)` pairs.

`prepare_intent_config.py` selects this bundle together with one actual first
Session native emission. It requires equal Source cut, selected API Source and
profile, principal, and run reference, plus exact header and raw-byte equality
for the four overlapping Intent, Work, Goal, and CoordinationContext originals.
It then selects the two exact transition
outputs. It creates a private configuration only; it does not admit records or
resolve the workflow owner outcome.

## Integration into the T31 final package

1. Include both helper modules and the selected `frame.py` as exact package
   members. The installed selected-python launcher must load them from its own
   selected root. Bundle preparation must run only after the final package is
   installed and the T03 first Session has produced its native emission.
2. In `ArchiveProof.capture`, dispatch an `original_bundles` entry with
   `kind: intent-framing` to this exact installed `intent_bundle.consume`.
   Preserve its records, two sealed transition routes, manifest and original
   receipt bindings with the existing duplicate-equality rule. Require a
   native-emission selection and compare its Source/profile/cut/principal/run
   and four overlapping original `(header, bytes)` pairs directly in
   `ArchiveProof.capture`; direct `run_current` configs can skip the config
   preparer. Retain the native-emission selection for identity and package pin.
3. In `current_fixture.example`, require header and raw-byte equality before
   its current Source and `frame.construct` loops replace an existing proof
   record at the same version reference. This covers Work and IntentResolution.
4. Run the two-stage config through the T31 final supervisor using a new
   private evidence root. The signed Source family and earlier failed claims
   remain unchanged. Check both native terminal results, original output
   bytes, process results, cold readbacks, and the cumulative T31 ledger.

## Verification boundary

The focused test module covers deterministic resolution, unchanged Work,
foreign Goal/Project relation, raw-edge projection access, private cold
readback/tamper refusal, and foreign native Work/cut config refusal. It has not yet run
against the installed final0004 package or produced a native transition.
