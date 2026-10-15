import GuardedIntentPayload
import SourceFixture

set_option autoImplicit false

namespace RelationalSuccessor.CandidateFiniteSourceCatalog.Examples
open RelationalSuccessor

abbrev fixtureRef := _root_.RelationalSuccessor.CandidateIntentSource.SourceFixture.revision
abbrev expectedFixture := _root_.RelationalSuccessor.CandidateIntentSource.SourceFixture.expected
abbrev rawFixture := _root_.RelationalSuccessor.CandidateIntentSource.SourceFixture.raw
abbrev fixtureTokens := _root_.RelationalSuccessor.CandidateIntentSource.SourceFixture.tokens

def frame : Frame :=
  ⟨fixtureRef "profile:catalog-fixture", expectedFixture.selectedSubjects[0]'(by decide), expectedFixture.intent,
    fixtureRef "context:catalog-fixture", fixtureRef "scope:catalog-fixture",
    fixtureRef "snapshot:catalog-fixture", 42, "fixture-epoch"⟩

def artifact (token : String) : Artifact String :=
  ⟨fixtureRef token, "synthetic-record", token, [1, 2, 3], fixtureRef ("review:" ++ token)⟩

def roles : List Role := [.intent, .decision, .subject, .satisfactionTest]
def bindings (role : Role) : List Binding :=
  (fixtureTokens role).map (fun token => ⟨role, token, (artifact token).ref⟩)
def approvals (role : Role) : List (Approval String) :=
  (fixtureTokens role).map (fun token => ⟨role, artifact token, frame⟩)
def capture : Capture String :=
  ⟨frame, roles.flatMap (fun role => (fixtureTokens role).map artifact),
    roles.flatMap bindings, roles.flatMap approvals⟩

def projectToken : String := rawFixture.selected_subject_refs[0]!
def project : Artifact String := artifact projectToken

def changedDigest : Artifact String :=
  { project with ref := { project.ref with digest := "conflicting-digest" } }
def conflictingAlias : Capture String :=
  { capture with
    records := capture.records ++ [changedDigest]
    bindings := capture.bindings ++ [⟨.subject, "alias:conflict", changedDigest.ref⟩]
    roots := capture.roots ++ [⟨.subject, changedDigest, frame⟩] }

def changedBody : Capture String :=
  { capture with records := capture.records.map (fun row =>
      if row.ref = project.ref then { row with body := "different-source-body" } else row) }

def changedBytes : Capture String :=
  { capture with records := capture.records.map (fun row =>
      if row.ref = project.ref then { row with content := [9] } else row) }

def changedKind : Capture String :=
  { capture with records := capture.records.map (fun row =>
      if row.ref = project.ref then { row with sourceKind := "another-record-kind" } else row) }

def changedReview : Capture String :=
  { capture with records := capture.records.map (fun row =>
      if row.ref = project.ref then { row with ownerReview := fixtureRef "review:replacement" } else row) }

def conflictingRoot : Capture String :=
  { capture with roots := capture.roots.map (fun root =>
      if root.artifact.ref = project.ref then
        { root with artifact := { root.artifact with body := "conflicting-root-body" } } else root) }

def wrongRoleRoots : Capture String :=
  { capture with roots := capture.roots.map (fun root =>
      if root.role = .subject then { root with role := .decision } else root) }

def staleRoots : Capture String :=
  { capture with roots := capture.roots.map (fun root =>
      { root with frame := { root.frame with epoch := 41 } }) }

def missingSecondTest : Capture String :=
  { capture with bindings := capture.bindings.filter (fun binding =>
      decide (binding.token ≠ rawFixture.satisfaction_test_refs[1]!)) }

def legitimateAlias : Capture String :=
  { capture with bindings := capture.bindings ++ [⟨.subject, "alias:legitimate", project.ref⟩] }

def conflictingBinding : Capture String :=
  { capture with bindings := capture.bindings ++
    [⟨.subject, projectToken, expectedFixture.selectedSubjects[1]'(by decide)⟩] }

end RelationalSuccessor.CandidateFiniteSourceCatalog.Examples
