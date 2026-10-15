import CompleteBodyProfiles
set_option autoImplicit false
namespace RelationalSuccessor.CandidateBodyDispatch
open CandidateBindingAst (J Decoder)
open CandidateTypedBodies (Kind decoderForKind)
abbrev PayloadBody := CandidateTypedBodies.Body

def kindName : Kind → String
  | .intent => "intent"
  | .agent_assignment => "agent-assignment"
  | .goal => "goal"
  | .product => "product"
  | .product_capability => "product-capability"
  | .project => "project"
  | .research_inquiry => "research-inquiry"

def decodeKind : String → Option Kind
  | "intent" => some .intent
  | "agent-assignment" => some .agent_assignment
  | "goal" => some .goal
  | "product" => some .product
  | "product-capability" => some .product_capability
  | "project" => some .project
  | "research-inquiry" => some .research_inquiry
  | _ => none

theorem kind_token_exact (text : String) (kind : Kind) :
    decodeKind text = some kind ↔ text = kindName kind := by
  cases kind <;> simp [decodeKind,kindName]
  all_goals split <;> simp_all
  all_goals split <;> simp_all
  all_goals split <;> simp_all
  all_goals split <;> simp_all
  all_goals split <;> simp_all
  all_goals split <;> simp_all
  all_goals split <;> simp_all

def bodyKind : PayloadBody → Kind
  | .intent _ => .intent
  | .agent_assignment _ => .agent_assignment
  | .goal _ => .goal
  | .product _ => .product
  | .product_capability _ => .product_capability
  | .project _ => .project
  | .research_inquiry _ => .research_inquiry

theorem fixed_decoder_constructor_exact (kind : Kind) (ast : J) (output : PayloadBody)
    (meaning : (decoderForKind kind).Meaning ast output) : bodyKind output = kind := by
  cases kind <;> simp only [decoderForKind,CandidateTypedBodies.mapped,
    CandidateTypedBodies.MappedMeaning] at meaning
  all_goals rcases meaning with ⟨input,_,same⟩; subst output; rfl

theorem lookup_none_exact (entries : CandidateJsonSource.Entries) (key : String) :
    CandidateJsonSource.lookup entries key = none ↔ key ∉ entries.map Prod.fst := by
  induction entries with
  | nil => simp [CandidateJsonSource.lookup]
  | cons first rest ih =>
    rcases first with ⟨name,value⟩
    by_cases same : name = key
    · simp [CandidateJsonSource.lookup,same]
    · simp [CandidateJsonSource.lookup,same,ih,Ne.symm same]

def goalSchema : String := "cyberalchemy-lab-goal/v1"

def TagMeaning (entries : CandidateJsonSource.Entries) (kind : Kind) : Prop :=
  if kind = .goal then
    "kind" ∉ entries.map Prod.fst ∧ ("schema_version", CandidateJsonSource.Value.string goalSchema) ∈ entries
  else ("kind", CandidateJsonSource.Value.string (kindName kind)) ∈ entries

def SelectorMeaning (ast : J) (kind : Kind) : Prop :=
  ∃ entries, ast = .object entries ∧ (entries.map Prod.fst).Nodup ∧ TagMeaning entries kind

def selectEntries (entries : CandidateJsonSource.Entries) : Option Kind :=
  match CandidateJsonSource.lookup entries "kind" with
  | some (.string text) =>
    match decodeKind text with
    | some .goal => none
    | answer => answer
  | some _ => none
  | none =>
    match CandidateJsonSource.lookup entries "schema_version" with
    | some (.string text) => if text = goalSchema then some .goal else none
    | _ => none

