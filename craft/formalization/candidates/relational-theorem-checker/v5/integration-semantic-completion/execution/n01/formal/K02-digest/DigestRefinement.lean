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
  | step _ ih => simp only [List.length_append,List.length_singleton] at ih; omega
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
  · simp [width]

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
  · simp [domain]

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

theorem split_blocks_sound (input : Bytes) (blocks : List Bytes)
    (parsed : splitBlocks input=some blocks) : BlocksMeaning input blocks := by
  rw [splitBlocks] at parsed
  split at parsed
  · rename_i empty
    subst input
    simp only [Option.some.injEq] at parsed
    subst blocks
    exact .nil
  · rename_i nonempty
    split at parsed
    · rename_i enough
      cases tailEq : splitBlocks (input.drop 64) with
      | none => simp only [tailEq,Option.map_none] at parsed; contradiction
      | some tail =>
        simp only [tailEq,Option.map_some,Option.some.injEq] at parsed
        subst blocks
        have tailMeaning := split_blocks_sound (input.drop 64) tail tailEq
        have width : (input.take 64).length=64 := by simp [List.length_take,Nat.min_eq_left enough]
        have joined := BlocksMeaning.cons width tailMeaning
        simpa only [List.take_append_drop] using joined
    · contradiction
termination_by input.length
decreasing_by simp only [List.length_drop]; omega

theorem split_blocks_complete {input : Bytes} {blocks : List Bytes}
    (meaning : BlocksMeaning input blocks) : splitBlocks input=some blocks := by
  induction meaning with
  | nil => rw [splitBlocks]; rfl
  | @cons block rest blocks width tail ih =>
    have nonempty : block ++ rest ≠ [] := by
      intro eq
      have h := congrArg List.length eq
      simp only [List.length_append,List.length_nil,width] at h
      omega
    have enough : 64 ≤ (block++rest).length := by simp only [List.length_append,width]; omega
    have tk : (block++rest).take 64=block := by
      simpa only [width] using (List.take_left (l₁:=block) (l₂:=rest))
    have dr : (block++rest).drop 64=rest := by
      simpa only [width] using (List.drop_left (l₁:=block) (l₂:=rest))
    rw [splitBlocks]
    simp only [if_neg nonempty,dif_pos enough,tk,dr,ih,Option.map_some]

theorem split_blocks_exact (input : Bytes) (blocks : List Bytes) :
    splitBlocks input=some blocks ↔ BlocksMeaning input blocks :=
  ⟨split_blocks_sound input blocks,split_blocks_complete⟩

theorem digest_exact (input : Bytes) (digest : String) :
    digestBytes input=some digest ↔ DigestMeaning input digest := by
  constructor
  · intro h
    cases pe : pad input with
    | none => simp only [digestBytes,pe,Option.bind_none] at h; contradiction
    | some padded =>
      cases be : splitBlocks padded with
      | none => simp only [digestBytes,pe,Option.bind_some,be,Option.bind_none] at h; contradiction
      | some blocks =>
        cases me : runMessage blocks initial with
        | none => simp only [digestBytes,pe,Option.bind_some,be,me,Option.map_none] at h; contradiction
        | some state =>
          simp only [digestBytes,pe,Option.bind_some,be,me,Option.map_some,Option.some.injEq] at h
          exact ⟨padded,blocks,state,(padding_exact input padded).mp pe,
            (split_blocks_exact padded blocks).mp be,(message_exact blocks initial state).mp me,h.symm⟩
  · rintro ⟨padded,blocks,state,pm,bm,mm,rfl⟩
    simp only [digestBytes,(padding_exact input padded).mpr pm,Option.bind_some,
      (split_blocks_exact padded blocks).mpr bm,(message_exact blocks initial state).mpr mm,Option.map_some]

theorem digest_unique (input : Bytes) (a b : String) (ha : DigestMeaning input a)
    (hb : DigestMeaning input b) : a=b := by
  have ea := (digest_exact input a).mpr ha
  have eb := (digest_exact input b).mpr hb
  rw [ea] at eb
  exact Option.some.inj eb

theorem digest_none_exact (input : Bytes) :
    digestBytes input=none ↔ ¬ ∃ digest, DigestMeaning input digest := by
  cases eq : digestBytes input with
  | none =>
    constructor
    · intro _ h; rcases h with ⟨digest,meaning⟩
      have e := (digest_exact input digest).mpr meaning
      rw [eq] at e; contradiction
    · intro _; rfl
  | some digest =>
    constructor
    · intro h; contradiction
    · intro h
      exact False.elim (h ⟨digest,(digest_exact input digest).mp eq⟩)

theorem accepted_digest_domain (input : Bytes) (digest : String)
    (accepted : digestBytes input=some digest) : input.length<2^61 := by
  rcases (digest_exact input digest).mp accepted with ⟨_,_,_,padding,_,_,_⟩
  exact padding.1

theorem aligned_blocks_exist (input : Bytes) (aligned : input.length%64=0) :
    ∃ blocks, BlocksMeaning input blocks := by
  by_cases empty : input=[]
  · subst input; exact ⟨[],.nil⟩
  · have positive : 0<input.length := by
      have nonzero : input.length≠0 := by
        intro h; exact empty (List.eq_nil_iff_length_eq_zero.mpr h)
      omega
    have enough : 64≤input.length := by omega
    have restAligned : (input.drop 64).length%64=0 := by
      simp only [List.length_drop]; omega
    rcases aligned_blocks_exist (input.drop 64) restAligned with ⟨blocks,bm⟩
    have width : (input.take 64).length=64 := by simp [List.length_take,Nat.min_eq_left enough]
    refine ⟨input.take 64::blocks,?_⟩
    simpa only [List.take_append_drop] using (BlocksMeaning.cons width bm)
