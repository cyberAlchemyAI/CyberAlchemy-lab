"""Observe and kill actual Service/Vault calls, then cold retry independently.

The parent observes filesystem events; production callables and clocks remain
unchanged. A boundary missed by the observer is a failed test, never a pass.
"""
import argparse
import copy
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import select
import signal
import stat
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, value):
    raw = (json.dumps(value, sort_keys=True, indent=2)+'\n').encode()
    fd = os.open(path, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())


def modules(args):
    need(sys.flags.isolated and sys.dont_write_bytecode, 'isolated no-bytecode child required')
    sys.path.insert(0, args.deps)
    api = Path(args.api).absolute()
    need(api.parent == ROOT/'product/lab/release-candidates/v1/interface', 'selected API origin differs')
    name = '_cal_t18_actual_service'
    spec = importlib.util.spec_from_file_location(name, api/'__init__.py', submodule_search_locations=[str(api)])
    package = importlib.util.module_from_spec(spec);sys.modules[name] = package;spec.loader.exec_module(package)
    import importlib
    values = {stem:importlib.import_module(name+'.'+stem) for stem in
        ('protocol','guard','auth','fixtures','service','example_fixture','integration_dispatch','handlers','workspace')}
    manifest = values['guard'].verify(args.source_sha256)
    need(manifest['profile_binding']['sha256'] == args.profile_sha256, 'profile selector differs')
    return values


def child(args):
    m = modules(args); P,G,A,F,S,EF,I,H,W = [m[k] for k in
        ('protocol','guard','auth','fixtures','service','example_fixture','integration_dispatch','handlers','workspace')]
    root = Path(args.root)
    need(root.is_relative_to(Path('/tmp')) and stat.S_IMODE(root.stat().st_mode)==0o700,
         'explicit owned private fixture required')
    schemas = P.Schemas(args.profile_sha256)
    with P.source.replay_source(P.source.CURRENT_LEGACY_NAME) as view:
        materials, metadata, target = EF.materials_for(view)
        if args.child == 'prepare':
            # Selected maintained metadata provisioner preserves its own closed
            # schema, actual source, purpose and independent operator identity.
            import importlib
            MF = importlib.import_module(S.__package__+'.metadata_fixture')
            key, path, pin = MF.provision(root, materials, metadata, scoped=False)
            write(root.parent/'policy-binding.json', {'path':str(path),'sha256':pin})
            return
        selection = json.loads((root.parent/'policy-binding.json').read_bytes())
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        key = load_pem_private_key(W.read_private(root/'reader.pem'), password=None)
        channel = A.ReaderChannel(selection['path'], selection['sha256'], schemas)
        service = None
        try:
            channel.authenticate(F.proof(key, channel.challenge)); key = None
            service = S.Service(view, channel, schemas)
            surface = I.IntegrationService(service)
            request = EF.candidate_call(service, target, key='fixture:prepare')
            request['idempotency_key'] = request['message']['idempotency_key']
            if args.child == 'effect':
                write(root.parent/'call-ready.json', {'request_fingerprint':S.jcs.fingerprint(request,channel.context),
                    'namespace':S.jcs.namespace(request['operation'],request['idempotency_key'],channel.context),
                    'operation':request['operation']})
                # Orchestrator has already installed the OS event observer.
                reply = surface.call(P.compact(request))
                write(root.parent/'normal-return.json', {'reply':reply})
                return
            original = json.loads((root.parent/'call-ready.json').read_bytes())
            need(S.jcs.fingerprint(request,channel.context)==original['request_fingerprint'],
                 'fresh retry changes exact original control fingerprint')
            before = {p.relative_to(root).as_posix():sha(p.read_bytes()) for p in (root/'workspace').rglob('*') if p.is_file()}
            reply = surface.call(P.compact(request))
            need(schemas.valid('api-reply',reply), 'cold retry returned invalid public envelope')
            if args.stage == 'claim':
                need(reply.get('kind')=='error' and reply['message']['code']=='recovery-required',
                     'pending Service claim was redispatched or refused for wrong cause')
            else:
                need(reply.get('kind')=='result' and reply['message']['posture']=='blocked',
                     'completed exact Service result was not read back')
            after = {p.relative_to(root).as_posix():sha(p.read_bytes()) for p in (root/'workspace').rglob('*') if p.is_file()}
            need(after==before, 'cold exact retry changed owned durable bytes')
            changed = copy.deepcopy(request); changed['call_id'] += ':changed'
            changed['message']['proposal_ref'] += ':changed'
            conflict = surface.call(P.compact(changed))
            need(conflict.get('kind')=='error' and conflict['message']['code']=='idempotency-conflict',
                 'changed control inputs accepted under original key')
            final = {p.relative_to(root).as_posix():sha(p.read_bytes()) for p in (root/'workspace').rglob('*') if p.is_file()}
            need(final==before, 'changed-request refusal altered durable bytes')
            write(root.parent/'cold-result.json', {'result':'PASS','stage':args.stage,
                'same_control_fingerprint':True,'actual_retry_kind':reply['kind'],
                'actual_retry_code':reply.get('message',{}).get('code'),
                'changed_request_code':conflict['message']['code'],'durable_bytes_unchanged':True,
                'actual_common_dispatcher':True,'canonical_admissions':0,'authority_effect':'none'})
        finally:
            if service is not None:
                service.close()
            channel.close()
        G.verify(args.source_sha256)