theorem select_entries_exact (entries : CandidateJsonSource.Entries)
    (unique : (entries.map Prod.fst).Nodup) (kind : Kind) :
    selectEntries entries = some kind ↔ TagMeaning entries kind := by
  cases present : CandidateJsonSource.lookup entries "kind" with
  | none =>
    have absent := (lookup_none_exact entries "kind").mp present
    have noKind : ∀ text, ("kind", CandidateJsonSource.Value.string text) ∉ entries := by
      intro text member
      exact absent (List.mem_map_of_mem member)
    cases version : CandidateJsonSource.lookup entries "schema_version" with
    | none =>
      have noSchema := (lookup_none_exact entries "schema_version").mp version
      have missing : ("schema_version", CandidateJsonSource.Value.string goalSchema) ∉ entries := by
        intro member; exact noSchema (List.mem_map_of_mem member)
      cases kind <;> simp [selectEntries,present,version,TagMeaning,absent,noKind,missing]
    | some value =>
      have field : ("schema_version",CandidateJsonSource.Value.string goalSchema) ∈ entries ↔ value = .string goalSchema := by
        constructor
        · intro member
          have found := CandidateJsonSource.lookup_complete entries "schema_version" _ unique member
          exact Option.some.inj (version.symm.trans found)
        · intro same
          subst value; exact CandidateJsonSource.lookup_sound _ _ _ version
      cases kind <;> cases value <;>
        simp [selectEntries,present,version,TagMeaning,absent,noKind,field]
  | some value =>
    have hasKind : "kind" ∈ entries.map Prod.fst :=
      List.mem_map_of_mem (CandidateJsonSource.lookup_sound _ _ _ present)
    have field : ∀ text, ("kind",CandidateJsonSource.Value.string text) ∈ entries ↔ value = .string text := by
      intro text; constructor
      · intro member
        have found := CandidateJsonSource.lookup_complete entries "kind" _ unique member
        exact Option.some.inj (present.symm.trans found)
      · intro same
        subst value; exact CandidateJsonSource.lookup_sound _ _ _ present
    cases value with
    | string text =>
      cases found : decodeKind text with
      | none =>
        have unknown : ∀ k, text ≠ kindName k := by
          intro k same; have accepted := (kind_token_exact text k).mpr same
          simp [found] at accepted
        cases kind <;> simp [selectEntries,present,found,TagMeaning,hasKind,field,unknown]
      | some actual =>
        have named := (kind_token_exact text actual).mp found
        cases actual <;> cases kind <;>
          simp [selectEntries,present,TagMeaning,hasKind,field,named,kindName,decodeKind]
    | null => cases kind <;> simp [selectEntries,present,TagMeaning,hasKind,field]
    | boolean b => cases kind <;> simp [selectEntries,present,TagMeaning,hasKind,field]
    | number token => cases kind <;> simp [selectEntries,present,TagMeaning,hasKind,field]
    | array values => cases kind <;> simp [selectEntries,present,TagMeaning,hasKind,field]
    | object fields => cases kind <;> simp [selectEntries,present,TagMeaning,hasKind,field]

def selectKind : J → Option Kind
  | .object entries => if (entries.map Prod.fst).Nodup then selectEntries entries else none
  | _ => none

theorem selector_exact (ast : J) (kind : Kind) :
    selectKind ast = some kind ↔ SelectorMeaning ast kind := by
  cases ast with
  | object entries =>
    by_cases unique : (entries.map Prod.fst).Nodup
    · simp only [selectKind,if_pos unique,select_entries_exact entries unique]
      simp [SelectorMeaning,unique]
    · simp [selectKind,unique,SelectorMeaning]
  | null => simp [selectKind,SelectorMeaning]
  | boolean b => simp [selectKind,SelectorMeaning]
  | number token => simp [selectKind,SelectorMeaning]
  | string text => simp [selectKind,SelectorMeaning]
  | array values => simp [selectKind,SelectorMeaning]

def BodyMeaning (ast : J) (output : PayloadBody) : Prop :=
  ∃ kind, SelectorMeaning ast kind ∧ (decoderForKind kind).Meaning ast output

def decodeBody (ast : J) : Option PayloadBody :=
  match selectKind ast with
  | none => none
  | some kind => (decoderForKind kind).decode ast

theorem body_dispatch_exact (ast : J) (output : PayloadBody) :
    decodeBody ast = some output ↔ BodyMeaning ast output := by
  constructor
  · intro accepted
    cases found : selectKind ast with
    | none => simp [decodeBody,found] at accepted
    | some kind =>
      exact ⟨kind,(selector_exact _ _).mp found,
        ((decoderForKind kind).exact _ _).mp (by simpa [decodeBody,found] using accepted)⟩
  · rintro ⟨kind,selected,meaning⟩
    simp [decodeBody,(selector_exact _ _).mpr selected,((decoderForKind kind).exact _ _).mpr meaning]

def bodyDecoder : Decoder PayloadBody := ⟨decodeBody,BodyMeaning,body_dispatch_exact⟩

theorem selected_kind_equals_constructor (ast : J) (output : PayloadBody)
    (accepted : decodeBody ast = some output) :
    SelectorMeaning ast (bodyKind output) := by
  rcases (body_dispatch_exact _ _).mp accepted with ⟨kind,selected,meaning⟩
  rw [fixed_decoder_constructor_exact _ _ _ meaning]
  exact selected

theorem body_refusal_exact (ast : J) :
    decodeBody ast = none ↔ ¬ ∃ output, BodyMeaning ast output := by
  constructor
  · intro refused
    rintro ⟨output,meaning⟩
    have accepted := (body_dispatch_exact _ _).mpr meaning
    simp [refused] at accepted
  · intro missing
    cases found : decodeBody ast with
    | none => rfl
    | some output => exact False.elim (missing ⟨output,(body_dispatch_exact _ _).mp found⟩)

#print axioms kind_token_exact
#print axioms fixed_decoder_constructor_exact
#print axioms lookup_none_exact
#print axioms select_entries_exact
#print axioms selector_exact
#print axioms body_dispatch_exact
#print axioms selected_kind_equals_constructor
#print axioms body_refusal_exact
end RelationalSuccessor.CandidateBodyDispatch
