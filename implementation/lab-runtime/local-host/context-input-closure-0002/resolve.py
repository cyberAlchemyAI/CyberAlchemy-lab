"""Closed public Context input disposition; no role effect or private archive read."""
from __future__ import annotations
import ast
import hashlib
import importlib.metadata
import json
import os
import platform
import stat
from pathlib import Path, PurePosixPath

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
HISTORY = REPO / 'implementation/lab-runtime/local-host/context-construction-0003/historical-closure-candidates.json'
HISTORY_SHA = 'e02c3061ee705d826f02d74887340ce85047ef989491dfddfdf1e3590aec350a'
PUBLIC = REPO / 'implementation/lab-runtime/local-host/context-closure-0001/public-selection.json'
PUBLIC_SHA = 'bf7597ed77ad71bbf45c9b6d5100805a60200139c9159e4321d8d5ebbb21c3e7'
PUBLIC_FREEZE = REPO / 'implementation/lab-runtime/local-host/context-closure-0001/freeze.json'
PUBLIC_FREEZE_SHA = 'd03f9967d80478b669b8600e20f7638705d119327cc1d55309c033e529f4cc8b'
PUBLIC_REVIEW = REPO / 'implementation/lab-runtime/local-host/CONTEXT-CLOSURE-INDEPENDENT-STATIC-REVIEW-0001.md'
PUBLIC_REVIEW_SHA = '5f7177bf13d2bffb4897b8b153c6c72f96fae7a36f0eee3e9ce03e2ff0529d6a'
POLICY_REVIEW = REPO / 'implementation/lab-runtime/local-host/CONTEXT-POLICY-INDEPENDENT-STATIC-REVIEW-0002.md'
POLICY_REVIEW_SHA = '6959f5f5dd82addca8827d2a322e92554639a24fba0ca5ee99d886c6377b5416'
INTEGRATION = REPO / 'implementation/lab-runtime/local-host/context-integration-0002/selection.json'
INTEGRATION_SHA = '16b46adf47f2f5c1482de4bd23597b32f49185d9c02d9e8d6a5dbdcaba78ae65'
API_ROOT = 'product/lab/release-candidates/v1/interface/api-v25/'
API_INPUTS = API_ROOT + 'schema-inputs.json'
API_INPUTS_SHA = '46ba45049ce2efc4772e6eb4c79c3f13f302eb37f2d6da48badd0d462aaac26c'
API_PROFILE = API_ROOT + 'contract-profile.json'
API_PROFILE_SHA = 'c9b9d88e37ff0e9514727bd71ac0091e0dd4dc59c707fb6b07e713503922d33d'
API_PROTOCOL = API_ROOT + 'protocol.py'
API_BRIDGE = API_ROOT + 'source_bridge.py'
DOC_SCHEMA_ROOT = 'docs/proposals/0007-lab-integrated-schema-package/'
DOC_API_ROOT = 'docs/proposals/0008-lab-api-contracts/'
RUNTIME_EXPECTED = {'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5'}
IMAGE_ID = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
SOURCE_REL = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0001'
READER_REL = 'product/lab/release-candidates/v1/interface/docker-reader-20261020-0001'
IMAGE_RECEIPT = HERE / 'image-environment-probe.json'
IMAGE_RECEIPT_SHA = '0dfa9663068c59b573381f933ce8115afd46697e4399866b447b0fda693e7a7b'
PROBE_WRAPPER_SHA = '2e45f1df96eaff6811e616781e822263c074f6552d90ef043438c5405707c201'
PROBE_CODE = ('import json,os,platform,importlib.metadata as m;'
              'print(json.dumps({"python":platform.python_version(),'
              '"versions":{k:m.version(k) for k in '
              '("jsonschema","cryptography","referencing")},'
              '"uid":os.getuid(),"euid":os.geteuid(),'
              '"gid":os.getgid(),"egid":os.getegid()},sort_keys=True))')