termination_by input.length
decreasing_by simp only [List.length_drop]; omega

theorem padding_aligned (input padded : Bytes) (meaning : PaddingMeaning input padded) :
    padded.length%64=0 := by
  rcases meaning with ⟨_,k,_,equation,rfl⟩
  simpa only [List.length_append,List.length_singleton,List.length_replicate,
    beBytes,List.length_map,List.length_range] using equation

theorem partition_message_exists {input : Bytes} {blocks : List Bytes}
    (meaning : BlocksMeaning input blocks) (s : State) : ∃ out, MessageMeaning blocks s out := by
  induction meaning generalizing s with
  | nil => exact ⟨s,.done s⟩
  | @cons block rest blocks width tail ih =>
    let mid := addState s (runRounds (constants.zip (extendSchedule 48 (seedWords block))) s)
    have bm : BlockMeaning block s mid :=
      ⟨width,_,_,schedule_construct 48 _,rounds_construct _ _,rfl⟩
    rcases ih mid with ⟨out,mm⟩
    exact ⟨out,.step bm mm⟩

theorem digest_domain_total (input : Bytes) (domain : input.length<2^61) :
    ∃ digest, digestBytes input=some digest := by
  let padded := input ++ [128] ++ List.replicate (zeroCount input.length) 0 ++ beBytes 8 (input.length*8)
  have pm : PaddingMeaning input padded :=
    ⟨domain,zeroCount input.length,zero_count_bounds _,zero_count_equation _,rfl⟩
  rcases aligned_blocks_exist padded (padding_aligned input padded pm) with ⟨blocks,bm⟩
  rcases partition_message_exists bm initial with ⟨out,mm⟩
  exact ⟨stateHex out,(digest_exact input _).mpr ⟨padded,blocks,out,pm,bm,mm,rfl⟩⟩

theorem digest_refusal_domain_exact (input : Bytes) :
    digestBytes input=none ↔ ¬ input.length<2^61 := by
  constructor
  · intro h domain
    rcases digest_domain_total input domain with ⟨digest,eq⟩
    rw [h] at eq; contradiction
  · intro h
    cases eq : digestBytes input with
    | none => rfl
    | some digest => exact False.elim (h (accepted_digest_domain input digest eq))

theorem state_hex_length (s : State) : (stateHex s).length=64 := by
  simp [stateHex,wordHex]

theorem accepted_digest_length (input : Bytes) (digest : String)
    (accepted : digestBytes input=some digest) : digest.length=64 := by
  rcases (digest_exact input digest).mp accepted with ⟨_,_,state,_,_,_,rfl⟩
  exact state_hex_length state

theorem hex_digit_meaning (n : Nat) (bound : n<16) : HexCharMeaning (hexDigit n) := by
  unfold hexDigit
  split
  · rename_i small
    have valid : (48+n).isValidChar := by unfold Nat.isValidChar; omega
    simp only [Char.ofNat,dif_pos valid,Char.ofNatAux]
    unfold HexCharMeaning
    change (48≤48+n ∧ 48+n≤57) ∨ (97≤48+n ∧ 48+n≤102)
    omega
  · rename_i large
    have valid : (87+n).isValidChar := by unfold Nat.isValidChar; omega
    simp only [Char.ofNat,dif_pos valid,Char.ofNatAux]
    unfold HexCharMeaning
    change (48≤87+n ∧ 87+n≤57) ∨ (97≤87+n ∧ 87+n≤102)
    omega

theorem word_hex_chars (word : UInt32) (c : Char) (member : c ∈ wordHex word) :
    HexCharMeaning c := by
  simp only [wordHex,List.mem_map] at member
  rcases member with ⟨i,_,rfl⟩
  exact hex_digit_meaning _ (Nat.mod_lt _ (by decide))

theorem state_hex_meaning (state : State) : HexMeaning (stateHex state) := by
  refine ⟨state_hex_length state,?_⟩
  intro c member
  simp only [stateHex,String.toList_ofList,List.mem_flatMap] at member
  rcases member with ⟨word,_,m⟩
  exact word_hex_chars word c m

theorem digest_hex_meaning (input : Bytes) (digest : String)
    (meaning : DigestMeaning input digest) : HexMeaning digest := by
  rcases meaning with ⟨_,_,state,_,_,_,rfl⟩
  exact state_hex_meaning state
#print axioms schedule_construct
#print axioms schedule_evaluate
#print axioms schedule_exact
#print axioms schedule_length
#print axioms full_schedule_length
#print axioms full_round_count
#print axioms round_exact
#print axioms rounds_construct
#print axioms rounds_evaluate
#print axioms rounds_exact
#print axioms block_exact
#print axioms message_exact
#print axioms zero_count_bounds
#print axioms zero_count_equation
#print axioms zero_count_unique
#print axioms padding_exact
#print axioms padding_unique
#print axioms block_partition_length
#print axioms split_blocks_sound
#print axioms split_blocks_complete
#print axioms split_blocks_exact
#print axioms digest_exact
#print axioms digest_unique
#print axioms digest_none_exact
#print axioms accepted_digest_domain
#print axioms aligned_blocks_exist
#print axioms padding_aligned
#print axioms partition_message_exists
#print axioms digest_domain_total
#print axioms digest_refusal_domain_exact
#print axioms state_hex_length
#print axioms accepted_digest_length
#print axioms hex_digit_meaning
#print axioms word_hex_chars
#print axioms state_hex_meaning
#print axioms digest_hex_meaning
end RelationalSuccessor.CandidateDigest
