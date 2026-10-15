#!/usr/bin/env python3
"""Stage exact immutable candidate catalog packages; no canonical writes."""
import copy
import json
from pathlib import Path
from bootstrap import *


def ref(repo, path, *, sized=False):
    raw = file_bytes(path)
    value = {'path':path.relative_to(repo).as_posix(),'sha256':byte_digest(raw)}
    if sized: value['size_bytes'] = len(raw)
    return value


def seed_materials(baseline):
    originals = RUNTIME/'semantic-proposals/method/v1'
    schema = file_bytes(originals/'schema.json'); method = load(originals/'example.json')
    implementation = load(ROOT/'authority/artifact-types/implementation/v1/fixtures/valid/record.json')
    capabilities=[s for s in baseline['subjects'].values() if s['kind']=='product-capability' and s['effective_state']=='admitted-current']
    require(len(capabilities)==1,'explicit Product Capability ambiguous')
    capability=capabilities[0]
    implementation.update(node_id='implementation:lab-candidate-catalog-generator', name='Candidate catalog and Method projection generator',
                          relation_refs=[{'relation_kind_ref':'relation.realizes','direction':'source','counterpart_kind':'product-capability','counterpart_ref':capability['identity']}],evidence_refs=['evidence:S01:exact-executable-manifest'],
                          claim_ceiling='Candidate exact generator realization; no conformance, value, owner admission, activation or execution grant.')
    implementation['payload'].update(implementation_kind='candidate-catalog-generator',
        conforms_to_schema_refs=['urn:cyberalchemy-lab:candidate-carrier:method:v1'],
        realizes_capability_refs=[capability['identity']],
        execution_entrypoint_ref=(PACKAGE/'generator.py').relative_to(ROOT).as_posix(),
        environment_contract_ref='candidate-contract:python-3:jsonschema-and-cryptography')
    descriptor={'artifact_type_ref':METHOD_TYPE,'semantic_kind':'method','semantic_definition_refs':[METHOD_DEFINITION],
                'schema_path':'method/schema.json','schema_sha256':byte_digest(schema),'schema_selector':None,
                'distinct_validation_purpose':'Closed repeatable Method specification, separate from Method Binding, workflow, Definition meaning, and application authority.'}
    materials={'baseline.json':encoded(baseline),'identities.json':file_bytes(RUNTIME/'design/contract-impact.json'),
               'environment-contract.json':encoded(environment_contract()),
               'generator-manifest.json':encoded(executable_manifest()),'method/schema.json':schema,
               'method/artifact.json':encoded(descriptor),'method/example.json':encoded(method),
               'method/example.md':method_markdown(method),'generator-implementation.json':encoded(implementation)}
    mappings=[]
    for carrier,kind,selector,fields in [('cal.artifact-type.project-identity/v1','project','/project_id',['purpose','coordination_scope']),
        ('cal.artifact-type.product-identity/v2','product','/product_id',['purpose','value_promise','scope'])]:
        c=baseline['contracts'][carrier]
        mappings.append({'carrier_ref':carrier,'descriptor_sha256':c['artifact_sha256'],'schema_sha256':c['schema_sha256'],
            'endpoint_kind':kind,'identity_selector':selector,'meaning_fields':fields,'posture':'candidate-semantic-review-required',
            'owner_ref':'role:definition-owner','authority_effect':'none'})
    def target(path,identity,version,selector,category,carrier,kind):
        return {'version_ref':version,'identity_ref':identity,'identity_selector':selector,'category':category,
                'identity_transform':'artifact-type-ref-root' if category=='artifact-type' else 'none',
                'carrier_ref':carrier,'semantic_kind':kind,'path':path,'sha256':byte_digest(materials[path]),'predecessor_ref':None}
    targets=[target('method/artifact.json',METHOD_TYPE.rsplit('/',1)[0],METHOD_TYPE,'/artifact_type_ref','artifact-type','cal.artifact-type.artifact-type/v3','artifact-type'),
        target('method/example.json',method['method_id'],method['method_id']+'@'+method['version'],'/method_id','artifact-instance',METHOD_TYPE,'method'),
        target('generator-implementation.json',implementation['node_id'],implementation['node_id']+'@candidate.1','/node_id','artifact-instance','cal.artifact-type.implementation/v1','implementation')]
    method_endpoint={'ref':method['method_id'],'version_ref':method['method_id']+'@'+method['version'],'kind':'method'}
    for kind in ['project','product']:
        subjects=[s for s in baseline['subjects'].values() if s['kind']==kind and s['effective_state']=='admitted-current']
        require(len(subjects)==1,'explicit source endpoint ambiguous')
        source=subjects[0]
        relation=load(ROOT/'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/fixtures/valid/record.json')
        relation.update(node_id='typed-relation:candidate-bootstrap:'+kind+'-uses-method',name='Candidate '+kind+' Method usage',
            lifecycle_state='candidate',relation_refs=[],evidence_refs=['evidence:S01:candidate-typed-closure'],
            claim_ceiling='Candidate exact existing uses-method pair; no connection admission or Method application authority.')
        relation['payload']={'relation_kind_ref':'relation.uses-method','source':{'ref':source['identity'],'version_ref':source['version_ref'],'kind':kind},
            'target':method_endpoint,'qualifiers':{'usage_role':'bounded-state-inspection'},'relation_lifecycle_state':'candidate',
            'relation_evidence_refs':['evidence:S01:candidate-typed-closure']}
        path='relations/'+kind+'-uses-method.json';materials[path]=encoded(relation)
        targets.append(target(path,relation['node_id'],relation['node_id']+'@candidate.1','/node_id','typed-relation','cal.artifact-type.typed-relation/v3','typed-relation'))
    realization=load(ROOT/'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/fixtures/valid/record.json')
    realization.update(node_id='typed-relation:candidate-bootstrap:generator-realizes-capability',name='Candidate generator realization',relation_refs=[],lifecycle_state='candidate',
        evidence_refs=['evidence:S01:exact-executable-manifest'],claim_ceiling='Candidate realization proposal; no adoption, usefulness or runtime activation claim.')
    realization['payload'].update(relation_kind_ref='relation.realizes',source={'ref':implementation['node_id'],'version_ref':implementation['node_id']+'@candidate.1','kind':'implementation'},
        target={'ref':capability['identity'],'version_ref':capability['version_ref'],'kind':'product-capability'},
        qualifiers={'realization_role':'candidate-catalog-and-Method-projection','exact_target_version_ref':capability['version_ref']},
        relation_lifecycle_state='candidate',relation_evidence_refs=['evidence:S01:exact-executable-manifest'])
    path='relations/generator-realizes-capability.json';materials[path]=encoded(realization)
    targets.append(target(path,realization['node_id'],realization['node_id']+'@candidate.1','/node_id','typed-relation','cal.artifact-type.typed-relation/v3','typed-relation'))
    mechanics={'schema_version':'lab-candidate-type-mechanics/v1','authority_effect':'none','artifact_type_ref':METHOD_TYPE,
        'artifact_type_id':METHOD_TYPE.rsplit('/',1)[0],
        'owner_ref':'role:artifact-type-owner','identity_selector':'/method_id','version_selector':'/version',
        'instance_discriminator':{'path':'/schema_version','value':'cyberalchemy-lab-method/v1-candidate'},
        'lifecycle':{'initial':'candidate-unadmitted','revision':'exact predecessor and stable identity','admission':'separate R08 owner decision','activation':'separate action authorization'},
        'generator':{'path':(PACKAGE/'generator.py').relative_to(ROOT).as_posix(),'sha256':byte_digest(file_bytes(PACKAGE/'generator.py')),'mode':'generated-only'},
        'validation':{'schema':'closed exact instance schema','projection':'deterministic canonical-body roundtrip','semantics':'separate owner review'},
        'relation_surface':sorted(k for k,r in baseline['relation_contracts'].items() if any('method' in pair.values() for pair in r['payload']['allowed_endpoint_pairs'])),
        'orthogonality':['Definition meaning != Method instance','Method != Method Binding','Method != Workflow','Method admission != Method application'],
        'claim_ceiling':'Exact candidate type mechanics; semantic admission and effective registry remain separate owner effects.'}
    inp={'schema_version':'lab-candidate-catalog-input/v1','authority_effect':'none','baseline_profile_sha256':baseline['source_profile_sha256'],
        'baseline_snapshot_digest':baseline['snapshot_digest'],'identity_bindings_sha256':byte_digest(materials['identities.json']),
        'generator_manifest_sha256':byte_digest(materials['generator-manifest.json']),'endpoint_mappings':mappings,'targets':targets,
        'type_mechanics':{METHOD_TYPE:mechanics}}
    materials['method/mechanics.json']=encoded(mechanics);materials['input.json']=encoded(inp)
    return materials


