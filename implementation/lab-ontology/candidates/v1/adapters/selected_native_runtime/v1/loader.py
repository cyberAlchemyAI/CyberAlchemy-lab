"""Closed selected technical runtime. It creates no actor, grant or episode."""
import ast,contextlib,hashlib,importlib,importlib.util,inspect,json,os,sys,types,uuid
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');HERE=Path(__file__).absolute().parent
CAPTURE=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-original55-execution-preparation-0002/capture.py';CAPTURE_SHA='b41f1914e0d6a9be125e228525ca92d1b28d853be79c118adffc040bcf01f0fa'
CONTROL=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/installed-proof-performance-preparation-0001/control.py';CONTROL_SHA='a212cf5352ce7994e6a041ccc69f8f5924f01b2be2e9067c066e082ee9a9a5dd'
_OWNED_MODULES={}
_AUXILIARY_MODULES={}
_AUXILIARY_DEPENDENCIES={}
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
FIELDS={'schema_version','authority_effect','own_modules','original_modules','factory_modules','source','profile','source_guard','fd_helper','production_selection','original_provenance','qualification_provenance','source_selection','actual_activation_or_results'}
def need(v,s):
    if not v:raise ValueError(s)
def sha(v):return hashlib.sha256(v).hexdigest()
def parse(raw):
    def pairs(rows):
        out={}
        for k,v in rows:need(k not in out,'duplicate selected runtime metadata key');out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'nonfinite runtime metadata'))