V1_FREEZE = REPO / 'implementation/lab-runtime/local-host/context-input-closure-0001/freeze.json'
V1_FREEZE_SHA = 'f84ca96d127b3be9c5e0b97aae4e6c4dd74e52b77d12996fd4be7a9e9bb2f0b4'
V1_REVIEW = REPO / 'implementation/lab-runtime/local-host/CONTEXT-INPUT-CLOSURE-INDEPENDENT-STATIC-REVIEW-0001.md'
V1_REVIEW_SHA = '5817c8830a38cff9177983a3ab9d5c83a585ea3ce3f9389b6e5ebfca5f69d72e'
V1_RESOLUTION = REPO / 'implementation/lab-runtime/local-host/context-input-closure-0001/row-resolution.json'
V1_RESOLUTION_SHA = '3f2807e4105582bd6fcaae53b6ed1a8a381657e9e7ad2addc2efcc3488995ebc'
RESOLUTION_SHA = 'd19d72f7028491659b847649213e6e519bb0e32d86141002a5cd41aeffef1a97'
LIMIT = 4 * 1024 * 1024
REPROJECT_API = frozenset({API_ROOT + name for name in ('source_bridge.py','protocol.py','contract-profile.json','source-manifest.json','source-selection.json')})
EXCLUDE_LEGACY_IMPORT = frozenset({
    'product/lab/release-candidates/v1/interface/inspection/lab_operator.py',
    'product/lab/release-candidates/v1/interface/coupling/loader.py',
    'product/lab/release-candidates/v1/interface/corrections-v1/loader.py',
})

class Refused(ValueError):
    pass

def require(ok, reason):
    if not ok:
        raise Refused(reason)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def read_exact(path, pin):
    require(type(pin) is str and len(pin) == 64 and all(c in '0123456789abcdef' for c in pin),
            'exact SHA-256 required')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and 0 <= before.st_size <= LIMIT,
                'public input must be bounded regular file')
        parts, count = [], 0
        while True:
            piece = os.read(fd, min(65536, before.st_size + 1 - count))
            if not piece:
                break
            count += len(piece)
            require(count <= before.st_size, 'public input grew')
            parts.append(piece)
        after = os.fstat(fd)
        require((before.st_dev,before.st_ino,before.st_mode,before.st_nlink,before.st_size) ==
                (after.st_dev,after.st_ino,after.st_mode,after.st_nlink,after.st_size) and
                count == before.st_size, 'public input changed during read')
        raw = b''.join(parts)
        require(sha(raw) == pin, 'public input digest differs')
        return raw
    finally:
        os.close(fd)

def canonical(relative):
    require(type(relative) is str and relative and not relative.startswith('/') and
            '\\' not in relative and '//' not in relative and
            str(PurePosixPath(relative)) == relative and
            not any(part in ('.','..') for part in relative.split('/')) and
            not relative.endswith('branch.snapshot') and
            'authorization.json' not in relative,
            'unsafe or protected dependency path')
    return relative

