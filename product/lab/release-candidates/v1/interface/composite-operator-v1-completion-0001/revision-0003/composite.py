"""Maintained candidate full34 launcher; authority stays in real branch guards."""
import base64,copy,importlib,importlib.util,os,sys,time,uuid
from contextlib import ExitStack
from datetime import datetime,timezone
from pathlib import Path
from control import *
from framing import Reader,FrameError,dispatch,write

HERE=Path(__file__).resolve().parent
INTERFACE=HERE.parents[1]
API=INTERFACE/'api-integration-v17'
INSTALL=INTERFACE/'runtime-dependencies-v2-completion-0001/installations/0004'
DEPENDENCY_SELECTION='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
DEPENDENCY_SHA='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
ACTION=('action.evaluate','action.dispatch','action.reconcile')
GOVERNANCE=('checkpoint.resolve','admission.apply','capability.adoption.prepare')
ACTION_FILES={'source.json','source.signature','grant.json','status.json','ledger-pins.json'}

def expiry(value):return datetime.fromisoformat(value.replace('Z','+00:00')).timestamp()
def key(value):
    raw=base64.b64decode(value,validate=True);need(len(raw)==32,'Ed25519 public key required');return raw
def dependency_guard(selection):
    closed(selection,'selection installation');need(selection['selection']=={'path':DEPENDENCY_SELECTION,'sha256':DEPENDENCY_SHA} and selection['installation']==str(INSTALL),'independent stable dependency selection required')
    value=parse(public(selection['selection']))
    # Keep original proof bindings present; this installed-byte verification
    # does not replace their physical proof guard or claim original /tmp exists.
    need(len(value['original_bindings'])==5 and len(value['inputs'])==720,'full declared dependency provenance required')
    expected={r['destination']:{'sha256':r['sha256'],'size_bytes':r['size_bytes'],'mode':0o755 if r['kind'] in {'interpreter','native-executable'} else 0o644} for r in value['inputs']}
    expected.update(value['wheel_members']);expected['lib/abi/ld-linux-x86-64.so.2']['mode']=0o755
    need(len(expected)==1010,'complete installed dependency closure required')
    return installed(INSTALL,expected)

def software_guard(config):
    s=config['source'];closed(s,'directory source_sha256 profile_sha256 members_sha256 bootstrap_bindings')
    need(s['directory']==str(API),'exact maintained API17 successor required')
    need(type(s['bootstrap_bindings']) is list and s['bootstrap_bindings'],'independent executable bootstrap closure required')
    names=[r['path'] for r in s['bootstrap_bindings']];need(len(names)==len(set(names)),'duplicate bootstrap source')
    needed={str((p).relative_to(ROOT)) for p in HERE.glob('*.py')}|{str((API/n).relative_to(ROOT)) for n in ['guard.py','__init__.py','source-manifest.json','contract-profile.json','integration-members.json']}
    need(needed<=set(names),'complete maintained launcher and API bootstrap pins required')
    for row in s['bootstrap_bindings']:public(row)
    manifest=public({'path':str((API/'source-manifest.json').relative_to(ROOT)),'sha256':s['source_sha256']})
    profile=parse(public({'path':str((API/'contract-profile.json').relative_to(ROOT)),'sha256':s['profile_sha256']}))
    members=parse(public({'path':str((API/'integration-members.json').relative_to(ROOT)),'sha256':s['members_sha256']}))
    need(profile['authority_effect']=='none' and profile['actual_owner_outcome'] is None and len(profile['implemented_operations'])==34 and len(set(profile['implemented_operations']))==34 and set(ACTION+GOVERNANCE)<=set(profile['implemented_operations']),'exact full34 candidate catalog required')
    need(set(members['members'])=={'actions','governance'} and members['authority_effect']=='none','independent branch member selection required')
    for kind,ops in [('actions',ACTION),('governance',GOVERNANCE)]:
        row=members['members'][kind];closed(row,'directory operations profile_sha256 source_sha256');need(row['operations']==list(ops) and '/' not in row['directory'] and '..' not in row['directory'],'exact branch selector required')
        folder=INTERFACE/row['directory']
        public({'path':str((folder/'source-manifest.json').relative_to(ROOT)),'sha256':row['source_sha256']});public({'path':str((folder/'contract-profile.json').relative_to(ROOT)),'sha256':row['profile_sha256']})
    dependency_guard(config['dependencies']);return profile,members