def command(args, child_mode, root, stage):
    if args.launcher:
        prefix = [args.launcher,'-I','-B','-S']
    else:
        native = Path(args.native_root)
        prefix = [str(native/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache',
            '--library-path',str(native/'lib/abi'),str(native/'bin/python'),'-I','-B','-S']
    return [*prefix,str(Path(__file__).resolve()),'--child',child_mode,'--root',str(root),
        '--stage',stage,'--api',args.api,'--source-sha256',args.source_sha256,
        '--profile-sha256',args.profile_sha256,'--deps',args.deps]


def wait_for(process, path, timeout):
    limit = time.monotonic()+timeout
    while not path.exists():
        need(process.poll() is None, 'actual child exited before selected durable boundary')
        need(time.monotonic()<limit, 'actual child did not reach selected durable boundary')
        time.sleep(.02)


def completed(arguments,timeout):
    """Bound every owned preparation/readback process group, including errors."""
    process=subprocess.Popen(arguments,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
    try:
        out,err=process.communicate(timeout=timeout)
        return subprocess.CompletedProcess(arguments,process.returncode,out,err)
    finally:
        if process.poll() is None:
            os.killpg(process.pid,signal.SIGKILL)
            process.communicate(timeout=30)


def run(args):
    results = []
    with tempfile.TemporaryDirectory(prefix='cal-T18-service-kill-') as folder:
        control = Path(folder); control.chmod(0o700)
        sibling = control/'unrelated.bin'; sibling.write_bytes(b'unrelated-preserved\x00')
        for stage in ('claim','result'):
            case = control/stage; case.mkdir(mode=0o700)
            root = case/'fixture'; root.mkdir(mode=0o700)
            prepared = completed(command(args,'prepare',root,stage),900)
            need(prepared.returncode==0, 'actual metadata fixture preparation failed; '+prepared.stderr.decode()[-3000:])
            journal = root/'workspace/journal'
            libc = ctypes.CDLL(None,use_errno=True)
            fd = libc.inotify_init1(os.O_CLOEXEC|os.O_NONBLOCK)
            need(fd>=0 and libc.inotify_add_watch(fd,os.fsencode(journal),0x80|0x100)>=0,
                 'OS durable-write observer unavailable')
            process = None
            try:
                process = subprocess.Popen(command(args,'effect',root,stage),stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,start_new_session=True)
                wait_for(process,case/'call-ready.json',900)
                call = json.loads((case/'call-ready.json').read_bytes())
                observed = journal/(call['namespace']+'.'+stage+'.json')
                limit = time.monotonic()+900
                while not observed.exists():
                    need(process.poll() is None, 'actual Service returned before observed durable write')
                    need(time.monotonic()<limit,'Service write observer timed out')
                    if select.select([fd],[],[],.2)[0]:
                        os.read(fd,65536)
                os.killpg(process.pid,signal.SIGSTOP)
                pid,status = os.waitpid(process.pid,os.WUNTRACED)
                need(pid==process.pid and os.WIFSTOPPED(status),'actual child did not stop')
                # Verify the actual stopped state. Missed claim windows fail.
                need(observed.is_file(),'observed durable marker disappeared')
                if stage=='claim':
                    need(not (journal/(call['namespace']+'.result.json')).exists(),
                         'observer missed claim-before-result window')
                marker_digest = sha(observed.read_bytes())
                os.killpg(process.pid,signal.SIGKILL)
                out,err = process.communicate(timeout=30)
                need(process.returncode == -signal.SIGKILL,'actual child was not killed')
                cold = completed(command(args,'cold',root,stage),1200)
                need(cold.returncode==0,'actual fresh Service cold retry failed; '+cold.stderr.decode()[-4000:])
                row = json.loads((case/'cold-result.json').read_bytes())
                need(sha(observed.read_bytes())==marker_digest,'durable marker changed on cold retry')
                row.update(actual_child_exit=process.returncode,observed_marker_sha256=marker_digest,
                    child_stdout_bytes=len(out),child_stderr_bytes=len(err),
                    cold_stdout_bytes=len(cold.stdout),cold_stderr_bytes=len(cold.stderr))
                results.append(row)
            finally:
                os.close(fd)
                if process is not None and process.poll() is None:
                    os.killpg(process.pid,signal.SIGKILL);process.communicate(timeout=30)
            need(sibling.read_bytes()==b'unrelated-preserved\x00','unrelated sibling changed')
    return {'schema_version':'lab-actual-service-vault-process-kill/v1','result':'PASS',
        'api':str(Path(args.api).relative_to(ROOT)),'source_sha256':args.source_sha256,
        'profile_sha256':args.profile_sha256,'probe_sha256':sha(Path(__file__).read_bytes()),
        'cases':results,'owned_cleanup':not Path(folder).exists(),'unrelated_sibling_preserved':True,
        'production_callbacks_changed':False,'clock_changed':False,'authority_effect':'none',
        'workflow_journal_interruption_qualified':False,'whole_T18_complete':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for key in ('api','source-sha256','profile-sha256','deps'):
        parser.add_argument('--'+key,required=True)
    parser.add_argument('--native-root');parser.add_argument('--launcher')
    parser.add_argument('--child',choices=('prepare','effect','cold'))
    parser.add_argument('--root');parser.add_argument('--stage',choices=('claim','result'))
    parser.add_argument('--output')
    args=parser.parse_args()
    if args.child:
        child(args)
    else:
        need(bool(args.launcher)!=bool(args.native_root),'exactly one selected native command required')
        need(args.output and not Path(args.output).exists(),'fresh result destination required')
        result=run(args);write(Path(args.output),result)
        print(json.dumps({'result':result['result'],'cases':len(result['cases'])}))
