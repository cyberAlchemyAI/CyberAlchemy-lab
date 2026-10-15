"""Closed disposition checks and current exact source observation verification."""
from build_inventory import *

TOP_FIELDS=set('actual_owner_outcome authority_effect claim_ceiling counts disposition_counts excluded_packages external_observations external_source_bindings intended_carrier_bindings items legacy_declared_roots legacy_manifest_binding mapping_inventory_binding namespace root_bindings root_relocation schema_version scope selected_package_keys selected_source_status selected_source_visibility source_schema_checks standalone_product_successor task unresolved_questions'.split())
COMMON=set('contract_fit dependency_ids disposition intended_carrier_ref item_id item_kind namespace privacy public_body_export_allowed reason source_binding source_preservation'.split())
RECORD_FIELDS=set('actual_owner_outcome dependency_resolution legacy_identity record_structure_sha256 source_posture source_qualified_identity unresolved_dependency_ids'.split())
ITEM_FIELDS={'file':COMMON,'node':COMMON|RECORD_FIELDS|{'represented_subject_carrier_ref','source_role'},
    'relation':COMMON|RECORD_FIELDS|set('direction edge_mode global_typed_relation_ref source_endpoint_id source_relation_type target_endpoint_id'.split()),
    'residue':COMMON|RECORD_FIELDS|{'subject_ids'},
    'dependency':COMMON|set('dependency_scope expected_sha256 legacy_identity observations original_locator original_owner_route resolution_route source_visibility_basis'.split())}


