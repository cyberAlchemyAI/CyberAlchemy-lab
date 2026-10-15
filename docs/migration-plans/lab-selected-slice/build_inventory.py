"""Bounded O04 inventory. Reads exact nominated paths; never executes sources."""
import collections
import copy
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'implementation/lab-ontology/candidates/v1/adapters'))
from represented_subjects import (parse,sha,object_sha,require,original,bind,MAPPING,MAPPING_SHA)
from jsonschema import Draft202012Validator

HERE=Path(__file__).resolve().parent
MANIFEST=ROOT/'implementation/bindings/ontology-product-event-runtime/v4/source-manifest.json'
PACKAGE_KEY='pkg-d6e11c35825b4e78ad3eb7a6aba86194173ddf5023f943a2858aec35978a3bb2'
SOURCE_ROOT=Path('/home/vlad_/projects/domainspec-core/cyberAlchemy-v2')
WORKSPACE_ROOT=SOURCE_ROOT.parent
STANDALONE_ROOT=Path('/home/vlad_/projects/cyberAlchemy-v2')
PROFILE_PATH='ontology/product/profile.json'
NAMESPACE='lab.legacy-source-assertion.cav2-product-thesis'
TARGET=ROOT/'implementation/lab-ontology/candidates/v1/migration/source-selection.json'


def git(root,*args):
    return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()


def repository(root):
    top=Path(git(root,'rev-parse','--show-toplevel')).resolve()
    metadata=[]
    refs=['HEAD'];symbolic=subprocess.run(['git','-C',str(root),'symbolic-ref','-q','HEAD'],stdout=subprocess.PIPE,text=True)
    if symbolic.returncode==0:refs.append(symbolic.stdout.strip())
    for ref in refs:
        p=Path(git(root,'rev-parse','--git-path',ref))
        if not p.is_absolute():p=root/p
        if p.is_file():metadata.append({'path':str(p.resolve()),'sha256':sha(p.read_bytes())})
    if len(metadata)<len(refs):
        p=Path(git(root,'rev-parse','--git-path','packed-refs'))
        if not p.is_absolute():p=root/p
        require(p.is_file(),'repository ref has no inspectable binding')
        metadata.append({'path':str(p.resolve()),'sha256':sha(p.read_bytes())})
    return {'material_root':str(root),'git_root':str(top),'head':git(root,'rev-parse','HEAD'),
        'root_is_git_repository':root==top,'repository_ref_bindings':metadata,
        'repository_identity':'local-git:'+sha(str(top).encode())}


def safe(root,path):
    require(type(path) is str and path and not Path(path).is_absolute() and '\\' not in path
        and Path(path).as_posix()==path and all(p not in ('.','..') for p in Path(path).parts), 'unsafe source relative path')
    require(root.is_dir() and not root.is_symlink(),'source root unavailable or symlink')
    current=root
    for part in Path(path).parts:
        current=current/part
        require(not current.is_symlink(),'source path symlink')
    require(current.resolve().is_relative_to(root.resolve()),'source escapes selected root')
    return current


def observation(root_ref,root,path,expected_sha):
    p=safe(root,path);exists=p.is_file();actual=sha(p.read_bytes()) if exists else None
    return {'root_ref':root_ref,'path':path,'material_path':str(p),'expected_sha256':expected_sha,
        'observed_sha256':actual,'available':exists,'expected_bytes_match':bool(exists and actual==expected_sha)}


def source_id(binding,selector,legacy_identity):
    return 'source-observation:'+sha(json.dumps([binding['root_ref'],binding['path'],binding['sha256'],selector,legacy_identity],
        separators=(',',':'),ensure_ascii=False).encode())


def carrier(ref,contracts,inventory):
    selected=next((c for c in inventory['carriers'] if c['carrier_ref']==ref),None)
    if selected:
        b={'path':selected['schema_path'],'sha256':selected['schema_sha256']}
        original(b)
        if ref in contracts:
            require(contracts[ref]['schema_path']==b['path'] and contracts[ref]['schema_sha256']==b['sha256'],
                'selected carrier inventory/signed schema join differs')
        return {'carrier_ref':ref,'semantic_kind':selected['semantic_kind'],'schema_binding':b,
            'catalog_posture':contracts.get(ref,{}).get('lifecycle_state','unresolved'),
            'meaning_inferred':False}
    proposal=next((p for p in inventory['endpoint_proposals'] if p['carrier_ref']==ref),None)
    require(proposal is not None,'unselected carrier hint')
    b={k:proposal['schema_binding'][k] for k in ('path','sha256')};original(b)
    return {'carrier_ref':ref,'semantic_kind':proposal['endpoint_kind'],'schema_binding':b,
        'catalog_posture':'candidate-unadmitted-proposal','meaning_inferred':False}


