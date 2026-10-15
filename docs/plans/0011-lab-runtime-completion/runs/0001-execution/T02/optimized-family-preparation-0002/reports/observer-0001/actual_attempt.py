"""One authorized sequential original optimized family episode; no retries."""
from datetime import datetime,timezone
import base64,fcntl,hashlib,json,os,stat,subprocess,sys,tempfile,time,traceback
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
INTERFACE=ROOT/'product/lab/release-candidates/v1/interface'
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
PREP=RUN/'T02/optimized-family-preparation-0002'
HERE=PREP/'reports/observer-0001'
INSTALL=INTERFACE/'runtime-dependencies-v2-completion-0001/installations/0004'
DEPENDENCY_SHA='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
RECIPE_SHA='54134cd404171931986b92651f534099f1652c7680b899804393b96605538eff'
OPT_SHA='295ff7139c855749a20083394ea013f3b6e7e6efd7812563e1e4daeddcf18fe9'
OPT=RUN/'T03/optimized-capture-selection-0002.json'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def need(value, reason):
    if not value:
        raise ValueError(reason)

def dependency_guard():
    selection_path = RUN / 'T07/revision-0002/dependency-selection-0002.json'
    raw = selection_path.read_bytes(); need(sha(raw) == DEPENDENCY_SHA, 'independent full dependency selection differs')
    selected = json.loads(raw)
    rows = {r['destination']: {'sha256': r['sha256'], 'size_bytes': r['size_bytes'],
                             'mode': 0o755 if r['kind'] in {'interpreter', 'native-executable'} else 0o644}
            for r in selected['inputs']}
    rows.update(selected['wheel_members']); rows['lib/abi/ld-linux-x86-64.so.2']['mode'] = 0o755
    need(len(rows) == 1010, 'full installed closure required')
    for name, row in rows.items():
        path = INSTALL / name
        need(not any(p.is_symlink() for p in (path, *path.parents)), 'unsafe selected dependency')
        before = path.lstat()
        need(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid()
             and stat.S_IMODE(before.st_mode) == row['mode'] and before.st_size == row['size_bytes'], 'selected dependency identity differs')
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        try:
            actual = os.fstat(fd); need((actual.st_dev, actual.st_ino, actual.st_mtime_ns, actual.st_ctime_ns)
                                        == (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_ctime_ns), 'dependency attachment differs')
            digest = hashlib.sha256()
            while chunk := os.read(fd, 1024 * 1024):
                digest.update(chunk)
            after = os.fstat(fd); current = path.lstat()
            fields = lambda x: (x.st_dev, x.st_ino, x.st_mode, x.st_uid, x.st_size, x.st_mtime_ns, x.st_ctime_ns)
            need(fields(before) == fields(after) == fields(current) and digest.hexdigest() == row['sha256'], 'dependency bytes changed')
        finally:
            os.close(fd)
    return {'status': 'PASS', 'installed_files': 1010, 'selection_sha256': DEPENDENCY_SHA}

def binding(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}
def save(path,value):
    with path.open('x') as stream:
        json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
def selected_guard():
    need(sha((PREP/'recipe-selection.json').read_bytes())==RECIPE_SHA,'frozen recipe selection differs')
    need(sha(OPT.read_bytes())==OPT_SHA,'frozen optimization selection differs')
    selection=json.loads((PREP/'recipe-selection.json').read_bytes())
    for row in selection['files']:
        need(binding(ROOT/row['path'])==row,'frozen recipe input differs')
    selected=json.loads(OPT.read_bytes())
    rows=[selected['helper_code_binding'],selected['helper_manifest_binding'],selected['T03_handoff_binding']]
    rows += [row[key] for row in selected['postimages'] for key in ('original_binding','postimage_binding')]
    for row in rows:need(binding(ROOT/row['path'])==row,'frozen optimization input differs')
    return {'status':'PASS','recipe_files':len(selection['files']),'selected_T03_inputs':len(rows)}