def write_package(repo, destination, materials, *, parent_selection=None):
    """Same executable, independently reviewed profiles and original file bindings."""
    repo=Path(repo).resolve();destination=Path(destination)
    require(destination.is_relative_to(repo/'implementation/lab-bootstrap/candidates/v1/packages'), 'candidate staging path outside task scope')
    require(not destination.exists(), 'candidate packages are immutable; use a new package number')
    materials=copy.deepcopy(materials);catalog=compose(materials);materials['catalog.json']=encoded(catalog)
    prefix=destination.relative_to(repo).as_posix()+'/'
    native={'schema_version':'lab-native-source-bindings/v1-candidate','authority_effect':'none','subject_bindings':[
        {'version_ref':t['version_ref'],'identity_ref':pointer(t['record'],t['identity_selector']),'identity_selector':t['identity_selector'],
         'path':prefix+t['path'],'sha256':t['sha256'],'semantic_kind':t['semantic_kind'],'carrier_ref':t['carrier_ref']} for t in catalog['candidate_subjects'].values()]}
    materials['bindings.json']=encoded(native)
    destination.mkdir(parents=True)
    def put(name,raw):
        p=under(destination,name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    for name,raw in materials.items():put(name,raw)
    content=[ref(repo,destination/n,sized=True) for n in sorted(materials)]
    basis=[ref(repo,destination/'input.json')]
    if parent_selection is not None:
        parent_ref=parent_selection.controls['profile'];basis=[parent_ref]
        content.append(ref(repo,under(repo,parent_ref['path']),sized=True))
    expected_cut='candidate-catalog:'+catalog['digest']
    put('content-manifest.json',encoded({'schema_version':'lab-source-content-manifest/v1-candidate','authority_effect':'none',
        'source_cut':expected_cut,'materials':content}))
    code_roots=[RUNTIME.relative_to(ROOT).as_posix()+'/lab_runtime',RUNTIME.relative_to(ROOT).as_posix()+'/lab.py',
                (PACKAGE/'bootstrap.py').relative_to(ROOT).as_posix(),(PACKAGE/'generator.py').relative_to(ROOT).as_posix()]
    policy={'schema_version':'lab-source-capture-policy/v1-candidate','authority_effect':'none',
        'policy_id':'policy:isolated-catalog:'+catalog['digest'],'allowed_source_roots':['implementation/lab-bootstrap/candidates/v1/packages'],
        'max_files':5000,'max_source_bytes':128*1024**2,'capture_provider':'native-byte-manifest',
        'capture_config':ref(repo,destination/'bindings.json'),'code_roots':code_roots,
        'compatibility_binding':ref(repo,repo/'docs/proposals/0007-lab-integrated-schema-package/schema-dependencies.json')}
    put('policy.json',encoded(policy))
    profile={'schema_version':'lab-independent-source-profile/v1-candidate','authority_effect':'none',
        'profile_id':'source-profile:isolated-catalog:'+catalog['digest'],'protocol_version':1,
        'executable_manifest_sha256':ref(repo,destination/'generator-manifest.json')['sha256'],
        'policy_core_sha256':ref(repo,destination/'policy.json')['sha256'],
        'authority_basis':[ref(repo,destination/'input.json')],'registries':[ref(repo,destination/'catalog.json')],
        'content_manifest':ref(repo,destination/'content-manifest.json'),'expected_cut':expected_cut,'domain_posture':'isolated-candidate',
        'transition_basis':{'mode':'initial' if parent_selection is None else 'reviewed-successor','basis_refs':basis}}
    put('profile.json',encoded(profile))
    review={'schema_version':'lab-profile-selection-review/v1-candidate','authority_effect':'none','purpose':'candidate-read-selection-only',
        'profile_sha256':ref(repo,destination/'profile.json')['sha256'],'policy_sha256':ref(repo,destination/'policy.json')['sha256'],
        'executable_manifest_sha256':profile['executable_manifest_sha256'],'content_manifest_sha256':profile['content_manifest']['sha256'],
        'expected_cut':expected_cut,'domain_posture':'isolated-candidate','scope_ref':'scope:S01:isolated-candidate-bootstrap',
        'provenance_ref':'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/context-S01.json'}
    put('selection-review.json',encoded(review))
    kwargs={'profile_path':ref(repo,destination/'profile.json')['path'],'profile_sha256':review['profile_sha256'],
        'policy_path':ref(repo,destination/'policy.json')['path'],'executable_manifest_path':ref(repo,destination/'generator-manifest.json')['path'],
        'review_path':ref(repo,destination/'selection-review.json')['path'],'review_sha256':ref(repo,destination/'selection-review.json')['sha256']}
    put('selection.json',encoded(kwargs))
    # External manifest includes every staged file and source bindings, never self-hashes.
    manifest={'schema_version':'lab-exact-candidate-package-manifest/v1','authority_effect':'none','catalog_digest':catalog['digest'],
        'contract_versions':len(catalog['contracts']),'source_subjects':len(catalog['source_subjects']),
        'candidate_subjects':len(catalog['candidate_subjects']),'relation_kinds':len(catalog['relation_contracts']),
        'file_bindings':[ref(repo,p,sized=True) for p in sorted(destination.rglob('*')) if p.is_file()],
        'source_bindings':load(ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/context-S01.json')['source_bindings'],
        'actual_owner_outcome':None,'admitted_registry_mutations':0}
    put('PACKAGE-MANIFEST.json',encoded(manifest))
    selected=select(repo,**kwargs);package_materials(repo,selected)
    return selected,catalog


def main():
    selections=load(RUNTIME/'profiles/selections.json')['selections']
    row=next(r for r in selections if r['name']=='d75')
    selected=select(ROOT,**{k:v for k,v in row.items() if k not in ['name','source_materials','source_bytes']})
    baseline=capture(selected);materials=seed_materials(baseline)
    index=1
    while (PACKAGE/f'packages/{index:04d}').exists():index+=1
    candidate,catalog=write_package(ROOT,PACKAGE/f'packages/{index:04d}',materials)
    print(json.dumps({'package':f'packages/{index:04d}','contracts':len(catalog['contracts']),
        'source_subjects':len(catalog['source_subjects']),'candidate_subjects':len(catalog['candidate_subjects']),
        'profile_sha256':candidate.profile_sha256,'authority_effect':'none'}))


if __name__=='__main__':main()
