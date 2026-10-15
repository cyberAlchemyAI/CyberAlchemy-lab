import TokenMeaning
set_option autoImplicit false
namespace RelationalSuccessor.CandidateJsonTokens
open CandidateJsonBytes

def scanRun (predicate : Nat → Prop) [DecidablePred predicate] : List Nat → List Nat × List Nat
  | [] => ([],[])
  | code::tail => if predicate code then
      let rest := scanRun predicate tail
      (code::rest.1,rest.2)
    else ([],code::tail)

theorem scanned_run_meaning (predicate : Nat → Prop) [DecidablePred predicate] (input : List Nat) :
    RunMeaning predicate input (scanRun predicate input).1 (scanRun predicate input).2 := by
  induction input with
  | nil => exact ⟨rfl,by intro code owned; change code ∈ ([] : List Nat) at owned; simp at owned,Or.inl rfl⟩
  | cons code tail ih =>
    by_cases allowed : predicate code
    · simp only [scanRun,if_pos allowed]
      refine ⟨?_,?_,ih.2.2⟩
      · exact congrArg (List.cons code) ih.1
      · intro value member
        rcases List.mem_cons.mp member with eq | owned
        · subst value; exact allowed
        · exact ih.2.1 value owned
    · simp only [scanRun,if_neg allowed]
      exact ⟨rfl,by simp,Or.inr ⟨code,tail,rfl,allowed⟩⟩

theorem scan_run_inverse (predicate : Nat → Prop) [DecidablePred predicate] (word remaining : List Nat)
    (allowed : ∀ code ∈ word, predicate code) (stop : Stops predicate remaining) :
    scanRun predicate (word ++ remaining) = (word,remaining) := by
  induction word with
  | nil =>
    rcases stop with empty | ⟨first,tail,same,denied⟩
    · subst remaining; rfl
    · rw [same]; simp [scanRun,denied]
  | cons first rest ih =>
    have head := allowed first (by simp)
    have tail := ih (by intro code owned; exact allowed code (by simp [owned]))
    simp only [List.cons_append,scanRun,if_pos head,tail]

theorem scan_run_exact (predicate : Nat → Prop) [DecidablePred predicate] (input word remaining : List Nat) :
    scanRun predicate input = (word,remaining) ↔ RunMeaning predicate input word remaining := by
  constructor
  · intro same
    have meaning := scanned_run_meaning predicate input
    simpa only [same] using meaning
  · rintro ⟨same,allowed,stop⟩
    rw [same]; exact scan_run_inverse predicate word remaining allowed stop

theorem run_meaning_unique (predicate : Nat → Prop) [DecidablePred predicate]
    (input word1 word2 rest1 rest2 : List Nat)
    (first : RunMeaning predicate input word1 rest1) (second : RunMeaning predicate input word2 rest2) :
    word1 = word2 ∧ rest1 = rest2 := by
  have same := ((scan_run_exact predicate input word1 rest1).mpr first).symm.trans
    ((scan_run_exact predicate input word2 rest2).mpr second)
  exact ⟨congrArg Prod.fst same,congrArg Prod.snd same⟩

theorem scanned_length_conservation (predicate : Nat → Prop) [DecidablePred predicate] (input : List Nat) :
    (scanRun predicate input).1.length + (scanRun predicate input).2.length = input.length := by
  have same := (scanned_run_meaning predicate input).1
  simpa only [List.length_append] using (congrArg List.length same).symm

def scanWhitespace (input : List Nat) : List Nat × List Nat := scanRun WhiteCode input

theorem scan_whitespace_exact (input word remaining : List Nat) :
    scanWhitespace input = (word,remaining) ↔
      input = word ++ remaining ∧ WhiteSpace word ∧ Stops WhiteCode remaining := by
  exact scan_run_exact WhiteCode input word remaining

#print axioms scanned_run_meaning
#print axioms scan_run_inverse
#print axioms scan_run_exact
#print axioms run_meaning_unique
#print axioms scanned_length_conservation
#print axioms scan_whitespace_exact
end RelationalSuccessor.CandidateJsonTokens
