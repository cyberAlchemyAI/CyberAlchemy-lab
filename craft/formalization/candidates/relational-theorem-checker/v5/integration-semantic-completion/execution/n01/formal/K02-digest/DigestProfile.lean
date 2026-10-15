import DigestRefinement
import SharedSemantics
set_option autoImplicit false
namespace RelationalSuccessor.CandidateDigest
structure Profile where
  ref : RevisionRef
  algorithm : String
  encoding : String
  deriving DecidableEq, Repr
-- This is a candidate interpretation, not authentic selection for a Frame.
def ProfileMeaning (expected : Profile) (submitted : RevisionRef) : Prop :=
  expected.ref=submitted ∧ expected.ref.key.owner≠"" ∧ expected.ref.key.artifact≠"" ∧
  expected.ref.key.revision≠"" ∧ expected.ref.digest≠"" ∧
  expected.algorithm="sha256-fips1804-2015" ∧ expected.encoding="lowerhex64"
instance (p : Profile) (r : RevisionRef) : Decidable (ProfileMeaning p r) := by
  unfold ProfileMeaning; infer_instance

def VerifiedDigestMeaning (p : Profile) (r : RevisionRef) (input : Bytes)
    (claimed : String) (budget : Nat) : Prop :=
  ProfileMeaning p r ∧ input.length<2^61 ∧ input.length≤budget ∧ DigestMeaning input claimed

def digestCheck (p : Profile) (r : RevisionRef) (input : Bytes)
    (claimed : String) (budget : Nat) : Bool :=
  decide (ProfileMeaning p r) && decide (input.length<2^61) &&
    decide (input.length≤budget) && decide (digestBytes input=some claimed)

theorem digest_check_exact (p : Profile) (r : RevisionRef) (input : Bytes)
    (claimed : String) (budget : Nat) :
    digestCheck p r input claimed budget=true ↔ VerifiedDigestMeaning p r input claimed budget := by
  simp only [digestCheck,Bool.and_eq_true,decide_eq_true_eq,digest_exact,VerifiedDigestMeaning,and_assoc]

inductive Outcome where
  | unsupportedProfile | outsideAlgorithmDomain | byteBudgetExceeded | malformedDigest
  | digestMismatch | verified
  deriving DecidableEq, Repr

def classifyDigest (p : Profile) (r : RevisionRef) (input : Bytes)
    (claimed : String) (budget : Nat) : Outcome :=
  if ¬ProfileMeaning p r then .unsupportedProfile
  else if ¬input.length<2^61 then .outsideAlgorithmDomain
  else if ¬input.length≤budget then .byteBudgetExceeded
  else if ¬HexMeaning claimed then .malformedDigest
  else if digestBytes input=some claimed then .verified else .digestMismatch

theorem profile_refusal_exact (p : Profile) (r : RevisionRef) (input : Bytes)
    (claimed : String) (budget : Nat) :
    classifyDigest p r input claimed budget=.unsupportedProfile ↔ ¬ProfileMeaning p r := by
  unfold classifyDigest
  by_cases h : ProfileMeaning p r <;> by_cases dm : input.length<2^61 <;>
    by_cases bm : input.length≤budget <;> by_cases hm : HexMeaning claimed <;>
    by_cases eq : digestBytes input=some claimed <;> simp [h,dm,bm,hm,eq]

theorem classified_verified_exact (p : Profile) (r : RevisionRef) (input : Bytes)
    (claimed : String) (budget : Nat) :
    classifyDigest p r input claimed budget=.verified ↔ VerifiedDigestMeaning p r input claimed budget := by
  by_cases pm : ProfileMeaning p r
  · by_cases dm : input.length<2^61
    · by_cases bm : input.length≤budget
      · by_cases hm : HexMeaning claimed
        · simp [classifyDigest,pm,dm,bm,hm,VerifiedDigestMeaning,digest_exact]
        · have noMeaning : ¬DigestMeaning input claimed := fun meaning => hm (digest_hex_meaning input claimed meaning)
          simp [classifyDigest,pm,dm,bm,hm,VerifiedDigestMeaning,noMeaning]
      · simp [classifyDigest,pm,dm,bm,VerifiedDigestMeaning]
    · simp [classifyDigest,pm,dm,VerifiedDigestMeaning]
  · simp [classifyDigest,pm,VerifiedDigestMeaning]