def main():
    started=time.monotonic();report={'schema_version':'lab-T02-actual-optimized-family-attempt/v1-candidate','instance':'optimized-0002','started_at':datetime.now(timezone.utc).isoformat(),'authority_effect':'none','actual_owner_outcome':None,'shared_API_qualified':False,'events':[]};lock=None;private=None;phase='runtime-lock';code=1
    def event(name,**extra):
        row={'event':name,'elapsed_seconds':time.monotonic()-started,**extra};report['events'].append(row)
        with (HERE/'events.jsonl').open('a') as stream:stream.write(json.dumps(row,sort_keys=True)+'\n');stream.flush();os.fsync(stream.fileno())
        print(json.dumps(row,sort_keys=True),flush=True)
    try:
        lock=os.open(RUN/'lease-sensitive-runtime.lock',os.O_RDWR|os.O_NOFOLLOW)
        info=os.fstat(lock);need(stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid(),'runtime lock identity differs')
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);event('runtime-lock-held-nonblocking')
        phase='dependency-entry';report['dependency_entry']=dependency_guard();event('all-1010-installed-inputs-entry-PASS')
        report['recipe_entry']=selected_guard();event('frozen-recipe-and-T03-inputs-entry-PASS')
        private=Path(tempfile.mkdtemp(prefix='cal-T02-optimized-observer-0001-'));os.chmod(private,0o700)
        save(HERE/'started.json',{'started_at':report['started_at'],'pid':os.getpid(),'recipe_sha256':RECIPE_SHA,'optimization_sha256':OPT_SHA,'private_output_bodies_exported':False})
        commands=[('stage','stage_optimized_family_v2.py',['--instance','optimized-0002','--optimization-selection',OPT.relative_to(ROOT).as_posix(),'--optimization-selection-sha256',OPT_SHA,'--recipe-selection',(PREP/'recipe-selection.json').relative_to(ROOT).as_posix(),'--recipe-selection-sha256',RECIPE_SHA])]
        commands += [(phase,'construct_optimized_v2.py',['--instance','optimized-0002','--phase',phase]) for phase in ['source','cold','reader','mapped','context']]
        commands += [('runtime-postimages','stage_runtime_optimized_v2.py',['--instance','optimized-0002'])]
        for phase,filename,args in commands:
            selected_guard();event('phase-started',phase=phase,script_binding=binding(PREP/filename),arguments=args)
            out=private/(phase+'.stdout');err=private/(phase+'.stderr')
            code_text='import sys,runpy;sys.path.insert(0,'+repr(str(INSTALL/'deps'))+');sys.argv='+repr([str(PREP/filename),*args])+';runpy.run_path('+repr(str(PREP/filename))+',run_name="__main__")'
            cmd=[str(INSTALL/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(INSTALL/'lib/abi'),str(INSTALL/'bin/python'),'-I','-X','utf8','-B','-S','-c',code_text]
            with os.fdopen(os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as stdout,os.fdopen(os.open(err,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as stderr:
                child=subprocess.Popen(cmd,stdout=stdout,stderr=stderr,env={**os.environ,'LC_ALL':'C'});event('phase-real-process-live',phase=phase,pid=child.pid)
                exitcode=child.wait()
            info={'phase':phase,'process_exit_code':exitcode,'stdout_sha256':sha(out.read_bytes()),'stderr_sha256':sha(err.read_bytes()),'private_output_bodies_exported':False}
            phase_report=PREP/'reports'/('optimized-0002-'+phase+'.json')
            if phase_report.exists():info['report_binding']=binding(phase_report);info['sanitized_phase_report']=json.loads(phase_report.read_bytes())
            if phase=='stage' and (PREP/'instances/optimized-0002/construction-selection.json').exists():info['construction_selection_binding']=binding(PREP/'instances/optimized-0002/construction-selection.json')
            if phase=='runtime-postimages' and (PREP/'instances/optimized-0002/runtime/runtime-selection.json').exists():info['runtime_selection_binding']=binding(PREP/'instances/optimized-0002/runtime/runtime-selection.json')
            if phase=='stage':
                selection=json.loads((PREP/'instances/optimized-0002/construction-selection.json').read_bytes());info['construction_prefix']=selection['prefix'];report['construction_selection_binding']=binding(PREP/'instances/optimized-0002/construction-selection.json');report['construction_prefix']=selection['prefix']
            if phase=='source' and exitcode==0:
                package=PREP/'instances/optimized-0002/source/packages/0001';archive=json.loads((package/'branch.snapshot').read_bytes());config=json.loads(base64.b64decode(archive['files']['config.json']['base64_original_bytes'],validate=True));need(config['store_id']==report['construction_prefix'],'actual signed native Store identity differs from prefix');info['actual_native_store_id']=config['store_id'];report['actual_native_store_id']=config['store_id'];report['actual_signed_archive_binding']=binding(package/'branch.snapshot');report['fixed_period_binding']=binding(package/'period.json')
            event('phase-terminal',**info);selected_guard()
            if exitcode!=0:
                report['failed_phase']=phase;report['primary_sanitized_code_frames']=info.get('sanitized_phase_report',{}).get('error');raise RuntimeError('authorized phase refused')
        report['status']='PASS-owned-family-and-runtime-postimages-only';code=0
    except BaseException as error:
        report['status']='REFUSED';report.setdefault('failed_phase',phase);report['error_class']=type(error).__name__;report['frames']=[{'file':frame.filename,'line':frame.lineno,'function':frame.name} for frame in traceback.extract_tb(error.__traceback__)]
        event('actual-attempt-refused',phase=phase,error_class=type(error).__name__)
    finally:
        try:report['dependency_exit']=dependency_guard();event('all-1010-installed-inputs-exit-PASS');report['recipe_exit']=selected_guard();event('frozen-recipe-and-T03-inputs-exit-PASS')
        except BaseException as error:report['exit_guard_error_class']=type(error).__name__;report['status']='REFUSED';code=1
        if lock is not None:os.close(lock);event('runtime-lock-released')
        if private is not None:report['private_output_root_sha256']=sha(str(private).encode());report['private_output_retained']=True
        report['finished_at']=datetime.now(timezone.utc).isoformat();report['elapsed_seconds']=time.monotonic()-started;save(HERE/'actual-attempt.json',report)
        print(json.dumps({'report_binding':binding(HERE/'actual-attempt.json'),'status':report['status'],'elapsed_seconds':report['elapsed_seconds']},sort_keys=True),flush=True)
    return code
if __name__=='__main__':raise SystemExit(main())
