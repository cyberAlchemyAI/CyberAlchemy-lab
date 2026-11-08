"""Live current-family Session selection through the inherited custody alias."""
import hashlib,importlib,importlib.metadata,importlib.util,json,platform,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
INSTALL=Path('/tmp/cal-T03-native-install-20261023/0001')
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v63-t16-abi423-alias-0001'
SOURCE='fc079aaf4390c8d523cb4036ef31421d146a663cc135694f492e02387b879edf'
PROFILE='022ede7e9c70975bc2aa33d9f99f81b3f16eb7145e6c341734fa3bd5681b2662'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(API/'source-manifest.json')!=SOURCE or sha(API/'contract-profile.json')!=PROFILE:raise ValueError('API63 source/profile differs')
sys.path.insert(0,str(INSTALL/'deps'))
if (platform.python_version(),importlib.metadata.version('jsonschema'),importlib.metadata.version('cryptography'))!=('3.14.4','4.23.0','46.0.5'):raise ValueError('selected ABI differs')
NAME='_cal_t16_api63_custody_alias_session'
spec=importlib.util.spec_from_file_location(NAME,API/'__init__.py',submodule_search_locations=[str(API)])
package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
importlib.import_module(NAME+'.guard').verify(SOURCE)
P=importlib.import_module(NAME+'.protocol');source=P.source
F=importlib.import_module(NAME+'.example_fixture')
A=importlib.import_module(NAME+'.auth')
S=importlib.import_module(NAME+'.service')
C=importlib.import_module(NAME+'.current_legacy_context_sessions')
H=importlib.import_module(NAME+'.handlers')
R=importlib.import_module(NAME+'.projection_refresh')
with source.replay_source('custody-participation') as view:
    schemas=P.Schemas(PROFILE)
    materials,metadata,_=F.materials_for(view)
    with tempfile.TemporaryDirectory(prefix='cal-T16-api63-alias-') as tmp:
        root=Path(tmp);root.chmod(0o700)
        key,policy,pin=F.provision(root,'custody-participation',materials,metadata,principal=C.R.PRINCIPAL,projection_control=R.control(view))
        channel=A.ReaderChannel(policy,pin,schemas)
        channel.authenticate(F.proof(key,channel.challenge))
        service=S.Service(view,channel,schemas)
        try:
            if type(service.sessions) is not C.ContextSessions:raise AssertionError('custody alias selected old Session runtime')
            if service.sessions.source is not view.custody_signed_sources or service.sessions.bridge.delivery_pin!=C.DELIVERY_PIN:raise AssertionError('custody alias source/Context pin differs')
            call=F.call(channel.context,'lab.status',H.cut(view))
            reply=service.call(P.compact(call))
            if reply.get('kind')!='result':raise AssertionError('custody alias status refused: '+str(reply))
            print(json.dumps({'api_source_sha256':SOURCE,'profile_sha256':PROFILE,'context_pin':C.DELIVERY_PIN,'session_runtime':'current_legacy_context_sessions','status_call':'PASS','authority_effect':'none'},sort_keys=True))
        finally:service.close()
