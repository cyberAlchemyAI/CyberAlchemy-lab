import DigestEvaluator
set_option autoImplicit false
namespace RelationalSuccessor.CandidateDigest

theorem schedule_construct (n : Nat) (seed : Words) :
    ScheduleMeaning n seed (extendSchedule n seed) := by
  induction n generalizing seed with
  | zero => exact .done seed
  | succ n ih => exact .step (ih _)
theorem schedule_evaluate {n : Nat} {seed out : Words}
    (meaning : ScheduleMeaning n seed out) : extendSchedule n seed=out := by
  induction meaning with
  | done => rfl
  | step _ ih => exact ih
theorem schedule_exact (n : Nat) (seed out : Words) :
    extendSchedule n seed=out ↔ ScheduleMeaning n seed out := by
  constructor
  · intro eq; subst out; exact schedule_construct n seed
  · exact schedule_evaluate
theorem schedule_length {n : Nat} {seed out : Words}
    (meaning : ScheduleMeaning n seed out) : out.length=seed.length+n := by
  induction meaning with
  | done => simp
  | step _ ih => simp_all [Nat.add_assoc]
theorem full_schedule_length (block : Bytes) :
    (extendSchedule 48 (seedWords block)).length=64 := by
  simpa [seedWords] using schedule_length (schedule_construct 48 (seedWords block))
theorem full_round_count (block : Bytes) :
    (constants.zip (extendSchedule 48 (seedWords block))).length=64 := by
  simp [List.length_zip,full_schedule_length,constants]

theorem round_exact (k w : UInt32) (s out : State) :
    runRound k w s=out ↔ RoundMeaning k w s out := by
  constructor
  · intro eq; subst out; exact ⟨_,_,rfl,rfl,rfl⟩
  · rintro ⟨t1,t2,rfl,rfl,rfl⟩; rfl
theorem rounds_construct (pairs : List (UInt32 × UInt32)) (s : State) :
    RoundsMeaning pairs s (runRounds pairs s) := by
  induction pairs generalizing s with
  | nil => exact .done s
  | cons pair rest ih =>
    rcases pair with ⟨k,w⟩
    exact .step ((round_exact k w s _).mp rfl) (ih _)
theorem rounds_evaluate {pairs : List (UInt32 × UInt32)} {s out : State}
    (meaning : RoundsMeaning pairs s out) : runRounds pairs s=out := by
  induction meaning with
  | done => rfl
  | @step k w pairs s mid out head tail ih =>
    simp only [runRounds,(round_exact k w s mid).mpr head,ih]
theorem rounds_exact (pairs : List (UInt32 × UInt32)) (s out : State) :
    runRounds pairs s=out ↔ RoundsMeaning pairs s out := by
  constructor
  · intro eq; subst out; exact rounds_construct pairs s
  · exact rounds_evaluate

theorem block_exact (block : Bytes) (s out : State) :
    runBlock block s=some out ↔ BlockMeaning block s out := by
  unfold runBlock BlockMeaning
  by_cases width : block.length=64
  · simp only [width,if_true,true_and,Option.some.injEq]
    constructor
    · intro eq; subst out
      exact ⟨_,_,schedule_construct 48 _,rounds_construct _ _,rfl⟩
    · rintro ⟨words,work,sm,rm,eq⟩
      rw [schedule_evaluate sm,rounds_evaluate rm]
      exact eq.symm
  · simp only [width,if_false,false_and,Option.noConfusion,iff_false]

theorem message_exact (blocks : List Bytes) (s out : State) :
    runMessage blocks s=some out ↔ MessageMeaning blocks s out := by
  induction blocks generalizing s out with
  | nil =>
    constructor
    · intro eq; cases eq; exact .done s
    · intro h; cases h; rfl
  | cons block rest ih =>
    constructor
    · intro h
      cases eq : runBlock block s with
      | none => simp only [runMessage,eq,Option.bind_none] at h; contradiction
      | some mid =>
        simp only [runMessage,eq,Option.bind_some] at h
        exact .step ((block_exact block s mid).mp eq) ((ih mid out).mp h)
    · intro h; cases h with
      | step head tail =>
        simp only [runMessage,(block_exact _ _ _).mpr head,Option.bind_some]
        exact (ih _ _).mpr tail

theorem zero_count_bounds (n : Nat) : zeroCount n<64 := by
  have bound := Nat.mod_lt n (by decide : 0<64)
  unfold zeroCount
  split <;> omega
theorem zero_count_equation (n : Nat) : (n+1+zeroCount n+8)%64=0 := by
  have bound := Nat.mod_lt n (by decide : 0<64)
  have decomp := Nat.mod_add_div n 64
  unfold zeroCount
  split <;> omega
theorem zero_count_unique (n k : Nat) (bound : k<64)
    (equation : (n+1+k+8)%64=0) : k=zeroCount n := by
  have rbound := Nat.mod_lt n (by decide : 0<64)
  have decomp := Nat.mod_add_div n 64
  unfold zeroCount
  split <;> omega

theorem padding_exact (input padded : Bytes) :
    pad input=some padded ↔ PaddingMeaning input padded := by
  unfold pad PaddingMeaning
  by_cases domain : input.length < 2^61
  · simp only [domain,if_true,true_and,Option.some.injEq]
    constructor
    · intro eq
      exact ⟨zeroCount input.length,zero_count_bounds _,zero_count_equation _,eq.symm⟩
    · rintro ⟨k,kbound,keq,eq⟩
      rw [zero_count_unique _ _ kbound keq] at eq
      exact eq.symm
  · simp only [domain,if_false,false_and,Option.noConfusion,iff_false]

theorem padding_unique (input a b : Bytes) (ha : PaddingMeaning input a)
    (hb : PaddingMeaning input b) : a=b := by
  have ea := (padding_exact input a).mpr ha
  have eb := (padding_exact input b).mpr hb
  rw [ea] at eb
  exact Option.some.inj eb

theorem block_partition_length {input : Bytes} {blocks : List Bytes}
    (meaning : BlocksMeaning input blocks) : input.length=64*blocks.length := by
  induction meaning with
  | nil => simp
  | cons width tail ih => simp only [List.length_append,List.length_cons,width,ih]; omega
end RelationalSuccessor.CandidateDigest
