import FiniteSourceCatalog
import IntentRecordShape

set_option autoImplicit false

namespace RelationalSuccessor.CandidateCapturedMetadata
open RelationalSuccessor
abbrev RawRecord := _root_.RelationalSuccessor.CandidateIntentRecordShape.RawRecord
abbrev Artifact (α : Type) := _root_.RelationalSuccessor.CandidateFiniteSourceCatalog.Artifact α
abbrev UniqueBy {τ κ : Type} (key : τ → κ) (values : List τ) : Prop :=
  _root_.RelationalSuccessor.CandidateFiniteSourceCatalog.UniqueBy key values
abbrev uniqueCheck {τ κ : Type} [DecidableEq τ] [DecidableEq κ] (key : τ → κ) (values : List τ) : Bool :=
  _root_.RelationalSuccessor.CandidateFiniteSourceCatalog.uniqueCheck key values

-- These are distinct statement roles. Their reference values need not be
-- unequal; no identity equivalence or authority grant follows from a binding.
structure IdentityBinding where
  ref : RevisionRef
  source : RevisionRef
  token : String
  frame : Frame
  deriving DecidableEq, Repr

structure OwnerBinding where
  ref : RevisionRef
  source : RevisionRef
  token : String
  holder : RevisionRef
  scope : RevisionRef
  frame : Frame
  deriving DecidableEq, Repr

structure ScopeBinding where
  ref : RevisionRef
  source : RevisionRef
  token : String
  scope : RevisionRef
  ownerBinding : RevisionRef
  frame : Frame
  deriving DecidableEq, Repr

structure Receipt where
  ref : RevisionRef
  schema : RevisionRef
  artifact : Artifact RawRecord
  frame : Frame
  identity : IdentityBinding
  owner : OwnerBinding
  scope : ScopeBinding
  deriving DecidableEq, Repr

-- Independently captured context. These lists are not copied from a proposal.
-- Authentic capture, source byte parsing and policy validity remain premises
-- for a later provider; this module proves structural binding, not signatures.
structure Context where
  frame : Frame
  schema : RevisionRef
  records : List Receipt
  roots : List Receipt
  identities : List IdentityBinding
  owners : List OwnerBinding
  scopes : List ScopeBinding
  deriving DecidableEq, Repr

def allReceipts (context : Context) : List Receipt := context.records ++ context.roots

def allArtifacts (context : Context) : List (Artifact RawRecord) :=
  (allReceipts context).map Receipt.artifact

structure ReceiptMeaning (context : Context) (receipt : Receipt) : Prop where
  issued : receipt ∈ context.roots
  frame : receipt.frame = context.frame
  schema : receipt.schema = context.schema
  sourceKind : receipt.artifact.sourceKind = receipt.artifact.body.kind
  identityOwned : receipt.identity ∈ context.identities
  identityFrame : receipt.identity.frame = receipt.frame
  identitySource : receipt.identity.source = receipt.artifact.ref
  identityToken : receipt.identity.token = receipt.artifact.body.node_id
  ownerOwned : receipt.owner ∈ context.owners
  ownerFrame : receipt.owner.frame = receipt.frame
  ownerSource : receipt.owner.source = receipt.artifact.ref
  ownerToken : receipt.owner.token = receipt.artifact.body.owner_ref
  ownerScope : receipt.owner.scope = receipt.frame.scope
  scopeOwned : receipt.scope ∈ context.scopes
  scopeFrame : receipt.scope.frame = receipt.frame
  scopeSource : receipt.scope.source = receipt.artifact.ref
  scopeToken : receipt.scope.token = receipt.artifact.body.scope_ref
  scopeValue : receipt.scope.scope = receipt.frame.scope
  ownerJoin : receipt.scope.ownerBinding = receipt.owner.ref

