"""Deterministic authoring of the 83 explicitly selected candidate targets."""
import copy
from catalog import TYPES, RELATIONS, LIFECYCLES, EVALUATIONS, POLICIES, DERIVED, LIMITS
from schemas import obj, array, TEXT, HASH, record_schema, profile_shapes
from examples import SUPPORT_KINDS, graph_records, graph_relations, profile_example
from support import ROOT, LAB, PREVIOUS, L1, load, dump, sha, binding, module, need
BASE=ROOT.parent/'0003-review-led-reconstruction'

def selected_targets():
    rows=load(PREVIOUS/'reconciliation.json')['targets']
    return [x['target_id'] for x in rows if x['construction_state']=='scaffold-only']

def semantic_bindings(target,scaffold):
    slug=target.split('.',1)[1]
    overrides={'capability-realization-binding':'product-capability','measurement-method':'residue-measurement','measurement-result':'residue-measurement','context-profile':'context','model-instance-binding':'parent-instance-authority-separation-invariant'}
    slug=overrides.get(slug,slug)
    candidates={x['target_id']:x for x in load(L1/'registry.json')['entries']}
    if 'semantic.'+slug in candidates:
        entry=candidates['semantic.'+slug]; path=LAB/entry['path']; data=load(path)
        return [{'definition_ref':data['definition_id']+'@'+data['version'],**binding(path),'admission_posture':'candidate-unadmitted'}],['semantic.'+slug]
    terms={'product':'Product','project':'Project'}
    if slug in terms:
        entry=next(x for x in load(LAB/'authority/definitions/registry.json')['entries'] if x['term']==terms[slug] and x['lifecycle_state']=='admitted')
        return [{'definition_ref':entry['definition_id']+'@'+entry['version'],**binding(LAB/entry['path']),'admission_posture':'admitted','admission_decision_ref':entry['admission_decision_ref']}],[]
    return [],[]

