"""Exact originals from an actually observed native capture qualification.

The trusted host selects these private receipts. The API does not accept them
from a public message, and their candidate records acquire no Source admission.
"""
import copy
import importlib
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator
import retained as R
import scope_profile as SC
ROOT=Path(__file__).resolve().parents[4]
VARIANT='implementation/lab-runtime/local-host/t31-current-ontology-capture-0001/external-postimages-0002/external_ontology_capture.py'
VARIANT_SHA='3c6bee19c635eb3bf052ac4c72da587d7dc1309f7f21899c9c572046f89eef7f'
def enc(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def original(binding):
    R.need(type(binding)is dict and set(binding)=={'ref','sha256'},'closed actual native capture original binding required')
    raw=R.read(Path(binding['ref']));R.need(R.sha(raw)==binding['sha256'],'actual native capture original differs');return raw

def produce(*,records,observations,controls):
    R.need(type(controls)is dict and set(controls)=={'capture_bindings','produce_assessment'}
           and type(controls['capture_bindings'])is list and controls['capture_bindings'] and type(controls['produce_assessment'])is bool,
           'closed exact actual native capture consumer selection required')
    selected=sys.modules.get('cal_installed_runtime_selection_v1');R.need(selected is not None and selected.root()==ROOT,'actual selected-root native capture consumer required');selected.guard()
    actual_producer={'path':str(ROOT/VARIANT),'sha256':VARIANT_SHA};R.need(R.sha((ROOT/VARIANT).read_bytes())==VARIANT_SHA,'actual native capture producer code differs')
    projected=[o for o in observations if o['actual_reply']['operation']=='ontology.project'and o['actual_reply']['kind']=='result'and o['projection_producer']is not None]
    R.need(len(projected)==1,'one exact passing actual projection producer required');observed=projected[0];projection=observed['projection_producer']
    view=projection['receipt']['ontology_view'];view={key:view[key]for key in R.FIELDS};R.need(view['version_ref']in records and records[view['version_ref']][0]==view,'actual returned original projection view required')
    output={};captures=[];cold_receipts=[];source_cut=observed['original_source_cut'];head=observed['files']['vault/ontology/HEAD.json'];head_value=json.loads(head)
    expected_manifest=observed['files']['vault/ontology/'+str(R.relative(head_value['generation']))+'/manifest.json']
    for binding in controls['capture_bindings']:
        raw=original(binding);result=json.loads(raw)
        R.need(result['schema_version']=='lab-actual-native-ontology-capture-observation/v1'and result['result']=='PASS-actual-native-capture-and-scope-observation'
               and result['actual_capture_producer_binding']==actual_producer and result['scope_observation_is_wrapper']is True
               and result['public_workflow_transition_dispatched']is False and result['SourceAdmission_requirement_satisfied']is False
               and result['api_source_sha256']==selected.binding('api.source')['sha256']and result['api_profile_sha256']==selected.binding('api.profile')['sha256']
               and result['source_cut']==source_cut and result['authority_effect']=='none','actual native capture selection/outcome boundary differs')
        R.need(result['transition_ref']in('transition:ontology-migration:mapped','transition:ontology-migration:candidate-validated'),'actual capture consumer route differs')
        receipt_raw=original(result['actual_capture_receipt_binding']);receipt=json.loads(receipt_raw)
        R.need(R.sha(receipt_raw)==result['actual_returned_capture_receipt_binding']['sha256']
               and receipt['schema_version']=='lab-original-ontology-typed-capture/v1-candidate'and receipt['run_binding']==result['run_binding']
               and receipt['work_ref']==result['work']['version_ref']and receipt['source_cut']==source_cut and receipt['work_satisfaction_asserted']is False
               and receipt['original_head_binding']['sha256']==R.sha(head)and receipt['original_manifest_binding']['sha256']==R.sha(expected_manifest),
               'actual capture receipt/Work/Run/source/generation differs')
        cold={name:original(b)for name,b in result['additional_cold_originals'].items()}
        R.need(set(cold)=={'head','manifest','native_read','cold_replay','mapping_policy','mapping'}
               and result['additional_actual_cold_replay']is True and result['original_capture_cold_receipt_reconstructed']is False,
               'fresh additional cold replay original closure required')
        replay=json.loads(cold['cold_replay']);native_manifest=json.loads(cold['manifest'])
        R.need(cold['head']==head and cold['manifest']==expected_manifest and R.sha(cold['native_read'])==native_manifest['native_read_sha256']
               and R.sha(cold['cold_replay'])==receipt['original_cold_replay_binding']['sha256']
               and replay['schema_version']=='lab-original-ontology-cold-correspondence/v1-candidate'and replay['cold_replayed']is True
               and replay['head_binding']['sha256']==R.sha(head)and replay['manifest_binding']['sha256']==R.sha(expected_manifest)
               and replay['native_read_binding']['sha256']==R.sha(cold['native_read'])and json.loads(cold['mapping'])['source_cut']==source_cut,
               'actual fresh cold read/head/manifest/source correspondence differs')
        _,index,_=SC.capture(result['scope_index_binding'])
        R.need(index['work']==result['work']and index['actor']==result['actor']and index['source_cut']==source_cut and index['run_ref']==result['run_ref']
               and index['journal_config_sha256']==result['journal_config_sha256'],'actual captured ScopeIndex Work/Actor/Source/Run/config differs')
        actual=[]
        for row in result['original_records']:
            R.need(type(row)is dict and set(row)=={'artifact','original_binding'},'closed actual captured record original required');h=row['artifact'];body_raw=original(row['original_binding']);body=json.loads(body_raw)
            R.need(type(h)is dict and set(h)==R.FIELDS and h in receipt['artifacts']and R.sha(body_raw)==h['byte_sha256']
                   and body['node_id']==h['identity_ref']and h['version_ref']==h['identity_ref']+'@'+receipt['record_version_contract']
                   and body['scope_ref']==h['scope_ref']==view['scope_ref']and body['owner_ref']==result['actor']['principal_ref']and body['authority_effect']=='none',
                   'actual typed capture header/body/revision/owner/native scope differs')
            kind,version=h['carrier_ref'].removeprefix('cal.artifact-type.').split('/')
            R.need(kind in('ontology-node','ontology-edge','ontology-cut','ontology-view'),'unselected native capture carrier')
            Draft202012Validator(json.loads((ROOT/'authority/artifact-types'/kind/version/'schema.json').read_bytes())).validate(body)
            ref=h['version_ref'];R.need(ref not in output or output[ref]==(h,body_raw),'conflicting captured original revision');output[ref]=(h,body_raw);actual.append(h)
        R.need(actual==receipt['artifacts']and len(actual)==32,'complete original typed capture return required')
        expected={'cal.artifact-type.ontology-node/v2':18,'cal.artifact-type.ontology-edge/v1':12}if result['transition_ref'].endswith(':mapped')else {'cal.artifact-type.ontology-cut/v1':1,'cal.artifact-type.ontology-view/v1':1}
        stage=result['selected_stage_outputs'];kinds=[h['carrier_ref']for h in stage]
        R.need(all(h in actual for h in stage)and set(kinds)==set(expected)and all(kinds.count(k)==n for k,n in expected.items())
               and all(any(entry['transition_ref']==result['transition_ref']and entry['artifact']==h for entry in index['entries'])for h in stage),
               'actual selected stage output/ScopeIndex correspondence differs')
        if captures:R.need(all(result[key]==captures[0][1][key]for key in('actor','run_ref','work','source_cut','journal_config_sha256')),'actual captures change semantic frame')
        captures.append((copy.deepcopy(binding),result));cold_receipts.append(copy.deepcopy(result['additional_cold_originals']['cold_replay']))
    if controls['produce_assessment']:
        R.need([r['transition_ref']for b,r in captures]==['transition:ontology-migration:mapped','transition:ontology-migration:candidate-validated'],'bounded native assessment needs both actual capture stages in order')
        last=captures[-1][1];base=ROOT/'authority/artifact-types/work-outcome-assessment/v1';body=json.loads((base/'fixtures/valid/record.json').read_bytes());seed=R.sha(enc({'captures':[b for b,r in captures],'work':last['work']}));identity='work-outcome-assessment:local-native-scope:'+seed
        body.update(node_id=identity,name='Bounded local ontology correspondence assessment',scope_ref=last['work']['scope_ref'],owner_ref=last['actor']['principal_ref'],lifecycle_state='candidate',successor_refs=[],
                    evidence_refs=[b['ref']for b in cold_receipts],claim_ceiling='Actual captured native original correspondence only. Original Work completion, canonical admission and the original domainspec SourceAdmission requirement remain unassessed or uncovered.')
        body['payload'].update(subject_ref=last['work']['version_ref'],expected_result_ref='protocol:bounded-native-source-correspondence',observed_result_ref=cold_receipts[-1]['ref'],
            disposition='supported-bounded-native-correspondence-only',evidence_refs=[b['ref']for b in cold_receipts],gap_refs=['gap:original-SourceAdmission-requirement-not-covered','gap:original-Work-completion-not-assessed'])
        body['relation_refs']=[{'relation_kind_ref':'relation.evaluates','direction':'source','counterpart_kind':'work','counterpart_ref':last['work']['version_ref']}]
        Draft202012Validator(json.loads((base/'schema.json').read_bytes())).validate(body);raw=enc(body);header={'scope_ref':body['scope_ref'],'identity_ref':identity,'version_ref':identity+'@candidate.native-scope.1','carrier_ref':'cal.artifact-type.work-outcome-assessment/v1','byte_sha256':R.sha(raw)};output[header['version_ref']]=(header,raw)
    selected.guard()
    return {'records':list(output.values()),'consumed_input_refs':[view['version_ref']],'consumed_observation_refs':[observed['observation_binding']['ref']],
            'receipt':{'schema_version':'lab-retained-actual-native-ontology-production/v1','actual_capture_result_bindings':[b for b,r in captures],
                       'actual_additional_cold_receipt_bindings':cold_receipts,'actual_producer_binding':actual_producer,'private_bounded_assessment_produced':controls['produce_assessment'],
                       'SourceAdmission_requirement_satisfied':False,'Work_completion_established':False,'authority_effect':'none'}}