def branch_inputs(branch):
    fd=directory(branch['workspace_root'],branch['root_identity']);os.close(fd)
    raw=protected(branch['policy'],branch['workspace_root'],branch['root_identity'],16384)
    files={name:protected(selector,branch['workspace_root'],branch['root_identity']) for name,selector in branch['files'].items()}
    return parse(raw),files

def config_shape(config):
    closed(config,'schema_version purpose authority_effect provisioning_binding source dependencies branches handoff transport')
    need(config['schema_version']=='lab-composite-operator-config/v2-candidate' and config['purpose']=='owned-candidate-rehearsal' and config['authority_effect']=='none','candidate-only explicit composite configuration required')
    closed(config['provisioning_binding'],'path sha256')
    closed(config['branches'],'base actions governance')
    for name,branch in config['branches'].items():
        fields='workspace_root root_identity policy public_key files'+(' source_public_key lease_ttl' if name=='actions' else ' vault' if name=='base' else '')
        closed(branch,fields);canonical(branch['workspace_root']);need(not Path(branch['workspace_root']).is_relative_to(ROOT) and Path(branch['workspace_root']).is_relative_to('/tmp'),'selected auth contract requires independent /tmp workspace')
        key(branch['public_key']);need(type(branch['files']) is dict,'exact branch input closure required')
        if name=='actions':need(set(branch['files'])==ACTION_FILES and type(branch['lease_ttl']) is int and 1<=branch['lease_ttl']<=900,'exact Action inputs and bounded fresh lease required');key(branch['source_public_key'])
        elif name=='base':
            need(set(branch['files'])=={'workspace/workspace.json'},'actual nested Base workspace manifest required')
            closed(branch['vault'],'root root_identity');need(branch['vault']['root']==str(Path(branch['workspace_root'])/'workspace'),'exact independently selected Base Vault root required')
            fd=directory(branch['vault']['root'],branch['vault']['root_identity']);os.close(fd)
        else:need(set(branch['files'])=={'native-store/config.json','native-store/baseline.json','native-store/HEAD.json'},'independent governance native root pins required')
        for filename,selector in branch['files'].items():need(Path(selector['path'])==Path(branch['workspace_root'])/filename,'branch input must use its exact owned locator')
    need(len({b['workspace_root'] for b in config['branches'].values()})==3,'independent branch workspace roots required')
    closed(config['handoff'],'contract issuers startup_seconds')
    need(config['handoff']['contract']=='fresh-session-current-source-handoff/v1-candidate' and type(config['handoff']['startup_seconds']) is int and 1<=config['handoff']['startup_seconds']<=300,'bounded same-process fresh lease handoff required')
    closed(config['handoff']['issuers'],'custody grant policy')
    for issuer in config['handoff']['issuers'].values():
        closed(issuer,'public_key authorization_binding posture');key(issuer['public_key']);need(issuer['posture']=='independently-selected-candidate-technical-issuer','genuine operational issuer authority remains unrepresented');closed(issuer['authorization_binding'],'path sha256')
    need(len({i['public_key'] for i in config['handoff']['issuers'].values()})==3,'distinct independent custody/grant/policy issuers required')
    closed(config['transport'],'max_frames max_wire_bytes max_frame_bytes max_response_bytes')
    t=config['transport'];need(all(type(v) is int for v in t.values()) and 4<=t['max_frames']<=2048 and 65536<=t['max_wire_bytes']<=64*1024*1024 and 4096<=t['max_frame_bytes']<=1048576 and 65536<=t['max_response_bytes']<=1048576,'bounded serialized transport required')