def build():
    targets=selected_targets()
    expected=['type.'+x for x in TYPES]+['profile.'+x for x in POLICIES]+['profile.'+x for x in LIFECYCLES]+['profile.'+x for x in EVALUATIONS]+['relation.'+x for x in RELATIONS]+['derived.'+x for x in DERIVED]
    need(len(targets)==83 and set(targets)==set(expected),'The 83-target frontier changed')
    index={x['target_id']:x for x in load(BASE/'target-candidate-index.json')['entries']}
    scaffolds={x:load(BASE/index[x]['machine_path']) for x in targets}
    ref=obj({'path':TEXT,'sha256':HASH})
    dump(ROOT/'support-node.schema.json',obj({'node_id':TEXT,'kind':{'enum':SUPPORT_KINDS},'status':{'const':'fixture-only'},'authority_effect':{'const':'none'},'scope_ref':TEXT,'owner_ref':TEXT,'fixture_only':{'const':True}}))
    dump(ROOT/'graph-manifest.schema.json',obj({'schema_version':{'const':'cal-review-graph-manifest/v1'},'authority_effect':{'const':'none'},'nodes':array(ref,1,10000),'relations':array(ref,0,20000)}))
    renderer=module(LAB/'tooling/generators/artifact_surface.py','batch_renderer')
    template=load(PREVIOUS/'artifact-types/projection-spec/v1/artifact.json')
    registry=[]; seed_targets=set(); admitted=[]; all_sources=[]
    for target in targets:
        folder=ROOT/'targets'/target; scaffold=scaffolds[target]; family=scaffold['family']; name=target.split('.',1)[1]
        scaffold_path=BASE/index[target]['machine_path']; refs,seeds=semantic_bindings(target,scaffold); seed_targets.update(seeds)
        admitted.extend(x for x in refs if x['admission_posture']=='admitted')
        all_sources.extend(scaffold['source_refs'])
        base={'target_id':target,'family':family,'status':'candidate-unadmitted','authority_effect':'none','normalization_contract':scaffold['normalized_contract'],'scaffold':binding(scaffold_path),'owner_route':scaffold['owner_route'],'claim_ceiling':LIMITS[family],
            'implementation':[binding(ROOT/x) for x in ['engine.py','catalog.py','profiles.py','schemas.py']], 'semantic_definition_bindings':refs}
        if family=='artifact-type':
            schema=record_schema(name); dump(folder/'schema.json',schema)
            artifact=copy.deepcopy(template); definition_refs=[x['definition_ref'] for x in refs]
            artifact.update(artifact_type_id='cal.artifact-type.'+name,artifact_type_ref='cal.artifact-type.'+name+'/v1',name=scaffold['normalized_contract']['name'],schema_ref='cal.schema.'+name+'-review-candidate/v1',schema_digest=sha(folder/'schema.json'),semantic_definition_refs=definition_refs,semantic_definition_bindings=refs,distinct_validation_purpose=scaffold['normalized_contract']['distinct_validation_purpose'])
            artifact['classification'].update(semantic_kind=name,lifecycle_posture_ref='candidate:remaining-targets-review/v1')
            artifact['instance_contract'].update(canonical_filename='record.json',human_filename='RECORD.md',identity_field='node_id',required_semantic_fields=sorted(set(schema['required'])-{'status','authority_effect'}))
            artifact['orthogonality_rules']=[{'rule_id':'BATCH-IDENTITY','statement':'Candidate identity and exact graph references do not authenticate owners or execute effects.'},{'rule_id':'BATCH-SCOPE','statement':scaffold['normalized_contract']['distinct_validation_purpose']}]
            artifact['four_facets']={'classification':'Candidate '+scaffold['normalized_contract']['name']+' with explicit source bindings.','schema':'Closed target-specific record contract.','machine_checkable':'Schema, typed reference closure and target-specific graph consistency checks.','human_continuation':'Generated RECORD.md and REVIEW.md document the example and its limits.'}
            artifact['typed_residue']=[{'residue_id':'BATCH-R1','owner_ref':'role:target-owner','missing':'Authenticated identity, real execution or domain proof, and owner admission.','consequence':LIMITS[family]}]
            artifact['claim_ceiling']=LIMITS[family]
            artifact['validation_contract'].update(positive_witness='fixtures/valid/record.json',positive_projection='fixtures/valid/RECORD.md',negative_witnesses=['fixtures/invalid/authority.json','fixtures/invalid/missing-field.json','fixtures/invalid/extra-field.json'],validator_path=str((ROOT/'validate.py').relative_to(LAB)))
            dump(folder/'artifact.json',artifact)
        elif family=='profile':
            p,q,bad=profile_example(name); a,b=profile_shapes(name)
            dump(folder/'parameters.schema.json',a); dump(folder/'input.schema.json',b)
            dump(folder/'parameters.json',p); dump(folder/'fixtures/valid/input.json',q); dump(folder/'fixtures/adverse/input.json',bad)
            base['carrier_ref']=scaffold['normalized_contract']['artifact_type_ref']; base['parameter_binding']=binding(folder/'parameters.json')
            base['integration_limit']='This proposed profile has its own closed input contract; earlier frozen carriers are not retrofitted or activated.'
        elif family=='relation-kind':
            source,target_kind=RELATIONS[name]; base.update(scaffold['normalized_contract']); base.update(source_kinds=source.split('|'),target_kinds=target_kind.split('|'),self_relations='rejected',evidence_required=True)
        else:
            base.update(source_kinds=DERIVED[name][0],relation_kinds=DERIVED[name][1],ordering='node_id then relation_id',activation='none')
        dump(folder/'contract.json',base)
        path=folder/('artifact.json' if family=='artifact-type' else 'contract.json')
        registry.append({'target_id':target,'family':family,'status':'candidate-unadmitted',**binding(path)})
    nodes=graph_records()
    contracts={x:scaffolds['relation.'+x]['normalized_contract'] for x in RELATIONS}
    edges=graph_relations(nodes,contracts)
    for node in nodes:
        name=node['kind']
        if name in TYPES and node['node_id']=='example:'+name:
            folder=ROOT/'targets'/('type.'+name)
            dump(folder/'fixtures/valid/record.json',node)
            bad=copy.deepcopy(node); bad['authority_effect']='admit'; dump(folder/'fixtures/invalid/authority.json',bad)
            bad=copy.deepcopy(node); bad.pop(next(iter(TYPES[name]))); dump(folder/'fixtures/invalid/missing-field.json',bad)
            bad=copy.deepcopy(node); bad['implicitly_authorized']=True; dump(folder/'fixtures/invalid/extra-field.json',bad)
            artifact=load(folder/'artifact.json'); (folder/'ARTIFACT.md').write_text(renderer.render_artifact(artifact)); (folder/'fixtures/valid/RECORD.md').write_text(renderer.render_instance(artifact,load(folder/'fixtures/valid/record.json')))
    graph={'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':nodes,'relations':edges}
    dump(ROOT/'examples/graph.json',graph)
    manifest={'schema_version':'cal-review-graph-manifest/v1','authority_effect':'none','nodes':[],'relations':[]}
    for i,node in enumerate(nodes):
        path=ROOT/f'examples/nodes/{i:03}.json'; dump(path,node); manifest['nodes'].append(binding(path))
    for edge in edges:
        path=ROOT/'examples/relations'/(edge['kind']+'.json'); dump(path,edge); manifest['relations'].append(binding(path))
        folder=ROOT/'targets'/('relation.'+edge['kind']); dump(folder/'fixtures/valid/relation.json',edge)
        bad=copy.deepcopy(edge); bad['target']='missing:target'; dump(folder/'fixtures/adverse/relation.json',bad)
    dump(ROOT/'examples/graph-manifest.json',manifest)
    from engine import project, relation_schema, profile_eval
    for name in RELATIONS: dump(ROOT/'targets'/('relation.'+name)/'instance.schema.json',relation_schema(name))
    for name in POLICIES+list(LIFECYCLES)+list(EVALUATIONS):
        folder=ROOT/'targets'/('profile.'+name); dump(folder/'fixtures/expected.json',profile_eval(name,load(folder/'parameters.json'),load(folder/'fixtures/valid/input.json')))
        dump(folder/'fixtures/adverse/expected.json',profile_eval(name,load(folder/'parameters.json'),load(folder/'fixtures/adverse/input.json')))
    for name in DERIVED:
        folder=ROOT/'targets'/('derived.'+name); dump(folder/'view.json',{'input':binding(ROOT/'examples/graph-manifest.json'),'result':project(name,graph)})
    dump(ROOT/'registry.json',{'authority_effect':'none','entries':registry})
    edges_dep=load(L1/'batches.json')['edges']; closure=set(seed_targets)
    while True:
        expanded=closure|{x['dependency_target_id'] for x in edges_dep if x['consumer_target_id'] in closure}
        if expanded==closure: break
        closure=expanded
    definitions={x['target_id']:x for x in load(L1/'registry.json')['entries']}
    sources={str(x):x for x in all_sources}
    dump(ROOT/'dependencies.json',{'authority_effect':'none','seed_targets':sorted(seed_targets),'definitions':[{'target_id':x,**binding(LAB/definitions[x]['path'])} for x in sorted(closure)],'admitted_definitions':list({x['path']:x for x in admitted}.values()),'source_lineage_residue':[x for x in load(L1/'drift-audit.json')['legacy_reference_residue'] if x['consumer_target_id'] in closure],'selected_source_refs':list(sources.values()),'inputs':[binding(PREVIOUS/'manifest.json'),binding(BASE/'target-candidate-index.json'),binding(L1/'manifest.json'),binding(L1/'batches.json'),binding(LAB/'authority/definitions/registry.json'),binding(LAB/'docs/normalizations/0001-definition-migration-model/normalization.json')]+[binding(BASE/index[x]['machine_path']) for x in targets]})
    for target in targets:
        folder=ROOT/'targets'/target; base=load(folder/'contract.json'); family=base['family']
        detail=('Fields: '+', '.join(TYPES[target.split('.',1)[1]])) if family=='artifact-type' else ('Contract: '+str(base['normalization_contract']))
        text='# '+target+'\n\n'+base['normalization_contract'].get('distinct_validation_purpose',base['normalization_contract'].get('name',target))+'\n\n'
        text+='Exact inputs -> candidate checks -> review evidence -> owner adoption.\n\n'+detail+'\n\n'+LIMITS[family]+'\n\n'
        if family=='artifact-type': text+='References are validated inside the bound example graph. Support nodes are explicitly fixture-only and do not prove real runs or grants.\n\n'
        if family=='profile': text+='Read parameters.json and the valid/adverse example results before adoption. These are proposed policy settings, not previously approved operational policy. Boolean evidence and gate assertions are not authenticated.\n\n'
        if family=='derived-surface': text+='view.json includes the exact input manifest. Team current/history is evaluated at the fixed as-of instant; other views show only supplied records.\n\n'
        text+='Approval meaning: adopt this exact candidate contract and its stated limits for a named scope. The batch itself authorizes no adoption, publication, deletion, identity verification or runtime cutover.\n'
        (folder/'REVIEW.md').write_text(text)
if __name__=='__main__': build()