def validate_image_receipt(receipt):
    """Reject reconstructed argv, mismatched OS results, and missing container absence."""
    require(type(receipt) is dict and set(receipt)=={
        'schema_version','observed_at_utc','wrapper_sha256','image_id',
        'image_config','container_name','image_inspect',
        'before_container_inspect','run','after_container_inspect'},
        'image receipt schema differs')
    require(receipt['schema_version']=='lab-context-image-environment-probe/v2' and
            receipt['image_id']==IMAGE_ID and receipt['wrapper_sha256']==PROBE_WRAPPER_SHA,
            'image receipt provenance differs')
    name=receipt['container_name']
    require(type(name) is str and name.startswith('cal-context-env-closure2-') and
            len(name)==41 and all(c in '0123456789abcdef' for c in name[-16:]),
            'probe container name differs')
    def checked(command, argv, exit_code, stdout=None, stderr=None):
        value=receipt[command]
        require(type(value) is dict and set(value)=={
            'argv','os_exit_code','stdout','stderr','stdout_sha256','stderr_sha256'} and
            value['argv']==argv and type(value['os_exit_code']) is int and
            value['os_exit_code']==exit_code and type(value['stdout']) is str and
            type(value['stderr']) is str and
            sha(value['stdout'].encode())==value['stdout_sha256'] and
            sha(value['stderr'].encode())==value['stderr_sha256'] and
            len(value['stdout'].encode())<=65536 and
            len(value['stderr'].encode())<=65536,
            'external Docker command/result mismatch: '+command)
        if stdout is not None:
            require(value['stdout']==stdout,'Docker stdout differs: '+command)
        if stderr is not None:
            require(value['stderr']==stderr,'Docker stderr differs: '+command)
        return value
    image=checked('image_inspect',['docker','image','inspect',IMAGE_ID],0,stderr='')
    parsed=json.loads(image['stdout'])
    require(type(parsed) is list and len(parsed)==1 and parsed[0]['Id']==IMAGE_ID and
            parsed[0]['Config'].get('Entrypoint') in (None,[]) and
            parsed[0]['Config'].get('Cmd')==['python3'] and
            receipt['image_config']=={
                'entrypoint':parsed[0]['Config'].get('Entrypoint'),
                'cmd':parsed[0]['Config'].get('Cmd'),
                'user':parsed[0]['Config'].get('User')},
            'inspected image identity/config differs')
    for label in ('before_container_inspect','after_container_inspect'):
        checked(label,['docker','container','inspect',name],1,stdout='[]\n',
                stderr='Error response from daemon: No such container: '+name+'\n')
    run_argv=['docker','run','--rm','--name',name,'--network','none',
              '--read-only','--cap-drop','ALL','--security-opt',
              'no-new-privileges','--pids-limit','16','--user','1000:1000',
              '--workdir','/',IMAGE_ID,'python3','-B','-c',PROBE_CODE]
    run=checked('run',run_argv,0,stderr='')
    probe=json.loads(run['stdout'])
    require(probe=={'python':'3.14.4',
                    'versions':{'jsonschema':'4.23.0','cryptography':'46.0.5',
                                'referencing':'0.37.0'},
                    'uid':1000,'euid':1000,'gid':1000,'egid':1000},
            'selected image dependency observation differs')
    return probe

