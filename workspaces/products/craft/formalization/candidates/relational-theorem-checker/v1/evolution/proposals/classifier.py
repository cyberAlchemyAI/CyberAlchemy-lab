"""Classify computed field changes; caller labels never select proof scope."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import jsonschema
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'references'))
import resolver as r
s=r.s
BASE=Path(__file__).resolve().parent
KIND_FIELDS={'id','version','pairs','fields','source','axis_id','unique_question','operational_effect',
             'forbidden_inferences','source_posture','effective_state'}
REGISTRY_FIELDS={'schema','normalization_version','kinds','node_kinds','kind_count','ordered_pair_count','authority_effect'}


def identity(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def differences(before,after,path=''):
    if before==after:return []
    if isinstance(before,dict) and isinstance(after,dict):
        output=[]
        for key in sorted(set(before)|set(after)):
            sub=path+'/'+key.replace('~','~0').replace('/','~1')
            if key not in before:output.append({'path':sub,'change':'added','after':after[key]})
            elif key not in after:output.append({'path':sub,'change':'removed','before':before[key]})
            else:output.extend(differences(before[key],after[key],sub))
        return output
    if isinstance(before,list) and isinstance(after,list):
        output=[]
        for index in range(max(len(before),len(after))):
            sub=path+'/'+str(index)
            if index>=len(before):output.append({'path':sub,'change':'added','after':after[index]})
            elif index>=len(after):output.append({'path':sub,'change':'removed','before':before[index]})
            else:output.extend(differences(before[index],after[index],sub))
        return output
    return [{'path':path,'change':'changed','before':before,'after':after}]


def structural_registry(registry):
    s.require(isinstance(registry,dict) and REGISTRY_FIELDS<=set(registry),'missing registry fields')
    s.require(isinstance(registry['kinds'],list) and isinstance(registry['node_kinds'],list),'registry collections must be lists')
    s.require(len(set(registry['node_kinds']))==len(registry['node_kinds']) and all(isinstance(k,str) and k and k!='*' for k in registry['node_kinds']),'invalid node kinds')
    ids=[];pairs=0
    for kind in registry['kinds']:
        s.require(KIND_FIELDS<=set(kind),'missing relation declaration fields')
        s.require(all(isinstance(kind[k],str) and kind[k] for k in ['id','version','axis_id','unique_question','operational_effect']),'invalid declaration text')
        ids.append(kind['id']);fields=kind['fields'];ps=kind['pairs']
        s.require(isinstance(fields,list) and all(isinstance(x,str) and x for x in fields) and len(set(fields))==len(fields),'invalid qualifier fields')
        s.require(isinstance(ps,list) and all(isinstance(p,dict) and set(p)=={'source_kind','target_kind'} and all(v in registry['node_kinds'] for v in p.values()) for p in ps),'invalid ordered pairs')
        s.require(len({(p['source_kind'],p['target_kind']) for p in ps})==len(ps),'duplicate ordered pair')
        s.require(isinstance(kind['forbidden_inferences'],list) and all(isinstance(v,str) and v for v in kind['forbidden_inferences']),'invalid forbidden inference declarations')
        s.require(isinstance(kind['source'],dict) and set(kind['source'])=={'path','sha256'},'invalid declaration source identity')
        s.check_binding(kind['source'])
        s.require(kind['version']=='sha256:'+kind['source']['sha256'],'declaration version/source mismatch')
        pairs+=len(ps)
    s.require(len(set(ids))==len(ids)==registry['kind_count'],'kind omission or duplication')
    s.require(pairs==registry['ordered_pair_count'],'pair count mismatch')


def baseline():
    return {'registry':s.read(s.BASE/'registry/normalized-registry.json'), 'rules':[],
            'graph':r.from_decoder((s.BASE/'demonstrations/l0/input.json').read_bytes())}


def classify(proposal,bind_baseline=True):
    jsonschema.Draft202012Validator(s.read(BASE/'proposal-schema.json')).validate(proposal)
    before=proposal['before'];after=proposal['after']
    s.require(proposal['baseline_identity']==identity(before),'wrong baseline identity')
    if bind_baseline:s.require(before==baseline(),'proposal is not based on the selected current baseline')
    structural_registry(before['registry']);structural_registry(after['registry'])
    changes=differences(before,after);old=before['registry'];new=after['registry']
    old_kinds={k['id']:k for k in old['kinds']};new_kinds={k['id']:k for k in new['kinds']}
    removed=sorted(set(old_kinds)-set(new_kinds));added=sorted(set(new_kinds)-set(old_kinds));modified=[]
    field_changes=[];unknown=[]
    for kind_id in sorted(set(old_kinds)&set(new_kinds)):
        diff=differences(old_kinds[kind_id],new_kinds[kind_id])
        if diff:modified.append(kind_id)
        for item in diff:
            first=item['path'].split('/')[1];category={
                'pairs':'ordered-pair-change','fields':'qualifier-contract-change','version':'exact-version-change',
                'source':'exact-source-identity-change','axis_id':'axis-meaning-change','unique_question':'semantic-question-change',
                'operational_effect':'operational-meaning-change','forbidden_inferences':'forbidden-inference-change',
                'source_posture':'source-posture-change','effective_state':'effective-state-change','id':'identity-change'}.get(first,'unclassified')
            entry={**item,'kind_id':kind_id,'classification':category};field_changes.append(entry)
            if category=='unclassified':unknown.append(entry)
    for stage in [old,new]:
        for field in set(stage)-REGISTRY_FIELDS:unknown.append({'path':'/registry/'+field,'classification':'unclassified'})
        for kind in stage['kinds']:
            for field in set(kind)-KIND_FIELDS:unknown.append({'path':'/registry/kinds/'+kind['id']+'/'+field,'classification':'unclassified'})
    schema_changed=any(old[k]!=new[k] for k in ['schema','normalization_version','authority_effect'])
    nodes_changed=old['node_kinds']!=new['node_kinds']
    rules_changed=before['rules']!=after['rules'];data_changed=before['graph']!=after['graph']
    no_registry_semantic_change=(not removed and not added and not modified and not nodes_changed and not schema_changed)
    if unknown:profile='unsupported-unclassified'
    elif no_registry_semantic_change and not rules_changed:profile='instance-only' if data_changed else 'unchanged'
    elif added and not removed and not modified and not nodes_changed and not schema_changed and not rules_changed:
        profile='fresh-kind-extension'
    elif no_registry_semantic_change and rules_changed:profile='rule-only-extension'
    else:profile='unsupported-structural-or-semantic-change'
    # Append-only order is part of the constructive preservation profile. A
    # reorder may retain equivalent semantics but needs a different proof.
    if profile=='fresh-kind-extension' and new['kinds'][:len(old['kinds'])]!=old['kinds']:
        profile='unsupported-reordered-extension'
    return {'schema':'relational.change-classification/v1','proposal_id':proposal['proposal_id'],
            'proposal_identity':identity(proposal),'before_identity':identity(before),'after_identity':identity(after),
            'profile':profile,'computed_changes':changes,'changed_kind_fields':field_changes,'added_kind_ids':added,
            'removed_kind_ids':removed,'modified_kind_ids':modified,'unclassified_changes':unknown,
            'rule_change':rules_changed,'graph_change':data_changed,'schema_change':schema_changed,'node_kind_change':nodes_changed,
            'selected_data_compatibility':'unchecked','invariant_preservation':'unchecked','model_conservativity':'unchecked',
            'full_source_semantics':'unsupported; inherited baseline obligations remain visible',
            'authority_effect':'none'}
