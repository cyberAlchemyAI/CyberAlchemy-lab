namespace RelationalExtensions.Evidence

structure Ref where
  id : String
  version : String
  deriving DecidableEq, Repr

structure Frame where
  profile : String
  context : Ref
  subject : Ref
  target : Ref
  scope : String
  epoch : Nat
  deriving DecidableEq, Repr

structure EvidenceRef where
  token : String
  sourceIdentity : String
  deriving DecidableEq, Repr

structure Assertion where
  id : String
  kind : String
  subject : Ref
  target : Ref
  scope : String
  kindVersion : String
  deriving DecidableEq, Repr

structure Node where
  ref : Ref
  kind : String
  deriving DecidableEq, Repr

structure Policy where
  kind : String
  version : String
  pairs : List (String × String)
  deriving DecidableEq, Repr

structure Assessment where
  token : String
  mode : String
  subject : Ref
  target : Ref
  scope : String
  accepted : Bool
  deriving DecidableEq, Repr

structure Source where
  identity : String
  frame : Frame
  assertions : List Assertion
  assessments : List Assessment
  roots : List String
  nodes : List Node
  policies : List Policy
  deriving DecidableEq, Repr

def endpointPolicy (source : Source) (selected : Assertion) : Bool :=
  source.policies.any fun policy =>
    selected.kind == policy.kind && selected.kindVersion == policy.version &&
    source.nodes.any fun left => left.ref == selected.subject &&
      source.nodes.any fun right => right.ref == selected.target && policy.pairs.contains (left.kind, right.kind)

def Linked (source : Source) (selected : Assertion) (frame : Frame) : Prop :=
  selected ∈ source.assertions ∧ selected.kind = "relation.conforms-to" ∧ source.frame = frame ∧
  selected.subject = frame.subject ∧ selected.target = frame.target ∧ selected.scope = frame.scope ∧ endpointPolicy source selected = true

def Eligible (source : Source) (frame : Frame) (refs : List EvidenceRef) (assessment : Assessment) : Prop :=
  ⟨assessment.token, source.identity⟩ ∈ refs ∧ assessment.mode = "conformance" ∧
  assessment.subject = frame.subject ∧ assessment.target = frame.target ∧ assessment.scope = frame.scope ∧ assessment.accepted = true

instance (source : Source) (selected : Assertion) (frame : Frame) : Decidable (Linked source selected frame) := by
  unfold Linked; infer_instance
instance (source : Source) (frame : Frame) (refs : List EvidenceRef) (assessment : Assessment) : Decidable (Eligible source frame refs assessment) := by
  unfold Eligible; infer_instance

def supports (source : Source) (selected : Assertion) (frame : Frame) (refs : List EvidenceRef) : List Assessment :=
  if Linked source selected frame then source.assessments.filter (fun a => decide (Eligible source frame refs a)) else []

def Meaning (source : Source) (selected : Assertion) (frame : Frame) (refs : List EvidenceRef) : Prop :=
  Linked source selected frame ∧ ∃ a ∈ source.assessments, Eligible source frame refs a

theorem all_supports_exact (source : Source) (selected : Assertion) (frame : Frame)
    (refs : List EvidenceRef) (a : Assessment) :
    a ∈ supports source selected frame refs ↔ Linked source selected frame ∧ a ∈ source.assessments ∧ Eligible source frame refs a := by
  by_cases h : Linked source selected frame <;> simp [supports, h]

theorem projection_sound_complete (source : Source) (selected : Assertion) (frame : Frame)
    (refs : List EvidenceRef) :
    (∃ a, a ∈ supports source selected frame refs) ↔ Meaning source selected frame refs := by
  constructor
  · rintro ⟨a, ha⟩
    obtain ⟨linked, member, eligible⟩ := (all_supports_exact source selected frame refs a).mp ha
    exact ⟨linked, a, member, eligible⟩
  · rintro ⟨linked, a, member, eligible⟩
    exact ⟨a, (all_supports_exact source selected frame refs a).mpr ⟨linked, member, eligible⟩⟩

structure Projection where
  evidence : List Assessment
  roots : List String
  deriving DecidableEq, Repr

def project (source : Source) (selected : Assertion) (frame : Frame) (refs : List EvidenceRef) : Projection :=
  ⟨supports source selected frame refs, source.roots⟩

theorem evidence_never_creates_roots (source : Source) (selected : Assertion) (frame : Frame)
    (refs : List EvidenceRef) : (project source selected frame refs).roots = source.roots := rfl

theorem rejected_has_no_support (source : Source) (selected : Assertion) (frame : Frame)
    (refs : List EvidenceRef) (a : Assessment) (rejected : a.accepted = false) :
    a ∉ supports source selected frame refs := by
  intro member
  have positive := ((all_supports_exact source selected frame refs a).mp member).2.2.2.2.2.2.2
  rw [rejected] at positive
  cases positive

def legacyReference (token sourceIdentity : String) : List EvidenceRef := [⟨token, sourceIdentity⟩]
theorem legacy_token_preserved (token sourceIdentity : String) :
    legacyReference token sourceIdentity = [⟨token, sourceIdentity⟩] := rfl

#print axioms all_supports_exact
#print axioms projection_sound_complete
#print axioms evidence_never_creates_roots
#print axioms rejected_has_no_support
#print axioms legacy_token_preserved
end RelationalExtensions.Evidence