def plan():
    """Read only pinned public selectors; excluded target bodies stay unopened."""
    history = json.loads(read_exact(HISTORY, HISTORY_SHA))
    public = json.loads(read_exact(PUBLIC, PUBLIC_SHA))
    read_exact(PUBLIC_FREEZE, PUBLIC_FREEZE_SHA)
    read_exact(PUBLIC_REVIEW, PUBLIC_REVIEW_SHA)
    read_exact(POLICY_REVIEW, POLICY_REVIEW_SHA)
    integration = json.loads(read_exact(INTEGRATION, INTEGRATION_SHA))
    receipt = json.loads(read_exact(IMAGE_RECEIPT, IMAGE_RECEIPT_SHA))
    read_exact(HERE/'probe_image.py',PROBE_WRAPPER_SHA)
    read_exact(V1_FREEZE,V1_FREEZE_SHA)
    read_exact(V1_REVIEW,V1_REVIEW_SHA)
    require(set(history) == {'historical_manifest_sha256','rows'} and
            len(history['rows']) == 1804 and
            len({r['path'] for r in history['rows']}) == 1804,
            'historical closure inventory differs')
    hist = {r['path']:r for r in history['rows']}
    require({r['state'] for r in history['rows']} ==
            {'unselected_candidate','historical_family_requires_projection','protected_archive_excluded'} and
            sum(r['state']=='protected_archive_excluded' for r in history['rows']) == 6,
            'historical row states differ')
    require(public['counts'] == {'api_v25':34,'fact_scope':4,'carrier_artifact':7,
                                 'carrier_schema':7,'carrier_fixture':7} and
            public['protected_body_read'] is False,
            'reviewed 59-row selection differs')
    require(integration['reader']['entrypoint']=='SelectedReader.open_signed' and
            integration['mapper_package'] is None and
            integration['protected_archive_body_read'] is False,
            'selected Source/Reader metadata differs')
    probe = validate_image_receipt(receipt)
    inputs = json.loads(read_exact(REPO/API_INPUTS, API_INPUTS_SHA))
    profile = json.loads(read_exact(REPO/API_PROFILE, API_PROFILE_SHA))
    require(set(inputs)=={'schema_version','authority_effect','files'} and
            inputs['authority_effect']=='none' and len(inputs['files'])==790 and
            len(profile['files'])==30 and profile['authority_effect']=='none' and
            profile['actual_owner_outcome'] is None,
            'API resource selector differs')
    sources = {}
    def select(path, pin, role):
        path = canonical(path)
        require(type(pin) is str and len(pin)==64 and all(c in '0123456789abcdef' for c in pin),
                'public selector digest invalid')
        if path in sources:
            require(sources[path]['sha256']==pin, 'conflicting public input binding')
            sources[path]['roles'].add(role)
        else:
            sources[path]={'sha256':pin,'roles':{role}}
    for row in public['public_rows']:
        select(row['path'],row['sha256'],'reviewed_59_'+row['role'])
    for row in inputs['files']:
        require(set(row)=={'path','sha256'}, 'API schema-input binding shape differs')
        select(row['path'],row['sha256'],'api_schema_inputs_guard')
    for row in profile['files']:
        require(set(row)=={'path','sha256'}, 'API profile binding shape differs')
        select(row['path'],row['sha256'],'api_profile_guard')
    for key in ('original_operation_catalog_binding','original_schema_inputs_binding'):
        row=profile[key]
        require(set(row)=={'path','sha256'}, 'API profile extra binding shape differs')
        select(row['path'],row['sha256'],'api_profile_'+key)
    for name in ('resources.py','schema-dependencies.json','domain-bindings.json','schema-catalog.json'):
        path=DOC_SCHEMA_ROOT+name
        require(path in hist, 'schema resource absent from historical inventory')
        select(path,hist[path]['historical_sha256'],'api_schema_registry_runtime')
    globs={
        'original_api_schemas':sorted(p.relative_to(REPO).as_posix() for p in
                                      (REPO/DOC_API_ROOT/'schemas').glob('*.schema.json')),
        'local_api_schemas':sorted(p.relative_to(REPO).as_posix() for p in
                                   (REPO/API_ROOT/'schemas').glob('*.schema.json')),
        'registry_schemas':sorted(p.relative_to(REPO).as_posix() for p in
                                  (REPO/DOC_SCHEMA_ROOT/'schemas').glob('*.schema.json')),
    }
    require({k:len(v) for k,v in globs.items()} ==
            {'original_api_schemas':5,'local_api_schemas':4,'registry_schemas':80},
            'API schema directory cardinality differs')
    for role,paths in globs.items():
        for path in paths:
            require(path in hist, 'globbed schema lacks historical binding')
            select(path,hist[path]['historical_sha256'],role)
    deps=json.loads(read_exact(REPO/(DOC_SCHEMA_ROOT+'schema-dependencies.json'),
                               hist[DOC_SCHEMA_ROOT+'schema-dependencies.json']['historical_sha256']))
    domains=json.loads(read_exact(REPO/(DOC_SCHEMA_ROOT+'domain-bindings.json'),
                                  hist[DOC_SCHEMA_ROOT+'domain-bindings.json']['historical_sha256']))
    catalog=json.loads(read_exact(REPO/(DOC_SCHEMA_ROOT+'schema-catalog.json'),
                                  hist[DOC_SCHEMA_ROOT+'schema-catalog.json']['historical_sha256']))
    registry_targets={b['target_path'] for b in deps['bindings']} | \
                     {b['schema_path'] for b in domains['bindings']} | \
                     {b['path'] for b in catalog['reused_storage_schemas']} | \
                     {catalog['ephemeral_memory_binding']['path']}
    require(len(registry_targets)==144 and registry_targets <= sources.keys(),
            'API registry target escapes selected public resource closure')
    for path in registry_targets:
        sources[path]['roles'].add('api_registry_target')
    # The original bridge must be replaced, not imported. These checks pin the
    # exact historical import topology without running either legacy module.
    protocol_raw=read_exact(REPO/API_PROTOCOL,sources[API_PROTOCOL]['sha256'])
    bridge_raw=read_exact(REPO/API_BRIDGE,sources[API_BRIDGE]['sha256'])
    protocol_tree=ast.parse(protocol_raw)
    require(sum(isinstance(n,ast.ImportFrom) and n.level==1 and
                any(a.name=='source_bridge' and a.asname=='source' for a in n.names)
                for n in protocol_tree.body)==1 and
            bridge_raw.count(b"HERE.parent/'inspection/lab_operator.py'")==1 and
            bridge_raw.count(b"HERE.parent/'corrections-v1/loader.py'")==1,
            'historical API bridge import preimage differs')
    profile_bindings={r['path']:r['sha256'] for r in profile['files']}
    require(profile_bindings[API_PROTOCOL]==sources[API_PROTOCOL]['sha256'] and
            profile_bindings[API_BRIDGE]==sources[API_BRIDGE]['sha256'],
            'API profile does not bind original bridge/protocol')
    for path,item in sources.items():
        if path in hist:
            require(hist[path]['state']=='unselected_candidate' and
                    hist[path]['historical_sha256']==item['sha256'],
                    'selected public input differs from historical pin')
        else:
            require('reviewed_59_carrier_fixture' in item['roles'],
                    'new public input lacks reviewed fixture basis')
    require(len([p for p in sources if p not in hist])==7,
            'new public fixture inventory differs')
    disposition=[]
    for row in history['rows']:
        path=row['path']; state=row['state']
        if state=='protected_archive_excluded': kind='EXCLUDE_PROTECTED_ARCHIVE'
        elif state=='historical_family_requires_projection': kind='EXCLUDE_OLD_FAMILY_REPROJECT_FRESH'
        elif path in REPROJECT_API: kind='REPROJECT_API_SAME_FAMILY'
        elif path in EXCLUDE_LEGACY_IMPORT: kind='EXCLUDE_LEGACY_API_IMPORT'
        elif path in sources: kind='ALLOW_PUBLIC_PREIMAGE'
        else: kind='EXCLUDE_DIRECT_CONTEXT_INPUT'
        disposition.append({'path':path,'historical_sha256':row['historical_sha256'],
                            'historical_state':state,'disposition':kind})
    counts={kind:sum(r['disposition']==kind for r in disposition)
            for kind in sorted({r['disposition'] for r in disposition})}
    definitions={
        'ALLOW_PUBLIC_PREIMAGE':'Exact current public byte in reviewed Context static carrier or API.Schemas resource chain; staging and final runtime admission remain separate.',
        'REPROJECT_API_SAME_FAMILY':'Historical API bridge/profile/protocol or selection preimage must be replaced and repinned to one fresh Source/Reader family before import.',
        'EXCLUDE_LEGACY_API_IMPORT':'Historical inspection/coupling/correction import reached through the old API bridge; never import in the selected Context family.',
        'EXCLUDE_OLD_FAMILY_REPROJECT_FRESH':'Historical Source/Reader/Mapper/Context-family evidence cannot be reused; select fresh same-family output where required.',
        'EXCLUDE_PROTECTED_ARCHIVE':'Historical protected archive body is forbidden to this public closure.',
        'EXCLUDE_DIRECT_CONTEXT_INPUT':'Not in the static Context and API.Schemas public chain. A Source-view dynamic contract or Mapper may independently select it later; this unit does not admit it.',
    }
    require(set(counts)==set(definitions), 'row disposition vocabulary differs')
    plan={
        'schema_version':'lab-context-public-input-closure/v1',
        'status':'ROW_LEVEL_PUBLIC_PREIMAGE_CLOSURE_EFFECT_DISABLED',
        'historical_inventory_sha256':HISTORY_SHA,
        'reviewed_public_selection_sha256':PUBLIC_SHA,
        'image_probe_sha256':IMAGE_RECEIPT_SHA,
        'historical_rows':disposition,
        'counts':counts,
        'disposition_definitions':definitions,
        'public_preimages':[{'path':p,'sha256':item['sha256'],'roles':sorted(item['roles'])}
                            for p,item in sorted(sources.items())],
        'selected_globs':globs,
        'api_registry_target_count':len(registry_targets),
        'api_bridge':{
            'status':'REPROJECT_REQUIRED_BEFORE_IMPORT',
            'old_protocol_sha256':sources[API_PROTOCOL]['sha256'],
            'old_source_bridge_sha256':sources[API_BRIDGE]['sha256'],
            'old_profile_sha256':API_PROFILE_SHA,
            'required_reprojection':sorted(REPROJECT_API),
            'must_bind':'same-family reviewed Reader.adapter.source and selected Source ROOT',
            'must_update':'protocol import, bridge implementation, profile bindings, source manifest, Context API_PROFILE_PIN',
            'old_inspection_and_correction_imports':'EXCLUDED',
        },
        'source_reader':{
            'source_source_sha256':integration['source']['source_manifest_sha256'],
            'source_package_sha256':integration['source']['package_manifest_sha256'],
            'source_period_sha256':integration['source']['period_sha256'],
            'reader_source_sha256':integration['reader']['source_manifest_sha256'],
            'reader_code_sha256':integration['reader']['reader_code_sha256'],
            'reader_entrypoint':integration['reader']['entrypoint'],
            'same_family_binding':'MECHANISM_ONLY_REQUIRES_SELECTED_STAGE',
        },
        'runtime':{
            'expected':RUNTIME_EXPECTED,
            'selected_image_id':IMAGE_ID,
            'selected_image_probe':probe,
            'host_observed':{'python':platform.python_version(),
                             'jsonschema':importlib.metadata.version('jsonschema'),
                             'cryptography':importlib.metadata.version('cryptography'),
                             'referencing':importlib.metadata.version('referencing')},
            'container_environment':'VERSION_TRIPLET_MATCHES_EXPECTED',
            'host_environment':'MISMATCH_JSONSCHEMA',
        },
        'mapper_source':'SYMBOLIC_FRESH_REVIEWED_PACKAGE_REQUIRED',
        'mapper_package':'SYMBOLIC_FRESH_REVIEWED_PACKAGE_REQUIRED',
        'development_authorization':'UNMINTED',
        'policy_and_key':'UNCREATED',
        'context_source_manifest':'REFUSED',
        'context_launch':'REFUSED',
        'protected_body_read':False,
        'effect':'NOT_RUN',
    }
    return plan

