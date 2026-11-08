"""Fixed fixture runner. Exact-byte loads; no actual host authority or native launch.

An externally selected manifest and Python invocation are prerequisites. This
process is a synthetic constructor oracle, not a security isolation boundary.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types


def need(ok,code):
    if not ok:raise RuntimeError(code)


def read(row,cap=64*1024*1024):
    fd=os.open(row['path'],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        before=os.fstat(fd);need(stat.S_ISREG(before.st_mode) and 0<=before.st_size<=cap,'REGULAR_BOUND')
        chunks=[];left=before.st_size
        while left:
            block=os.read(fd,min(left,1048576));need(bool(block),'SHORT_READ');chunks.append(block);left-=len(block)
        after=os.fstat(fd)
        need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'READ_DRIFT')
        value=b''.join(chunks)
        need(len(value)==row['size_bytes'] and hashlib.sha256(value).hexdigest()==row['sha256'],'INPUT_DRIFT')
        return value
    finally:os.close(fd)


def execute(selection):
    need(selection['posture']=='synthetic-only' and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,'FIXTURE_RUNTIME')
    need(sys.pycache_prefix==selection['cache']['path'],'CACHE_PREFIX')
    need(Path(selection['interpreter']['path']).resolve()==Path(sys.executable).resolve(),'INTERPRETER_IDENTITY')
    read(selection['cache']);read(selection['interpreter'])
    rows=selection['bindings'];need(len(rows)<=8192 and len({r['path'] for r in rows})==len(rows),'INPUT_INVENTORY')
    originals={r['path']:read(r) for r in rows}
    def raw(role):return originals[selection['roles'][role]]
    def package(name):
        need(name not in sys.modules,'MODULE_COLLISION');mod=types.ModuleType(name);mod.__path__=[];sys.modules[name]=mod
    def module(name,role,extra=None):
        need(name not in sys.modules,'MODULE_COLLISION');mod=types.ModuleType(name)
        mod.__file__=selection['roles'][role];mod.__package__=name.rpartition('.')[0]
        if extra:mod.__dict__.update(extra)
        sys.modules[name]=mod;exec(compile(raw(role),mod.__file__,'exec'),mod.__dict__);return mod
    package('_mapper_transport')
    module('_mapper_transport.mapper_package_ipc_model_0004','wire')
    client=module('_mapper_transport.mapper_package_client_0004','client')
    bridge=module('_mapper_transport.mapper_package_bridge_0004','bridge')
    adapter=module('_mapper_transport.adapter','adapter')
    adapter.verify_postimage(raw('preimage'),raw('builder'),expected_preimage_sha256=selection['preimage_sha256'])
    # fd is supplied only by the fixed test launcher; remap once, close the inherited alias.
    inherited=selection['inherited_fd'];need(type(inherited)is int and inherited>=3,'FD_SELECTION')
    if inherited!=3:os.dup2(inherited,3,inheritable=False);os.close(inherited)
    c=client.Client.from_fd3(attempt_id=selection['attempt_id'],selection_sha256=selection['selection_sha256'],
        begin_pins=selection['begin_pins'],peer=tuple(selection['peer']),package_path=selection['package'],timeout_seconds=60)
    bridge.install(c);need('_t35_external_runtime_capture' not in sys.modules,'BRIDGE_COLLISION')
    sys.modules['_t35_external_runtime_capture']=bridge
    package('_mapper_fixture')
    # Explicit fixture dependency, selected separately; never an original protected reader.
    module('_mapper_fixture.base','fixture_base',{'FIXTURE_CONFIG':json.loads(raw('fixture_config'))})
    # Detection in this trusted fixture process, not OS security isolation.
    def no_effect(event,args):
        if event=='open':
            mode=args[1];flags=args[2]
            need(not (isinstance(mode,str) and any(c in mode for c in 'wax+')) and not (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)),'DIRECT_WRITE_REFUSED')
        need(event not in {'os.mkdir','os.remove','os.rename','os.rmdir','os.link','os.symlink','os.chmod','os.chown','os.truncate','subprocess.Popen','os.system','os.exec','os.posix_spawn','socket.connect','socket.bind'},'DIRECT_EFFECT_REFUSED')
    sys.addaudithook(no_effect)
    build=module('_mapper_fixture.build','builder')
    try:
        build.build(selection['begin_pins']['mapper'])
        need(c.step==61 and not c.failed,'INCOMPLETE_PROTOCOL')
        for row in rows:read(row)
        allowed=set(originals)
        for mod in tuple(sys.modules.values()):
            path=getattr(mod,'__file__',None)
            if path and path.endswith(('.py','.so')):
                need(str(Path(path).resolve()) in allowed or Path(path).resolve()==Path(__file__).resolve(),'UNSELECTED_IMPORT')
        print(json.dumps({'fixture_only':True,'actions':c.step,'packets':c.packets,'wire_bytes':c.total,'native_processes':0,'protected_reads':0}),flush=True)
    finally:c.close()


if __name__=='__main__':
    try:
        path,sha,size=sys.argv[1:]
        raw=read({'path':path,'sha256':sha,'size_bytes':int(size)},1024*1024)
        execute(json.loads(raw))
    except Exception:
        print('MAPPER_FIXTURE_RUNNER_REFUSED',file=sys.stderr);sys.exit(1)
