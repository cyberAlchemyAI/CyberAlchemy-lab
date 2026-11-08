"""Effect-disabled Source/Reader/Mapper family and public API projection closure."""
from __future__ import annotations
import hashlib
import json
import os
import stat
from pathlib import Path, PurePosixPath

REPO=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).resolve().parent
ROOT=Path('/tmp/cal-mapper-only-dev-20261020-0001-release3/root')
INTERFACE=Path('product/lab/release-candidates/v1/interface')
SOURCE='docker-source-20261020-0001'
READER='docker-reader-20261020-0001'
MAPPER='docker-mapped-20261020-0001'
API='api-v25'
SOURCE_SHA='7e0938e70ac00b5308851b5a5a7c7bdb92041efab3be17296998acb4160395c1'
SOURCE_PACKAGE_SHA='f132b3e1908e9e116464ad29c3db7f56ca17d4dee080e60ffa62547dd9588a5b'
READER_SHA='4b61293453ec763f1c3567d3dac114e0d0782a2c58b85bc941ca34a0c974d251'
MAPPER_SHA='0bd6696a1e33750bca01cdeae65d3a5ae977b433c0e0b608009422161b3c1358'
MAPPER_PACKAGE_SHA='0b3635dc9896034203e9e318ad99d58f2c37ca5acd419841d338f6ec9e4a1aea'
NATIVE_SHA='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
FUTURE_STAGE=Path('/tmp/cal-context-family-20261020-0001/root')
MAPPER_FINAL_SHA='4824a7b1af36a30891e3500d66da91619fa02b00b4e5aa4885d8c6f31bea1f00'
MAPPER_REVIEW_SHA='44b249a6daf05239e5f1a481ef873a4f7832cb139acc423cc284ccdd7f3cfa12'
INPUT_FREEZE_SHA='49d32c06a9942b3a359c340639a5884a81475c7bdc4610635a95b46353def315'
INPUT_REVIEW_SHA='c405d3b88fe56eb47f0ea449dfe064a8e30eef65249cf7fcda743559ebda1558'
INPUT_RESOLUTION_SHA='d19d72f7028491659b847649213e6e519bb0e32d86141002a5cd41aeffef1a97'
LIMIT=4*1024*1024

