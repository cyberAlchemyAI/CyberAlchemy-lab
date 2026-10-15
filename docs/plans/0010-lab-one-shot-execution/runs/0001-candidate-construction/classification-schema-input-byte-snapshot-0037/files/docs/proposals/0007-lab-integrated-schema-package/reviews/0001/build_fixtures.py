#!/usr/bin/env python3
"""Materialize static candidate schema review examples, not runtime tests."""
import copy,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parents[1]

def example(name):return json.loads((PACKAGE/'examples'/f'{name}.json').read_text())
cases=[]
def add(name,schema,value,valid):cases.append({'case':name,'schema':schema,'expected_valid':valid,'instance':value})
a=example('artifact-inspect-result');a.update(included_sections=['lifecycle'],envelope=None,contract_binding=None,authority_bindings=[],provenance_bindings=[],connections=[],evidence_bindings=[],gaps=[])
add('metadata-only-inspection','artifact-inspect-result',a,True)
b=copy.deepcopy(a);b['envelope']=example('artifact-envelope');add('body-leaked-in-metadata-inspection','artifact-inspect-result',b,False)
a=example('context-delivery');a.update(posture='blocked',context_view=None,ontology_view=None);add('blocked-context-without-views','context-delivery',a,True)
b=copy.deepcopy(a);b.update(posture='ready',scope_enforced=True);add('ready-context-without-views','context-delivery',b,False)
a=example('agent-session-result');a.update(posture='blocked',session_ref=None,agent_instance_ref=None,started_at=None,expires_at=None);add('blocked-session-without-created-identity','agent-session-result',a,True)
b=copy.deepcopy(a);b['posture']='active';add('active-session-without-identity','agent-session-result',b,False)
a=example('agent-session-close-receipt');a.update(posture='blocked',ended_at=None);add('blocked-close-without-ended-time','agent-session-close-receipt',a,True)
b=copy.deepcopy(a);b.update(posture='closed',discarded_memory=True);add('closed-session-without-ended-time','agent-session-close-receipt',b,False)
a=example('artifact-query-result');a.update(query_basis='canonical',projection_generation=None);add('canonical-read-without-projection','artifact-query-result',a,True)
b=copy.deepcopy(a);b['query_basis']='projection';add('projected-read-without-generation','artifact-query-result',b,False)
a=example('file-materialization-receipt');a.update(posture='failed',manifest_binding=None,generation_ref=None,output_bindings=[]);add('failed-generation-without-fictional-manifest','file-materialization-receipt',a,True)
b=copy.deepcopy(a);b.update(posture='published',recovery_required=False,gaps=[]);add('published-generation-without-manifest-or-outputs','file-materialization-receipt',b,False)
a=example('error-result');a.update(code='indeterminate',retry_policy='idempotent-retry');add('blind-retry-after-indeterminate','error-result',a,False)
a=example('commit-receipt');a.update(posture='rejected',commit_binding={'ref':'example:commit','sha256':'0'*64},output_bindings=[],projection_posture='pending',file_generation_posture='not-selected');add('rejected-admission-with-commit','commit-receipt',a,False)
a=example('workflow-transition-receipt');a.update(posture='blocked',event_binding={'ref':'example:event','sha256':'0'*64},output_artifact_refs=[],recovery_required=False);add('blocked-transition-with-applied-event','workflow-transition-receipt',a,False)
a=example('installation-receipt');a.update(posture='rolled-back',postimage_binding=None,verification_bindings=[],recovery_required=False);add('rollback-without-verified-postimage','installation-receipt',a,False)
a=example('typed-extension-request');a['relation_kind_candidate']['carrier_ref']='cal.artifact-type.work/v1';add('extension-with-wrong-kind-carrier','typed-extension-request',a,False)
a=example('package-export-request');a['artifact_refs']=[];add('empty-package-export-selection','package-export-request',a,False)
a=example('recovery-receipt');a.update(posture='recovered',observed_bindings=[],gaps=[]);add('recovered-without-observation','recovery-receipt',a,False)
a=example('ontology-projection-receipt');a.update(posture='indeterminate',recovery_required=False);add('uncertain-ontology-without-recovery','ontology-projection-receipt',a,False)
(HERE/'schema-scenarios.json').write_text(json.dumps({'schema_version':'lab-schema-review-scenarios/v1-candidate','authority_effect':'none','scope':'Static authoring shapes only; no runtime behavior or authority verified.','cases':cases},indent=2,sort_keys=True)+'\n')
print(json.dumps({'schema_review_scenarios':len(cases)}))