def verify_plan(plan_value, expected):
    require(plan_value == expected, 'frozen row-level closure differs')
    require(len(plan_value['historical_rows']) == 1804 and
            sum(plan_value['counts'].values()) == 1804,
            'historical row disposition incomplete')
    return True

def verify_public_preimages(expected):
    for row in expected['public_preimages']:
        read_exact(REPO/row['path'],row['sha256'])
    return len(expected['public_preimages'])

def verify_frozen():
    candidate=json.loads(read_exact(HERE/'row-resolution.json',RESOLUTION_SHA))
    expected=plan()
    verify_plan(candidate,expected)  # Before opening selected public target bodies.
    predecessor=json.loads(read_exact(V1_RESOLUTION,V1_RESOLUTION_SHA))
    static_fields=('historical_rows','counts','public_preimages','selected_globs',
                   'api_registry_target_count','api_bridge','source_reader')
    require(all(candidate[key]==predecessor[key] for key in static_fields),
            'reviewed 0001 static closure changed')
    count=verify_public_preimages(expected)
    return {'status':'PUBLIC_PREIMAGES_EXACT_PASS_REPROJECTION_HELD',
            'historical_rows':1804,'public_preimages':count,
            'api_bridge':'REPROJECT_REQUIRED','mapper':'SYMBOLIC',
            'context_launch':'REFUSED','protected_body_read':False}

