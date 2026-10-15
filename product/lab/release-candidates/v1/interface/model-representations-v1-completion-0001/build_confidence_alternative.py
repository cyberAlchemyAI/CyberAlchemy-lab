"""Concrete separate-axis not-assessed vocabulary option; approval before use."""
import copy
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[6];HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def main():
    original=json.loads((HERE/'dispositions/20.json').read_text())
    source=ROOT/original['original_axes']['original_control_bindings'][0]['path']
    confidence=json.loads(source.read_text());assert confidence['allowed_levels']==['not-assessed']
    assert confidence['evidence_level']=='not-assessed'and confidence['commitment_level']=='not-assessed'
    body=json.loads((ROOT/original['original_body_binding']['path']).read_text())
    scheme='classification-scheme:T10:source-qualified-not-assessed'
    value_ids={axis:'classification-value:T10:'+axis+':not-assessed'for axis in ('evidence','commitment')}
    def common(kind,node,name):
        v={k:copy.deepcopy(x)for k,x in body.items()if k not in ('payload','relation_refs')}
        v.update(schema_version='cyberalchemy-lab-'+kind+'/v1',node_id=node,kind=kind,name=name,
            claim_ceiling='Meaning-change candidate representing only original source-qualified not-assessed vocabulary. Evidence and commitment axes remain distinct. No positive assessment, original protocol identity alias, current owner, classification assignment, admission, reliance or action permission. Accountable meaning approval is required before use.')
        return v
    candidates=[]
    record=common('classification-scheme',scheme,'Source-qualified unassessed confidence vocabulary option')
    record['relation_refs']=[{'relation_kind_ref':'relation.member-of','direction':'target','counterpart_kind':'classification-value','counterpart_ref':value_ids[a]}for a in value_ids]
    record['payload']={'scheme_name':'Original O02 source-qualified not-assessed vocabulary',
        'axis_refs':[confidence['scheme_ref']+'#'+a for a in value_ids],
        'value_refs':list(value_ids.values()),
        'cardinality_rules':['Only not-assessed is allowed on each original evidence and commitment axis.'],
        'compatibility_rules':['No assessed evidence strength, owner commitment/reliance or action authority is implied.','Same label on evidence and commitment does not collapse the two axes.'],
        'mapping_refs':[source.relative_to(ROOT).as_posix()+'#','implementation/lab-ontology/candidates/v1/adapters/lifecycle/profiles/translation-profile.json#/confidence']}
    candidates.append(('scheme.json',record))
    for axis,identity in value_ids.items():
        record=common('classification-value',identity,'Source-qualified '+axis+' is not assessed')
        record['relation_refs']=[{'relation_kind_ref':'relation.member-of','direction':'source','counterpart_kind':'classification-scheme','counterpart_ref':scheme}]
        record['payload']={'scheme_ref':scheme,'axis_ref':confidence['scheme_ref']+'#'+axis,'value_code':'not-assessed',
            'definition_ref':source.relative_to(ROOT).as_posix()+'#/meaning','parent_value_refs':[],
            'compatibility_refs':[source.relative_to(ROOT).as_posix()+'#/allowed_levels']}
        candidates.append((axis+'-not-assessed.json',record))
    folder=HERE/'candidate-alternatives/unknown-confidence';folder.mkdir(parents=True,exist_ok=True)
    checks=[]
    for name,record in candidates:
        kind=record['kind'];schema=ROOT/'authority/artifact-types'/kind/'v1/schema.json'
        descriptor=ROOT/'authority/artifact-types'/kind/'v1/artifact.json';d=json.loads(descriptor.read_text())
        Draft202012Validator(json.loads(schema.read_text())).validate(record)
        for relation in record['relation_refs']:
            assert len([r for r in d['relation_roles']if r['relation_kind_ref']==relation['relation_kind_ref']and r['direction']==relation['direction']and relation['counterpart_kind']in r['counterpart_kinds']])==1
        target=folder/name
        if target.exists():raise RuntimeError('retain prior alternative construction')
        target.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
        checks.append({'candidate_binding':binding(target),'original_schema_binding':binding(schema),'original_descriptor_binding':binding(descriptor),'schema_valid':True,'original_direction_and_counterpart_role_valid':True})
    proposal={'schema_version':'lab-T10-meaning-change-candidate-option/v1','member_ref':original['member_ref'],
        'original_wrapper_binding':original['original_body_binding'],'original_vocabulary_binding':binding(source),
        'candidates':checks,'purpose':'Separate original evidence/commitment not-assessed sentinel vocabulary from a behavior Model. Preserve exact old protocol bytes and identity independently.',
        'actual_code_bindings':[binding(ROOT/'implementation/lab-ontology/candidates/v1/adapters/lifecycle'/name)for name in ['native_store.py','translation.py','profiles/translation-profile.json']],
        'code_locations':['native_store.py constructs level=not-assessed under original confidence.scheme_ref','translation.py emits distinct #evidence:not-assessed and #commitment:not-assessed source-qualified references'],
        'definition_ref_disposition':'Exact original /meaning text is source-qualified vocabulary evidence; it is not promoted into an admitted Definition artifact.',
        'axis_ref_disposition':'Original source-local protocol namespace remains source-local; no global Axis admission or namespace alias is inferred.',
        'actual_owner_outcome':None,'accountable_meaning_change_approval_required':True,'actual_global_endpoint_pair_review_complete':False,
        'native_proposal_or_use_allowed':False,'owner_authority_resolved':False,'task_complete':False,'authority_effect':'none'}
    (folder/'option.json').write_text(json.dumps(proposal,indent=2)+'\n')
    print(json.dumps({'member':original['member_ref'],'schema_valid_alternative_postimages':3,'meaning_approval_required':True,'native_use_allowed':False}))

if __name__=='__main__':main()