def receiptCheck (context : Context) (receipt : Receipt) : Bool :=
  decide (receipt ∈ context.roots) && decide (receipt.frame = context.frame) &&
  decide (receipt.schema = context.schema) &&
  decide (receipt.artifact.sourceKind = receipt.artifact.body.kind) &&
  decide (receipt.identity ∈ context.identities) &&
  decide (receipt.identity.frame = receipt.frame) &&
  decide (receipt.identity.source = receipt.artifact.ref) &&
  decide (receipt.identity.token = receipt.artifact.body.node_id) &&
  decide (receipt.owner ∈ context.owners) && decide (receipt.owner.frame = receipt.frame) &&
  decide (receipt.owner.source = receipt.artifact.ref) &&
  decide (receipt.owner.token = receipt.artifact.body.owner_ref) &&
  decide (receipt.owner.scope = receipt.frame.scope) &&
  decide (receipt.scope ∈ context.scopes) && decide (receipt.scope.frame = receipt.frame) &&
  decide (receipt.scope.source = receipt.artifact.ref) &&
  decide (receipt.scope.token = receipt.artifact.body.scope_ref) &&
  decide (receipt.scope.scope = receipt.frame.scope) &&
  decide (receipt.scope.ownerBinding = receipt.owner.ref)

theorem receipt_check_exact (context : Context) (receipt : Receipt) :
    receiptCheck context receipt = true ↔ ReceiptMeaning context receipt := by
  have fields : ReceiptMeaning context receipt ↔
      receipt ∈ context.roots ∧ receipt.frame = context.frame ∧ receipt.schema = context.schema ∧
      receipt.artifact.sourceKind = receipt.artifact.body.kind ∧
      receipt.identity ∈ context.identities ∧ receipt.identity.frame = receipt.frame ∧
      receipt.identity.source = receipt.artifact.ref ∧ receipt.identity.token = receipt.artifact.body.node_id ∧
      receipt.owner ∈ context.owners ∧ receipt.owner.frame = receipt.frame ∧
      receipt.owner.source = receipt.artifact.ref ∧ receipt.owner.token = receipt.artifact.body.owner_ref ∧
      receipt.owner.scope = receipt.frame.scope ∧ receipt.scope ∈ context.scopes ∧
      receipt.scope.frame = receipt.frame ∧ receipt.scope.source = receipt.artifact.ref ∧
      receipt.scope.token = receipt.artifact.body.scope_ref ∧ receipt.scope.scope = receipt.frame.scope ∧
      receipt.scope.ownerBinding = receipt.owner.ref := by
    constructor
    · intro h; exact ⟨h.issued, h.frame, h.schema, h.sourceKind, h.identityOwned,
        h.identityFrame, h.identitySource, h.identityToken, h.ownerOwned, h.ownerFrame,
        h.ownerSource, h.ownerToken, h.ownerScope, h.scopeOwned, h.scopeFrame,
        h.scopeSource, h.scopeToken, h.scopeValue, h.ownerJoin⟩
    · rintro ⟨a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s⟩
      exact ⟨a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s⟩
  rw [fields]
  simp only [receiptCheck, Bool.and_eq_true, decide_eq_true_eq, and_assoc]

structure ContextMeaning (context : Context) : Prop where
  artifacts : UniqueBy (fun artifact => artifact.ref.key) (allArtifacts context)
  receipts : UniqueBy (fun receipt => receipt.artifact.ref.key) (allReceipts context)
  identityRefs : UniqueBy (fun binding => binding.ref.key) context.identities
  ownerRefs : UniqueBy (fun binding => binding.ref.key) context.owners
  scopeRefs : UniqueBy (fun binding => binding.ref.key) context.scopes
  completeRecords : ∀ receipt ∈ context.records, ReceiptMeaning context receipt
  completeRoots : ∀ receipt ∈ context.roots, ReceiptMeaning context receipt

def contextCheck (context : Context) : Bool :=
  uniqueCheck (fun artifact => artifact.ref.key) (allArtifacts context) &&
  uniqueCheck (fun receipt => receipt.artifact.ref.key) (allReceipts context) &&
  uniqueCheck (fun binding => binding.ref.key) context.identities &&
  uniqueCheck (fun binding => binding.ref.key) context.owners &&
  uniqueCheck (fun binding => binding.ref.key) context.scopes &&
  context.records.all (receiptCheck context) && context.roots.all (receiptCheck context)

theorem context_check_exact (context : Context) :
    contextCheck context = true ↔ ContextMeaning context := by
  simp only [contextCheck, Bool.and_eq_true, CandidateFiniteSourceCatalog.unique_check_exact, List.all_eq_true,
    receipt_check_exact]
  constructor
  · rintro ⟨⟨⟨⟨⟨⟨a, b⟩, c⟩, d⟩, e⟩, f⟩, g⟩; exact ⟨a, b, c, d, e, f, g⟩
  · intro h; exact ⟨⟨⟨⟨⟨⟨h.artifacts, h.receipts⟩, h.identityRefs⟩, h.ownerRefs⟩,
      h.scopeRefs⟩, h.completeRecords⟩, h.completeRoots⟩