def validate_selection(value,check_sources=False):
    require(type(value) is dict and set(value)==TOP_FIELDS,'closed source selection fields required')
    require(value['schema_version']=='lab-O04-selected-source-disposition/v1-candidate'
        and value['authority_effect']=='none' and value['actual_owner_outcome'] is None,'inventory cannot confer authority')
    require(value['selected_package_keys']==[PACKAGE_KEY],'exact useful domain selection required')
    scope=value['scope']
    for field in ('whole_legacy_tree_selected','transitive_closure_claimed','private_body_export_allowed',
                  'raw_source_bodies_copied','source_execution_allowed','source_mutation_allowed','source_authority_transferred'):
        require(scope[field] is False,'source boundary violation: '+field)
    require(scope['selected_package_files']==8 and value['selected_source_visibility']=='private'
        and value['selected_source_status']=='candidate' and value['namespace']==NAMESPACE,'source profile/scope posture differs')
    require(value['legacy_manifest_binding']==bind(MANIFEST),'exact immutable v4 source manifest required')
    original(value['mapping_inventory_binding'])
    require(value['mapping_inventory_binding']=={'path':MAPPING.relative_to(ROOT).as_posix(),'sha256':MAPPING_SHA},'unselected mapping inventory')
    root_paths={'historical-cav2':SOURCE_ROOT,'historical-workspace':WORKSPACE_ROOT,'standalone-cav2':STANDALONE_ROOT}
    require(set(value['root_bindings'])==set(root_paths),'unselected source root')
    for key,path in root_paths.items():
        require(value['root_bindings'][key]['material_root']==str(path),'source root silently replaced')
        require(value['root_bindings'][key]==repository(path),'source repository identity/ref metadata differs')
    require(value['root_relocation']['selected_observed_root']=='historical-cav2'
        and value['root_relocation']['identity_alias_inferred'] is False,'root relocation cannot infer identity alias')
    manifest=parse(MANIFEST.read_bytes());package=next(p for p in manifest['packages'] if p['package_key']==PACKAGE_KEY)
    files={r['path']:r for r in package['documents']}
    original_data={}
    for path,row in files.items():
        material=safe(SOURCE_ROOT,path)
        require(sha(material.read_bytes())==row['sha256'],'selected original package drift')
        if material.suffix=='.json':original_data[path]=parse(material.read_bytes())
    originals={}
    for family,array,path in [('node','nodes','ontology/product/nodes.json'),
                              ('relation','relations','ontology/product/relations.json'),
                              ('residue','residue','ontology/product/residue.json')]:
        for index,row in enumerate(original_data[path][array]):
            originals[family+':'+row['id']]={'row':row,'binding':{'root_ref':'historical-cav2','path':path,
                'sha256':files[path]['sha256'],'selector':'/'+array+'/'+str(index)}}
    dependencies={s['id']:s for s in original_data['ontology/product/sources.json']['sources']}
    expected_observations=[('historical-cav2',r['path'],r['sha256']) for r in package['documents']]
    for source in dependencies.values():
        expected_observations.append(('historical-workspace',source['path'],source['sha256']))
        if source['path'].startswith('cyberAlchemy-v2/'):
            expected_observations.append(('standalone-cav2',source['path'].removeprefix('cyberAlchemy-v2/'),source['sha256']))
    expected_observations.extend(('standalone-cav2',r['path'],r['sha256']) for r in package['documents'])
    require([(o['root_ref'],o['path'],o['expected_sha256']) for o in value['external_observations']]==expected_observations,
        'source observation read set outside exact nominated closure')
    positive={}
    for o in value['external_observations']:
        require(o['material_path']==str(safe(root_paths[o['root_ref']],o['path'])), 'external source observation path differs')
        if o['available']:positive[o['material_path']]={'path':o['material_path'],'sha256':o['observed_sha256']}
    for r in value['root_bindings'].values():
        for b in r['repository_ref_bindings']:positive[b['path']]=b
    require(value['external_source_bindings']==list(positive.values()), 'external binding closure differs from observed source/ref bytes')
    wanted={*('file:'+p for p in files),*originals,*('dependency:'+s for s in dependencies)}
    items=value['items'];by_id={r['item_id']:r for r in items}
    require(len(by_id)==len(items) and set(by_id)==wanted,'selected item inventory must be an exact closed partition')
    require(value['counts']==dict(collections.Counter(r['item_kind'] for r in items))
        and value['disposition_counts']==dict(collections.Counter(r['disposition'] for r in items)), 'inventory accounting differs')
    node_ids={n['id'] for n in original_data['ontology/product/nodes.json']['nodes']}
    qualified=set()
    for item in items:
        require(item['item_kind'] in ITEM_FIELDS and set(item)==ITEM_FIELDS[item['item_kind']], 'closed per-item metadata fields required')
        require(item['disposition'] in ('import','adapt','reference','defer','exclude','block')
            and item['reason'] and item['source_preservation'] and item['contract_fit'], 'per-item disposition/fit/reason required')
        require(item['namespace']==NAMESPACE and item['public_body_export_allowed'] is False,'private boundary/namespace not preserved')
        require(not any(k in item for k in ('record','source_record','content','approval','signature','normative_statement')),
            'inventory materializes a raw source body or approval')
        if item['item_kind']=='file':
            path=item['source_binding']['path'];require(path in files,'unselected source file')
            require(item['source_binding']=={'root_ref':'historical-cav2','path':path,'sha256':files[path]['sha256'],'selector':''}
                and item['disposition']=='reference' and item['privacy']=='private','source file digest/root/disposition differs')
        elif item['item_kind']=='dependency':
            source=dependencies[item['legacy_identity']]
            require(item['original_locator']==source['path'] and item['expected_sha256']==source['sha256'],'source dependency revision differs')
            observations=item['observations']
            require(observations,'source access cannot be assumed')
            expected=[]
            expected.append(('historical-workspace',source['path']))
            if source['path'].startswith('cyberAlchemy-v2/'):
                expected.append(('standalone-cav2',source['path'].removeprefix('cyberAlchemy-v2/')))
            require([(o['root_ref'],o['path']) for o in observations]==expected,'dependency lookup outside nominated exact locations')
            for o in observations:
                require(o['material_path']==str(safe(root_paths[o['root_ref']],o['path']))
                    and o['expected_sha256']==source['sha256']
                    and o['expected_bytes_match']==bool(o['available'] and o['observed_sha256']==source['sha256']),
                    'source dependency observation mismatched')
            match=next((o for o in observations if o['expected_bytes_match']),None)
            require(item['disposition']==('reference' if match else 'block'),'unavailable/stale source must remain blocked')
            if match:
                require(item['source_binding']=={'root_ref':match['root_ref'],'path':match['path'],'sha256':source['sha256'],'selector':''},
                    'dependency provenance root/revision silently replaced')
            else:require(item['source_binding'] is None,'unavailable source acquires a fabricated binding')
            require(item['privacy']==('public-scoped-source' if source['posture'].startswith('public ') else 'private'),
                'source public/private classification differs from exact source posture')
        else:
            selected=originals[item['item_id']];row=selected['row'];binding=selected['binding']
            require(item['source_binding']==binding and item['legacy_identity']==row['id']
                and item['record_structure_sha256']==object_sha(row),'source selector/identity/record digest differs')
            require(item['source_qualified_identity']==source_id(binding,binding['selector'],row['id'])
                and item['source_qualified_identity'] not in qualified,'source-qualified identity duplicate or altered')
            qualified.add(item['source_qualified_identity'])
            require(item['privacy']=='private' and item['source_posture']=='candidate; authority-effect:none'
                and item['actual_owner_outcome'] is None,'source body becomes Lab authority/public material')
            wanted_refs=[{'item_id':'dependency:'+r['source_id'],'selector':r['selector'],
                'status':'exact-source-bytes-observed' if by_id['dependency:'+r['source_id']]['disposition']=='reference' else 'blocked-source-revision',
                'selector_status':'inert source locator; literal selector resolution remains O05'} for r in row.get('source_refs',[])]
            require(item['dependency_resolution']==wanted_refs and item['dependency_ids']==[r['item_id'] for r in wanted_refs]
                and item['unresolved_dependency_ids']==[r['item_id'] for r in wanted_refs if r['status']=='blocked-source-revision'],
                'declared dependencies or unresolved gaps dropped')
            if item['item_kind']=='node':
                require(item['source_role']==row['role'] and item['intended_carrier_ref']=='cal.artifact-type.ontology-node/v2'
                    and item['represented_subject_carrier_ref']=='cal.artifact-type.source/v1'
                    and item['contract_fit']['domain_conformance'] is False, 'source role/shape cannot infer a domain instance')
                hint=item['contract_fit']['domain_carrier_hint']
                if hint:
                    original(hint['schema_binding']);schema=parse(original(hint['schema_binding']))
                    require(hint['meaning_inferred'] is False
                        and item['contract_fit']['source_instance_valid_under_target_schema']==(not list(Draft202012Validator(schema).iter_errors(row)))
                        and item['contract_fit']['missing_required_fields']==sorted(set(schema.get('required',[]))-set(row)),
                        'target carrier/schema fit invented')
            elif item['item_kind']=='relation':
                require(item['source_endpoint_id']==row['source'] and item['target_endpoint_id']==row['target']
                    and item['source_endpoint_id'] in node_ids and item['target_endpoint_id'] in node_ids
                    and item['source_relation_type']==row['type'] and item['direction']==row['direction'],
                    'source relation endpoint/direction/type tuple differs')
                require(item['intended_carrier_ref']=='cal.artifact-type.ontology-edge/v1'
                    and item['edge_mode']=='local-interpretation' and item['global_typed_relation_ref'] is None
                    and item['contract_fit']['source_relation_vocabulary_is_global_axis'] is False
                    and item['contract_fit']['domain_conformance'] is False,'legacy predicate cannot acquire a global typed axis')
            else:
                require(item['subject_ids']==row['subject_refs'] and item['intended_carrier_ref']=='cal.artifact-type.source/v1'
                    and item['disposition']=='reference','source residue cannot fabricate a Challenge Event/resolution')
    require({p['package_key'] for p in value['excluded_packages']}=={p['package_key'] for p in manifest['packages'] if p['package_key']!=PACKAGE_KEY}
        and all(p['disposition']=='exclude' and p['reason'] for p in value['excluded_packages']), 'unselected package exclusions not accounted')
    require(value['standalone_product_successor']['disposition']=='defer','changed standalone epoch cannot silently replace source package')
    for row in value['intended_carrier_bindings'].values():original(row['schema_binding'])
    if check_sources:verify_observations(value)
    return {'result':'PASS','authority_effect':'none','items_checked':len(items),'private_raw_bodies_exported':0,
        'domain_instances_conformed':0,'blocked_dependencies':sum(i['disposition']=='block' for i in items)}


def verify_observations(value):
    for o in value['external_observations']:
        p=Path(o['material_path'])
        require(p.is_file()==o['available'] and not p.is_symlink()
            and (not o['available'] or sha(p.read_bytes())==o['observed_sha256']), 'original source observation changed: '+o['material_path'])
    for b in value['external_source_bindings']:
        require(Path(b['path']).is_file() and sha(Path(b['path']).read_bytes())==b['sha256'],'source/ref bytes changed')
    for row in value['root_bindings'].values():
        require(git(Path(row['material_root']),'rev-parse','HEAD')==row['head'],'selected repository ref moved')


if __name__=='__main__':
    value=parse(TARGET.read_bytes());print(json.dumps(validate_selection(value,True),sort_keys=True))