class Refused(ValueError): pass
def require(ok,why):
    if not ok: raise Refused(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def exact(path,pin):
    require(type(pin) is str and len(pin)==64 and all(x in '0123456789abcdef' for x in pin),'pin shape')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        a=os.fstat(fd)
        require(stat.S_ISREG(a.st_mode) and a.st_size<=LIMIT and a.st_size>=0,'bounded regular metadata required')
        parts=[];count=0
        while True:
            chunk=os.read(fd,min(65536,a.st_size+1-count))
            if not chunk:break
            count+=len(chunk)
            require(count<=a.st_size,'metadata grew')
            parts.append(chunk)
        b=os.fstat(fd)
        require((a.st_dev,a.st_ino,a.st_mode,a.st_nlink,a.st_size)==
                (b.st_dev,b.st_ino,b.st_mode,b.st_nlink,b.st_size) and count==a.st_size,
                'metadata changed during read')
        raw=b''.join(parts)
        require(sha(raw)==pin,'metadata digest differs')
        return raw
    finally:os.close(fd)
def safe_rel(name):
    require(type(name) is str and name and not name.startswith('/') and '\\' not in name and
            '//' not in name and PurePosixPath(name).as_posix()==name and
            all(x not in ('.','..') for x in name.split('/')) and
            not name.endswith('branch.snapshot'),'unsafe public path')
    return name
def rel(role,name):return (INTERFACE/role/name).as_posix()

def predecessor():
    local=REPO/'implementation/lab-runtime/local-host'
    exact(local/'context-input-closure-0002/freeze.json',INPUT_FREEZE_SHA)
    exact(local/'CONTEXT-INPUT-CLOSURE-INDEPENDENT-STATIC-REVIEW-0002.md',INPUT_REVIEW_SHA)
    exact(local/'MAPPER-ONLY-DOCKER-RELEASE-INDEPENDENT-EFFECT-REVIEW-0003.md',MAPPER_REVIEW_SHA)
    exact(Path('/tmp/cal-mapper-only-dev-20261020-0001-release3/evidence/final.json'),MAPPER_FINAL_SHA)
    value=json.loads(exact(local/'context-input-closure-0002/row-resolution.json',INPUT_RESOLUTION_SHA))
    require(len(value['historical_rows'])==1804 and len(value['public_preimages'])==836 and
            value['protected_body_read'] is False and value['context_launch']=='REFUSED' and
            value['api_registry_target_count']==144,'reviewed public closure differs')
    require(value['api_bridge']['required_reprojection']==sorted(
            rel(API,n) for n in ('source_bridge.py','protocol.py','contract-profile.json',
                                 'source-manifest.json','source-selection.json')),
            'five API reprojections differ')
    return value

def selected_family():
    require(ROOT.is_absolute() and ROOT.resolve()==ROOT and not ROOT.is_symlink(),
            'selected family root alias')
    source=ROOT/INTERFACE/SOURCE
    reader=ROOT/INTERFACE/READER
    mapper=ROOT/INTERFACE/MAPPER
    for path in (source,reader,mapper):
        require(path.parent==ROOT/INTERFACE and path.is_dir() and not path.is_symlink() and
                path.resolve()==path,'family sibling layout differs')
    s=json.loads(exact(source/'source-manifest.json',SOURCE_SHA))
    sp=json.loads(exact(source/'packages/0001/manifest.json',SOURCE_PACKAGE_SHA))
    r=json.loads(exact(reader/'source-manifest.json',READER_SHA))
    m=json.loads(exact(mapper/'source-manifest.json',MAPPER_SHA))
    mp=json.loads(exact(mapper/'packages/0001/manifest.json',MAPPER_PACKAGE_SHA))
    require(all(v['authority_effect']=='none' and v['actual_owner_outcome'] is None for v in (s,sp,r,m,mp)),
            'selected role grants authority')
    def binding(role,name,pin):return {'path':rel(role,name),'sha256':pin}
    require(r['producer_source_binding']==binding(SOURCE,'source-manifest.json',SOURCE_SHA) and
            r['producer_package_binding']==binding(SOURCE,'packages/0001/manifest.json',SOURCE_PACKAGE_SHA) and
            m['original_source_binding']==binding(SOURCE,'source-manifest.json',SOURCE_SHA) and
            m['original_package_binding']==binding(SOURCE,'packages/0001/manifest.json',SOURCE_PACKAGE_SHA) and
            m['adapter_source_binding']==binding(READER,'source-manifest.json',READER_SHA) and
            mp['source_manifest_binding']==binding(MAPPER,'source-manifest.json',MAPPER_SHA),
            'Source Reader Mapper same-family binding differs')
    require(m['selected_native_executable']==
            {'path':'/attempt/input/lab-context-native-reader','sha256':NATIVE_SHA},
            'Mapper absolute native mount binding differs')
    require(len(mp['files'])==54 and len({x['path'] for x in mp['files']})==54 and
            all(x['path'].startswith(rel(MAPPER,'packages/0001/')) and
                safe_rel(x['path'])==x['path'] for x in mp['files']),
            'Mapper 55-leaf manifest closure differs')
    names={PurePosixPath(x['path']).relative_to(PurePosixPath(rel(MAPPER,'packages/0001'))).as_posix() for x in mp['files']}
    expected={f'{kind}/{i:08d}.json' for kind in ('semantic','governance') for i in range(1,26)}|{
        'request.json','native-output.json','mapping.json','build-result.json'}
    require(names==expected,'Mapper output leaf schedule differs')
    return {'source_manifest_sha256':SOURCE_SHA,'source_package_sha256':SOURCE_PACKAGE_SHA,
            'reader_manifest_sha256':READER_SHA,'mapper_manifest_sha256':MAPPER_SHA,
            'mapper_package_manifest_sha256':MAPPER_PACKAGE_SHA,
            'native_executable_container_path':'/attempt/input/lab-context-native-reader',
            'native_executable_sha256':NATIVE_SHA,
            'mapper_output_files':54,'mapper_package_files_including_manifest':55,
            'root':str(ROOT),'sibling_names':[SOURCE,READER,MAPPER]}

def bridge_bytes():
    # The Context base loads Mapper before API.protocol. Reuse its exact selected
    # Reader.adapter.source object; importing this module never opens an archive.
    return ('''"""Construction-only Context API.Schemas bridge to the loaded same-family Reader."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
NAME='_cal_legacy_context_dev_20261020_0003_legacy_fixture_context_mapper_0257.build'
mapper=sys.modules.get(NAME)
if mapper is None: raise RuntimeError('selected Mapper must load before Context API')
if mapper.HERE != HERE.parent/'docker-mapped-20261020-0001': raise RuntimeError('Mapper sibling differs')
if mapper.reader.HERE != HERE.parent/'docker-source-20261020-0001': raise RuntimeError('Source sibling differs')
if mapper.reader.adapter.HERE != HERE.parent/'docker-reader-20261020-0001': raise RuntimeError('Reader sibling differs')
source=mapper.reader.adapter.source
ROOT=source.ROOT
if ROOT != HERE.parents[5]: raise RuntimeError('family root differs')
sha=source.sha
parse=source.parse
original=source.original
require=source.require
''').encode()

def api_projection(rows):
    old={x['path']:x['sha256'] for x in rows['public_preimages']}
    api_prefix=rel(API,'')
    def current(name):
        path=rel(API,name)
        return exact(REPO/path,old[path])
    bridge=bridge_bytes()
    protocol=current('protocol.py')
    selection=encoded({'schema_version':'lab-context-same-family-api-selection/v1-candidate',
        'authority_effect':'none','actual_owner_outcome':None,
        'source_manifest_binding':{'path':rel(SOURCE,'source-manifest.json'),'sha256':SOURCE_SHA},
        'source_package_binding':{'path':rel(SOURCE,'packages/0001/manifest.json'),'sha256':SOURCE_PACKAGE_SHA},
        'reader_manifest_binding':{'path':rel(READER,'source-manifest.json'),'sha256':READER_SHA},
        'mapper_manifest_binding':{'path':rel(MAPPER,'source-manifest.json'),'sha256':MAPPER_SHA},
        'mapper_package_binding':{'path':rel(MAPPER,'packages/0001/manifest.json'),'sha256':MAPPER_PACKAGE_SHA},
        'claim_ceiling':'Context API.Schemas construction only; no old inspection source or effect.'})
    profile=json.loads(current('contract-profile.json'))
    replacements={'source_bridge.py':sha(bridge),'source-selection.json':sha(selection),
                  'protocol.py':sha(protocol)}
    for item in profile['files']:
        for name,pin in replacements.items():
            if item['path']==rel(API,name):item['sha256']=pin
    require(len(profile['files'])==30 and all(any(x['path']==rel(API,n) and x['sha256']==p
        for x in profile['files']) for n,p in replacements.items()),'profile API bindings incomplete')
    profile['claim_ceiling']='Context API.Schemas same-family projection only; full API suite and effect not run.'
    profile_bytes=encoded(profile)
    projected={'source_bridge.py':bridge,'source-selection.json':selection,
               'protocol.py':protocol,'contract-profile.json':profile_bytes}
    api_public={x['path']:x['sha256'] for x in rows['public_preimages']
                if x['path'].startswith((INTERFACE/API).as_posix()+'/')}
    manifest_files=[]
    for path,pin in sorted(api_public.items()):
        name=path.removeprefix((INTERFACE/API).as_posix()+'/')
        if name=='source-manifest.json':continue
        manifest_files.append({'path':path,'sha256':sha(projected[name]) if name in projected else pin})
    manifest=encoded({'schema_version':'lab-context-api-schemas-source/v1-candidate',
        'authority_effect':'none','actual_owner_outcome':None,
        'environment':{'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5'},
        'source_family':{'source_sha256':SOURCE_SHA,'reader_sha256':READER_SHA,
                         'mapper_source_sha256':MAPPER_SHA,'mapper_package_sha256':MAPPER_PACKAGE_SHA},
        'files':manifest_files,'claim_ceiling':'API.Schemas import projection; no full API or Context effect.'})
    projected['source-manifest.json']=manifest
    require(set(projected)=={'source_bridge.py','source-selection.json','protocol.py',
                             'contract-profile.json','source-manifest.json'},'five API outputs required')
    for name in projected:
        compile(projected[name],name,'exec') if name.endswith('.py') else json.loads(projected[name])
    return projected

def verify_public_and_schema(rows,projections):
    original={x['path']:x['sha256'] for x in rows['public_preimages']}
    changed={rel(API,name):sha(raw) for name,raw in projections.items()}
    unchanged={path:pin for path,pin in original.items() if path not in changed}
    require(len(unchanged)==831 and len(changed)==5,'public projection cardinality differs')
    for path,pin in unchanged.items():
        exact(REPO/safe_rel(path),pin)
    inputs_path=rel(API,'schema-inputs.json')
    inputs=json.loads(exact(REPO/inputs_path,unchanged[inputs_path]))
    require(len(inputs['files'])==790 and inputs['authority_effect']=='none','API schema inputs differ')
    for item in inputs['files']:
        require(item['path'] in unchanged and item['sha256']==unchanged[item['path']],
                'API schema input escapes exact staged public closure')
    profile=json.loads(projections['contract-profile.json'])
    selected=unchanged|changed
    for item in profile['files']:
        require(item['path'] in selected and item['sha256']==selected[item['path']],
                'projected API profile escapes exact public closure')
    for key in ('original_operation_catalog_binding','original_schema_inputs_binding'):
        item=profile[key]
        require(item['path'] in unchanged and item['sha256']==unchanged[item['path']],
                'profile original resource escapes public closure')
    manifest=json.loads(projections['source-manifest.json'])
    require(all(item['path'] in selected and item['sha256']==selected[item['path']]
                for item in manifest['files']), 'projected API source manifest escapes public closure')
    return {'public_preimages_rechecked':len(unchanged),'api_schema_input_bindings':790,
            'profile_file_bindings':30,'registry_targets':rows['api_registry_target_count']}

def mapper_source_schema_join(rows):
    package=ROOT/INTERFACE/MAPPER/'packages/0001'
    manifest=json.loads(exact(package/'manifest.json',MAPPER_PACKAGE_SHA))
    files={x['path']:x['sha256'] for x in manifest['files']}
    def output(name):
        path=rel(MAPPER,'packages/0001/'+name)
        require(path in files,'Mapper output binding missing: '+name)
        return json.loads(exact(package/name,files[path]))
    mapping=output('mapping.json')
    native=output('native-output.json')
    result=output('build-result.json')
    public={x['path']:x['sha256'] for x in rows['public_preimages']}
    provenance=mapping['source_closure']['schema_provenance']
    require(len(provenance)==21 and len({x['carrier_ref'] for x in provenance})==21 and
            all(public.get(x['schema_binding']['ref'])==x['schema_binding']['sha256']
                for x in provenance),'signed Source schema provenance escapes public closure')
    require(mapping['source_package_binding']==
            {'path':rel(SOURCE,'packages/0001/manifest.json'),'sha256':SOURCE_PACKAGE_SHA} and
            mapping['source_cut']==mapping['source_closure']['source_cut'] and
            mapping['authority_effect']=='none' and mapping['actual_owner_outcome'] is None and
            mapping['source_closure']['context_or_ontology_views_generated'] is False and
            len(mapping['rows'])==25 and mapping['governance_cursor']==25 and
            native['authority_effect']=='none' and len(native['governed_nodes'])==15 and
            len(native['context']['selected_node_ids'])==15 and
            len(native['context']['selected_relation_ids'])==10 and
            native['governance_cursor']==25 and
            result['result']=='PASS' and result['task_complete'] is False and
            result['same_signed_source_cut'] is True and
            result['cold_native_replay_byte_parity'] is True and
            result['exact_governance_joins']==25,
            'Mapper Source/native metadata join differs')
    return {'signed_source_schema_provenance_public_joins':21,
            'mapped_rows':25,'native_nodes':15,'native_relations':10,
            'native_governance_cursor':25,
            'archive_body_read':False,
            'current_signed_Source_view':'DEFERRED_TO_CONTEXT_EFFECT',
            'native_cold_replay':'REVIEWED_MAPPER_RESULT_NOT_RERUN'}

def stage_partition(rows,projections):
    replaced={rel(API,name) for name in projections}
    existing=[];from_checkout=[]
    for item in rows['public_preimages']:
        path=safe_rel(item['path'])
        if path in replaced:continue
        source=ROOT/path
        require(not source.is_symlink(),'selected stage public symlink')
        if source.exists():
            require(source.resolve()==source,'selected stage public ancestry alias')
            exact(source,item['sha256'])
            existing.append(item)
        else:
            exact(REPO/path,item['sha256'])
            from_checkout.append(item)
    require(len(existing)+len(from_checkout)==831,'staged public partition incomplete')
    return {'already_in_selected_family':existing,'copy_exact_public_from_checkout':from_checkout,
            'overlay_projected_api':[{'path':rel(API,name),'sha256':sha(raw)}
                                      for name,raw in sorted(projections.items())]}

CONTEXT_PREIMAGES={'__init__.py':'7f3b05a3e452e6794df35715c6f68f98022be7ea6ed3ee5beec00ac95cbd0d69',
    'base.py':'df247c331a17939a7b7e2b9229e2ef6850f4b8fe52973cff388642bbfca5b415',
    'build.py':'f465f1f1f8b9c8269935d9590f4a6006633d8c335416e3b46703a6c190e0711b',
    'control.py':'a8b1ea219f74d085b9d8355e27a0c11444388774e5b76199d7e565efad4d53ba',
    'generation.py':'3a6e41afb837af7a1388491bf6ac98fb9a0289216a3189fdb5404a8e3b0635f4',
    'lifetime-policy.json':'57f1a7b4757b551aefd05ed6efeada6ce416988d14b3aab73a4119f2b3f31e4a'}
def context_import_gaps():
    root=REPO/'implementation/lab-runtime/local-host/context-construction-0003/rendered'
    files={name:exact(root/name,pin) for name,pin in CONTEXT_PREIMAGES.items()}
    base=files['base.py'];build=files['build.py'];generation=files['generation.py'];control=files['control.py']
    required={
        'mapper_sibling':(base,b"HERE.parent / 'mapped'"),
        'mapper_source_pin':(base,b"MAPPED_PIN = '04a22ae3cd37ee70f2e2eb4dcf9a6b2d164fd08382a90c50e2d6a26be8f3f73c'"),
        'mapper_package_pin':(base,b"MAPPED_PACKAGE_PIN = 'ba99b0023708613af17196ff4d5ed3ef9f2e9ddb68de06ab14d374182f5a5b94'"),
        'old_source_pin':(build,b"SOURCE_PIN = 'f3cbec21c32dce3938460a1203e6e3f3575608f463aa3f3fffae9f9338a798f2'"),
        'old_source_package':(build,b"SOURCE_PACKAGE = '8e7b675666308e0e73fb23962b310ea3a89baa48ad6bf2c9cf1c5c9ce9e96964'"),
        'generation_mapper_pin':(generation,b"MAPPED_SOURCE_SHA = '04a22ae3cd37ee70f2e2eb4dcf9a6b2d164fd08382a90c50e2d6a26be8f3f73c'"),
        'old_auth':(control,b"AUTH_SHA = '4d3c34a7f19b4b47892b3fbf5673544b36b0517e516961adcc77722f5d08e906'"),
        'old_snapshot_root':(base,b"ROOT = Path('/tmp/cal-context-construction-20261020-0003/snapshot')"),
    }
    require(all(raw.count(token)==1 for raw,token in required.values()),'old Context import preimage topology differs')
    return {'pinned_role_preimages':CONTEXT_PREIMAGES,
            'exact_obsolete_sites':sorted(required),
            'required_context_role_reprojection':'UNFINISHED',
            'old_auth_custody':'FORBIDDEN_TO_REUSE',
            'actual_import':'REFUSED'}

def construct():
    require(not os.path.lexists(FUTURE_STAGE.parent),
            'future exclusive Context stage name already occupied')
    rows=predecessor()
    family=selected_family()
    projections=api_projection(rows)
    schema=verify_public_and_schema(rows,projections)
    native_schema=mapper_source_schema_join(rows)
    partition=stage_partition(rows,projections)
    context_gaps=context_import_gaps()
    projected_paths={rel(API,name) for name in projections}
    unchanged=[x for x in rows['public_preimages'] if x['path'] not in projected_paths]
    require(len(unchanged)==831 and len(projected_paths)==5 and
            not any(x['path'].endswith('branch.snapshot') for x in unchanged),
            'public staging selection differs')
    # No protected Source archive is copied in this construction. A future
    # exclusive stage must copy the selected family without changing relative
    # layout, then overlay only these public API projected bytes.
    plan={'schema_version':'lab-context-family-static-selection/v1-candidate',
        'status':'EFFECT_DISABLED_STAGED_FAMILY_IMPORT_PLAN',
        'selected_existing_root':str(ROOT),
        'future_exclusive_stage_root':str(FUTURE_STAGE),
        'future_exclusive_stage_created':False,
        'family':family,'unchanged_public_preimages':unchanged,
        'projected_api':[{ 'path':rel(API,name),'sha256':sha(raw),'size':len(raw)}
                         for name,raw in sorted(projections.items())],
        'api_registry_targets':rows['api_registry_target_count'],
        'schema_projection':schema,
        'reviewed_mapper_source_native_join':native_schema,
        'staged_public_partition':partition,
        'context_import_gaps':context_gaps,
        'source_schema_join':'METADATA_AND_PUBLIC_RESOURCE_ONLY',
        'native_schema_join':'MAPPER_PACKAGE_MANIFEST_ONLY_DYNAMIC_SOURCE_VIEW_DEFERRED',
        'source_private_archive':'UNOPENED_AND_UNCOPIED',
        'same_family_reader_binding':'SOURCE_READER_MAPPER_MANIFEST_JOIN',
        'staged_runtime_import':'NOT_RUN',
        'context_source_manifest':'REFUSED','context_launch':'REFUSED',
        'authority_effect':'none','actual_owner_outcome':None}
    return plan,projections

def final_manifest(*_args,**_kwargs):raise Refused('dynamic signed Source schema, runtime import and JIT custody remain')
def launch(*_args,**_kwargs):raise Refused('effect-disabled Context family selection')

if __name__=='__main__':
    plan,projection=construct()
    print(json.dumps({'status':plan['status'],'public_unchanged':len(plan['unchanged_public_preimages']),
                      'api_projected':len(projection),'mapper_package_files':55,
                      'context_launch':plan['context_launch']},sort_keys=True))