def lookup (context : Context) (ref : RevisionRef) : Option Receipt :=
  CandidateFiniteSourceCatalog.lookup (fun (receipt : Receipt) => receipt.artifact.ref) context.records ref

theorem records_unique_ref (context : Context) (valid : ContextMeaning context) :
    UniqueBy (fun (receipt : Receipt) => receipt.artifact.ref) context.records := by
  intro a ha b hb same
  exact valid.receipts a (by simp [allReceipts, ha]) b (by simp [allReceipts, hb])
    (congrArg RevisionRef.key same)

structure ResolvedMeaning (context : Context) (expected : Frame) (ref : RevisionRef)
    (receipt : Receipt) : Prop where
  contextValid : ContextMeaning context
  frame : context.frame = expected
  source : receipt.artifact.ref = ref
  owned : receipt ∈ context.records
  receiptMeaning : ReceiptMeaning context receipt

def resolve (context : Context) (expected : Frame) (ref : RevisionRef) : Option Receipt :=
  if contextCheck context then
    if context.frame = expected then lookup context ref else none
  else none

theorem resolve_exact (context : Context) (expected : Frame) (ref : RevisionRef) (receipt : Receipt) :
    resolve context expected ref = some receipt ↔ ResolvedMeaning context expected ref receipt := by
  constructor
  · intro accepted
    unfold resolve at accepted
    split at accepted
    · rename_i checked
      have valid := (context_check_exact context).mp checked
      split at accepted
      · rename_i frame
        have found := CandidateFiniteSourceCatalog.lookup_sound
          (fun (receipt : Receipt) => receipt.artifact.ref) context.records ref receipt accepted
        exact ⟨valid, frame, found.2, found.1, valid.completeRecords receipt found.1⟩
      · simp at accepted
    · simp at accepted
  · intro meaning
    have found := CandidateFiniteSourceCatalog.lookup_complete
      (fun (receipt : Receipt) => receipt.artifact.ref) context.records ref receipt
      (records_unique_ref context meaning.contextValid) meaning.owned meaning.source
    simp [resolve, (context_check_exact context).mpr meaning.contextValid,
      meaning.frame, lookup, found]

theorem resolved_scope_exact (context : Context) (expected : Frame) (ref : RevisionRef)
    (receipt : Receipt) (resolved : resolve context expected ref = some receipt) :
    receipt.scope.scope = expected.scope ∧ receipt.owner.scope = expected.scope := by
  have meaning := (resolve_exact context expected ref receipt).mp resolved
  have frame := meaning.receiptMeaning.frame.trans meaning.frame
  exact ⟨meaning.receiptMeaning.scopeValue.trans (congrArg Frame.scope frame),
    meaning.receiptMeaning.ownerScope.trans (congrArg Frame.scope frame)⟩

theorem wrong_frame_refuses (context : Context) (expected : Frame) (ref : RevisionRef)
    (wrong : context.frame ≠ expected) : resolve context expected ref = none := by
  simp only [resolve, if_neg wrong]
  split <;> rfl

theorem invalid_context_refuses (context : Context) (expected : Frame) (ref : RevisionRef)
    (invalid : ¬ ContextMeaning context) : resolve context expected ref = none := by
  cases decoded : resolve context expected ref with
  | none => rfl
  | some receipt => exact False.elim (invalid ((resolve_exact context expected ref receipt).mp decoded).contextValid)

theorem absent_ref_refuses (context : Context) (expected : Frame) (ref : RevisionRef)
    (absent : ∀ receipt ∈ context.records, receipt.artifact.ref ≠ ref) :
    resolve context expected ref = none := by
  cases decoded : resolve context expected ref with
  | none => rfl
  | some receipt =>
    have meaning := (resolve_exact context expected ref receipt).mp decoded
    exact False.elim (absent receipt meaning.owned meaning.source)

#print axioms receipt_check_exact
#print axioms context_check_exact
#print axioms records_unique_ref
#print axioms resolve_exact
#print axioms resolved_scope_exact
#print axioms wrong_frame_refuses
#print axioms invalid_context_refuses
#print axioms absent_ref_refuses
end RelationalSuccessor.CandidateCapturedMetadata