def project_reader_binding(family):
    """Pure binding bytes for a disposable same-family metadata stage only."""
    root = PurePosixPath(str(family))
    require(root.is_absolute() and str(root)==str(family) and
            '..' not in root.parts and PurePosixPath('/tmp') in root.parents,
            'exact external family root required')
    selected=json.loads(read_exact(INTEGRATION,INTEGRATION_SHA))
    source_root=Path(family)/'snapshot'/SOURCE_REL
    reader_root=Path(family)/'reader'
    source_manifest=source_root/'source-manifest.json'
    package_manifest=source_root/'packages/0001/manifest.json'
    reader_manifest=reader_root/'source-manifest.json'
    reader_code=reader_root/'reader.py'
    source=json.loads(read_exact(source_manifest,selected['source']['source_manifest_sha256']))
    package=json.loads(read_exact(package_manifest,selected['source']['package_manifest_sha256']))
    reader=json.loads(read_exact(reader_manifest,selected['reader']['source_manifest_sha256']))
    code=read_exact(reader_code,selected['reader']['reader_code_sha256'])
    require(source['authority_effect']=='none' and source['actual_owner_outcome'] is None and
            reader['authority_effect']=='none' and reader['actual_owner_outcome'] is None and
            reader['environment']==RUNTIME_EXPECTED and
            reader['producer_source_binding']=={'path':SOURCE_REL+'/source-manifest.json',
                'sha256':selected['source']['source_manifest_sha256']} and
            reader['producer_package_binding']=={'path':SOURCE_REL+'/packages/0001/manifest.json',
                'sha256':selected['source']['package_manifest_sha256']} and
            b'class SelectedReader:' in code and b'def open_signed(' in code and
            type(package) is dict,
            'same-family Source/Reader public binding differs')
    value={
        'schema_version':'lab-original-reader-implementation-evidence/v1-candidate',
        'code_binding':{'ref':str(reader_code),'sha256':selected['reader']['reader_code_sha256']},
        'entrypoint_ref':str(reader_code)+'#SelectedReader.open_signed',
        'environment':RUNTIME_EXPECTED,
        'environment_contract_ref':'protocol:R03-selected-R02-reader-environment',
        'authority_effect':'none','actual_owner_outcome':None,
        'claim_ceiling':'Same-family Reader code projection only; no issuer grant or Context delivery.',
    }
    raw=(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()
    return raw,{'status':'SAME_FAMILY_PUBLIC_METADATA_JOIN_ONLY',
                'source_manifest_sha256':selected['source']['source_manifest_sha256'],
                'source_package_sha256':selected['source']['package_manifest_sha256'],
                'reader_manifest_sha256':selected['reader']['source_manifest_sha256'],
                'reader_code_sha256':selected['reader']['reader_code_sha256'],
                'binding_sha256':sha(raw),'private_archive_body_read':False}

def final_context_manifest(*_args,**_kwargs):
    raise Refused('API same-family bridge, Mapper and JIT authority are not selected')

def launch_context(*_args,**_kwargs):
    raise Refused('effect-disabled Context input closure')

if __name__=='__main__':
    print(json.dumps(verify_frozen(),sort_keys=True))