def semantic_fit(record,role,contracts,inventory):
    hints={'product':'cal.artifact-type.product-identity/v2','thesis':'cal.artifact-type.product-thesis/v1',
        'capability':'cal.artifact-type.product-capability/v1','project':'cal.artifact-type.project-identity/v1',
        'goal':'cal.artifact-type.goal/v1','research':'cal.artifact-type.research-inquiry/v1',
        'experiment':'cal.artifact-type.experiment-design/v1','method':'cal.artifact-type.method/v1'}
    if role not in hints:
        return {'role':role,'domain_carrier_hint':None,'fit':'unresolved-semantic-carrier',
            'reason':'A source role label does not select a Lab actor, Policy, output or other domain carrier.',
            'route':'O05 exact adapter; S02/R08 review','domain_conformance':False}
    target=carrier(hints[role],contracts,inventory);schema=parse(original(target['schema_binding']))
    errors=list(Draft202012Validator(schema).iter_errors(record))
    return {'role':role,'domain_carrier_hint':target,'fit':'adapter-required' if errors else 'shape-compatible-only',
        'missing_required_fields':sorted(set(schema.get('required',[]))-set(record)),
        'source_fields_outside_target_schema':sorted(set(record)-set(schema.get('properties',{}))),
        'source_instance_valid_under_target_schema':not errors,'domain_conformance':False,
        'reason':'Original source schema and candidate ontology role are distinct from an exact governed Lab domain instance.',
        'route':'O05 exact adapter or retained source-only representation; S02/R08 review'}