def preflight(config,independent_sha):
    need(sha(compact(config))==independent_sha,'independent exact configuration pin differs');config_shape(config)
    provisioning=parse(public(config['provisioning_binding']));need(provisioning['task_id']=='T34' and provisioning['authority_effect']=='none' and provisioning['actual_admitted_provisioning'] is False,'separately selected T34 technical provisioner receipt required')
    # Validate every private branch selection before importing/constructing an
    # API branch or producing any challenge, evidence, lock, channel or service.
    controls={}
    for name,branch in config['branches'].items():
        policy,files=branch_inputs(branch);need(policy['authority_effect']=='none' and policy['actual_owner_outcome'] is None and policy['revoked'] is False and expiry(policy['expires_at'])>time.time(),'branch policy is not a current candidate selection')
        if 'not_before' in policy:need((expiry(policy['not_before']) if type(policy['not_before']) is str else policy['not_before'])<=time.time(),'branch policy period has not started')
        actual=bytes.fromhex(policy['reader_public_key_hex']) if name=='governance' else key(policy['reader_public_key'] if name=='base' else policy['public_key'])
        need(actual==key(branch['public_key']),'independent branch public credential differs')
        need(policy['max_request_bytes']<=config['transport']['max_frame_bytes'] and policy['max_response_bytes']<=config['transport']['max_response_bytes'],'transport cannot hold exact selected branch budgets')
        if name=='base':
            vault=branch['vault'];need(policy['workspace']['root']==vault['root'] and policy['workspace']['manifest_sha256']==branch['files']['workspace/workspace.json']['sha256'],'original policy must select the exact nested Vault bytes')
            fd=directory(vault['root'],vault['root_identity']);os.close(fd)
        controls[name]=(policy,files)
    need(len({b['policy']['path'] for b in config['branches'].values()})==3,'three independent pinned policy selections required')
    action=config['branches']['actions'];source=parse(controls['actions'][1]['source.json']);grant=parse(controls['actions'][1]['grant.json']);policy=controls['actions'][0]
    need(grant['source_sha256']==action['files']['source.json']['sha256'] and grant['principal_ref']==policy['principal_ref'] and grant['scope_ref']==policy['scope_ref'] and grant['not_before']<=time.time()<grant['expires_at'],'current independent Action grant selection differs')
    profile,members=software_guard(config)
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    Ed25519PublicKey.from_public_bytes(key(action['source_public_key'])).verify(base64.b64decode(controls['actions'][1]['source.signature'],validate=True),controls['actions'][1]['source.json'])
    for issuer in config['handoff']['issuers'].values():public(issuer['authorization_binding'])
    return {'profile':profile,'members':members,'controls':controls}

def authorize_handoff(config,config_sha,lease,raw,initial):
    packet=parse(raw);closed(packet,'schema_version configuration_sha256 fresh_lease files authorizations')
    fresh={'instance':lease.instance_ref,'session':lease.session_ref}
    need(packet['schema_version']=='lab-composite-current-handoff/v1-candidate' and packet['configuration_sha256']==config_sha and packet['fresh_lease']==fresh,'handoff does not select this exact live process/lease/configuration')
    need(not lease.closed and time.time()<lease.expires,'fresh Action lease ended during handoff')
    closed(packet['authorizations'],'custody grant policy');need(set(packet['files'])==ACTION_FILES|{'operator-policy.json'},'complete exact current Action handoff required')
    body={k:v for k,v in packet.items() if k!='authorizations'}
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    for kind,issuer in config['handoff']['issuers'].items():
        closed(packet['authorizations'][kind],'signature_base64')
        public(issuer['authorization_binding'])
        signed={'schema_version':'lab-composite-current-selection-authorization/v1-candidate','selection_kind':kind,'purpose':'candidate-technical-current-selection','authority_effect':'none','issuer_authorization_binding':issuer['authorization_binding'],'handoff':body}
        Ed25519PublicKey.from_public_bytes(key(issuer['public_key'])).verify(base64.b64decode(packet['authorizations'][kind]['signature_base64'],validate=True),compact(signed))
    action=config['branches']['actions'];materials={}
    for name,selector in packet['files'].items():
        need(Path(selector['path'])==Path(action['workspace_root'])/name,'handoff may not select arbitrary private bytes')
        materials[name]=protected(selector,action['workspace_root'],action['root_identity'])
    before_policy,old_files=initial['controls']['actions'];before_source=parse(old_files['source.json']);before_status=parse(old_files['status.json']);before_grant=parse(old_files['grant.json'])
    expected=copy.deepcopy(before_source);expected['runtime_bindings']=fresh
    refs=before_source['refs'];handles={refs['agent-instance']:lease.instance_ref,refs['agent-session']:lease.session_ref}
    need(set(before_source['initial_status']['runtime_handle_bindings'])==set(handles),'exact original runtime attribution keys required')
    expected['initial_status']['runtime_handle_bindings']=handles
    need(parse(materials['source.json'])==expected,'handoff changed immutable source records/refs/scope/periods/RoleAssignments')
    expected_status=copy.deepcopy(before_status);expected_status['runtime_handle_bindings']=handles
    need(parse(materials['status.json'])==expected_status,'handoff changed current revocation/stop/approval/status attribution')
    expected_grant=copy.deepcopy(before_grant);expected_grant['source_sha256']=sha(materials['source.json'])
    need(parse(materials['grant.json'])==expected_grant,'handoff changed grant authority/scope/period/limits')
    expected_policy=copy.deepcopy(before_policy);expected_policy['source_binding']={'ref':'action-source:'+sha(materials['source.json']),'sha256':sha(materials['source.json'])};expected_policy['grant_binding']={'ref':'action-grant:'+sha(materials['grant.json']),'sha256':sha(materials['grant.json'])}
    need(parse(materials['operator-policy.json'])==expected_policy,'handoff changed policy credential/permissions/period/profile')
    Ed25519PublicKey.from_public_bytes(key(action['source_public_key'])).verify(base64.b64decode(materials['source.signature'],validate=True),materials['source.json'])
    need(time.time()<before_grant['expires_at'] and time.time()<expiry(before_policy['expires_at']) and lease.expires<=before_grant['expires_at'],'handoff renewed or exhausted original permission')
    return packet['files']

