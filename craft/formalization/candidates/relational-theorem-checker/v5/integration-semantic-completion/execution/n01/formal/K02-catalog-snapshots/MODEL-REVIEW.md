Complete original catalog snapshot review

The new byte entrypoint derives all three original catalogs from checked raw
captures. The caller supplies the source, its qualifiers, and three named snapshots:
metadata-context, payload-context and owned-qualifier-context. It cannot supply
separate typed catalogs or JSON trees on this entrypoint. All five captures pass
one combined budget and ordered preflight before any catalog is decoded.

| Snapshot | Complete contents retained |
| --- | --- |
| Metadata | Frame/schema; all receipt records/roots; every identity, owner and scope binding. Each receipt includes full artifact body/bytes/ref/kind/review, frame and bindings. |
| Payload | Frame; full artifact records; all role/token/ref bindings; full framed role approvals. |
| Owned qualifiers | Both resolution and addressing-role catalogs, every record/root, target, token, original content, review and frame. |

The full original source record still contains fourteen fields, its five-field
payload and four-field companion relation references. The new snapshots serialize
complete original context structures; they do not replace the source with a smaller
relation witness. Ordered arrays preserve every duplicate, alias and unused record.
Original role, non-equivocation, full-frame and source/payload checks still run.

The main theorem `CandidateCatalogSnapshots.run_exact` says:

    captured-catalog run = ok(output)
      iff there exist original typed catalogs such that
        exact snapshot bytes parse and completely represent those catalogs
        AND original guarded source-byte meaning holds for output.

The latter meaning includes exact original source/qualifier parsing, all five
capture budgets/preflights, the original full structural pipeline and the source
revision digest join. The snapshot meanings are independent object, field and
positional-array propositions; they do not call the executable decoder. The generic
payload body decoder preserves the original polymorphic catalog. The supplied JSON
schema and worked controls instantiate its String payload profile.

Example: the original 1208-byte Intent Resolution source selects a project and a
goal, retains an excluded subject and two satisfaction tests. A coherent synthetic
context using its actual hash succeeds through all three snapshot decoders. Repeated
identical metadata records succeed and retain two records. An unused payload record
with conflicting content refuses; an unused conflicting owned-role record also
refuses. Missing owner fields, swapped snapshot kinds and embedded byte 256 refuse.
The supported exact numeric adapter accepts epoch 42.0 as 42 and byte 255.0 as 255.

Twenty-two general declarations pass eight fresh new-module compile/replay calls,
forty-four declaration axiom inspections and eight import audits. Seventeen runtime
controls pass in each phase. Thirty-three decoded JSON shape controls pass, and the
schema audit confirms the full original source body and exact bytes are retained in
both metadata record and root. The 125 unchanged dependency modules are bound to
registered matching-phase outputs and reused; they were not rebuilt. Checking uses
the same Lean kernel and does not satisfy mandatory independent checking. Compilation
and evaluation durations are not measured operational time/memory limits.

A snapshot is a captured statement about nested artifacts. Its valid hash proves
integrity of that snapshot. It does not authenticate its owner, validate every
nested artifact digest or prove that an artifact body was parsed from its embedded
content. These are explicit original source/provider policy requirements. Fixture
encoders are control generators, not a proved general serializer. JSON schemas
validate decoded shapes; raw byte/schema equivalence is not claimed.

The next integration requirements are nested artifact source/body/content/digest
correspondence where those raw artifacts are consumed, owned profile-selection
binding, actual authentic-root/source policy evidence and the authentic world/
selection contract. The world and claim remain explicit original inputs. Mandatory
consumers, whole-theory countermodels, independent checking and measured limits
also remain. The fixed five-capture manifest is complete for these context snapshot
inputs; it is not a complete manifest of all future provider/profile/world inputs.

All 263 inherited IDs remain open and all 90 original discharges retain scope.
K04/global assessments remain pending. Only N00 is accepted; this component neither
accepts N01 nor completes the seven-extension/twenty-task plan.
