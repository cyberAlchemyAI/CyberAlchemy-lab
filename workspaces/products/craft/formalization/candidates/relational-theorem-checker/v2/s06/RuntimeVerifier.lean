import Lean
import Lean.Replay

open Lean

-- The driver parses no submitted Lean source and loads no submitted extensions.
-- Expected statements come from a separately loaded read-only trusted environment.
def sameMeaning (a b : ConstantInfo) : Bool :=
  a.name == b.name && a.type == b.type && a.levelParams == b.levelParams &&
  a.value? (allowOpaque := true) == b.value? (allowOpaque := true) &&
  a.isUnsafe == b.isUnsafe && a.isPartial == b.isPartial &&
  (match a, b with
  | .axiomInfo _, .axiomInfo _ | .defnInfo _, .defnInfo _
  | .thmInfo _, .thmInfo _ | .opaqueInfo _, .opaqueInfo _
  | .inductInfo _, .inductInfo _ | .ctorInfo _, .ctorInfo _
  | .recInfo _, .recInfo _ | .quotInfo _, .quotInfo _ => true
  | _, _ => false)

partial def dependencies (env : Environment) (pending : List Name)
    (visited : NameSet := {}) (axioms : Array Name := #[]) : IO (NameSet × Array Name) := do
  match pending with
  | [] => return (visited, axioms)
  | n :: rest =>
    if visited.contains n then return ← dependencies env rest visited axioms
    let some ci := env.find? n | throw <| IO.userError s!"missing proof dependency {n}"
    if ci.isUnsafe || ci.isPartial then
      throw <| IO.userError s!"unsafe or partial proof dependency {n}"
    let mut next := rest
    for d in ci.getUsedConstantsAsSet do next := d :: next
    -- Replay of an inductive block also needs its mutual declarations and constructors.
    match ci with
    | .inductInfo info => next := info.all ++ info.ctors ++ next
    | .quotInfo _ => next := `Eq :: next
    | _ => pure ()
    let axioms := match ci with | .axiomInfo _ => axioms.push n | _ => axioms
    return ← dependencies env next (visited.insert n) axioms

unsafe def audit (expectedModule expectedName mode theoremName : String) : IO Json := do
  initSearchPath (← findSysroot)
  let objectFile ← findOLean `Submitted
  let mut files := #[objectFile]
  for level in [OLeanLevel.server, OLeanLevel.private] do
    let file := level.adjustFileName objectFile
    if ← file.pathExists then files := files.push file
  let parts ← readModuleDataParts files
  if parts.isEmpty then throw <| IO.userError "missing submitted module data"
  let allowedImports := #[`Init, `RelationalInput, `RelationalSemantics, `SemanticLogic,
    `RegistryChecker, `Preservation, `ConservativeExpansion, `InferenceCore,
    `DerivationSoundness, `ClosureAdequacy, `ProtectedLineage, `ModelSemantics,
    `RuleConservativity, `InferenceFixture, `RequirementSemantics, `RequiredStatements,
    `ContextProjection, `ProjectionCatalog, `ProjectionProofs, `ObligationSemantics, `StressTypes, `RuntimeCatalog, `RuntimeProofs]
  for part in parts do
    for imp in part.1.imports do
      if !allowedImports.contains imp.module then
        throw <| IO.userError s!"unapproved submitted import: {imp.module}"
  if !(parts.any fun part => part.1.constNames.contains theoremName.toName) then
    throw <| IO.userError "requested theorem is not declared by the submitted module"
  IO.eprintln "audit: load trusted declarations"
  let trusted ← importModules #[{module := expectedModule.toName}] {} 0 #[] false false
  IO.eprintln "audit: load submitted data without extensions"
  let submitted ← importModules #[{module := `Submitted}] {} 0 #[] false false
  let expectedName := expectedName.toName
  let theoremName := theoremName.toName
  let some expected := trusted.find? expectedName
    | throw <| IO.userError "trusted required statement does not exist"
  let expectedType ← match mode with
    | "definition-value" =>
      match expected with
      | .defnInfo info => pure info.value
      | _ => throw <| IO.userError "required proposition must be a trusted definition"
    | "theorem-type" =>
      match expected with
      | .thmInfo info => pure info.type
      | _ => throw <| IO.userError "required concrete type must belong to a trusted theorem"
    | _ => throw <| IO.userError "unsupported required statement mode"
  if (trusted.find? theoremName).isSome then
    throw <| IO.userError "submission theorem must be newly declared in the submitted module"
  let some (.thmInfo submittedThm) := submitted.find? theoremName
    | throw <| IO.userError "submitted identity is missing or is not a theorem"
  if !submittedThm.levelParams.isEmpty || !expected.levelParams.isEmpty then
    throw <| IO.userError "this catalog requires closed universe parameters"
  IO.eprintln "audit: collect trusted statement dependencies"
  let (expectedDependencies, _) ← dependencies trusted [expectedName, `propext, `Classical.choice, `Quot.sound]
  let mut checkedDefinitions := 0
  for n in expectedDependencies do
    let some ci := trusted.find? n | throw <| IO.userError s!"missing trusted definition {n}"
    let some actual := submitted.find? n
      | throw <| IO.userError s!"trusted declaration missing from submitted environment: {n}"
    if !sameMeaning ci actual then
      throw <| IO.userError s!"trusted declaration substituted: {n}"
    checkedDefinitions := checkedDefinitions + 1
  IO.eprintln s!"audit: compared {checkedDefinitions} trusted statement dependencies"
  let (_, axioms) ← dependencies submitted [theoremName]
  let allowed := #[`propext, `Classical.choice, `Quot.sound]
  for ax in axioms do
    if !allowed.contains ax then
      throw <| IO.userError s!"unapproved transitive axiom: {ax}"
  -- Reconstruct the submitted and imported pure declarations in an empty kernel.
  -- This uses the pinned Lean kernel, not a second independently implemented kernel.
  let (closure, _) ← dependencies submitted [theoremName, expectedName]
  let mut constants : Std.HashMap Name ConstantInfo := {}
  for n in closure do
    let some ci := submitted.find? n | throw <| IO.userError s!"missing replay declaration {n}"
    constants := constants.insert n ci
  IO.eprintln s!"audit: replay {constants.size} proof/type declarations"
  let fresh ← (← mkEmptyEnvironment).replay constants
  let exact : Declaration := .thmDecl {
    name := `ProofVerifierExactTypeCheck, levelParams := [], type := expectedType,
    value := mkConst theoremName }
  match fresh.toKernelEnv.addDeclCore 0 0 exact (cancelTk? := none) with
  | .error ex => throw <| IO.userError s!"exact required theorem type rejected: {← ex.toMessageData {} |>.toString}"
  | .ok _ => pure ()
  return Json.mkObj [
    ("schema", toJson "relational.independent-kernel-audit/v1"),
    ("accepted", toJson true), ("theorem_id", toJson theoremName.toString),
    ("required_statement", toJson expectedName.toString),
    ("statement_mode", toJson mode),
    ("transitive_axioms", toJson (axioms.map Name.toString)),
    ("trusted_definitions_checked", toJson checkedDefinitions),
    ("fresh_kernel_replay", toJson true),
    ("replayed_declarations", toJson constants.size),
    ("allowed_axiom_types_bound", toJson true),
    ("load_submitted_extensions", toJson false)]

unsafe def main (args : List String) : IO UInt32 := do
  try
    match args with
    | [expectedModule, expectedName, mode, theoremName] =>
      let report ← audit expectedModule expectedName mode theoremName
      IO.println report.compress
      return 0
    | _ => throw <| IO.userError "expected module, required declaration, mode and theorem identity"
  catch error =>
    IO.eprintln s!"independent proof audit rejected: {error}"
    return 1