theorem classified_check_agree (p : Profile) (r : RevisionRef) (input : Bytes)
    (claimed : String) (budget : Nat) :
    classifyDigest p r input claimed budget=.verified ↔ digestCheck p r input claimed budget=true :=
  (classified_verified_exact p r input claimed budget).trans (digest_check_exact p r input claimed budget).symm

theorem accepted_exact_profile (p : Profile) (r : RevisionRef) (input : Bytes)
    (claimed : String) (budget : Nat) (accepted : digestCheck p r input claimed budget=true) : p.ref=r :=
  ((digest_check_exact p r input claimed budget).mp accepted).1.1

theorem wrong_profile_refused (p : Profile) (r : RevisionRef) (input : Bytes)
    (claimed : String) (budget : Nat) (wrong : p.ref≠r) :
    digestCheck p r input claimed budget≠true := by
  intro accepted; exact wrong (accepted_exact_profile p r input claimed budget accepted)

theorem wrong_digest_refused (p : Profile) (r : RevisionRef) (input : Bytes)
    (claimed : String) (budget : Nat) (wrong : ¬DigestMeaning input claimed) :
    digestCheck p r input claimed budget≠true := by
  intro accepted
  exact wrong ((digest_check_exact p r input claimed budget).mp accepted).2.2.2

theorem budget_refusal_exact (p : Profile) (r : RevisionRef) (input : Bytes)
    (claimed : String) (budget : Nat) :
    classifyDigest p r input claimed budget=.byteBudgetExceeded ↔
      ProfileMeaning p r ∧ input.length<2^61 ∧ ¬input.length≤budget := by
  unfold classifyDigest
  by_cases pm : ProfileMeaning p r <;> by_cases dm : input.length<2^61 <;>
    by_cases bm : input.length≤budget <;> by_cases hm : HexMeaning claimed <;>
    by_cases eq : digestBytes input=some claimed <;> simp [pm,dm,bm,hm,eq]

theorem malformed_refusal_exact (p : Profile) (r : RevisionRef) (input : Bytes)
    (claimed : String) (budget : Nat) :
    classifyDigest p r input claimed budget=.malformedDigest ↔
      ProfileMeaning p r ∧ input.length<2^61 ∧ input.length≤budget ∧ ¬HexMeaning claimed := by
  unfold classifyDigest
  by_cases pm : ProfileMeaning p r <;> by_cases dm : input.length<2^61 <;>
    by_cases bm : input.length≤budget <;> by_cases hm : HexMeaning claimed <;>
    by_cases eq : digestBytes input=some claimed <;> simp [pm,dm,bm,hm,eq]

theorem mismatch_refusal_exact (p : Profile) (r : RevisionRef) (input : Bytes)
    (claimed : String) (budget : Nat) :
    classifyDigest p r input claimed budget=.digestMismatch ↔
      ProfileMeaning p r ∧ input.length<2^61 ∧ input.length≤budget ∧ HexMeaning claimed ∧
        ¬DigestMeaning input claimed := by
  unfold classifyDigest
  by_cases pm : ProfileMeaning p r <;> by_cases dm : input.length<2^61 <;>
    by_cases bm : input.length≤budget <;> by_cases hm : HexMeaning claimed <;>
    simp [pm,dm,bm,hm,digest_exact]

theorem domain_refusal_exact (p : Profile) (r : RevisionRef) (input : Bytes)
    (claimed : String) (budget : Nat) :
    classifyDigest p r input claimed budget=.outsideAlgorithmDomain ↔
      ProfileMeaning p r ∧ ¬input.length<2^61 := by
  unfold classifyDigest
  by_cases pm : ProfileMeaning p r <;> by_cases dm : input.length<2^61 <;>
    by_cases bm : input.length≤budget <;> by_cases hm : HexMeaning claimed <;>
    by_cases eq : digestBytes input=some claimed <;> simp [pm,dm,bm,hm,eq]
#print axioms digest_check_exact
#print axioms profile_refusal_exact
#print axioms classified_verified_exact
#print axioms classified_check_agree
#print axioms accepted_exact_profile
#print axioms wrong_profile_refused
#print axioms wrong_digest_refused
#print axioms budget_refusal_exact
#print axioms malformed_refusal_exact
#print axioms mismatch_refusal_exact
#print axioms domain_refusal_exact
end RelationalSuccessor.CandidateDigest
