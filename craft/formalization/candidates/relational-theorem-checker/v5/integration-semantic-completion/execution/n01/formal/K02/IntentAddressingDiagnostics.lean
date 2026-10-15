import IntentAddressingCheck
import IntentAddressingWitnesses

set_option autoImplicit false

namespace RelationalSuccessor.CandidateIntentAddressing.Checker.Examples
open RelationalSuccessor
open Witnesses

-- Update owned record and claim together so other membership checks still pass.
def withResolution (kind : SubjectKind) (replacement : Resolution) : World × Claim :=
  ({ world kind with resolutions := [replacement] },
   { claim kind with resolution := replacement })

def withRole (kind : SubjectKind) (replacement : Role) : World × Claim :=
  ({ world kind with roles := [replacement] }, { claim kind with role := replacement })

def withSelection (kind : SubjectKind) (replacement : Selection) : World × Claim :=
  ({ world kind with selections := [replacement] },
   { claim kind with selection := replacement })

def isolatedCases (kind : SubjectKind) : List ((World × Claim) × List Diagnostic) :=
  [(withResolution kind { resolution kind with excludedSubjects := [(subject kind).ref] }, [.notExcluded]),
   (withResolution kind { resolution kind with selectedSubjects := [] }, [.selected]),
   (withResolution kind { resolution kind with intent := ref "other-intent" }, [.target]),
   ((world kind, { claim kind with resolutionQualifier := ref "different-resolution" }), [.resolutionQualifier]),
   (withRole kind { role kind with subjectKind := .other }, [.roleKind]),
   (({ world kind with decisions := [] }, claim kind), [.decisionOwned]),
   (withSelection kind { selection kind with frame := { frame kind with snapshot := ref "stale" } }, [.frameSnapshot]),
   (({ world kind with tests := [ref "Q1"] }, claim kind), [.testsOwned]),
   (({ world kind with roles := [] }, claim kind), [.roleOwned]),
   (withResolution kind { resolution kind with satisfactionTests := [ref "Q1", ref "Q1", ref "Q2"] }, [.testsDistinct]),
   ((world kind, { claim kind with addressingRole := "all-powerful" }), [.roleQualifier])]

def isolatedChecksPass (kind : SubjectKind) : Bool :=
  (isolatedCases kind).all (fun specimen =>
    decide (diagnostics specimen.1.1 specimen.1.2 = specimen.2))

theorem isolated_refusals_all_six (kind : SubjectKind) (allowed : kind ∈ allowedSources) :
    isolatedChecksPass kind = true := by
  cases kind
  · decide
  · decide
  · decide
  · decide
  · decide
  · decide
  · simp [allowedSources] at allowed

theorem positive_diagnostics_empty_all_six (kind : SubjectKind) (allowed : kind ∈ allowedSources) :
    diagnostics (world kind) (claim kind) = [] :=
  (diagnostics_empty_exact _ _).mpr (legitimate_addressing kind allowed)

theorem positive_checker_accepts_all_six (kind : SubjectKind) (allowed : kind ∈ allowedSources) :
    check (world kind) (claim kind) = true :=
  (check_exact _ _).mpr (legitimate_addressing kind allowed)

#print axioms isolated_refusals_all_six
#print axioms positive_diagnostics_empty_all_six
#print axioms positive_checker_accepts_all_six
end RelationalSuccessor.CandidateIntentAddressing.Checker.Examples
