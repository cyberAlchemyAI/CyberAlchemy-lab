"""Owned technical events sealed by the complete original native entrypoint."""
import json
from pathlib import Path
import subprocess

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()

def call(executable,mode,*args,env=None):
    return subprocess.run([str(executable),mode,*map(str,args)],capture_output=True,timeout=30,env=env)

def sealed_fixture(executable,parent):
    parent=Path(parent);parent.mkdir(mode=0o700)
    semantic=[]
    for n in range(1,4):
        identity={'subject_id':'T32-node-'+str(n),'ontology_id':'T32-owned-technical','subject_kind':'node','type_ref':'T32-node-type/v1'}
        state={'identity':identity,'lifecycle':'active','label':'Owned technical node '+str(n),'definition_or_claim':'Process interruption conformance fixture only.','scope':'T32-owned-process-kill','semantic_components':[],'semantic_definition_refs':[{'definition_id':'CAL-GON-D002','selector_sha256':'b'*64}],'typed_properties':{'profile_ref':'T32-empty/v1','values':{}},'use_obligations':[],'forbidden_collapse':[],'profile_ref':'T32-empty/v1'}
        semantic.append({'source_kind':'canonical_event','event_family':'semantic','event_id':'T32-semantic-'+str(n),'event_digest':'0'*64,'stream_id':'semantic:T32-owned-technical:node:T32-node-'+str(n),'subject_identity':identity,'previous_event_digest':None,'semantic_cursor':n,'complete_resulting_semantic_state':state})
    drafts=parent/'semantic-drafts.json';drafts.write_bytes(canonical({'semantic':semantic,'governance':[]}));p=call(executable,'seal',drafts);assert p.returncode==0,p.stderr
    semantic=json.loads(p.stdout)['semantic'];governance=[]
    for n,event in enumerate(semantic,1):
        ref={'semantic_event_id':event['event_id'],'semantic_event_digest':event['event_digest'],'semantic_cursor':n}
        state={'semantic_ref':ref,'provenance':[{'source_ref':'T32-owned-fixture','relation':'derived-from','operation':'construct','owner_route':'T32-technical-only','posture':'candidate'}],'owner_route':'T32-technical-only','candidate_or_maturity_status':'candidate','promotion_state_or_handle':'not-promoted','authority_kind_and_posture':{'kind':'technical-fixture','posture':'non-authoritative'},'authority_effect':'none','evidence_confidence':{'scheme_ref':'T32-confidence/v1','level':'not-assessed'},'commitment_confidence':{'scheme_ref':'T32-confidence/v1','level':'not-assessed'},'challenge_contract':{'challenge_response':'Inspect owned technical fixture.','valid_challenge_modes':['evidence','contradiction','owner_review'],'contradiction_edges':[],'validation_edges':[],'owner_route':'T32-technical-only','resolution_gate':'T32-technical-gate','blocking_questions':[],'challenge_residue_route':'T32-technical-only'},'residue':[],'conflicts':[],'drift_owner':'T32-technical-only','invalidation_route':'T32-technical-only'}
        governance.append({'source_kind':'canonical_event','event_family':'governance','event_id':'T32-governance-'+str(n),'event_digest':'0'*64,'stream_id':'governance:T32-owned-technical:node:T32-node-'+str(n),'semantic_ref':ref,'governance_cursor':n,'previous_event_digest':None,'complete_resulting_governance_state':state})
    drafts=parent/'all-drafts.json';drafts.write_bytes(canonical({'semantic':semantic,'governance':governance}));p=call(executable,'seal',drafts);assert p.returncode==0,p.stderr
    output=parent/'sealed-events.json';output.write_bytes(p.stdout);return output,json.loads(p.stdout)
