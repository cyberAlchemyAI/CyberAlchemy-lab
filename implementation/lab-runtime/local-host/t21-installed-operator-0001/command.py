"""Local operator commands over the real installed common Lab API."""
import argparse
import copy
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid

PICK=sys.modules.get('cal_installed_runtime_selection_v1')
if PICK is None:raise ValueError('Run this command with the installed selected-python launcher')
PICK.require_runtime_ready();ROOT=PICK.root()
API=ROOT/PICK.current().package['entrypoint']['api_directory']
sys.path.insert(0,str(API.parent))
M={name:importlib.import_module(API.name+'.'+name) for name in
   ('protocol','guard','fixtures','auth','service','integration_dispatch','handlers','example_fixture','metadata_fixture','artifact_model')}
P=M['protocol'];SOURCE=PICK.binding('api.source')['sha256'];PROFILE=PICK.binding('api.profile')['sha256']


def need(value,message):
    if not value:raise ValueError(message)


def load(path):
    name='_lab_operator_'+uuid.uuid4().hex
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module


def write(path,value):
    raw=value if isinstance(value,bytes) else (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    return hashlib.sha256(raw).hexdigest()


def output_root(path):
    if path is None:
        parent=Path.home()/'.local/share/cyberalchemy-lab/operator-results'
        parent.mkdir(mode=0o700,parents=True,exist_ok=True)
        path=parent/uuid.uuid4().hex
    else:path=Path(path).absolute()
    need(not path.exists() and not path.is_symlink() and path.parent.is_dir()
         and not any(p.is_symlink() for p in path.parents) and not path.is_relative_to(ROOT),
         'Choose a fresh output directory outside the installed repository')
    path.mkdir(mode=0o700)
    return path


def invoke(surface,request,schemas):
    need(type(surface) is M['integration_dispatch'].IntegrationService,'actual common dispatcher required')
    raw=P.compact(request);operation=request['operation'];row=schemas.operations[operation]
    need(schemas.valid('api-call',request) and schemas.protocol_valid(row['request_schema']['resource_uri'],request['message']),
         'operator request violates selected contract')
    reply=surface.call(raw)
    need(schemas.valid('api-reply',reply) and reply.get('request_binding',{}).get('sha256')==hashlib.sha256(raw).hexdigest()
         and reply.get('contract_profile_binding')==schemas.profile_binding,'actual reply binding or contract differs')
    uri=row['result_schema' if reply.get('kind')=='result' else 'error_schema']['resource_uri']
    if operation=='artifact.inspect' and reply.get('kind')=='result':uri='urn:cyberalchemy-lab:protocol:artifact-inspect-result:v2-candidate'
    need(schemas.protocol_valid(uri,reply['message']),'actual reply violates operation contract')
    return reply


def execute(command,artifact,output):
    M['guard'].verify(SOURCE);schemas=P.Schemas(PROFILE)
    fixture=custody=None
    if command=='workflow':
        fixture=load(ROOT/'implementation/lab-runtime/local-host/t31-public-owned-transition-0001/public_fixture.py')
        custody=load(ROOT/'implementation/lab-runtime/local-host/t17-current-common-caller-0001/retain.py')
    out=output_root(output) if command=='workflow' else None
    with P.source.replay_source(P.source.CURRENT_LEGACY_NAME) as view:
        if command=='workflow':
            with fixture.example(view,schemas,api_namespace=API.name,preserve_failed_root=True) as (host,request,witness):
                try:
                    selected=request();surface=M['integration_dispatch'].IntegrationService(host)
                    reply=invoke(surface,selected,schemas)
                    # Capture actual originals before this fixture closes, including
                    # failure/indeterminate replies. Credentials are never copied.
                    retained=custody.archive(out/'originals',host.vault.root,{
                        'api_source_sha256':SOURCE,'profile_sha256':PROFILE,
                        'original_request':selected,'actual_reply':reply,'operation':'workflow.transition'})
                    write(out/'reply.json',reply)
                    if reply.get('kind')!='result':
                        write(out/'RESULT.json',{'result':'REFUSED-OR-INDETERMINATE','actual_reply':reply,
                            'retained_originals':retained,'authority_effect':'none'})
                        raise ValueError('Workflow did not complete; actual evidence retained at '+str(out))
                    need(reply['message']['posture']=='applied','workflow result did not record an applied transition')
                    store=witness['store'];head,run_raw=store.replay();consumed=store.consume(head['sequence'])
                    records=[]
                    for i,(header,original) in enumerate(consumed,1):
                        digest=write(out/(str(i).zfill(2)+'-artifact.json'),original)
                        need(digest==header['byte_sha256'],'produced original changed during retention')
                        records.append(header)
                    need(bool(records),'workflow produced no actual typed output')
                    before={p.relative_to(host.vault.root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in host.vault.root.rglob('*') if p.is_file()}
                    retry=copy.deepcopy(selected);retry['call_id']+=':retry';again=invoke(surface,retry,schemas)
                    after={p.relative_to(host.vault.root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in host.vault.root.rglob('*') if p.is_file()}
                    need(again.get('kind')=='result' and again['message']==reply['message'] and before==after,
                         'exact workflow retry changed result or durable bytes')
                    result={'result':'applied','workflow_state':json.loads(run_raw)['state'],'typed_outputs':records,
                        'exact_retry_read_only':True,'output_directory':str(out),'work_completed':False,
                        'api_source_sha256':SOURCE,'source_cut':M['handlers'].cut(view),'authority_effect':'none'}
                    write(out/'RESULT.json',result)
                except BaseException as error:
                    try:
                        write(out/'FAILED-RETAINED.json',{'result':'FAILED-original-private-Vault-retained',
                            'fixture_root':str(host.vault.root.parent),'exception_class':type(error).__name__,'authority_effect':'none'})
                    except OSError:
                        pass
                    # Keep the actual final Vault even if envelope validation or
                    # a retry failed after an effect. Never infer its state.
                    try:
                        custody.archive(out/'failure-originals',host.vault.root,{
                            'api_source_sha256':SOURCE,'profile_sha256':PROFILE,
                            'operation':'workflow.transition','exception_class':type(error).__name__})
                    except BaseException:
                        pass
                    raise
        else:
            with tempfile.TemporaryDirectory(prefix='cal-local-operator-') as temporary:
                root=Path(temporary);root.chmod(0o700)
                materials,metadata,_=M['example_fixture'].materials_for(view)
                key,path,pin=M['metadata_fixture'].provision(root,materials,metadata,scoped=False)
                channel=M['auth'].ReaderChannel(path,pin,schemas);host=None
                try:
                    channel.authenticate(M['fixtures'].proof(key,channel.challenge));key=None
                    host=M['service'].Service(view,channel,schemas)
                    operation={'status':'lab.status','catalog':'catalog.get','inspect':'artifact.inspect'}[command]
                    fields={}
                    if command=='inspect':
                        with M['artifact_model'].model_read_batch(view):
                            rows=[row for row in view.subjects.values() if row['identity']==artifact and row['effective_state'] in ('admitted-current','local-admitted-current')]
                            need(len(rows)==1,'Choose one exact current artifact identity from this Source')
                            fields={'artifact':M['artifact_model'].artifact_ref(view,rows[0]),'include':['body','contract','authority','provenance','gaps']}
                    request=M['fixtures'].call(channel.context,operation,M['handlers'].cut(view),**fields)
                    reply=invoke(M['integration_dispatch'].IntegrationService(host),request,schemas)
                    need(reply.get('kind')=='result','Operation refused: '+str(reply.get('message',{}).get('code')))
                    result={'result':'ok','operation':operation,'data':reply['message'],
                        'declared_operation_count':len(schemas.operations),'authority_effect':'none'}
                finally:
                    if host is not None:host.close()
                    channel.close()
    M['guard'].verify(SOURCE);return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Run the installed local Lab fixture API')
    parser.add_argument('command',choices=('status','catalog','inspect','workflow'))
    parser.add_argument('--artifact',default='product:cyberalchemy-lab')
    parser.add_argument('--output',help='Fresh private directory for actual workflow results')
    args=parser.parse_args()
    print(json.dumps(execute(args.command,args.artifact,args.output),sort_keys=True,indent=2),flush=True)