def package(path):
    name='_cal_composite_'+path.name.replace('-','_')+'_'+uuid.uuid4().hex
    spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return name

def run(config,config_sha,input_stream,output_stream):
    selected=preflight(config,config_sha);started=time.monotonic();deadline=started+config['handoff']['startup_seconds']
    reader=Reader(input_stream,max_frames=config['transport']['max_frames'],max_wire_bytes=config['transport']['max_wire_bytes'])
    t=config['transport'];owned=ExitStack();success=False
    try:
        base_name=package(API);guard=importlib.import_module(base_name+'.guard');guard.verify(config['source']['source_sha256'])
        protocol=importlib.import_module(base_name+'.protocol');schemas=protocol.Schemas(config['source']['profile_sha256'])
        action_name=package(INTERFACE/selected['members']['members']['actions']['directory']);A=importlib.import_module(action_name+'.runtime');AS=importlib.import_module(action_name+'.service')
        governance_name=package(INTERFACE/selected['members']['members']['governance']['directory']);GH=importlib.import_module(governance_name+'.host');GS=importlib.import_module(governance_name+'.service')
        grant=parse(selected['controls']['actions'][1]['grant.json']);policy=selected['controls']['actions'][0]
        ttl=min(config['branches']['actions']['lease_ttl'],int(min(grant['expires_at'],expiry(policy['expires_at']))-time.time()))
        need(ttl>=1,'current Action permission cannot support a fresh lease')
        lease=A.SessionLease(ttl=ttl);owned.callback(lease.close)
        write(output_stream,{'schema_version':'lab-composite-fresh-session-request/v1-candidate','configuration_sha256':config_sha,'fresh_lease':{'instance':lease.instance_ref,'session':lease.session_ref},'lease_expires_at':lease.expires,'startup_seconds_remaining':max(0,deadline-time.monotonic()),'authority_effect':'none','private_credentials_in_context':False},t['max_response_bytes'])
        raw=reader.receive(65536,deadline);need(raw is not None,'current per-run handoff missing');pins=authorize_handoff(config,config_sha,lease,raw,selected)
        software_guard(config);guard.verify(config['source']['source_sha256'])
        for kind in ['base','governance']:branch_inputs(config['branches'][kind])
        action=config['branches']['actions'];runtime=A.ActionRuntime(action['workspace_root'],lease,pins['source.json']['sha256'],action['source_public_key'],pins['grant.json']['sha256']);owned.callback(runtime.close)
        ac=A.ActionChannel(pins['operator-policy.json']['path'],pins['operator-policy.json']['sha256'],runtime,schemas,integration_profile_binding=schemas.profile_binding);owned.callback(ac.close)
        base=config['branches']['base'];BA=importlib.import_module(base_name+'.auth');bc=BA.ReaderChannel(base['policy']['path'],base['policy']['sha256'],schemas);owned.callback(bc.close)
        gov=config['branches']['governance'];gm=selected['members']['members']['governance'];host=GH.GovernanceHost(gov['workspace_root'],gov['policy']['sha256'],schemas,gm['source_sha256'],gm['profile_sha256'],integration_profile_binding=schemas.profile_binding);gc=GH.GovernanceChannel(host);owned.callback(gc.close)
        channels={'base':bc,'actions':ac,'governance':gc}
        write(output_stream,{'schema_version':'lab-composite-challenges/v1-candidate','challenges':{kind:channel.challenge for kind,channel in channels.items()},'authority_effect':'none'},t['max_response_bytes'])
        # Governance authenticates last because its original auth writes owned
        # proof evidence. All missing/failed earlier proofs refuse before it.
        authenticated={}
        for kind in ['base','actions','governance']:
            raw=reader.receive(32768,deadline);need(raw is not None,'independent branch proof missing');proof=parse(raw);closed(proof,'schema_version branch proof_base64');need(proof['schema_version']=='lab-composite-branch-proof/v1-candidate' and proof['branch']==kind,'wrong independent branch proof order')
            exact=base64.b64decode(proof['proof_base64'],validate=True);need(len(exact)<=16384,'branch proof exceeds bound');authenticated[kind]=channels[kind].authenticate(exact)
        for channel in channels.values():channel.guard()
        source=importlib.import_module(base_name+'.source_bridge');view=owned.enter_context(source.replay_source(bc.policy['source_name']))
        B=importlib.import_module(base_name+'.service');bs=B.Service(view,bc,schemas);owned.callback(bs.close)
        am=selected['members']['members']['actions'];acts=AS.ActionService(runtime,ac,schemas,source_sha256=am['source_sha256'],profile_sha256=am['profile_sha256'],integration_profile_binding=schemas.profile_binding);owned.callback(acts.close)
        govs=GS.GovernanceService(host,gc);owned.callback(govs.close)
        I=importlib.import_module(base_name+'.integration_dispatch');service=I.IntegrationService(bs,action_service=acts,governance_service=govs);owned.callback(service.close)
        need(all(branch.schemas is schemas for branch in service.branches),'actual full34 branches do not share exact Schemas')
        write(output_stream,{'schema_version':'lab-composite-ready/v1-candidate','composition':'Base28+Action3+Governance3','catalog_operation_count':len(schemas.profile['implemented_operations']),'contexts':authenticated,'catalog_visibility_implies_permission':False,'authority_effect':'none'},t['max_response_bytes'])
        result=dispatch(service,reader,output_stream,t['max_frame_bytes'],t['max_response_bytes']);success=True;return result
    finally:
        owned.close()
        # All callbacks were constructed/owned here. Durable branches, old
        # credentials and operator directories are retained, never deleted.
        software_guard(config)

def main():
    import argparse
    parser=argparse.ArgumentParser(description='Candidate full34 serialized composite Lab stdio operator')
    parser.add_argument('--config',required=True);parser.add_argument('--config-sha256',required=True)
    args=parser.parse_args()
    try:
        path=canonical(args.config);need(not path.is_relative_to(ROOT),'private operator config outside Git required')
        raw=capture(path,args.config_sha256,limit=1024*1024,owner=os.getuid(),mode=0o600)
        config=parse(raw);return run(config,args.config_sha256,sys.stdin.buffer,sys.stdout.buffer)
    except FrameError as error:
        write(sys.stdout.buffer,{'schema_version':'lab-composite-transport-error/v1-candidate','code':error.code,'request_byte_sha256':error.byte_sha256,'authority_effect':'none'},4096);return 2
    except Exception:
        # No exception/policy/source/body/private credential detail is emitted.
        write(sys.stdout.buffer,{'schema_version':'lab-composite-startup-error/v1-candidate','code':'startup-or-channel-refused','authority_effect':'none'},4096);return 2

if __name__=='__main__':raise SystemExit(main())