def encoded(v):return(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def path(row):
    need(type(row)is dict and set(row)=={'path','sha256'},'closed public runtime code binding required');p=Path(row['path']);need(type(row['path'])is str and not p.is_absolute()and p.as_posix()==row['path']and '..'not in p.parts and '\\'not in row['path'],'canonical original runtime path required');return ROOT/p
def capture_path(p,pin=None,**kwargs):
    raw=CAPTURE.read_bytes();need(sha(raw)==CAPTURE_SHA,'exact original bounded capture required');m=types.ModuleType('_maintained_native_capture');exec(compile(raw,str(CAPTURE),'exec'),m.__dict__);return m.capture_path(Path(p),pin,**kwargs)
def exact(row):return capture_path(path(row),row['sha256'])
def selected_module(name,row):
    raw=exact(row);p=path(row)
    if name in sys.modules:
        m=sys.modules[name];need(_OWNED_MODULES.get(name)is m and Path(m.__file__)==p and sys.modules.get(m.__name__)is m,'occupied foreign or unselected canonical import name refused');return m
    m=types.ModuleType(name);m.__file__=str(p);m.__package__=name.rpartition('.')[0];sys.modules[name]=m
    try:exec(compile(raw,str(p),'exec'),m.__dict__);_OWNED_MODULES[name]=m
    except BaseException:
        if sys.modules.get(name)is m:sys.modules.pop(name)
        raise
    return m
def _dependency_state(value):
    if type(value)is not types.FunctionType:return None
    return(value.__code__,value.__defaults__,value.__kwdefaults__,tuple((value.__kwdefaults__ or {}).items()),value.__globals__,value.__closure__)
def _capture_auxiliary_dependencies(module,row):
    """Finite imported globals/attribute paths declared in selected code."""
    tree=ast.parse(exact(row));imports={}
    for node in tree.body:
        if isinstance(node,ast.Import):
            for alias in node.names:
                name=alias.asname or alias.name.split('.')[0];expected=importlib.import_module(alias.name if alias.asname else alias.name.split('.')[0]);need(vars(module).get(name)is expected,'selected auxiliary import is not canonical '+name);imports[name]=expected
        elif isinstance(node,ast.ImportFrom):
            need(node.level==0 and all(alias.name!='*'for alias in node.names),'explicit auxiliary import dependency required');origin=importlib.import_module(node.module)
            for alias in node.names:
                name=alias.asname or alias.name;expected=inspect.getattr_static(origin,alias.name);need(vars(module).get(name)is expected,'selected auxiliary imported member is not canonical '+name);imports[name]=expected
    paths=set()
    for node in ast.walk(tree):
        chain=[]
        while isinstance(node,ast.Attribute):chain.append(node.attr);node=node.value
        if isinstance(node,ast.Name)and node.id in imports and chain:paths.add((node.id,*reversed(chain)))
    attributes=[]
    for chain in sorted(paths):
        value=imports[chain[0]]
        for name in chain[1:]:value=inspect.getattr_static(value,name)
        attributes.append((chain,value,_dependency_state(value)))
    # The selected Source's declared physical roots also remain provenance.
    roots=tuple((name,type(vars(module)[name]),tuple(vars(module)[name].parts))for name in ('HERE','ROOT')if name in vars(module))
    return(tuple((name,value,_dependency_state(value))for name,value in sorted(imports.items())),tuple(attributes),roots)
def _guard_auxiliary_dependencies(module,selected):
    """Check static bindings without invoking a replacement getter/callback."""
    imports,attributes,roots=selected
    def state(value,expected):
        if expected is None:return
        code,defaults,kwdefaults,kwitems,namespace,closure=expected
        need(type(value)is types.FunctionType and value.__code__ is code and value.__defaults__ is defaults and value.__kwdefaults__ is kwdefaults and value.__globals__ is namespace and value.__closure__ is closure,'selected auxiliary imported callable implementation changed')
        need(kwdefaults is None or len(kwdefaults)==len(kwitems)and all(kwdefaults.get(name)is item for name,item in kwitems),'selected auxiliary imported callable defaults changed')
    for name,expected,seal in imports:
        actual=vars(module).get(name);need(actual is expected,'selected auxiliary imported global changed '+name);state(actual,seal)
    for chain,expected,seal in attributes:
        actual=vars(module)[chain[0]]
        for name in chain[1:]:actual=inspect.getattr_static(actual,name)
        need(actual is expected,'selected auxiliary imported attribute changed '+'.'.join(chain));state(actual,seal)
    for name,kind,parts in roots:
        actual=vars(module).get(name);need(type(actual)is kind and tuple(actual.parts)==parts,'selected auxiliary physical root changed '+name)
"""This file is an authoring fragment, not a runtime import or effect port."""

SOURCE7_API='product/lab/release-candidates/v1/interface/api-integration-v17/'
CURRENT_DESCRIPTOR_FIELDS={'schema_version','authority_effect','current_edition','static_selection_binding','static_handoff_binding','static_peer_binding','composition_binding','composition_peer_binding','source','profile','source_guard','capture_result_binding','capture_acceptance_binding','actual_activation_or_results'}
PARENT3_HANDOFF={'path':'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/maintained-native57-integration-preparation-0003/HANDOFF.json','sha256':'ffc4c6d5d65c5a83e4f419958f70c4e83acb21cd5a88ef29161e50e98e9492ab'}
PARENT3_PEER={'path':'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/maintained-native57-integration-independent-review-0004/review.json','sha256':'318b7d29cbcfe2b7d841d07376dedbaa3318d5a9a0c925ac7029dab0acc0e95a'}
BASE42={'path':'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/current42-actual-legacy-proposal-0001/union42-INACTIVE.json','sha256':'33462af3e187b6cc34a25bca2bd0077999d44d51d095f68d5541c760dc3e18a2'}
GUARD7={'path':SOURCE7_API+'guard.py','sha256':'723cf85f7caa6bda81bc088358217a471ae9925d6153e4a0fd65b6e4094867b2'}
SOURCE6_PREDECESSOR={'historical_original_binding': {'path': 'product/lab/release-candidates/v1/interface/api-integration-v17/source-manifest.json', 'sha256': 'e6f154b9454d87682c31a0d3a7fd6ff6cf136f3f94a1312340465020b8b4580a'}, 'exact_retained_snapshot_binding': {'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T00/Source7-current-preimages-Root-0001/snapshots/source-manifest.json', 'sha256': 'e6f154b9454d87682c31a0d3a7fd6ff6cf136f3f94a1312340465020b8b4580a'}, 'guard_original_binding': {'path': 'product/lab/release-candidates/v1/interface/api-integration-v17/guard.py', 'sha256': '03d41dc73ea8b04cd98460cd5adb75c088029903b425fcfa4495c7709241e940'}, 'exact_retained_guard_binding': {'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T00/Source7-current-preimages-Root-0001/snapshots/guard.py', 'sha256': '03d41dc73ea8b04cd98460cd5adb75c088029903b425fcfa4495c7709241e940'}, 'snapshot_index_binding': {'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T00/Source7-current-preimages-Root-0001/snapshot-index.json', 'sha256': 'ff9d15342ebf2413803f478559b7505c7087920e3c4d2e27a33331840ca67588'}, 'old_origin_reinterpreted_as_current': False}


SOURCE7_PREDECESSOR={'historical_original_binding': {'path': 'product/lab/release-candidates/v1/interface/api-integration-v17/source-manifest.json', 'sha256': '95217baae4d7fb2c91ecab8dee5b1f680f57b0f742a175f5826112f6034b7e71'}, 'exact_retained_snapshot_binding': {'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T08/future-publication-Source8-preparation-0004/preimages/source-manifest.json', 'sha256': '95217baae4d7fb2c91ecab8dee5b1f680f57b0f742a175f5826112f6034b7e71'}, 'original_exact_capture_invocation_accepted': False, 'current_state_adoption_selection_binding': {'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/root-Source7-current-state-descriptor-selection-0001.json', 'sha256': '97241299371f255abc88b81f91ce7e2285865543b0a3f30bbe1787c5de4258db'}, 'old_origin_reinterpreted_as_current': False}
T08_PORT = {'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T08/future-publication-Source8-preparation-0004/private_content.py', 'sha256': 'e751847f53ea257b5ce7ba2fb7d4c9b5e9fd29d4f978281b69c5f21879d6f3ac'}
T08_PEER={'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T08/current-standing-host-integration-independent-review-0001/review.json', 'sha256': '51d533a9b50895a00f20f78f9d9145cfde8b1255301dd720d343f65de519bc66'}
SOURCE8_API_POSTIMAGES = {'product/lab/release-candidates/v1/interface/api-integration-v17/completion_bridges.py': {'path': 'product/lab/release-candidates/v1/interface/api-integration-v17/completion_bridges.py', 'sha256': 'e05c93c3323de037a7a34d6be63a3c2ebd09e39d0f209924e67b3ce7caf641c9'}, 'product/lab/release-candidates/v1/interface/api-integration-v17/protected_bridge.py': {'path': 'product/lab/release-candidates/v1/interface/api-integration-v17/protected_bridge.py', 'sha256': 'd4c69fbbdc3dac2325adf76bcf54b98c23f6434370a4b1decc58fce65ce60634'}, 'product/lab/release-candidates/v1/interface/api-integration-v17/host-bridge.schema.json': {'path': 'product/lab/release-candidates/v1/interface/api-integration-v17/host-bridge.schema.json', 'sha256': '7c3f5cf0d075ddab840aca6e397c4ccfb2f840db8d6b36cd17d4751005f8edb9'}, 'product/lab/release-candidates/v1/interface/api-integration-v17/current_legacy_context_sessions.py': {'path': 'product/lab/release-candidates/v1/interface/api-integration-v17/current_legacy_context_sessions.py', 'sha256': '9ed3652f81ba5b8e6654cee3258996d59fa89b81243c9a8f246b9d7649e2001f'}, 'product/lab/release-candidates/v1/interface/api-integration-v17/auth.py': {'path': 'product/lab/release-candidates/v1/interface/api-integration-v17/auth.py', 'sha256': 'f667de38d845b59de41679d7cdad4f632ff4b60bc98d419557fb4091d0693bef'}, 'product/lab/release-candidates/v1/interface/api-integration-v17/service.py': {'path': 'product/lab/release-candidates/v1/interface/api-integration-v17/service.py', 'sha256': '6c6cd97c1735e162758bb9c6d2df745db782ac4b3dd051d95192acfc569f0e60'}, 'product/lab/release-candidates/v1/interface/api-integration-v17/authentication.schema.json': {'path': 'product/lab/release-candidates/v1/interface/api-integration-v17/authentication.schema.json', 'sha256': '6d2295da0df45019f0cd4573da5bcb300d27aef58fa665bff5c1dc7d54bef540'}}

MAPPING_PIN_REPAIR = {'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T08/future-publication-Source8-preparation-0004/MAPPING-PIN-REPAIR.json', 'sha256': '04c1c954f22e2396a828eeac4c945f87fbf29ac74fdb23f590655ee55eb16a34'}
SOURCE8_CURRENT_CONTEXT='product/lab/release-candidates/v1/interface/api-integration-v17/current_legacy_context_sessions.py'

def _review(value,schema,*,candidate=None):
    need(type(value)is dict and value.get('schema_version')==schema and value.get('result')=='PASS'and value.get('authority_effect')=='none'and value.get('findings')==[],'complete exact independent inactive/current review required')
    if candidate is not None:need(value.get('candidate_handoff_binding')==candidate,'independent current runtime review candidate differs')

def _current_descriptor(runtime):
    """Strict data joins; genuine Source/329/FD/current permission remain separate."""
    need(exact(runtime.static_binding)==runtime.static_raw and parse(runtime.static_raw)==runtime.static_value and encoded(runtime.static_value)==runtime.static_seal,'captured static runtime selection changed')
    need(exact(runtime.binding)==runtime.raw,'independently selected current runtime descriptor changed')
    current=parse(runtime.raw);need(type(current)is dict and set(current)==CURRENT_DESCRIPTOR_FIELDS and current['schema_version']=='lab-maintained-native-current-descriptor/v2-candidate'and current['authority_effect']=='none'and current['current_edition']=='Source8'and current['actual_activation_or_results']is None,'closed separately selected Source6 descriptor required; no ambient/historical capability')
    need(current['static_selection_binding']==runtime.static_binding,'current descriptor must name exact separately captured static edition')
    need(current['source']['path']==SOURCE7_API+'source-manifest.json'and current['profile']['path']==SOURCE7_API+'contract-profile.json'and current['source_guard']==GUARD7,'exact canonical current Source/profile and known reviewed guard required')
    static_review=parse(exact(current['static_peer_binding']));_review(static_review,'lab-maintained-native-current-runtime-independent-review/v1-candidate',candidate=current['static_handoff_binding'])
    need(static_review.get('future_static_selection_binding')==runtime.static_binding and static_review.get('complete_current_descriptor_extension_reviewed')is True,'complete reviewed future static selection/current-descriptor gate required')
    handoff=parse(exact(current['static_handoff_binding']));need(handoff.get('authority_effect')=='none'and handoff.get('future_static_selection_binding')==runtime.static_binding,'static runtime handoff selection differs')
    composition=parse(exact(current['composition_binding']));composition_review=parse(exact(current['composition_peer_binding']))
    _review(composition_review,'lab-maintained-native-Source8-composition-independent-review/v1-candidate')
    need(composition_review.get('composition_binding')==current['composition_binding']and composition_review.get('complete_original42_components31_held11')is True,'complete final56 composition independent review required')
    need(composition.get('schema_version')=='lab-maintained-native-Source8-composition/v1-candidate'and composition.get('authority_effect')=='none'and composition.get('base42_union_binding')==BASE42,'exact reviewed final56 composition required')
    base=parse(exact(BASE42));targets=composition.get('all56_target_rows');need(type(targets)is list and len(targets)==56 and targets[:42]==base['rows'],'all original42 rows must remain literal')
    expected={r['target']:r for r in targets};need(len(expected)==56,'unique exact56 targets required')
    maintained={str((HERE/leaf).relative_to(ROOT))for leaf in('__init__.py','loader.py','context.py','lifecycle.py','withdrawal.py','mapping.py','cold.py','selection.json')}
    consumer={'product/lab/release-candidates/v1/interface/native-maintained-adoption-v1-completion-0001/'+leaf for leaf in('__init__.py','origins.py','software.py','gateway.py','adoption.py','bootstrap.py')}
    need(set(expected)=={r['target']for r in base['rows']}|maintained|consumer,'current56 target paths differ')
    source=parse(exact(current['source']));need(type(source)is dict and source.get('schema_version')=='lab-runtime-execution-source/v2-candidate'and source.get('authority_effect')=='none'and source.get('actual_owner_outcome')is None,'actual current execution Source with unchanged authority ceiling required')
    source_rows=source.get('files');need(type(source_rows)is list,'current complete Source file closure required');files={r['path']:r for r in source_rows};need(len(files)==len(source_rows),'ambiguous current Source file rows')
    need(files.get(current['profile']['path'])==current['profile']and files.get(GUARD7['path'])==GUARD7,'current profile/guard must belong to actual Source')
    overrides=composition.get('current_target_overrides');need(type(overrides)is list and len(overrides)==9,'exact nine separately reviewed current target replacements required')
    replacements={r['target']:r for r in overrides};need(len(replacements)==9 and set(replacements)==set(SOURCE8_API_POSTIMAGES)|{str((HERE/n).relative_to(ROOT))for n in('loader.py','selection.json')},'no implicit final56 target expansion')
    supplemental=composition.get('supplemental_current_target_rows');auth_name=SOURCE7_API+'auth.py'
    held7=parse(exact(SOURCE7_PREDECESSOR['exact_retained_snapshot_binding']));held_files=held7.get('files');need(type(held_files)is list and len(held_files)==30083,'complete exact Source7 metadata required for supplemental auth preimage');auth_rows=[r for r in held_files if r['path']==auth_name];need(len(auth_rows)==1 and auth_rows[0]['sha256']=='83ce93f76a77a51fb1b5b786c589bc58e2b5c7ccd0f42ee193bc595aa3b804e2','independent Source7 auth preimage required');auth_before=auth_rows[0]
    need(auth_name not in expected and supplemental==[replacements[auth_name]]and composition.get('full_current_target_count')==57,'original56 unchanged plus exactly one supplemental current auth target required')
    desired=dict(SOURCE8_API_POSTIMAGES);desired[str((HERE/'loader.py').relative_to(ROOT))]=runtime.static_value['own_modules']['loader.py'];desired[str((HERE/'selection.json').relative_to(ROOT))]=runtime.static_binding
    for name,row in replacements.items():
        need(set(row)=={'target','preimage_binding','held_preimage_binding','postimage_source_binding','postimage_binding','publication'}and row['publication']=='EXACT-PREIMAGE-REPLACE'and row['preimage_binding']==(expected[name]['postimage_binding']if name in expected else auth_before)and row['postimage_binding']==desired[name]and row['held_preimage_binding']['sha256']==row['preimage_binding']['sha256']and row['held_preimage_binding']['path']!=name and row['postimage_source_binding']['sha256']==desired[name]['sha256']and row['postimage_source_binding']['path']!=name,'exact Source7-to-Source8 target correspondence required')
        exact(row['held_preimage_binding']);exact(row['postimage_source_binding'])
    need(composition.get('T08_standalone_dependency')==T08_PORT and composition.get('T08_external_implementation_peer_binding')==T08_PEER and files.get(T08_PORT['path'])==T08_PORT,'exact separately selected T08 port and complete external implementation peer required');exact(T08_PORT)
    t08_review=parse(exact(T08_PEER));need(t08_review.get('result')=='PASS'and t08_review.get('findings')==[]and t08_review.get('authority_effect')=='none'and t08_review.get('complete_four_target_standing_host_implementation_reviewed')is True,'whole T08 implementation peer required')
    need(composition_review.get('complete_nine_current_overrides_supplemental_auth_and_standalone_port_reviewed')is True,'full original ancestry and current replacement/port review required')
    repair_row=composition.get('api_mapping_pin_repair_binding');need(repair_row==MAPPING_PIN_REPAIR and files.get(repair_row['path'])==repair_row,'exact independently reviewed family package-pin repair required');repair=parse(exact(repair_row));need(repair.get('target_disposition')==replacements[SOURCE8_CURRENT_CONTEXT]and repair.get('independent_package_pin')=='2733616fd011be8b62146f8d64f9718afaf9bde9749117a22a8ef15aea1ebe7c'and repair.get('retained_mapper_source_pin')=='497b71b66621cb30176df7edc6c5765be1f6cf4e9d8034965838a6dcc3036434','separate package/source identities required')
    for row in targets:
        post=replacements.get(row['target'],row).get('postimage_binding');need(type(post)is dict and set(post)=={'path','sha256'}and post['path']==row['target']and files.get(row['target'])==post,'every exact56 current postimage must belong to actual current Source')
    need(files.get(auth_name)==replacements[auth_name]['postimage_binding'],'supplemental auth actual current Source member required')
    need(files.get(runtime.static_binding['path'])==runtime.static_binding,'exact reviewed static selection absent from actual Source')
    for row in runtime.static_value['own_modules'].values():need(files.get(row['path'])==row,'each actual maintained code body must belong to actual Source')
    need(runtime.binding['path']not in files,'postcapture current descriptor cannot be an input of its own Source')
    capture=parse(exact(current['capture_result_binding']));need(capture.get('result')=='PASS-focused-Source8-capture'and capture.get('authority_effect')=='none'and capture.get('source_binding')==current['source']and capture.get('changed_metadata')==['SCHEMA-EXECUTION-DEPENDENCIES.json','contract-profile.json','INPUT-ACCOUNTING.json','source-manifest.json']and capture.get('failure')is None and capture.get('exit_errors')==[]and capture.get('runtime_qualified')is False,'actual complete four-output Source6 capture result required')
    acceptance=parse(exact(current['capture_acceptance_binding']));_review(acceptance,'lab-T00-current56-Source8-capture-acceptance/v1-candidate')
    joins={'source_binding':'source','profile_binding':'profile','guard_binding':'source_guard','capture_result_binding':'capture_result_binding','composition_binding':'composition_binding','composition_peer_binding':'composition_peer_binding','static_selection_binding':'static_selection_binding'}
    need(all(acceptance.get(k)==current[v]for k,v in joins.items())and acceptance.get('full_actual_Source_guard_verified')is True,'independent actual capture/current Source/profile/guard/composition acceptance differs')
    for key in('capture_result_binding','capture_acceptance_binding'):
        need(current[key]['path']not in files,'postcapture outcome cannot be a static Source dependency')
    predecessor=source.get('capture6_predecessor_source');need(type(predecessor)is dict and predecessor.get('historical_original_binding')==runtime.static_value['source_selection']['immutable_actual57']['source']and predecessor.get('old_origin_reinterpreted_as_current')is False,'actual Source52 ancestry/held preimage distinction required')
    held=predecessor.get('exact_retained_snapshot_binding');need(type(held)is dict and held.get('sha256')==predecessor['historical_original_binding']['sha256']and held.get('path')!=predecessor['historical_original_binding']['path'],'independent exact retained old Source bytes required');exact(held)
    need(source.get('capture7_predecessor_source')==SOURCE6_PREDECESSOR,'exact distinct captured Source6 predecessor required; no epoch relabel')
    for key in('exact_retained_snapshot_binding','exact_retained_guard_binding','snapshot_index_binding'):exact(SOURCE6_PREDECESSOR[key])
    need(source.get('capture8_predecessor_source')==SOURCE7_PREDECESSOR,'exact Source7 predecessor and permanently nonconforming original invocation required');exact(SOURCE7_PREDECESSOR['exact_retained_snapshot_binding']);exact(SOURCE7_PREDECESSOR['current_state_adoption_selection_binding'])
    value=parse(runtime.static_raw)
    for name in('source','profile','source_guard'):value[name]=current[name]
    need(runtime.value==value and encoded(runtime.value)==runtime.seal,'current runtime view cannot mutate static ancestry or current binding')
    exact(current['profile']);return current

class RuntimeSelection:
    def __init__(self,selection_binding,*,current_descriptor_binding,independent_current_descriptor_sha256):
        need(Path(sys.executable)==INSTALL/'bin/python'and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,'exact selected0004 isolated -I -B -S runtime required')
        need(path(selection_binding)==HERE/'selection.json','true separately selected static runtime selection required')
        need(current_descriptor_binding['sha256']==independent_current_descriptor_sha256 and current_descriptor_binding!=selection_binding,'separately and independently pinned current descriptor required')
        self.static_binding=dict(selection_binding);self.static_raw=exact(self.static_binding);self.static_value=parse(self.static_raw)
        need(type(self.static_value)is dict and set(self.static_value)==FIELDS and self.static_value['schema_version']=='lab-maintained-native57-static/v6-candidate'and self.static_value['authority_effect']=='none'and self.static_value['actual_activation_or_results']is None,'closed static maintained4 code/provenance selection required')
        self.static_seal=encoded(self.static_value);self.binding=dict(current_descriptor_binding);self.raw=exact(self.binding);current=parse(self.raw)
        self.value=parse(self.static_raw)
        for name in('source','profile','source_guard'):self.value[name]=current[name]
        self.seal=encoded(self.value);self.code_guard()
        self.source_guard=selected_module('_maintained_native_Source_'+uuid.uuid4().hex,self.value['source_guard']);self.fd_helper=selected_module('_maintained_native_FD_'+uuid.uuid4().hex,self.value['fd_helper'])
        _AUXILIARY_MODULES[self]=((self.source_guard,self.source_guard.__name__,dict(self.value['source_guard'])),(self.fd_helper,self.fd_helper.__name__,dict(self.value['fd_helper'])))
        _AUXILIARY_DEPENDENCIES[self]=tuple(_capture_auxiliary_dependencies(module,row)for module,name,row in _AUXILIARY_MODULES[self])
        self.auxiliary_guard(kind=None)
    def code_guard(self):
        _current_descriptor(self)
        need(set(self.value['own_modules'])=={'__init__.py','loader.py','context.py','lifecycle.py','withdrawal.py','mapping.py','cold.py'}and set(self.value['original_modules'])=={'represented_subjects','translation','native_store','source'},'complete exact maintained successor/original import closure required')
        for name,row in self.value['own_modules'].items():need(path(row)==HERE/name,'true maintained successor member origin required');exact(row)
        for group in('original_modules','factory_modules','qualification_provenance'):
            for row in self.value[group].values():exact(row)
        for name in('source','profile','source_guard','fd_helper','production_selection'):exact(self.value[name])
        source=self.static_value['source_selection'];need(type(source)is dict and set(source)=={'immutable_actual57','current_edition','future_Source8','separate_reviewed_Source8_rebind_and_fresh_qualification_required','accepted_maintained3_handoff_binding','accepted_maintained3_peer_binding','external_current_descriptor_required'}and source['current_edition']=='Source8-separate-current-descriptor-required'and source['future_Source8']is None and source['separate_reviewed_Source8_rebind_and_fresh_qualification_required']is True and source['external_current_descriptor_required']is True,'explicit static ancestry and separately selected current Source6 required')
        historical=source['immutable_actual57'];need(type(historical)is dict and set(historical)=={'source','profile','guard'}and historical=={k:self.static_value[v]for k,v in{'source':'source','profile':'profile','guard':'source_guard'}.items()},'static Source52 ancestry cannot become current capability')
        need([historical[k]['sha256']for k in('source','profile','guard')]==['9b609db3f4d681eb712a4d3e87925e6d5105668e08aa1cc70521f911ae8a813d','1506f79ba26686494af1fba4992206cc8ec224c44defac15b68766f9e0979c50','03d41dc73ea8b04cd98460cd5adb75c088029903b425fcfa4495c7709241e940'],'immutable actual57 Source52 provenance required')
        need(source['accepted_maintained3_handoff_binding']==PARENT3_HANDOFF and source['accepted_maintained3_peer_binding']==PARENT3_PEER,'exact accepted maintained3 ancestor required');exact(PARENT3_HANDOFF);ancestor=parse(exact(PARENT3_PEER))
        need(ancestor.get('schema_version')=='lab-maintained8-complete-independent-review/v1-candidate'and ancestor.get('authority_effect')=='none'and ancestor.get('result')=='PASS-complete-inactive-selected-auxiliary-dependency-repair'and ancestor.get('findings')==[]and ancestor.get('candidate_handoff')==PARENT3_HANDOFF and ancestor.get('actual_activation_Source6_or_integration_qualified')is False,'complete maintained3 predecessor peer required')
        self.qualification_guard()
    def qualification_guard(self):
        q=self.value['qualification_provenance'];need(set(q)=={'native57_handoff','native57_peer','native57_manifest_metadata_only','actual_tool_terminal','public_archive_manifest','original_batch_result','original_attempts','original_result_index','archived_aggregate','original_cases'},'closed native57 qualification metadata ancestry required');peer=parse(exact(q['native57_peer']));terminal=parse(exact(q['actual_tool_terminal']));result=parse(exact(q['original_batch_result']));attempts=parse(exact(q['original_attempts']));index=parse(exact(q['original_result_index']));aggregate=parse(exact(q['archived_aggregate']));archive=parse(exact(q['public_archive_manifest']));cases=parse(exact(q['original_cases']))['cases'];ids=[v['id']for v in cases]
        need(peer['result'].startswith('PASS')and peer['authority_effect']=='none'and not peer['findings']and peer['candidate']['HANDOFF.json']==q['native57_handoff'],'exact complete native57 nonauthor peer required');need(terminal['authority_effect']=='none'and terminal['actual_tool_result']['exit_code']==0 and result['authority_effect']=='none'and result['result']=='PASS-complete-original55'and result['original55_tests_and2_episodes']is True,'actual Root native57 exit0/result ancestry required');need(len(cases)==57 and len(set(ids))==57 and attempts['required_cases']==57 and attempts['all_tests_complete']is True and [v['case']for v in attempts['attempts']]==ids and all(v['result']=='PASS'for v in attempts['attempts']),'all original57 actual attempts required');need([v['case']for v in index['results']]==ids and len(index['results'])==57,'all exact original57 result/selection index rows required');need(aggregate['result']=='PASS-complete-original26plus29-and-two-maintained-episodes'and aggregate['candidate_handoff_binding']==q['native57_handoff']and(aggregate['original_lifecycle_tests'],aggregate['original_withdrawal_tests'],aggregate['original_maintained_episodes'],aggregate['actual_testsRun'],aggregate['skips'])==(26,29,2,55,0)and aggregate['Source_guard_and_strict_operational_FD_each_case']is True,'whole genuine native57 cohort required');need(aggregate['all57_independent_cases']=={v['case']:{k:v[k]for k in('result_binding','selection_binding')}for v in index['results']},'actual aggregate/index full57 join differs');need(len(archive['files'])==690 and archive['archive_paths_are_identity_aliases']is False and archive['original_physical_origins_retained']is True and archive['private_Source_archive_bodies_or_keys_copied']is False,'original public690 archive metadata boundary required');matches=[v for v in archive['files']if v['original_binding']==result['aggregate_binding']];need(len(matches)==1 and matches[0]['archive_binding']==q['archived_aggregate']and matches[0]['archive_is_original_identity']is False and q['archived_aggregate']['sha256']==result['aggregate_binding']['sha256'],'retained original and separately selected archive content are not physical identity aliases')
        terminal_rows=[parse(line)for line in terminal['actual_tool_result']['output'].splitlines()if line.strip()];need(any(v.get('root_result_binding')==q['original_batch_result']and v.get('result')=='PASS-complete-original55'for v in terminal_rows),'actual Root terminal must independently join exact public batch result')
        need(result['result_index_binding']==q['original_result_index'],'actual batch result/index independent binding join differs')
        for row in index['results']:
            packet=parse(exact(row['selection_binding']));need(packet['case']['id']==row['case']and packet['api_source_binding']==self.value['source_selection']['immutable_actual57']['source']and packet['api_profile_binding']==self.value['source_selection']['immutable_actual57']['profile']and packet['factory_code_bindings']==self.value['factory_modules']and packet['ontology_execution_selection_binding']==self.value['production_selection'],'all57 immutable historical packet Source5.2/factory/runtime joins required; old grants and clocks never selected')
    def proof_guard(self):
        refs=self.value['original_provenance'];guard=parse(exact(refs['guard153']))['files'];old=parse(exact(refs['execution176']))['files'];current=parse(exact(refs['current175']));locator=parse(exact(refs['occurrence_map']));need(len(guard)==153 and len(old)==176 and len(current['files'])==175 and len(locator['occurrences'])==176,'all original153+176 occurrences required');need(locator['historical_manifest_binding']==refs['execution176']and locator['current_manifest_binding']==refs['current175']and locator['runtime_occurrences']==176 and locator['archive_captures_each_all_selected_call']==2 and locator['old_path_restored_or_alias_equivalence_claimed']is False,'original/current proof locator distinction required');need([v['historical_row']for v in locator['occurrences']]==old and [v['historical_index']for v in locator['occurrences']]==list(range(176)) and [v['current_index']for v in locator['occurrences']]==[i if i<82 else 130 if i==82 else i-1 for i in range(176)],'all176 original literal indexed declarations and exact finite current map required');missing=locator['unavailable_historical_index'];archive=locator['already_selected_archive_historical_index'];need((missing,archive)==(82,131)and locator['unavailable_historical_path']==old[82]['path'] and not os.path.lexists(locator['unavailable_historical_path']),'old missing physical locator remains absent/refused');need(current['files']==[v for i,v in enumerate(old)if i!=82]and old[82]['sha256']==old[131]['sha256']=='b126e629fc314325391dffcf3a93609196ad6218e6efaf54ff4e98ffaae0fe5a','exact original content retained at independently selected archive origin')
        def selected(row):
            p=Path(row['path']);p=p if p.is_absolute()else ROOT/p;kwargs={}
            if str(p)=='/home/vlad_/.rustup/toolchains/1.98.1-x86_64-unknown-linux-gnu/bin/cargo':
                need(row['sha256']=='da77c8b33849312255ccde3179198ada4c8deb370488d050286146b1d1b27e14'and row['size_bytes']==40680304,'sole exact original Cargo exception required');body=capture_path(CONTROL,CONTROL_SHA);m=types.ModuleType('_maintained_exact_Cargo_capture');m.__file__=str(CONTROL);exec(compile(body,str(CONTROL),'exec'),m.__dict__);raw=m.capture(p,row['sha256'],limit=40680304,size=40680304)
            else:raw=capture_path(p,row['sha256'])
            need(len(raw)==row['size_bytes'],'entire selected original proof size differs')
        for row in guard:selected(row)
        for item in locator['occurrences']:
            row=current['files'][item['current_index']];need(row==(old[131]if item['historical_index']==82 else item['historical_row']),'exact original176 indexed proof correspondence required');selected(row)
    @contextlib.contextmanager
    def selected_environment(self):
        before=sys.path[:];sys.path.insert(0,str(INSTALL/'deps'))
        try:yield
        finally:sys.path[:]=before
    def auxiliary_guard(self,*,kind=None):
        """Selected object identity and fresh complete local callable bodies.

        A filename or module label is insufficient. No alternate proof port,
        callback injection option or cached permission exists in this runtime.
        """
        need(kind in (None,'source_guard','fd_helper'),'closed auxiliary proof selection required')
        selected=_AUXILIARY_MODULES.get(self)
        need(type(selected)is tuple and len(selected)==2,'original selected auxiliary custody required')
        def shape(c):return(c.co_argcount,c.co_posonlyargcount,c.co_kwonlyargcount,c.co_nlocals,c.co_stacksize,c.co_flags,c.co_code,c.co_names,c.co_varnames,c.co_freevars,c.co_cellvars,tuple(shape(v)if isinstance(v,types.CodeType)else v for v in c.co_consts))
        dependencies=_AUXILIARY_DEPENDENCIES.get(self);need(type(dependencies)is tuple and len(dependencies)==2,'selected auxiliary dependency custody required')
        for index,(key,(module,name,row))in enumerate(zip(('source_guard','fd_helper'),selected)):
            if kind is not None and key!=kind:continue
            need(getattr(self,key)is module and type(module)is types.ModuleType and module.__name__==name and sys.modules.get(name)is module and _OWNED_MODULES.get(name)is module and Path(module.__file__)==path(row)and self.value[key]==row,'selected auxiliary module object/origin changed '+key)
            _guard_auxiliary_dependencies(module,dependencies[index])
            raw=exact(row);compiled=compile(raw,str(path(row)),'exec');tree=ast.parse(raw)
            functions={c.co_name:c for c in compiled.co_consts if isinstance(c,types.CodeType)}
            need(functions and all(isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))),'closed selected auxiliary function module required')
            need(set(functions)=={k for k,v in vars(module).items()if type(v)is types.FunctionType and v.__module__==name},'complete selected auxiliary local function set changed '+key)
            declarations={node.name:node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}
            for member,expected in functions.items():
                actual=getattr(module,member,None);node=declarations[member]
                need(not node.decorator_list and type(actual)is types.FunctionType and actual.__module__==name and actual.__globals__ is vars(module)and Path(actual.__code__.co_filename)==path(row)and shape(actual.__code__)==shape(expected)and actual.__closure__ is None,'selected auxiliary callable implementation/origin changed '+key+'.'+member)
                defaults=tuple(ast.literal_eval(value)for value in node.args.defaults)or None;kwdefaults={arg.arg:ast.literal_eval(value)for arg,value in zip(node.args.kwonlyargs,node.args.kw_defaults)if value is not None}or None
                need(actual.__defaults__==defaults and actual.__kwdefaults__==kwdefaults,'selected auxiliary callable defaults changed '+key+'.'+member)
    def fd_snapshot(self):
        self.auxiliary_guard(kind='fd_helper');return self.fd_helper.fd_snapshot()
    def full_guard(self):
        errors=[];selected=parse(self.raw)
        def Source():
            self.auxiliary_guard(kind='source_guard')
            with self.selected_environment():need(self.source_guard.verify(selected['source']['sha256']),'full current Source verification refused')
        for phase,fn in[('current-code',self.code_guard),('selected-auxiliary-modules-and-callables',lambda:self.auxiliary_guard(kind=None)),('all329-original-proof-occurrences',self.proof_guard),('full-current-Source',Source),('current-profile',lambda:exact(selected['profile']))]:
            try:fn()
            except BaseException as error:errors.append({'phase':phase,'exception_class':type(error).__name__})
        need(not errors,'independent maintained runtime proofs refused '+encoded(errors).decode())
    def prepare_original_imports(self):
        self.code_guard();saved=sys.path[:]
        try:
            sys.path.insert(0,str(INSTALL/'deps'))
            for name in('represented_subjects','translation','native_store','source'):selected_module(name,self.value['original_modules'][name])
        finally:sys.path[:]=saved
        self.code_guard()
    def own_module(self,leaf):
        need(leaf+'.py'in self.value['own_modules']and leaf not in('__init__','loader'),'explicit maintained member required');self.code_guard();module=selected_module(__package__+'.'+leaf,self.value['own_modules'][leaf+'.py']);compiled=compile(exact(self.value['own_modules'][leaf+'.py']),module.__file__,'exec')
        def shape(c):return(c.co_argcount,c.co_posonlyargcount,c.co_kwonlyargcount,c.co_nlocals,c.co_stacksize,c.co_flags,c.co_code,c.co_names,c.co_varnames,c.co_freevars,c.co_cellvars,tuple(shape(v)if isinstance(v,types.CodeType)else v for v in c.co_consts))
        def function(actual,expected):
            if hasattr(actual,'__wrapped__'):
                sample=contextlib.contextmanager(lambda:None);need(type(actual)is types.FunctionType and shape(actual.__code__)==shape(sample.__code__)and actual.__globals__ is vars(contextlib)and actual.__closure__ is not None and len(actual.__closure__)==1 and actual.__closure__[0].cell_contents is actual.__wrapped__,'exact maintained contextmanager wrapper required');actual=actual.__wrapped__
            need(type(actual)is types.FunctionType and actual.__globals__ is vars(module)and shape(actual.__code__)==shape(expected),'maintained module callback implementation changed')
        for code in compiled.co_consts:
            if not isinstance(code,types.CodeType):continue
            actual=getattr(module,code.co_name,None)
            if isinstance(actual,type):
                need(actual.__module__==module.__name__,'maintained class actual module differs')
                for method in code.co_consts:
                    if isinstance(method,types.CodeType):
                        member=actual.__dict__.get(method.co_name);function(member.fget if isinstance(member,property)else member,method)
            else:function(actual,code)
        return module
    def run_lifecycle(self,output,*,store_factory):
        self.prepare_original_imports();context=self.own_module('context');producer=self.own_module('lifecycle')
        with context.runtime_factory(store_factory,self):return producer.run(store_factory.executor.executable_path,store_factory.executor.executable_sha256,output,store_factory=store_factory)
    def run_withdrawal(self,output,*,store_factory):
        self.prepare_original_imports();context=self.own_module('context');self.own_module('mapping');producer=self.own_module('withdrawal')
        with context.runtime_factory(store_factory,self):return producer.run(store_factory.executor.executable_path,store_factory.executor.executable_sha256,output,store_factory=store_factory)
    def cold_snapshot(self,selection,*,store_factory):
        context=self.own_module('context');consumer=self.own_module('cold')
        with context.runtime_factory(store_factory,self):return consumer.snapshot(selection,store_factory=store_factory)
