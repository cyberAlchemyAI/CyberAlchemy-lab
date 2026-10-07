#!/usr/bin/env python3
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parent; SHARED=ROOT.parent/"_candidate_pack.py"
def hostile(s):
 f=set(); k=s.get("kind")
 if k=="machine-agent-instance" and s.get("session_bound") is not True: f.add("machine-agent-must-be-session-ephemeral")
 if k=="session-memory" and s.get("survives_session") is not False: f.add("session-memory-must-expire")
 if k=="project-state" and s.get("owned_by_agent") is True: f.add("project-state-must-not-be-agent-owned")
 if k=="agent-output" and s.get("authority_effect")!="none": f.add("agent-output-must-not-carry-authority")
 if k=="ontology-node" and s.get("replaces_subject") is True: f.add("ontology-node-must-not-replace-subject")
 if k=="ontology-edge" and s.get("scope") not in {"global-projection","ontology-local"}: f.add("ontology-edge-must-declare-scope")
 if k=="typed-relation" and not s.get("exact_pair_ref"): f.add("typed-relation-must-bind-exact-pair")
 if k=="operational-lesson" and s.get("grants_authority") is True: f.add("lesson-must-not-grant-authority")
 if k=="classification" and s.get("establishes_identity") is True: f.add("classification-must-not-establish-identity")
 if k=="failure-occurrence" and not s.get("boundary_ref"): f.add("failure-occurrence-must-name-boundary")
 if k=="source" and s.get("implies_truth") is True: f.add("source-must-not-imply-truth")
 if k=="generated-output" and s.get("canonical_by_generation") is True: f.add("generated-output-must-not-imply-canonical")
 if k=="agent-capability" and s.get("implies_authority") is True: f.add("agent-capability-must-not-imply-authority")
 if k=="agent-assignment" and s.get("grants_authority") is True: f.add("agent-assignment-must-not-grant-authority")
 if k=="agent-action" and s.get("completion_proves_effect") is True: f.add("agent-action-must-not-prove-effect")
 if k=="agent" and s.get("self_activates_profile_change") is True: f.add("agent-must-not-self-activate-change")
 if k=="ontology-view" and s.get("canonical_replay_source") is True: f.add("ontology-view-must-not-be-replay-source")
 return f
if __name__=="__main__":
 spec=importlib.util.spec_from_file_location("candidate_pack",SHARED); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module); module.hostile_failures=hostile
 raise SystemExit(module.validate(ROOT,{'cal.definition.actor','cal.definition.agent','cal.definition.principal','cal.definition.agent-profile','cal.definition.agent-capability','cal.definition.agent-instance','cal.definition.agent-session','cal.definition.project-state','cal.definition.session-memory','cal.definition.ontology-view','cal.definition.agent-action','cal.definition.agent-assignment','cal.definition.delegation','cal.definition.agent-reflection','cal.definition.operational-lesson','cal.definition.lesson-application','cal.definition.lesson-outcome-assessment','cal.definition.improvement-target','cal.definition.operational-learning-cycle','cal.definition.classification','cal.definition.classification-scheme','cal.definition.classification-value','cal.definition.classification-assignment','cal.definition.failure','cal.definition.failure-mode','cal.definition.failure-occurrence','cal.definition.failure-assessment','cal.definition.failure-control-binding','cal.definition.incident','cal.definition.intent-resolution','cal.definition.implementation','cal.definition.relation-kind','cal.definition.typed-relation','cal.definition.ontology-node','cal.definition.ontology-edge','cal.definition.ontology-manifest','cal.definition.ontology-cut','cal.definition.semantic-event-history','cal.definition.governance-event-history','cal.definition.work','cal.definition.tool','cal.definition.generated-output','cal.definition.principal-reference','cal.definition.governed-model','cal.definition.policy','cal.definition.decision','cal.definition.contract','cal.definition.decision-scope','cal.definition.effect','cal.definition.review','cal.definition.source','cal.definition.challenge-contract','cal.definition.challenge-event','cal.definition.operational-observation','cal.definition.work-outcome-assessment','cal.definition.feedback-record','cal.definition.communication-preference','cal.definition.preference-application-assessment','cal.definition.drift-assessment','cal.definition.improvement-signal' }))
