"""Prepare deterministic logical package members and sealed metadata templates.

This builds a plan of exact bytes, not an installation or runtime verdict.
Archive creation/materialization checks every selected byte before writing it.
"""
import hashlib
import base64
import importlib.util
import json
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
API73 = ROOT/'product/lab/release-candidates/v1/interface/api-integration-v73-t15-learning-selector-0001'
API74 = API73.parent/'api-integration-v76-current-repairs-0001'
PREPARED_REPORT = 'API76-CODE-PREPARATION-0004.json'
PREPARED_SHA = '65b43dec5fa71e160d89166cbddfd0a8ae743b883d7095659ae5078ca3740b15'
GOVERNANCE = ROOT/'product/lab/release-candidates/v1/interface/api-governance-integration-v5-current-t12-0001'
GOVERNANCE_SOURCE_SHA = '8a215ad66e94179385bcb4dcac79eab5267ee6ac50e12e7b1dac21645301d337'
GOVERNANCE_PROFILE_SHA = '7798fda1f9e7e4038425bc8aa6f227f2e22612affa4acb2c28c9a12d31531af3'
FAMILY_HELPER = ROOT/'implementation/lab-runtime/local-host/t25-portable-family-0001/metadata.py'
PROJECTION = FAMILY_HELPER.parent/'PROJECTED-CODE-0005.json'
DATASET_FAMILY = 'implementation/lab-runtime/local-host/t15-integrated-fixture-0001/instances/legacy-local-4636eca980a5d94d'
COLD_TARGET = 'implementation/lab-runtime/local-host/t25-portable-family-0001/receipts/source-cold.json'
CURRENT_CALLER_INPUTS = (
    ('docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/common-all34-0277/caller.py',
     '45ce0d17e61a49855f0dd2735f7ad8cbf0da58dbadc959631bb36095b53b384a'),
    ('docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/common-all34-selection-0278/selection-plan.json',
     '1625d9229d855796a7b32661c4a11a084b37a5352138c193de1ec8069aa0891b'),
)
CONSTRUCTOR_SOURCE_INPUTS = (
    ('product/lab/release-candidates/v1/interface/classification-preparation-v10/__init__.py','829152df27c2cf016b2f9e78a711f27ffa75f216d013871847ac18e97678449e'),
    ('product/lab/release-candidates/v1/interface/classification-preparation-v10/preparation.py','29fc7de3d3abe064707b529743af43f0acbd9706e240a1e4e977ddb2fcf876fb'),
    ('product/lab/release-candidates/v1/interface/classification-preparation-v10/routing.schema.json','af0102c9150aa277c96eaa2a886c287bf3677fc7747d45909ddc676039acb286'),
    ('product/lab/release-candidates/v1/interface/failure-preparation-v6/__init__.py','fb183c962d59e8f15185a72afb9a19e5b75f8ab985bc1a48f1e4fd4e75bac49e'),
    ('product/lab/release-candidates/v1/interface/failure-preparation-v6/preparation.py','0f0369dcebd2bd3576f816bc4b47e6ba3c194f60035da77bdac519acf4fcf985'),
    ('product/lab/release-candidates/v1/interface/failure-preparation-v6/routing.schema.json','65ea8ceb40cfd897247f3a5595a9da4660736675f735deb7b9dcee35e35d0e51'),
    ('authority/artifact-types/ontology-view/v1/fixtures/valid/record.json','d8ede0835633b5559419042f448f729fbb398be279bf6ffde89f7bed572b41eb'),
    ('authority/admissions/governance-transaction-surface/v1/instances/governance/decisions/decision-0074a.json','46532a777693e37c9d5ca336cb6bced7e39af3cfd7366fe1f0ec1aa42a048864'),
    ('product/lab/release-candidates/v1/interface/checkpoint-owner-verification-v3/receipts/checks-0001.json','71e20196798452b917dfe9d653d6b6cd2cee585efaaa195048a35893b52d879a'),
)
V8 = ROOT/'product/lab/release-candidates/v1/interface/lesson-application-v8-t03-scope-custody-0001'
sha = lambda raw:hashlib.sha256(raw).hexdigest()
encoded = lambda value:(json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()


def need(value, reason):
    if not value:
        raise ValueError(reason)


def source_row(path):
    info = Path(path).lstat()
    need(stat.S_ISREG(info.st_mode),'selected package source must be regular')
    return {'input_path':str(path),'sha256':sha(Path(path).read_bytes()),
            'size_bytes':info.st_size,'mode':stat.S_IMODE(info.st_mode)}


def current_caller_inputs(root, selected=CURRENT_CALLER_INPUTS):
    rows={}
    for name,pin in selected:
        path=Path(name)
        need(not path.is_absolute() and path.as_posix()==name and '..'not in path.parts
             and path.suffix!='.pyc','closed caller source/data input required')
        row=source_row(Path(root)/path)
        need(row['sha256']==pin,'independently selected historical caller input changed')
        need(name not in rows,'duplicate selected caller input')
        rows[name]=row
    return rows


def module(path,name):
    spec = importlib.util.spec_from_file_location(name,path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def renewed_projection(projection,fresh):
    if fresh is None or 'projection_binding' not in fresh:return projection
    family=fresh['family'];selected=fresh['projection_binding']
    need(type(selected)is dict and set(selected)=={'path','sha256'},'closed explicit fresh projection binding required')
    name=Path(selected['path']);need(not name.is_absolute() and name.as_posix()==selected['path'] and '..'not in name.parts,'closed fresh projection locator required')
    raw=(ROOT/name).read_bytes();need(sha(raw)==selected['sha256'],'explicitly selected fresh projection bytes differ')
    renewed=json.loads(raw)
    original_family='implementation/lab-runtime/local-host/t03-long-local-fixture-0001/instances/legacy-local-5bd4f03a7076695c'
    expected=[{**row,'path':row['path'].replace(original_family+'/',family+'/')} for row in projection['projected_code']]
    need(renewed['projected_code']==expected,'renewed projection may only retarget reviewed logical family paths; generic bytes remain exact')
    return renewed


def build(output, fresh=None):
    output = Path(output)
    need(output.is_absolute() and not output.exists() and not output.resolve().is_relative_to(ROOT),
         'package view requires fresh disjoint owned staging destination')
    output.mkdir(mode=0o700,parents=True)
    family=DATASET_FAMILY if fresh is None else fresh['family']
    family_path=Path(family);need(not family_path.is_absolute() and family_path.as_posix()==family and '..'not in family_path.parts,'closed packaged family locator required')
    metadata_input=FAMILY_HELPER if fresh is None else FAMILY_HELPER.parent/'metadata_0008.py'
    if fresh is not None:
        need(sha(metadata_input.read_bytes())=='fd7fb2b1d898a9d9684e87e7ba42ad67a54c80a0e281ecf5ef4ba5157a02753d','reviewed fresh metadata constructor differs')
    inventory = json.loads((HERE/'DECLARED-CLOSURE-0001.json').read_bytes())
    repo = {}
    host = {}
    native = {}
    for row in inventory['members']:
        if row['member'].startswith('repository/'):
            repo[row['member'][len('repository/'):]] = {key:row[key] for key in ('input_path','sha256','size_bytes','mode')}
        elif row['member'].startswith('host-inputs/'):
            original = '/'+row['member'][len('host-inputs/'):]
            host[original] = {key:row[key] for key in ('input_path','sha256','size_bytes','mode')}
        elif row['member'].startswith('native-payload/'):
            native[row['member'][len('native-payload/'):]] = {key:row[key] for key in ('sha256','size_bytes','mode')}
    need(len(native)==1010,'package view native count differs')
    # The predecessor's broad public toolchain declaration retained one stale
    # libz pin. The new profile explicitly selects today's public snapshot;
    # predecessor bytes/history and the exact bundled native ABI stay intact.
    rebases=[]
    for locator,old_pin,new_pin in (('/usr/lib/x86_64-linux-gnu/libz.so.1.3.1',
        '47b61967895b30e8c0c6818dd633ffeb87711cf637c688f981896f0dd84ce23b',
        '27fa6c6cb94fb5b099ead61758a300dbc392d1dbf307fff6c16a9b8e57fdc9de'),):
        need(host[locator]['sha256']==old_pin,'predecessor public snapshot declaration differs')
        row=source_row(Path(locator));need(row['sha256']==new_pin,'new explicitly selected public snapshot differs')
        host[locator]=row
        rebases.append({'path':locator,'predecessor_sha256':old_pin,'selected_sha256':new_pin,
                        'classification':'public-profile-declaration-only; native ABI unchanged'})
    tool_receipt=HERE/'READELF-TOOLCHAIN-0001.json'
    tool=json.loads(tool_receipt.read_bytes())
    need(tool['schema_version']=='lab-public-ELF-inspection-runtime/v1' and tool['actual_tool_inspection_completed'] is True,'actual ELF tool closure declaration required')
    for selected in tool['host_inputs']:
        row=source_row(Path(selected['path']))
        need(all(row[key]==selected[key] for key in ('sha256','size_bytes','mode')),'actual selected readelf dependency differs')
        if selected['path'] in host:
            need(all(host[selected['path']][key]==selected[key] for key in ('sha256','size_bytes','mode')),'ELF tool conflicts with historical host snapshot')
        else:host[selected['path']]=row
    for alias in tool['tool_namespace_aliases']:
        need(alias['source_path'] in host and all(alias[key]==host[alias['source_path']][key] for key in ('sha256','size_bytes','mode')),'tool alias target differs from selected canonical snapshot')
    repo[str(tool_receipt.relative_to(ROOT))]=source_row(tool_receipt)
    projection_path=PROJECTION if fresh is None else FAMILY_HELPER.parent/'PROJECTED-CODE-0006.json'
    projection_pin='e9d2e3415ecea81a291ab37497f2e1d5431f67ee267aa8cf9301ca607e5ed84c' if fresh is None else 'f7d965f5d289dca4a39861e29ca7ed66663496e8aeb48022cb5baab53fcdf3b1'
    need(sha(projection_path.read_bytes())==projection_pin,'reviewed portable family projection differs')
    projection = json.loads(projection_path.read_bytes())
    projection=renewed_projection(projection,fresh)
    if fresh is not None:
        lane=Path(family).parents[1].as_posix()+'/'
        queue=[row for row in fresh['bindings'].values()]+fresh['original_source_artifacts']
        seen={}
        while queue:
            binding=queue.pop();name=binding['path']
            need(type(name)is str and not Path(name).is_absolute() and '..'not in Path(name).parts,'fresh declared member locator differs')
            if not name.startswith(lane):continue
            if name in seen:
                need(seen[name]==binding['sha256'],'fresh declared member has inconsistent pins');continue
            row=source_row(ROOT/name);need(row['sha256']==binding['sha256'],'fresh declared member differs: '+name)
            seen[name]=binding['sha256'];repo[name]=row
            if not name.endswith('.json'):continue
            def declared(value):
                if isinstance(value,list):
                    for item in value:declared(item)
                elif isinstance(value,dict):
                    if isinstance(value.get('path'),str) and isinstance(value.get('sha256'),str) and value['path'].startswith(lane):queue.append({'path':value['path'],'sha256':value['sha256']})
                    for item in value.values():declared(item)
            declared(json.loads((ROOT/name).read_bytes()))

    for row in projection['projected_code']:
        source = ROOT/row['source_binding']['path']
        need(sha(source.read_bytes())==row['source_binding']['sha256'],'generic family code projection changed')
        repo[row['path']] = source_row(source)
    # Retain the superseded first portable loader as immutable historical
    # package data. Only the newly selected Source manifest names the live one.
    superseded=FAMILY_HELPER.parent/'portable-role-origin-0003/role_loader.py'
    need(sha(superseded.read_bytes())=='b1080017f4f8245673cc7804eef8319541ed5f7371c656bd393419edd9fcb027','superseded portable loader data changed')
    repo[str(superseded.relative_to(ROOT))]=source_row(superseded)
    # All explicitly prepared API code/static data is selected by its own
    # constructor receipt. No untracked file can enter through a directory glob.
    prepared_raw=(HERE/PREPARED_REPORT).read_bytes()
    need(sha(prepared_raw)==PREPARED_SHA,'independently reviewed API76 code preparation differs')
    repo[str((HERE/PREPARED_REPORT).relative_to(ROOT))]=source_row(HERE/PREPARED_REPORT)
    constructor=HERE/'prepare_api76_code_0003.py'
    need(sha(constructor.read_bytes())=='76025c35397c426369a0f7580f4e6cc5054de46682cfe61240af8d9404744513',
         'selected API76 source constructor changed')
    repo[str(constructor.relative_to(ROOT))]=source_row(constructor)
    classifier_stage=ROOT/'product/lab/release-candidates/v1/interface/classification-preparation-v10'
    for name,pin in (
        ('test_scan.py','716a612513308dece0e9aaaac9f98e734cae6c755d706a15badec781ee460468'),
        ('DESIGN.md','1461e21896d9d965ddd57f77f7de6483864ba096d0fec8cb747b3bdb6be653b8'),
        ('TEST-RESULT-0001.json','9f7f9d00dfde7f30db301f7c841208033ccf8436011edaa9feed8ec6884e0427')):
        path=classifier_stage/name;row=source_row(path)
        need(row['sha256']==pin,'reviewed classification v10 evidence changed')
        repo[str(path.relative_to(ROOT))]=row
    prepared = json.loads(prepared_raw)
    for row in prepared['files']:
        source = ROOT/row['path']
        need(sha(source.read_bytes())==row['sha256'],'portable API code changed after constructor')
        repo[row['path']] = source_row(source)
    # The current T12 governance member was selected by the API76 member
    # record. Its own complete source manifest is independently checked and
    # installed at each true repository origin required by its guard.
    governance_source=GOVERNANCE/'source-manifest.json'
    governance_profile=GOVERNANCE/'contract-profile.json'
    need(sha(governance_source.read_bytes())==GOVERNANCE_SOURCE_SHA
         and sha(governance_profile.read_bytes())==GOVERNANCE_PROFILE_SHA,
         'selected current T12 governance source/profile differs')
    governance_files=json.loads(governance_source.read_bytes())['files']
    need(len(governance_files)==986 and len({item['path'] for item in governance_files})==986,
         'current T12 governance closure differs')
    for item in governance_files:
        path=ROOT/item['path'];row=source_row(path)
        need(row['sha256']==item['sha256'], 'current T12 governance original changed: '+item['path'])
        if item['path'] in repo:
            need(repo[item['path']]['sha256']==row['sha256'],
                 'current T12 governance original collides with selected package bytes: '+item['path'])
        repo[item['path']]=row
    governance_rows=[*governance_files,
                     {'path':str(governance_source.relative_to(ROOT)),'sha256':GOVERNANCE_SOURCE_SHA}]
    repo[str(governance_source.relative_to(ROOT))]=source_row(governance_source)
    governance_test=HERE/'test_api76_governance_selection.py'
    need(sha(governance_test.read_bytes())=='d82e9aac70b279c7ec65ee9d62706bb6634b3e2083fe3ae84b0f49eb70fdf22e',
         'selected current T12 governance member test changed')
    repo[str(governance_test.relative_to(ROOT))]=source_row(governance_test)
    governance_probe=HERE/'probe_governance_v5.py'
    need(sha(governance_probe.read_bytes())=='435a6f9e3d7875aeda114b11078c0b1f62795b8ffaa27dffa4f0b3cbfe9761c6',
         'selected current T12 isolated governance probe changed')
    repo[str(governance_probe.relative_to(ROOT))]=source_row(governance_probe)
    governance_note=HERE/'API76-GOVERNANCE-T12-REPIN.md'
    need(sha(governance_note.read_bytes())=='c310c644c0b60561d5add36dcfb094f7aa2e136b933c56acbae8bb0cc60abe0e',
         'reviewed current T12 governance repin note changed')
    repo[str(governance_note.relative_to(ROOT))]=source_row(governance_note)
    for name in ('__init__.py','preparation.py'):
        path = V8/name
        repo[path.relative_to(ROOT).as_posix()] = source_row(path)
    component = ROOT/'implementation/lab-runtime/local-host/t31-owned-produced-0001/RUNTIME-COMPONENT-BINDINGS-0001.json'
    need(sha(component.read_bytes())=='e5a45363700fcf83accc1d8fd750304c0cb4be1593705efe6c2d2bfb090435c0',
         'additional maintained component selection changed')
    extra = json.loads(component.read_bytes())
    repo[component.relative_to(ROOT).as_posix()] = source_row(component)
    for row in extra['direct_components_and_original_carrier_documents']:
        path = ROOT/row['path']
        need(sha(path.read_bytes())==row['sha256'],'maintained direct component changed')
        repo[row['path']] = source_row(path)
    scoped=ROOT/'implementation/lab-runtime/local-host/t31-scoped-output-0001/RUNTIME-COMPONENT-BINDINGS-0001.json'
    need(sha(scoped.read_bytes())=='154c8ec60d161bb447b02d302663d1cf9e34b5c2f61a642cfd4f6ac0b064d884','reviewed scoped runtime component selection changed')
    repo[str(scoped.relative_to(ROOT))]=source_row(scoped)
    for row in json.loads(scoped.read_bytes())['members']:
        path=ROOT/row['path'];need(sha(path.read_bytes())==row['sha256'],'scoped runtime component changed')
        repo[row['path']]=source_row(path)
    callers=ROOT/'implementation/lab-runtime/local-host/t31-public-owned-transition-0001/CALLER-CLOSURE-0002.json'
    need(sha(callers.read_bytes())=='088cbee95b9cf9d935094e660a994d519007f94cd009e0ce36a6ca892687d15f','selected owned current caller closure changed')
    repo[str(callers.relative_to(ROOT))]=source_row(callers)
    for row in json.loads(callers.read_bytes())['files']:
        path=ROOT/row['path'];need(sha(path.read_bytes())==row['sha256'],'selected owned current caller component changed')
        repo[row['path']]=source_row(path)
    # Close the exact operator/retained-work transitive import gap observed
    # in final0003 before attempting the successor workflow command.
    operator_closure=HERE/'API76-OPERATOR-IMPORT-CLOSURE-0001.json'
    need(sha(operator_closure.read_bytes())=='dabd84dcd943b32f25273725b376ad6a206be5b1cdc0c7c4bef4512377eb15a0',
         'selected operator import closure changed')
    repo[str(operator_closure.relative_to(ROOT))]=source_row(operator_closure)
    for selected in json.loads(operator_closure.read_bytes())['files']:
        path=ROOT/selected['path'];row=source_row(path)
        need(row['sha256']==selected['sha256'],'selected operator import differs')
        repo[selected['path']]=row
    current_caller=ROOT/'implementation/lab-runtime/local-host/t17-current-common-caller-0001/CALLER-AND-PROBE-CLOSURE-0009.json'
    need(sha(current_caller.read_bytes())=='ee48191f9bfbfd54c6f68999bdcbc4340c1d020a55b7bd7dc5bfc1943e2342c2','selected current common caller closure changed')
    repo[str(current_caller.relative_to(ROOT))]=source_row(current_caller)
    for row in json.loads(current_caller.read_bytes())['files']:
        path=ROOT/row['path'];need(sha(path.read_bytes())==row['sha256'],'current common caller component changed')
        repo[row['path']]=source_row(path)
    # The maintained caller imports these exact historical caller functions and
    # reads the exact operation-unit plan. Historical provider pycs are data in
    # that plan, never executable or selected live qualification inputs.
    repo.update(current_caller_inputs(ROOT))
    for name,pin in (
        ('implementation/lab-runtime/local-host/t17-current-common-caller-0002/run_remaining.py','353397004fcb18ea29eda9e0c86ecdc9cdb76d3b433ae19a41f19559860ea747'),
        ('implementation/lab-runtime/local-host/t25-integrated-runtime-0004/supervise_full345_api76.py','4c98b672bdf0eda241f57f9f78c292b12618501a2edcfdee2ad38f4b31ac91d3'),
        ('implementation/lab-runtime/local-host/t25-integrated-runtime-0004/supervise_whole24_api76.py','d21d98cfa3335dabfbbc4a7298c084b1b76a1b54fd9ebe107dc09a80288ed856'),
        ('implementation/lab-runtime/local-host/t25-integrated-runtime-0004/qualify_relation_closure_0002.py','39a82df8e9c118134078949e0d6bf9d494063e2ace8ff187c8a8650cce16c581'),
        ('implementation/lab-runtime/local-host/t25-scratch-docker-0001/build_context.py','bcc4d5306f21989138a6a3eaff19633a4544dd70b874c839c417ac5aa35370d8'),
        ('implementation/lab-runtime/local-host/t25-scratch-docker-0001/run_complete_qualification.py','358bdcb0fffe4f0a7c3660e754217ed9447d5b008d2ee3831e07181ce02b7ea8')):
        path=ROOT/name;row=source_row(path);need(row['sha256']==pin,'reviewed exact installed batch/Docker qualification helper changed');repo[name]=row
    for name,pin in CONSTRUCTOR_SOURCE_INPUTS:
        row=source_row(ROOT/name);need(row['sha256']==pin,'exact currently selected constructor input changed')
        need(name not in repo or repo[name]['sha256']==pin,'constructor input conflicts with historical package declaration');repo[name]=row
    historical=[]
    for name,pin in (
        ('implementation/lab-runtime/local-host/t25-original-package-accounting-0001/RESULT.json','bbe970bd0e63c3df52f6075c4317a7f10dbe7df6d2c509caacd9c374e23f38c7'),
        ('implementation/lab-runtime/local-host/t25-original-member-reconciliation-0002/RECONCILIATION.json','9956ad0286f6d86c9c124122f077f2eb5442eced8f86c6e0837f150e68c3888b')):
        path=ROOT/name;row=source_row(path);need(row['sha256']==pin,'historical 363-member inventory changed');repo[name]=row;historical.append(json.loads(path.read_bytes()))
    original_ids=historical[0]['member_ids'];reconciled_ids=[row['original_member_ref'] for row in historical[1]['members']]
    need(len(original_ids)==len(set(original_ids))==len(reconciled_ids)==len(set(reconciled_ids))==363
         and set(original_ids)==set(reconciled_ids),'original historical member identities differ')
    retained_helper=ROOT/'implementation/lab-runtime/local-host/t31-retained-api-0001/CURRENT-HELPER-CLOSURE-0013.json'
    need(sha(retained_helper.read_bytes())=='5e9618b728a38e67b90caca353076ea99d52bf089bd65d688cca53247f955c6a','reviewed retained workflow helper closure changed')
    repo[str(retained_helper.relative_to(ROOT))]=source_row(retained_helper)
    helper_body=json.loads(retained_helper.read_bytes())
    runtime_names=set(helper_body['runtime_module_files'])
    selected_helper_rows=(helper_body['files']+helper_body['required_public_runtime_inputs']
                          +helper_body['standalone_qualification_runners'])
    file_names={row['path'] for row in helper_body['files']}
    need(len(runtime_names)==9 and len(helper_body['files'])==31
         and len(helper_body['required_public_runtime_inputs'])==28
         and len(helper_body['dynamic_helper_files'])==8
         and set(helper_body['dynamic_helper_files'])<=file_names
         and len(helper_body['standalone_qualification_runners'])==2,
         'closed retained runtime helper/input selection differs')
    for row in selected_helper_rows:
        path=ROOT/row['path'];need(sha(path.read_bytes())==row['sha256'],'reviewed retained workflow helper changed')
        need(row['path'] not in repo or repo[row['path']]['sha256']==row['sha256'],
             'retained workflow helper conflicts with an earlier selected package row')
        repo[row['path']]=source_row(path)
    for name,pin in (
        ('implementation/lab-runtime/local-host/t31-retained-api-0001/prepare_config.py',
         '7abd16678ea79726bed376cee19f824549b7051475690112fe77ce7a13b5f570'),
        ('implementation/lab-runtime/local-host/t31-retained-api-0001/normalize_learning.py',
         '1889543d74320a5e31c950b7ac69ab7b83407c21336c9d19bad421c69405c3fc'),
        ('implementation/lab-runtime/local-host/t31-current-ontology-capture-0001/capture_current.py',
         'aecc7f8b1f4a8341a16c43e557f32a3fa09d23285b41ef46e10ca72bba6342cc')):
        path=ROOT/name;row=source_row(path)
        need(row['sha256']==pin,'selected current workflow producer input changed')
        need(name not in repo or repo[name]['sha256']==pin,
             'selected current workflow producer conflicts with earlier package row')
        repo[name]=row
    for name,pin in (
        ('authority/artifact-types/lesson-application/v1/fixtures/valid/record.json','711d72999a4ca5a7abff8ba938d50387020583214c668de2859c056a157b9b12'),
        ('authority/artifact-types/lesson-outcome-assessment/v1/fixtures/valid/record.json','fb14ca2e2ba2ed75b5c742318e8233b49b0458fe305c96b6645c77fc02e6e9bc'),
        ('authority/artifact-types/decision/v1/fixtures/valid/record.json','c7075578a24a7d7658740f2e018e56faa2dbd60289741b040c755ea4e91024fe'),
        ('authority/artifact-types/decision-scope/v1/fixtures/valid/record.json','b74aca5c195f32ab9864ec7ea8890cc026244feeea0b8a5049d2cf2d94692b3c'),
        ('authority/artifact-types/authority-claim/v1/fixtures/valid/record.json','4011c90bca8b75e6dce574e39365808043cd35ce8c2b2c7a67f8b93d0025e48a'),
        ('product/lab/release-candidates/v1/interface/api-integration-v71-t15-integrated-closure-0001/t22-validation-receipt.json','9b993689d1737bcd0f98029aea0333321972a4e172e808b2860c35866e681fd6'),
        ('implementation/lab-runtime/local-host/t31-current-ontology-capture-0001/external-postimages-0002/external_ontology_capture.py','3c6bee19c635eb3bf052ac4c72da587d7dc1309f7f21899c9c572046f89eef7f')):
        path=ROOT/name;row=source_row(path);need(row['sha256']==pin,'reviewed executable public template/evidence or host capture changed');repo[name]=row
    capture_closure=ROOT/'implementation/lab-runtime/local-host/t31-current-ontology-capture-0001/CAPTURE-INTEGRATION-CLOSURE-0001.json'
    need(sha(capture_closure.read_bytes())=='cf9aa4116f2c41dcd130b464b4dce45dfe26523e3b5ce87b51e795caac4c8626','reviewed additional capture reader closure changed')
    repo[str(capture_closure.relative_to(ROOT))]=source_row(capture_closure)
    name='implementation/lab-runtime/local-host/t31-retained-api-0001/ontology_capture_records.py';row=source_row(ROOT/name)
    need(row['sha256']=='619523a2af3256f5a4451204bebdcded4701b3f4305ff0d53809157f7678e547','reviewed selected-root capture reader changed');repo[name]=row
    learning_closure=ROOT/'implementation/lab-runtime/local-host/t31-retained-api-0001/LEARNING-PRODUCER-CLOSURE-0001.json'
    need(sha(learning_closure.read_bytes())=='7c277357010fe128b0283e9a6d0ed0a707cb41ce4c7c88b68dd8080412078ea9','reviewed learning reader closure changed');repo[str(learning_closure.relative_to(ROOT))]=source_row(learning_closure)
    learning_body=json.loads(learning_closure.read_bytes());learning_path='implementation/lab-runtime/local-host/t31-retained-api-0001/learning_records.py'
    for selected in [row for row in learning_body['files'] if row['path']==learning_path]+learning_body['required_public_runtime_inputs']:
        row=source_row(ROOT/selected['path']);need(row['sha256']==selected['sha256'],'reviewed learning reader/public input changed');repo[selected['path']]=row
    if API74.name=='api-integration-v76-current-repairs-0001':
        margin_prefix='implementation/lab-runtime/local-host/t03-installed-learning-caller-0001/'
        software_path=HERE/'MARGIN-SOFTWARE-API76-0003.json'
        software_row=source_row(software_path)
        need(software_row['sha256']=='9a71a448d8d9db2342aaff8457a4b386e8e8251e7fcbca228620b6cc934e2979','reviewed exact API76 margin software selection changed')
        for selected in json.loads(software_path.read_bytes())['files']:
            need(repo.get(selected['path'],{}).get('sha256')==selected['sha256'],'margin software input differs from selected stable package code')
        # The unchanged caller selects this stable logical target by package
        # digest. Preserve the historical workspace file and include successor
        # provenance separately; the new artifact selects exact reviewed bytes.
        repo[margin_prefix+'margin-software.json']=dict(software_row)
        repo['implementation/lab-runtime/local-host/t03-installed-learning-caller-0005/margin-software.json']=dict(software_row)
        repo[str(software_path.relative_to(ROOT))]=dict(software_row)
        path=ROOT/(margin_prefix+'margin-instrumentation.json')
        row=source_row(path);need(row['sha256']=='e5e97745c3239d79b9a8b4b06937612b86dcfc14a2ae973850783575eba84921','selected public actual-margin instrumentation changed');repo[str(path.relative_to(ROOT))]=row
        repo['implementation/lab-runtime/local-host/t03-installed-learning-caller-0005/margin-instrumentation.json']=dict(row)
    retained='implementation/lab-runtime/local-host/t22-retained-origin-resolution-0001'
    for name,pin in (('inputs.py','f3ff659d0e80a1f1edb94e38c662ee9e2da432570aa0547c1b7ec339aabaab92'),('fixture.py','3f15888bb73220d19edebae246a6a961385efca1d4c8f0ece9533b92d27fd9d2'),('PUBLIC-SEED-DATA-AUDIT-0001.json','5a28b119c4972119726a75dbe66f402eef7940688317454e05dbd71ffba7838b')):
        path=ROOT/retained/name;row=source_row(path);need(row['sha256']==pin,'independently reviewed retained-origin fixture input changed');repo[str(path.relative_to(ROOT))]=row
    origin_raw=Path('/home/vlad_/.local/share/cyberalchemy-lab/t22-origin71-public-seed-0001.json').read_bytes()
    origin_pin='491052937d701601b105eaa30b451358f7a2f4e00cc3a0d943ebd63e7370a005'
    need(sha(origin_raw)==origin_pin,'independently audited synthetic origin seed changed')
    origin_target=output/'.cal-fixture-seed/t22-origin71.json';origin_target.parent.mkdir(mode=0o700,parents=True,exist_ok=True);origin_target.write_bytes(origin_raw);origin_target.chmod(0o644);repo[str(origin_target.relative_to(output))]=source_row(origin_target)
    renew_lane=ROOT/'implementation/lab-runtime/local-host/t03-long-local-fixture-0001'
    for name,pin in (('renew_and_install_0002.py','020271b29fca2e0572b67634c9900ac274cb96ce518965946b79fb329bd9cf5a'),('renew_local.py','34412e05df31c46f86ad6a3f7c4d211b80ea3ca291c23477f37773b59ca4b4dd')):
        path=renew_lane/name;row=source_row(path);need(row['sha256']==pin,'selected explicit WSL build station renewal entry changed');repo[str(path.relative_to(ROOT))]=row
    t03_v5=ROOT/'implementation/lab-runtime/local-host/t03-installed-learning-caller-0005'
    t03_receipt=t03_v5/'TEST-RESULT-0001.json'
    need(sha(t03_receipt.read_bytes())=='72195e73ece2be7cf1c8b34058cc54f156008e72caa5a0c528fe844b1883474d',
         'reviewed first-emitter caller source test receipt changed')
    t03_selection=json.loads(t03_receipt.read_bytes())
    need(t03_selection['result']=='PASS-source-tests' and t03_selection['test_count']==11,
         'current T03 caller source checks differ')
    for name,pin in t03_selection['caller_v5_file_sha256'].items():
        path=t03_v5/name;row=source_row(path)
        need(row['sha256']==pin,'reviewed current T03 caller file changed')
        repo[str(path.relative_to(ROOT))]=row
    repo[str(t03_receipt.relative_to(ROOT))]=source_row(t03_receipt)
    emitter=ROOT/'implementation/lab-runtime/local-host/t31-native-first-emitter-0002/native_first_emitter.py'
    need(sha(emitter.read_bytes())=='7b75b4f3cddb39f57f553bf1908cc9ae9457617f0f409f711931a70baaebc7db',
         'reviewed native first-emitter adapter changed')
    repo[str(emitter.relative_to(ROOT))]=source_row(emitter)
    replay=ROOT/'implementation/lab-runtime/local-host/t03-lesson-domain-resolver-0001'
    for name,pin in (
        ('supervise_replay.py','67729983895abc2538477120ccf89678673916ef7a8619dd9a73d46c8ec89a49'),
        ('make_replay_selection.py','f941fd6ab860a79085f42cdd651bb73f34bcaa6c1d96b2dbfb91d3ad0edd3b33')):
        path=replay/name;row=source_row(path)
        need(row['sha256']==pin,'reviewed installed T03 replay helper changed')
        repo[str(path.relative_to(ROOT))]=row
    t31_supervisor=ROOT/'implementation/lab-runtime/local-host/t31-final-supervisor-0001'
    for name,pin in (
        ('supervise.py','149686891e51945a10448f8f01af101e55b593549f3c8df8653f89f003f11164'),
        ('make_control_plan.py','fd5faa8a9f83a6bb0a81dda8355151593f36bbad49e2f9c5cd2eb74f80277198'),
        ('make_transition_plan.py','f1684084273dbbb3477491c1d91032adf978701d1f9f3e40f6be58f967e4b1dc'),
        ('README.md','c9c9e7bb906e01750336a673ca9dc00be99757d8a100e2aef6fa21fac02a93dd')):
        path=t31_supervisor/name;row=source_row(path)
        need(row['sha256']==pin,'reviewed all28 supervisor source changed')
        repo[str(path.relative_to(ROOT))]=row
    operator=ROOT/'implementation/lab-runtime/local-host/t21-installed-operator-0001'
    operator_pins=operator/'PINS-0004.json';need(sha(operator_pins.read_bytes())=='0a436a64718fda492ea11898c7083225bb7b20a120dd03b9f9b1bc9bd8500499','selected working product operator declaration changed')
    repo[str(operator_pins.relative_to(ROOT))]=source_row(operator_pins)
    command=operator/'command.py';row=source_row(command);need(row['sha256']=='340f34ce33eff145233aa651834dd13a241437324bc6b71a77ce5076db74f331','selected working product command changed');repo[str(command.relative_to(ROOT))]=row
    demo=ROOT/'implementation/lab-runtime/local-host/t21-operator-workflow-deps-0001'
    selection=demo/'SELECTION.json';need(sha(selection.read_bytes())=='c2c2abaa0870b8940febdec66a625e8ff01c25874d4ad45a9cafc4c32a478594','reviewed production demo import/consumer selection changed')
    repo[str(selection.relative_to(ROOT))]=source_row(selection);demo_selection=json.loads(selection.read_bytes())
    for selected in (demo_selection['selected_bundle_postimage'],demo_selection['selected_consumer']):
        row=source_row(ROOT/selected['source_path']);need(row['sha256']==selected['sha256'],'reviewed production demo postimage changed');repo[selected['target_path']]=dict(row);repo[selected['source_path']]=dict(row)
    demo_inputs=demo/'RETAINED-DEMO-INPUTS-0001.json';need(sha(demo_inputs.read_bytes())=='44ea3022d8dae66d2c51997f957e3cbf6c24b0d1590aea42048e29abcb807baa','reviewed exact retained demo inputs changed')
    repo[str(demo_inputs.relative_to(ROOT))]=source_row(demo_inputs)
    selected_demo_inputs=json.loads(demo_inputs.read_bytes())['input_files'];need(len(selected_demo_inputs)==20,'closed retained demo input count differs')
    for selected in selected_demo_inputs:
        row=source_row(ROOT/selected['path']);need(row['sha256']==selected['sha256'] and row['size_bytes']==selected['size_bytes'],'reviewed retained demo original changed');repo[selected['path']]=row
    for name,pin in (
        ('implementation/lab-runtime/local-host/LOCAL-ENGINEERING-RELEASE.md','f76d3fdfb12665609876a98b6c065b5978c3e6c41a1042d7c4a1f02798f8ab7f'),
        ('implementation/lab-runtime/local-host/LOCAL-PRODUCT.md','60991005140b31449d1e3225367904261877472440db3636cc72908fbabe7e3f'),
        ('implementation/lab-runtime/local-host/t20-final-artifact-privacy-0001/scan.py','c212bba15b6d72349b6632a925e56a05f5bd7a888143f2abe3f363c54e2eacc4')):
        row=source_row(ROOT/name);need(row['sha256']==pin,'reviewed operator documentation/privacy scanner changed');repo[name]=row
    # Explicit startup files; no package claims that these alone close imports.
    for path in (HERE/'installed_selection.py',HERE/'native_install.py',HERE/'child_bootstrap.py',
                 FAMILY_HELPER,FAMILY_HELPER.parent/'construction_child.py',HERE/'api_runtime_selection.py',
                 HERE/'materialize.py',HERE/'package_view.py',HERE/'package_view_api76.py',HERE/'configure_installation.py',
                 HERE/'qualify_installed_api.py',HERE/'construction_runner.py',HERE/'archive.py',HERE/'install_from_archive.py',
                 HERE/'regression.py',HERE/'regression_worker.py',ROOT/'implementation/lab-runtime/local-host/t16-api49-provisional-regression-0001/INVENTORY-0001.json'):
        repo[path.relative_to(ROOT).as_posix()] = source_row(path)
    lifecycle=HERE/'uninstall_restore.py'
    need(sha(lifecycle.read_bytes())=='97a11ef7c298b3fd8e0cdebee3f537ff041f1310afd79e4c6e148b9d259224fc','reviewed exact installation lifecycle observer changed')
    repo[str(lifecycle.relative_to(ROOT))]=source_row(lifecycle)
    launcher = ROOT/'implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python'
    repo[launcher.relative_to(ROOT).as_posix()] = source_row(launcher)
    for name in ('selected_python.c','native_members.h','build.py','probe_tree.py'):
        path=launcher.parent/name
        repo[path.relative_to(ROOT).as_posix()]=source_row(path)
    seed_helper=module(HERE/'fixture_seed.py','cal_T25_synthetic_fixture_seed')
    seed_pin=seed_helper.PIN if fresh is None else fresh['fixture_seed']['sha256']
    seed_raw,seed_audit=seed_helper.audit() if fresh is None else seed_helper.audit(fresh['fixture_seed']['path'],seed_pin)
    seed_body=json.loads(seed_raw)
    signed_baseline=json.loads(base64.b64decode(seed_body['files']['baseline.json']['base64_original_bytes'],validate=True))
    baseline_materials=signed_baseline['materials']
    need(type(baseline_materials)is dict and len(baseline_materials)==859,'signed baseline direct material closure differs')
    baseline_added=[]
    for name,pin in sorted(baseline_materials.items()):
        path=Path(name)
        need(not path.is_absolute() and '..'not in path.parts and path.as_posix()==name,'signed baseline material locator differs')
        row=source_row(ROOT/path);need(row['sha256']==pin,'signed baseline material current bytes differ: '+name)
        if name in repo:need(repo[name]['sha256']==pin,'code projection would alter signed baseline material: '+name)
        else:baseline_added.append(name)
        repo[name]=row
    seed_path=output/seed_helper.TARGET
    seed_path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    seed_path.write_bytes(seed_raw);seed_path.chmod(0o644)
    repo[seed_helper.TARGET]=source_row(seed_path)
    audit_path=seed_path.parent/'AUDIT.json';audit_path.write_bytes(encoded(seed_audit));audit_path.chmod(0o644)
    repo[str(audit_path.relative_to(output))]=source_row(audit_path)
    batch=FAMILY_HELPER.parent/'construction_child_0003.py'
    need(sha(batch.read_bytes())=='ab46ca3b50b4ef0caae4eff1495718da2f3a633ae4a81341f8ccb627ac7895d0','reviewed native cold batch constructor differs')
    repo[str((FAMILY_HELPER.parent/'construction_child.py').relative_to(ROOT))]=source_row(batch)
    batch_helper=FAMILY_HELPER.parent/'cold_original_batch_0001.py'
    need(sha(batch_helper.read_bytes())=='e3b36f79a2f1763aa599bbc1b296e6604be9e6ad6f30f3439bdbc3f0c2686607','reviewed original cold batch helper differs')
    repo[str(batch_helper.relative_to(ROOT))]=source_row(batch_helper)
    kill_probe=ROOT/'implementation/lab-runtime/local-host/t18-current-service-kill-0001/probe.py'
    need(sha(kill_probe.read_bytes())=='1c3f6bd49a469b5c0db5cede08a00cd0a36a90b7b50b6848b4be4694f3246feb','reviewed actual kill qualification caller changed')
    repo[str(kill_probe.relative_to(ROOT))]=source_row(kill_probe)
    repo[str(FAMILY_HELPER.relative_to(ROOT))]=source_row(metadata_input)
    helper = module(metadata_input,'cal_T25_selected_family_metadata')
    generated = set(helper.template_targets(ROOT)) if fresh is None else set(helper.template_targets(ROOT,family))
    templates = helper.emit_templates(ROOT,output) if fresh is None else helper.emit_templates(ROOT,output,family=family)
    prefix73 = API73.relative_to(ROOT).as_posix()+'/'
    prefix74 = API74.relative_to(ROOT).as_posix()+'/'
    def rebind_path(value):
        if isinstance(value,list):
            return [rebind_path(item) for item in value]
        if isinstance(value,str):
            return value.replace('lesson-application-v7-t03-derived-effect-0001',V8.name)
        if not isinstance(value,dict):
            return value
        result = {key:rebind_path(item) for key,item in value.items()}
        if fresh is not None and isinstance(result.get('path'),str):
            old_lane=str(Path(DATASET_FAMILY).parents[1])
            if result['path'].startswith(old_lane+'/'):
                candidate=str(Path(family).parents[1])+result['path'][len(old_lane):]
                candidate=candidate.replace(Path(DATASET_FAMILY).name,Path(family).name)
                if candidate in repo or candidate in generated:result['path']=candidate
        if isinstance(result.get('path'),str) and result['path'].startswith(prefix73):
            result['path'] = prefix74+result['path'][len(prefix73):]
        return result
    api_source = rebind_path(json.loads((API73/'source-manifest.json').read_bytes()))
    api_profile = rebind_path(json.loads((API73/'contract-profile.json').read_bytes()))
    # Only fixed public bindings are changed here. Per-install generated byte
    # bindings are refreshed by the private metadata constructor afterward.
    for value in (api_source,api_profile):
        value['files'] = [row for row in value['files'] if not row['path'].startswith(prefix74)]
        value['files'].extend({'path':row['path'],'sha256':row['sha256']} for row in prepared['files'])
        value['files'].extend(governance_rows)
        if value is api_source:
            value['files'].extend({'path':name,'sha256':pin} for name,pin in CONSTRUCTOR_SOURCE_INPUTS)
            value['files'].append({'path':prefix74+'contract-profile.json','sha256':'0'*64})
            value['files'].extend({'path':str(path.relative_to(ROOT)),'sha256':repo[str(path.relative_to(ROOT))]['sha256']}
                                  for path in (HERE/'installed_selection.py',HERE/'native_install.py',HERE/'child_bootstrap.py',launcher))
        # v8 supersedes only the current diagnostic helper; historical method
        # and artifact data remain unchanged in the package.
        for row in value['files']:
            row['path'] = row['path'].replace('lesson-application-v7-t03-derived-effect-0001',V8.name)
            if row['path'] in repo:
                row['sha256'] = repo[row['path']]['sha256']
        value['files'] = sorted({row['path']:row for row in value['files']}.values(),key=lambda row:row['path'])
    for row in api_profile['files']:
        if row['path'] in host:row['sha256']=host[row['path']]['sha256']
    api_source['profile_binding']['path'] = prefix74+'contract-profile.json'
    api_source['predecessor_source_manifest_binding'] = {'path':prefix73+'source-manifest.json',
        'sha256':sha((API73/'source-manifest.json').read_bytes())}
    receipt = {'successor_package':API74.relative_to(ROOT).as_posix(),
               'successor_manifest_sha256':'0'*64,'authority_effect':'none',
               'schema_version':'lab-portable-api-install-receipt/v1'}
    seed_templates = {prefix74+'source-manifest.json':api_source,
                      prefix74+'contract-profile.json':api_profile,
                      prefix74+'rebind-receipt.json':receipt,
                      COLD_TARGET:{'schema_version':'lab-private-native-cold-construction/v1',
                                   'result':'UNQUALIFIED-CONSTRUCTION','authority_effect':'none'}}
    for target,value in seed_templates.items():
        path = output/'.cal-metadata-templates'/target
        path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
        raw = encoded(value)
        path.write_bytes(raw)
        path.chmod(0o644)
        templates[target] = {'path':path.relative_to(output).as_posix(),'sha256':sha(raw)}
        generated.add(target)
    for target in generated:
        repo.pop(target,None)
    for target,row in templates.items():
        path = output/row['path']
        need(sha(path.read_bytes())==row['sha256'],'metadata template changed while sealing')
        repo[row['path']] = source_row(path)
    binding_paths = {
        'api.source':prefix74+'source-manifest.json','api.profile':prefix74+'contract-profile.json',
        'family.source':family+'/source/source-manifest.json',
        'family.source_package':family+'/source/packages/0001/manifest.json',
        'family.reader_source':family+'/reader/source-manifest.json',
        'family.reader_package':family+'/source/packages/0001/manifest.json',
        'family.mapper_source':family+'/mapped/source-manifest.json',
        'family.mapper_package':family+'/mapped/packages/0001/manifest.json',
        'family.mapping':family+'/mapped/packages/0001/mapping.json',
        'family.context_source':family+'/context/source-manifest.json',
        'family.context_package':family+'/context/packages/0001/manifest.json',
        'family.delivery':family+'/context/packages/0001/delivery.json',
        'family.period':family+'/source/packages/0001/period.json',
        'family.record_index':family+'/source/packages/0001/record-index.json',
        'family.archive_handle':family+'/source/packages/0001/archive-handle.json',
        'family.context_native_role':family+'/source/context-native-role.json','family.cold':COLD_TARGET,
        'engine.profile':'implementation/lab-runtime/local-host/t15-integrated-fixture-0001/engine-v3/runtime/profile.json',
        'engine.manifest':'implementation/lab-runtime/local-host/t15-integrated-fixture-0001/engine-v3/engine-manifest.json',
        'engine.loader':'implementation/lab-runtime/local-host/t15-integrated-fixture-0001/engine-v3/loader.py',
        'engine.pins':'implementation/lab-runtime/local-host/t15-integrated-fixture-0001/engine-v3/pins.json'}
    if fresh is not None:
        binding_paths.update({slot:row['path'] for slot,row in fresh['bindings'].items()})
    fixture_index=json.loads((ROOT/family/'source/packages/0001/record-index.json').read_bytes())
    fixture_records={}
    for kind in ('work','challenge-contract'):
        selected_rows=[row for row in fixture_index if row['kind']==kind]
        need(len(selected_rows)==1,'unique independently signed fixture record required')
        selected=selected_rows[0];body=selected['original_binding']
        need(repo.get(body['path'],{}).get('sha256')==body['sha256'],'fixture record outside stable dataset members')
        fixture_records[kind]={**body,'version_ref':selected['version_ref']}
    manifest = {'schema_version':'lab-stable-runtime-package/v1','authority_effect':'none',
        'dataset':inventory['dataset'] if fresh is None else fresh['dataset'],'fixture_records':fixture_records,'binding_paths':binding_paths,
        'generated_metadata_paths':sorted(generated),'metadata_templates':templates,
        'members':[{'path':name,**{key:row[key] for key in ('sha256','size_bytes','mode')}}
                   for name,row in sorted(repo.items())],
        'retained_origin_fixture':{'seed_binding':{'path':'.cal-fixture-seed/t22-origin71.json','sha256':origin_pin},'inputs_binding':{'path':retained+'/inputs.py','sha256':repo[retained+'/inputs.py']['sha256']},'data_audit_binding':{'path':retained+'/PUBLIC-SEED-DATA-AUDIT-0001.json','sha256':repo[retained+'/PUBLIC-SEED-DATA-AUDIT-0001.json']['sha256']},'classification':'SYNTHETIC-retained-native-origin-fixture-public-seed-eligible'},
        'tool_namespace_aliases':tool['tool_namespace_aliases'],
        'host_inputs':[{'path':name,**{key:row[key] for key in ('sha256','size_bytes','mode')}}
                       for name,row in sorted(host.items())],
        'native_payload':{'selection_binding':inventory['dependency_selection_binding'],'members':native},
        'fixture_seed':{'path':seed_helper.TARGET,'sha256':seed_pin,'classification':'SYNTHETIC-fixture-only; no private signing keys or policies'},
        'entrypoint':{'api_directory':API74.relative_to(ROOT).as_posix()},
        'signed_baseline_material_closure':{'actual_materials':859,'newly_included_paths':baseline_added,'all_selected_exact_bytes':True},
        'public_snapshot_rebases':rebases,
        'qualification':{'status':'UNQUALIFIED-PACKAGE-VIEW','full_API_installed':False}}
    (output/'PACKAGE-MANIFEST.json').write_bytes(encoded(manifest))
    # Snapshot changing current implementation bytes before a long archive or
    # materialization pass. Historical declared data/native payload stays pinned
    # and refuses drift; each current code/template input is independently copied.
    mutable_prefixes=('implementation/lab-runtime/local-host/t25-',
                      'implementation/lab-runtime/local-host/t21-',
                      'implementation/lab-runtime/local-host/t20-final-artifact-',
                      'implementation/lab-runtime/local-host/t03-margin-software-',
                      'implementation/lab-runtime/local-host/LOCAL-',
                      'implementation/lab-runtime/local-host/t31-',
                      'implementation/lab-runtime/local-host/t17-',
                      'implementation/lab-runtime/local-host/t18-',
                      str(API74.relative_to(ROOT)))
    for name,row in repo.items():
        source=Path(row['input_path'])
        if source.is_relative_to(output):continue
        if name.startswith(mutable_prefixes) or source.as_posix().startswith(str(FAMILY_HELPER.parent)):
            raw=source.read_bytes();need(sha(raw)==row['sha256'] and len(raw)==row['size_bytes'],'current source changed before package-input snapshot')
            sealed=output/'.sealed-inputs'/(row['sha256']+'-'+str(row['mode']))
            if not sealed.exists():
                sealed.parent.mkdir(mode=0o700,parents=True,exist_ok=True);sealed.write_bytes(raw);sealed.chmod(row['mode'])
            row['input_path']=str(sealed)
    inputs = {'schema_version':'lab-package-input-assembly/v1','repository_inputs':repo,'host_inputs':host,
              'native_payload_root':'/home/vlad_/.local/share/cyberalchemy-lab/native-install/t22-0001',
              'package_manifest_sha256':sha(encoded(manifest)),'authority_effect':'none'}
    (output/'BUILD-INPUTS.json').write_bytes(encoded(inputs))
    return manifest


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('output',type=Path)
    parser.add_argument('--api',choices=('api76',),default='api76')
    parser.add_argument('--fresh-dataset',action='store_true',help='Select the newly authored, independently pinned 3600-second local fixture')
    parser.add_argument('--dataset-contract',type=Path,help='Explicitly authored fresh dataset constructor input')
    parser.add_argument('--dataset-contract-sha256',help='Independent exact fresh contract digest')
    args = parser.parse_args()
    fresh=None
    if args.fresh_dataset:
        need(args.api=='api76','fresh dataset requires the maintained API76')
        fresh_path=FAMILY_HELPER.parent/'FRESH-DATASET-ACTUAL-INPUTS-0001.json'
        need(sha(fresh_path.read_bytes())=='ea0c47d8ad222f3e4034578e45be3b3d92052042ffef1a8620658973c7348dc7','actual fresh dataset selection changed')
        fresh=json.loads(fresh_path.read_bytes())
    if args.dataset_contract is not None or args.dataset_contract_sha256 is not None:
        need(not args.fresh_dataset and args.dataset_contract is not None and args.dataset_contract_sha256 is not None,'select exactly one complete explicit fresh contract')
        need(args.api=='api76','fresh dataset requires maintained API76')
        raw=args.dataset_contract.read_bytes();need(sha(raw)==args.dataset_contract_sha256,'independently selected dataset contract differs')
        fresh=json.loads(raw)
        need(fresh['schema_version']=='lab-fresh-qualified-dataset-inputs/v1' and fresh['authority_effect']=='none','exact fresh dataset input schema required')
    result = build(args.output,fresh)
    print(json.dumps({'status':'UNQUALIFIED-PACKAGE-VIEW','repository_members':len(result['members']),
                      'host_inputs':len(result['host_inputs']),'native_payload_files':len(result['native_payload']['members']),
                      'generated_metadata_targets':len(result['generated_metadata_paths'])},sort_keys=True))
