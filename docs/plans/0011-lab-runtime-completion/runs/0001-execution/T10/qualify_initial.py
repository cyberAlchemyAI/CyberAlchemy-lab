"""Exact first T10 candidate and all retained original refusals, no admission."""
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[5]
COMPONENT=ROOT/'product/lab/release-candidates/v1/interface/model-representations-v1-completion-0001'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    result_path=RUN/'initial-qualification-0001.json'
    if result_path.exists():raise RuntimeError('retain previous qualification')
    start=datetime.now(timezone.utc).isoformat();context=json.loads((RUN/'context.json').read_text())
    for r in context['selected_sources']:assert sha(ROOT/r['path'])==r['sha256']
    ledger=json.loads((COMPONENT/'disposition-ledger-initial.json').read_text())
    before={p.as_posix():sha(p)for p in COMPONENT.rglob('*')if p.is_file()}
    schema_path=ROOT/'authority/artifact-types/governed-model/v1/schema.json';validator=Draft202012Validator(json.loads(schema_path.read_text()))
    original=[]
    for member in ledger['members']:
        row=json.loads((ROOT/member['disposition_binding']['path']).read_text());raw=(ROOT/row['retained_original_body_binding']['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==row['original_body_binding']['sha256']
        errors=list(validator.iter_errors(json.loads(raw)));assert len(errors)==1 and errors[0].validator=='minItems' and list(errors[0].path)==['relation_refs']
        original.append({'member_ref':row['member_ref'],'original_schema_status':'REFUSED','reason':'relation_refs.minItems','original_binding':row['original_body_binding']})
    row=json.loads((COMPONENT/'dispositions/03.json').read_text());body=json.loads((ROOT/row['selected_candidate_binding']['path']).read_text());validator.validate(body)
    descriptor=json.loads((ROOT/'authority/artifact-types/governed-model/v1/artifact.json').read_text());rel=body['relation_refs'][0]
    assert len([r for r in descriptor['relation_roles']if r['relation_kind_ref']==rel['relation_kind_ref']and r['direction']==rel['direction']and rel['counterpart_kind']in r['counterpart_kinds']])==1
    counterpart=json.loads((ROOT/row['counterpart_binding']['path']).read_text());assert counterpart['node_id']==rel['counterpart_ref']and counterpart['kind']=='implementation'
    Draft202012Validator(json.loads((ROOT/'authority/artifact-types/implementation/v1/schema.json').read_text())).validate(counterpart)
    relations=json.loads((ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json').read_text())
    rc=next(r for r in relations['entries']if r['relation_kind_ref']=='relation.instance-of');record=json.loads((ROOT/rc['instance_path']).read_text());assert sha(ROOT/rc['instance_path'])==rc['instance_sha256']
    assert {'source_kind':'implementation','target_kind':'governed-model'}in record['payload']['allowed_endpoint_pairs']
    assert row['actual_owner_outcome']is None and not row['admission_or_runtime_use_allowed']
    bindings=row['code_bindings']+row['test_source_bindings']+row['historical_actual_evidence_bindings']+[row['counterpart_binding']]
    for ref in bindings:assert sha(ROOT/ref['path'])==ref['sha256']
    # Actual unchanged consumer reads exact selected controls. No native store,
    # profile rewrite, signatures, source effects, or live service is invoked.
    package=ROOT/'implementation/lab-runtime/candidates/repeatable-operation';sys.path.insert(0,str(package))
    from lab_runtime.profiles import select
    selected=json.loads((package/'profiles/selections.json').read_text());d75=next(r for r in selected['selections']if r['name']=='d75')
    chosen=select(ROOT,**{k:v for k,v in d75.items()if k not in ('name','source_materials','source_bytes')})
    assert chosen.profile_sha256==d75['profile_sha256']and chosen.selection_sha256==d75['review_sha256']
    for path,digest in before.items():assert sha(Path(path))==digest
    for r in context['selected_sources']:assert sha(ROOT/r['path'])==r['sha256']
    env={'python_version':sys.version.split()[0],'interpreter_path':sys.executable,'interpreter_sha256':sha(Path(sys.executable)),
         'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')}
    assert env['python_version']=='3.14.4'and env['jsonschema']=='4.23.0'and env['cryptography']=='46.0.5'and env['interpreter_sha256']=='52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41'
    result={'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'status':'PASS-FIRST-GROUNDED-CANDIDATE / T10-INCOMPLETE','original_members':29,'original_refusals':original,'candidate_schema_valid':True,'original_descriptor_direction_and_pair_valid':True,'original_unchanged_counterpart_schema_valid':True,'actual_readonly_consumer_selection':{'profile_sha256':chosen.profile_sha256,'selection_sha256':chosen.selection_sha256},'original_full_code_test_and_historical_evidence_bindings':bindings,'environment':env,'inputs_unchanged':True,'all29_representations_complete':False,'remaining_individual_representations':28,'actual_owner_outcome':None,'task_complete':False,'authority_effect':'none'}
    result_path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'original_refusals_preserved':29,'actual_candidate_valid':1,'remaining':28,'report':str(result_path)}))

if __name__=='__main__':main()
