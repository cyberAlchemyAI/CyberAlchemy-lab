"""Produce a private proposed review scope from actual exact review originals.

This fills a template input absent from proposal.review's two returned carriers.
It grants no owner authority and applies none of the proposed target effects.
"""
import copy
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[4]

def need(value,reason):
    if not value:raise ValueError(reason)
def enc(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()

def produce(*,records,observations,controls):
    need(type(controls)is dict and set(controls)=={'review_observation_ref'},'closed actual review selection required')
    selected=[o for o in observations if o['observation_binding']['ref']==controls['review_observation_ref']]
    need(len(selected)==1,'one independently selected actual review observation required');observed=selected[0]
    reply=observed['actual_reply'];need(reply['operation']=='proposal.review' and reply['kind']=='result','successful original review producer required')
    result=reply['message'];files=observed['files']
    def object_original(binding):
        name='vault/objects/'+binding['sha256']+'.json';need(name in files and sha(files[name])==binding['sha256'],'actual review object original differs');return files[name]
    manifest_raw=object_original(result['manifest_binding']);manifest=json.loads(manifest_raw)
    bundle_h=result['decision_bundle'];checkpoint_h=result['checkpoint'];bundle_h={k:bundle_h[k] for k in ('scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256')};checkpoint_h={k:checkpoint_h[k] for k in bundle_h}
    need(bundle_h['version_ref'] in records and checkpoint_h['version_ref'] in records
         and records[bundle_h['version_ref']][0]==bundle_h and records[checkpoint_h['version_ref']][0]==checkpoint_h,'actual returned review carrier bindings differ')
    bundle=json.loads(records[bundle_h['version_ref']][1]);checkpoint=json.loads(records[checkpoint_h['version_ref']][1])
    need(bundle['payload']['checkpoint_ref']==checkpoint_h['identity_ref'] and checkpoint['payload']['decision_bundle_ref']==bundle_h['identity_ref']
         and checkpoint['payload']['presentation_state']=='pending' and checkpoint['payload']['closed_at']is None,
         'actual bundle/checkpoint connection or pending state differs')
    need(manifest['schema_version']=='lab-exact-review-materialization/v1-candidate' and manifest['base_cut']==observed['original_source_cut']
         and manifest['all_targets_materialized']is True and manifest['actual_owner_outcome']is None
         and manifest['repository_admissions_applied']==0 and manifest['runtime_activations']==0 and manifest['external_effect_refs']==[],
         'actual retained review outcome or no-effect boundary differs')
    declared=bundle['payload']['ordered_decisions'];need(len(declared)==len(manifest['targets']) and declared,'actual ordered target closure required')
    workspace=json.loads(files['vault/workspace.json']);target_bindings=[];subjects=[];kinds=[]
    for row,entry in zip(declared,manifest['targets']):
        target=entry['target'];header=target['artifact'];binding=entry['original_content_binding']
        need(target['operation']!='withdraw' and binding is not None,'private scope producer requires materialized nonwithdraw targets')
        need(row['selected_outcome']is None and row['target_refs']==[header['version_ref']]
             and row['target_digests']==[{'target_ref':header['version_ref'],'sha256':header['byte_sha256']}]
             and row['decision_core_sha256']==entry['core_binding']['sha256'],'exact ordered review target/core digest differs')
        matches=[m for m in workspace['materials'] if m['ref']==binding['ref'] and m['sha256']==binding['sha256']]
        need(len(matches)==1,'exact actual review target original unavailable');name='vault/'+matches[0]['path']
        need(name in files and sha(files[name])==binding['sha256']==header['byte_sha256'],'actual review target bytes differ')
        body=json.loads(files[name]);need(body['node_id']==header['identity_ref'] and body['scope_ref']==header['scope_ref']==bundle_h['scope_ref'],
                                         'actual reviewed target identity/scope differs')
        subjects.append(header['version_ref']);kinds.append(header['carrier_ref']);target_bindings.append(copy.deepcopy(header))
    need(len(subjects)==len(set(subjects)),'duplicate exact reviewed target')
    seed=sha(enc({'observation':observed['observation_binding'],'bundle':bundle_h,'checkpoint':checkpoint_h,'targets':target_bindings}))
    scope_id='decision-scope:private-review-ready:'+seed;boundary_id='authority-boundary:private-review-ready:'+seed
    scope_root=ROOT/'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/decision-scope/v2'
    boundary_root=ROOT/'authority/artifact-types/authority-boundary/v1'
    scope=json.loads((scope_root/'fixtures/valid/record.json').read_bytes());boundary=json.loads((boundary_root/'fixtures/valid/record.json').read_bytes())
    for body,identity in [(scope,scope_id),(boundary,boundary_id)]:
        body.update(node_id=identity,scope_ref=bundle_h['scope_ref'],owner_ref=bundle['owner_ref'],lifecycle_state='candidate',successor_refs=[],
                    evidence_refs=[observed['observation_binding']['ref'],result['manifest_binding']['ref']],
                    claim_ceiling='Private proposed review-ready metadata scope over exact actual pending review targets only. No owner grant, target effect, Source admission, activation or publication.')
    effect='candidate-review-ready-metadata'
    scope['payload'].update(subject_refs=subjects,subject_kind_refs=list(dict.fromkeys(kinds)),permitted_effects=[effect],
                            excluded_effects=['admission','owner-decision','canonical-application','runtime-activation','deployment','external-publication'])
    scope['relation_refs']=[{'relation_kind_ref':'relation.scopes-authority-over','direction':'target','counterpart_kind':'authority-boundary','counterpart_ref':boundary_id+'@candidate.1'}]
    boundary['payload'].update(accountable_principal_ref=bundle['owner_ref'],owner_role_ref='protocol:pending-review-owner-only',authority_scope_ref=scope_id+'@candidate.1',
                               allowed_effect_kinds=[effect],excluded_effect_kinds=scope['payload']['excluded_effects'],effective_period='private-proposal-only-no-active-grant')
    boundary['relation_refs']=[{'relation_kind_ref':'relation.scopes-authority-over','direction':'source','counterpart_kind':'decision-scope','counterpart_ref':scope_id+'@candidate.1'}]
    outputs=[]
    for body,folder,carrier in [(scope,scope_root,'cal.artifact-type.decision-scope/v2'),(boundary,boundary_root,'cal.artifact-type.authority-boundary/v1')]:
        Draft202012Validator(json.loads((folder/'schema.json').read_bytes())).validate(body);raw=enc(body)
        header={'scope_ref':body['scope_ref'],'identity_ref':body['node_id'],'version_ref':body['node_id']+'@candidate.1','carrier_ref':carrier,'byte_sha256':sha(raw)};outputs.append((header,raw))
    return {'records':outputs,'consumed_input_refs':[bundle_h['version_ref'],checkpoint_h['version_ref']],
            'consumed_observation_refs':[observed['observation_binding']['ref']],
            'receipt':{'schema_version':'lab-private-exact-review-scope-production/v1','review_observation_binding':observed['observation_binding'],
                       'review_manifest_binding':result['manifest_binding'],'actual_pending_bundle':bundle_h,'actual_pending_checkpoint':checkpoint_h,
                       'exact_reviewed_targets':target_bindings,'new_scope':outputs[0][0],'new_boundary':outputs[1][0],
                       'owner_decision_or_grant_created':False,'Source_admission':False,'authority_effect':'none'}}
