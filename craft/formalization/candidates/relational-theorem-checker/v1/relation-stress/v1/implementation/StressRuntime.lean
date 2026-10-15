import StressCheckers
import Lean.Data.Json.FromToJson
import Lean.Data.Json.Printer

namespace Stress.Runtime
open Lean

def refJson (r : Ref) : Json := Json.mkObj [("id",toJson r.id),("version",toJson r.version)]
def verdictText : Verdict → String
  | .yes => "yes" | .no => "no" | .unknown => "unknown" | .invalid => "invalid"
def normText : NormMode → String
  | .require => "require" | .forbid => "forbid" | .permit => "permit"
def normJson (n : Norm) : Json := Json.mkObj [("mode",toJson (normText n.mode)),("action",toJson n.action)]
def inheritanceJson (e : Inheritance) : Json := Json.mkObj [
  ("id",toJson e.id),("subject",refJson e.subject),("contract",refJson e.contract),
  ("binding",refJson e.binding),("scope",toJson e.scope),("condition",toJson e.condition)]
def factJson (f : Fact) : Json := Json.mkObj [("edge",inheritanceJson f.edge),("norm",normJson f.norm)]
def stepJson (s : Step) : Json := Json.mkObj [
  ("rule",toJson (match s.rule with | .propagate => "propagate" | .forward => "forward")),
  ("fact",factJson s.fact),("parent",toJson s.parent)]

def actsReason (ds : List Delegation) (s : Snapshot) (e : ActsEdge) (a : String) (r : Bool) : String :=
  if ¬ ActsInventoryValid ds s e a then "malformed-or-ambiguous-input"
  else if ¬ DelegationResolved ds e then "unresolved-delegation"
  else if ¬ InterpretationKnown ds s e then "unresolved-policy-or-gate"
  else if r = true ∧ PermitsRedelegation ds e then "redelegation-chain-unsupported"
  else if ActsHolds ds s e a r then "effective-at-snapshot" else "not-effective-at-snapshot"

def inheritanceReason (g : Graph) (budget : Nat) : String :=
  if ¬ GraphValid g then "malformed-or-ambiguous-input"
  else if ¬ InheritanceKnown g then "unresolved-reference-interpretation-or-override"
  else if ¬ InheritanceMatches g then "binding-or-context-mismatch"
  else if workUnits g > budget then "closure-budget-exceeded"
  else "complete-for-fixed-rule-profile"

def actsResult (ds : List Delegation) (s : Snapshot) (e : ActsEdge) (a : String) (r : Bool) : Json :=
  Json.mkObj [("operation",toJson "evaluate-acts-for"),
    ("status",toJson (verdictText (checkActs ds s e a r))),
    ("reason",toJson (actsReason ds s e a r)),
    ("snapshot",refJson s.ref),("epoch",toJson s.epoch),("assertionId",toJson e.id)]

def inheritanceResult (g : Graph) (budget : Nat) : Json := Id.run do
  let status := checkInheritance g budget
  let facts := if status = .yes then closure g else []
  let pairs := if status = .yes then conflicts g else []
  return Json.mkObj [("operation",toJson "close-inherits-contract"),
    ("status",toJson (verdictText status)),("complete",toJson (status == .yes)),
    ("reason",toJson (inheritanceReason g budget)),
    ("facts",Json.arr (facts.map factJson).toArray),
    ("conflicts",Json.arr (pairs.map fun (f,h) => Json.mkObj [
      ("required",factJson f),("forbidden",factJson h)]).toArray),
    ("certificate",Json.arr (facts.map fun f => stepJson ⟨.propagate,f,none⟩).toArray)]

def certificateResult (g : Graph) (budget : Nat) (steps : List Step) : Json :=
  let ready := checkInheritance g budget
  let status := if ready ≠ .yes then ready
    else if checkCertificate g steps then Verdict.yes else Verdict.no
  Json.mkObj [("operation",toJson "replay-certificate"),
    ("status",toJson (verdictText status)),("accepted",toJson (status == .yes)),
    ("reason",toJson (if ready ≠ .yes then inheritanceReason g budget
      else if status = .yes then "certificate-valid" else "certificate-invalid")),
    ("stepCount",toJson steps.length)]

end Stress.Runtime
