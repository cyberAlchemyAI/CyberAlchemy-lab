"""Trusted selected-Python child initialization, before target API imports.

The separately attested launcher executes the original immutable Python ELF
through the selected loader. sys.executable intentionally names that launcher
for further children; sys._base_executable and executable maps prove the actual
interpreter and ABI. Neither field is used to pretend the launcher is Python.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import runpy
import stat
import sys

ROOT = Path(__file__).resolve().parents[4]
PRIVATE = ROOT.parent/'.cal-runtime'
PROVIDER_NAME = 'cal_installed_runtime_selection_v1'
LAUNCHER = ROOT/'implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def pairs(rows):
        result = {}
        for key,value in rows:
            need(key not in result,'duplicate bootstrap control key')
            result[key] = value
        return result
    return json.loads(raw,object_pairs_hook=pairs,
        parse_constant=lambda _:need(False,'nonfinite bootstrap control'))


def exact(path, expected=None, *, private=False):
    path = Path(path)
    need(path.is_absolute() and '..' not in path.parts,'absolute bootstrap input required')
    handles = []
    fd = None
    try:
        parent = os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        handles.append(parent)
        for part in path.parts[1:-1]:
            parent = os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
            handles.append(parent)
        fd = os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_size<=128*1024*1024,
             'bounded bootstrap regular file required')
        if private:
            need(before.st_uid==os.getuid() and stat.S_IMODE(before.st_mode)==0o600,
                 'bootstrap private control ownership differs')
        chunks = []
        while block := os.read(fd,1024*1024):
            chunks.append(block)
        raw = b''.join(chunks)
        stamp = lambda value:(value.st_dev,value.st_ino,value.st_size,value.st_mtime_ns,value.st_ctime_ns,value.st_mode)
        need(stamp(before)==stamp(os.fstat(fd))==stamp(path.lstat()) and len(raw)==before.st_size,
             'bootstrap file changed during capture')
        need(expected is None or sha(raw)==expected,'bootstrap selected bytes differ')
        return raw
    finally:
        if fd is not None:
            os.close(fd)
        for handle in reversed(handles):
            os.close(handle)


def relative(value):
    path = Path(value)
    need(type(value) is str and value and path.as_posix()==value and not path.is_absolute()
         and '..' not in path.parts and '\\' not in value and '\0' not in value,
         'closed bootstrap repository locator required')
    return path


def load_selected_module(name, path, member):
    raw = exact(path,member['sha256'])
    need(name not in sys.modules,'ambient bootstrap module or selection already present')
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        exec(compile(raw,str(path),'exec',dont_inherit=True),module.__dict__)
    except BaseException:
        sys.modules.pop(name,None)
        raise
    return module


def mapped_native_proof(native, members):
    """Every file-backed executable map must name selected native bytes."""
    native = Path(native)
    expected_python = native/'bin/python'
    need(Path(sys._base_executable)==expected_python,'actual Python ELF path differs')
    mapped = {}
    for line in Path('/proc/self/maps').read_text().splitlines():
        fields = line.split(None,5)
        if len(fields)!=6 or 'x' not in fields[1] or not fields[5].startswith('/'):
            continue
        path = Path(fields[5])
        need(path.is_relative_to(native),'executable mapping escaped selected native installation')
        name = path.relative_to(native).as_posix()
        need(name in members,'executable map outside exact native payload')
        exact(path,members[name]['sha256'])
        mapped[name] = members[name]['sha256']
    loader = native/'lib/abi/ld-linux-x86-64.so.2'
    executable = Path(os.readlink('/proc/self/exe'))
    need(executable==loader,'process did not enter through selected bundled loader')
    need('bin/python' in mapped and 'lib/abi/ld-linux-x86-64.so.2' in mapped,
         'selected Python/loader mappings missing')
    return {'actual_python':str(expected_python),'actual_python_sha256':members['bin/python']['sha256'],
            'process_executable':str(executable),'executable_native_maps':mapped,
            'all_executable_maps_selected':True}


def initialize():
    need(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,
         'selected isolated no-site no-bytecode startup required')
    launcher = parse(exact(PRIVATE/'launcher.json',private=True))
    need(type(launcher) is dict and set(launcher)=={'schema_version','installation_receipt_sha256'}
         and launcher['schema_version']=='lab-installed-launcher-selection/v1',
         'closed installed launcher selection required')
    receipt_raw = exact(PRIVATE/'installation.json',launcher['installation_receipt_sha256'],private=True)
    receipt = parse(receipt_raw)
    package = parse(exact(ROOT/'.cal-package-manifest.json',receipt['package_manifest_sha256']))
    need(package['schema_version']=='lab-stable-runtime-package/v1'
         and package['authority_effect']=='none','stable package bootstrap schema differs')
    by_repo = {}
    for row in package['members']:
        repository_path = row.get('repository_path',row.get('path'))
        if repository_path is not None and row.get('namespace_path') is None:
            path = relative(repository_path)
            need(str(path) not in by_repo,'duplicate stable repository member')
            by_repo[str(path)] = row
            raw = exact(ROOT/path,row['sha256'])
            need(len(raw)==row['size_bytes'] and stat.S_IMODE((ROOT/path).lstat().st_mode)==row['mode'],
                 'stable repository file size/mode differs')
        elif row.get('namespace_path') is not None:
            # These are explicit public host snapshots materialized at their
            # declared absolute locations inside the private Docker namespace.
            path = Path(row['namespace_path'])
            need(path.is_absolute() and '..' not in path.parts,'namespace snapshot locator differs')
            raw = exact(path,row['sha256'])
            need(len(raw)==row['size_bytes'],'namespace snapshot size differs')
    for row in package.get('host_inputs',[]):
        path = Path(row['path'])
        need(path.is_absolute() and '..' not in path.parts,'closed host snapshot locator required')
        raw = exact(path,row['sha256'])
        need(len(raw)==row['size_bytes'],'public host snapshot size differs')
    component = 'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/'
    provider_path = component+'installed_selection.py'
    native_path = component+'native_install.py'
    launcher_path = 'implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python'
    for path in (provider_path,native_path,launcher_path,str(Path(__file__).relative_to(ROOT))):
        need(path in by_repo,'trusted startup component missing from public package')
    provider = load_selected_module(PROVIDER_NAME,ROOT/provider_path,by_repo[provider_path])
    purpose = 'construct-context' if receipt['phase']=='construct-context' else 'runtime'
    selected = provider.activate(launcher['installation_receipt_sha256'],purpose=purpose)
    native_module = load_selected_module('_cal_trusted_installed_native',ROOT/native_path,by_repo[native_path])
    native = Path(selected.value['values']['native.root'])
    payload = package['native_payload']
    native_module.verify(native,payload['members'],payload['selection_binding']['sha256'])
    proof = mapped_native_proof(native,payload['members'])
    need(exact(LAUNCHER,by_repo[launcher_path]['sha256'])[:4]==b'\x7fELF',
         'attested selected child launcher is not the packaged ELF')
    # This is an explicit child-command contract. Actual interpreter identity
    # remains sys._base_executable + the selected executable mappings above.
    sys.executable = str(LAUNCHER)
    sys.path.insert(0,str(native/'deps'))
    sys.path.insert(0,str(ROOT))
    import importlib.metadata
    import platform
    environment = {'python':platform.python_version(),
                   'jsonschema':importlib.metadata.version('jsonschema'),
                   'cryptography':importlib.metadata.version('cryptography')}
    need(environment=={'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5'},
         'selected installed dependency versions differ')
    proof['environment'] = environment
    proof['selected_child_launcher'] = str(LAUNCHER)
    proof['selected_child_launcher_sha256'] = by_repo[launcher_path]['sha256']
    proof['phase'] = selected.phase
    # Snapshot bytes are immutable; the callable inspects mappings again after
    # a target has imported native extension modules. Neither is a wire hook.
    provider.PROCESS_PROOF_JSON = json.dumps(proof,sort_keys=True).encode()
    def process_proof():
        current = mapped_native_proof(native,payload['members'])
        current['environment'] = dict(environment)
        current['selected_child_launcher'] = str(LAUNCHER)
        current['selected_child_launcher_sha256'] = by_repo[launcher_path]['sha256']
        current['phase'] = selected.phase
        return current
    provider.process_proof = process_proof
    return provider


def dispatch(arguments):
    args = list(arguments)
    if args and args[0]=='--':
        args.pop(0)
    need(args,'selected Python target is missing')
    if args[0]=='-c':
        need(len(args)>=2,'selected Python -c code is missing')
        sys.argv = ['-c',*args[2:]]
        namespace = {'__name__':'__main__','__package__':None,'__builtins__':__builtins__}
        exec(compile(args[1],'<string>','exec'),namespace)
    elif args[0]=='-m':
        need(len(args)>=2,'selected Python -m module is missing')
        sys.argv = [args[1],*args[2:]]
        runpy.run_module(args[1],run_name='__main__',alter_sys=True)
    else:
        need(not args[0].startswith('-'),'unsupported selected Python target option')
        target = Path(args[0]).absolute()
        exact(target)
        sys.argv = [str(target),*args[1:]]
        sys.path.insert(0,str(target.parent))
        runpy.run_path(str(target),run_name='__main__')


if __name__=='__main__':
    initialize()
    dispatch(sys.argv[1:])