def build():
    from represented_subjects import signed_catalog
    manifest=parse(MANIFEST.read_bytes())
    chosen=[p for p in manifest['packages'] if p['package_key']==PACKAGE_KEY]
    require(len(chosen)==1,'explicit useful legacy package unresolved');package=chosen[0]
    require(package['ontology_id']=='cav2.product-thesis' and len(package['documents'])==8
        and not package['endpoint_aliases'],'selected source package contract changed')
    inventory=parse(original({'path':MAPPING.relative_to(ROOT).as_posix(),'sha256':MAPPING_SHA}))
    roots={'historical-cav2':repository(SOURCE_ROOT),'historical-workspace':repository(WORKSPACE_ROOT),
        'standalone-cav2':repository(STANDALONE_ROOT)}
    files=[];observations=[];positive={}
    def remember(o):
        observations.append(o)
        if o['available']:positive[o['material_path']]={'path':o['material_path'],'sha256':o['observed_sha256']}
    documents={}
    for row in package['documents']:
        o=observation('historical-cav2',SOURCE_ROOT,row['path'],row['sha256']);remember(o)
        require(o['expected_bytes_match'],'selected v4 package source absent/stale: '+row['path'])
        documents[row['path']]=(safe(SOURCE_ROOT,row['path']),row)
        files.append({'item_id':'file:'+row['path'],'item_kind':'file','source_binding':{
            'root_ref':'historical-cav2','path':row['path'],'sha256':row['sha256'],'selector':''},
            'disposition':'reference','reason':'Preserve exact original source as inert external evidence; no body copy or execution.',
            'privacy':'private','intended_carrier_ref':'cal.artifact-type.source/v1','namespace':NAMESPACE,
            'source_preservation':'original external bytes remain untouched','public_body_export_allowed':False,
            'dependency_ids':[],'contract_fit':'metadata-source-wrapper requires O05 construction; source domain schema checked separately'})
    profile=parse(documents[PROFILE_PATH][0].read_bytes())
    require(profile['visibility']=='private' and profile['candidate_status']=='candidate'
        and profile['authority_effect']=='none','selected source privacy/posture changed')
    schema_path='ontology/product/schemas/product-ontology.schema.json'
    schema=parse(documents[schema_path][0].read_bytes());source_checks=[]
    for path in [PROFILE_PATH,'ontology/product/nodes.json','ontology/product/relations.json','ontology/product/sources.json','ontology/product/residue.json']:
        data=parse(documents[path][0].read_bytes());ref=data['schema_ref'].split('#',1)[1]
        require(ref.startswith('/$defs/'),'unselected source schema selector')
        validator=Draft202012Validator({'$ref':'#'+ref,'$defs':schema['$defs']})
        errors=list(validator.iter_errors(data));require(not errors,'original source schema violation: '+path)
        source_checks.append({'path':path,'schema_path':schema_path,'schema_selector':ref,'result':'PASS',
            'claim_ceiling':'Exact source schema only; no Lab domain conformance or source authority.'})
    nodes=parse(documents['ontology/product/nodes.json'][0].read_bytes())['nodes']
    relations=parse(documents['ontology/product/relations.json'][0].read_bytes())['relations']
    sources=parse(documents['ontology/product/sources.json'][0].read_bytes())['sources']
    residue=parse(documents['ontology/product/residue.json'][0].read_bytes())['residue']
    deps=[]
    for source in sources:
        candidates=[observation('historical-workspace',WORKSPACE_ROOT,source['path'],source['sha256'])]
        if source['path'].startswith('cyberAlchemy-v2/'):
            candidates.append(observation('standalone-cav2',STANDALONE_ROOT,source['path'].removeprefix('cyberAlchemy-v2/'),source['sha256']))
        for o in candidates:remember(o)
        match=next((o for o in candidates if o['expected_bytes_match']),None)
        public=source['posture'].startswith('public ')
        deps.append({'item_id':'dependency:'+source['id'],'item_kind':'dependency','legacy_identity':source['id'],
            'original_locator':source['path'],'expected_sha256':source['sha256'],
            'source_binding':{'root_ref':match['root_ref'],'path':match['path'],'sha256':source['sha256'],'selector':''} if match else None,
            'observations':candidates,'disposition':'reference' if match else 'block',
            'reason':'Exact original dependency bytes independently observed at the explicitly selected root.' if match else
                'Expected original dependency unavailable or stale at both nominated locations; current bytes do not substitute for its revision.',
            'privacy':'public-scoped-source' if public else 'private','public_body_export_allowed':False,
            'source_visibility_basis':source['posture'],'namespace':NAMESPACE,
            'intended_carrier_ref':'cal.artifact-type.source/v1','dependency_ids':[],
            'dependency_scope':'one named first-level source only; its own transitive references are excluded until explicitly selected',
            'contract_fit':'exact source evidence; no semantic admission or current implementation claim',
            'source_preservation':'reference original exact bytes; never overwrite, execute or retire source',
            'original_owner_route':source['owner_route'],'resolution_route':'O05 explicit new source epoch or retain blocked reference; S02/R08'})
    dep_ids={d['legacy_identity']:d for d in deps};record_items=[]
    with signed_catalog() as (catalog,operations):
        contracts=catalog.projection['contracts']
        selected_carriers={ref:carrier(ref,contracts,inventory) for ref in (
            'cal.artifact-type.source/v1','cal.artifact-type.ontology-node/v2','cal.artifact-type.ontology-edge/v1')}
        ids={n['id'] for n in nodes};require(len(ids)==len(nodes),'duplicate selected node identity')
        for family,rows,path in [('node',nodes,'ontology/product/nodes.json'),
                                 ('relation',relations,'ontology/product/relations.json'),
                                 ('residue',residue,'ontology/product/residue.json')]:
            binding=documents[path][1]
            for i,row in enumerate(rows):
                selector='/'+('nodes' if family=='node' else 'relations' if family=='relation' else 'residue')+'/'+str(i)
                source_binding={'root_ref':'historical-cav2','path':path,'sha256':binding['sha256'],'selector':selector}
                dependencies=[]
                for ref in row.get('source_refs',[]):
                    require(ref['source_id'] in dep_ids,'unknown declared first-level source')
                    dependencies.append({'item_id':'dependency:'+ref['source_id'],'selector':ref['selector'],
                        'status':'exact-source-bytes-observed' if dep_ids[ref['source_id']]['disposition']=='reference' else 'blocked-source-revision',
                        'selector_status':'inert source locator; literal selector resolution remains O05'})
                item={'item_id':family+':'+row['id'],'item_kind':family,'legacy_identity':row['id'],
                    'source_binding':source_binding,'record_structure_sha256':object_sha(row),
                    'source_qualified_identity':source_id(source_binding,selector,row['id']),
                    'disposition':'adapt' if family in ('node','relation') else 'reference',
                    'intended_carrier_ref':'cal.artifact-type.ontology-edge/v1' if family=='relation' else 'cal.artifact-type.ontology-node/v2' if family=='node' else 'cal.artifact-type.source/v1',
                    'namespace':NAMESPACE,'privacy':'private','public_body_export_allowed':False,
                    'source_preservation':'original selected row remains inert external source; exact selector/digest retained',
                    'dependency_ids':[d['item_id'] for d in dependencies],'dependency_resolution':dependencies,
                    'unresolved_dependency_ids':[d['item_id'] for d in dependencies if d['status']=='blocked-source-revision'],
                    'source_posture':'candidate; authority-effect:none','actual_owner_outcome':None}
                if family=='node':
                    item.update(reason='Source-qualified representation of an observed legacy assertion; domain adaptation requires independent exact contract fit.',
                        source_role=row['role'],contract_fit=semantic_fit(row,row['role'],contracts,inventory),
                        represented_subject_carrier_ref='cal.artifact-type.source/v1')
                elif family=='relation':
                    require(row['source'] in ids and row['target'] in ids,'selected relation endpoint outside package')
                    item.update(reason='Preserve an explicitly local legacy assertion; global Typed Relation mapping requires axis-specific review.',
                        source_endpoint_id=row['source'],target_endpoint_id=row['target'],source_relation_type=row['type'],
                        direction=row['direction'],edge_mode='local-interpretation',global_typed_relation_ref=None,
                        contract_fit={'fit':'local-profile-declaration-required','source_endpoints_closed':True,
                            'source_relation_vocabulary_is_global_axis':False,'domain_conformance':False,
                            'reason':'Legacy predicates including requires and belongs_to cannot select one Lab typed axis by label.',
                            'route':'O05 exact local edge vocabulary/profile and no-collapse check; S02/R08'})
                else:
                    require(all(n in ids for n in row['subject_refs']),'residue subject outside selected scope')
                    item.update(reason='Retain original unresolved source residue as evidence; no new Challenge Event or resolution inferred.',
                        subject_ids=row['subject_refs'],contract_fit='inert source residue; Challenge Contract/Event or failure classification not inferred')
                record_items.append(item)
    alternatives=[]
    for row in package['documents']:
        o=observation('standalone-cav2',STANDALONE_ROOT,row['path'],row['sha256']);remember(o)
        alternatives.append(o)
    excluded=[{'package_key':p['package_key'],'ontology_id':p['ontology_id'],'disposition':'exclude',
        'reason':'Outside explicitly selected useful Product Thesis ontology slice.'} for p in manifest['packages'] if p['package_key']!=PACKAGE_KEY]
    selected=files+record_items+deps
    for repository_row in roots.values():
        for b in repository_row['repository_ref_bindings']:positive[b['path']]=b
    for o in observations:
        p=Path(o['material_path'])
        require(p.is_file()==o['available'] and (not o['available'] or sha(p.read_bytes())==o['observed_sha256']),
            'nominated source observation changed during inventory')
    for b in positive.values():
        require(sha(Path(b['path']).read_bytes())==b['sha256'],'exact source/ref binding changed during inventory')
    return {'schema_version':'lab-O04-selected-source-disposition/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
        'task':'O04','selected_package_keys':[PACKAGE_KEY],'legacy_manifest_binding':bind(MANIFEST),
        'mapping_inventory_binding':{'path':MAPPING.relative_to(ROOT).as_posix(),'sha256':MAPPING_SHA},
        'scope':{'domain':'CyberAlchemy v2 Product Thesis ontology: exact historical package and nominated first-level dependencies',
            'whole_legacy_tree_selected':False,'selected_package_files':8,'transitive_closure_claimed':False,
            'private_body_export_allowed':False,'raw_source_bodies_copied':False,'source_execution_allowed':False,
            'source_mutation_allowed':False,'source_authority_transferred':False},
        'root_bindings':roots,'legacy_declared_roots':manifest['roots'],
        'root_relocation':{'old_cav2_root_available':Path(manifest['roots']['cav2']).exists(),
            'selected_observed_root':'historical-cav2','evidence':'All eight selected original package digests match the v4 manifest; Git repository/ref and source bytes remain independently recorded.',
            'identity_alias_inferred':False},
        'selected_source_visibility':'private','selected_source_status':'candidate','namespace':NAMESPACE,
        'items':selected,'counts':dict(collections.Counter(i['item_kind'] for i in selected)),
        'disposition_counts':dict(collections.Counter(i['disposition'] for i in selected)),
        'source_schema_checks':source_checks,'intended_carrier_bindings':selected_carriers,
        'external_observations':observations,'external_source_bindings':list(positive.values()),
        'excluded_packages':excluded,
        'standalone_product_successor':{'disposition':'defer','reason':'Different independently observed checkout/epoch; matching labels or some matching files do not replace the selected historical package.',
            'observations':alternatives,'route':'Separately qualified future source selection; no root or semantic alias'},
        'unresolved_questions':['Which exact local edge profile/vocabulary will O05 declare for the preserved legacy assertions?',
            'Which domain instances have sufficient exact source fields and evidence for an independent governed adapter?',
            'Which stale/unavailable source epochs will be explicitly replaced or remain blocked?',
            'Final S02/R08 must resolve exact private use/publication and source/target ownership; current package allows no public body export.'],
        'claim_ceiling':'Exact selected private candidate source/dependency inventory and per-item disposition/fit only. Original source schema validity is separate from Lab domain conformance. No source execution, import/admission, public body export, implementation realization, transitive closure or owner outcome.'}


if __name__=='__main__':
    result=build();TARGET.parent.mkdir(parents=True,exist_ok=True)
    require(not TARGET.exists(),'source selection already exists; create an exact successor instead of overwriting')
    with TARGET.open('x') as stream:stream.write(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    print(json.dumps({'counts':result['counts'],'dispositions':result['disposition_counts'],'selection':str(TARGET.relative_to(ROOT))}))
