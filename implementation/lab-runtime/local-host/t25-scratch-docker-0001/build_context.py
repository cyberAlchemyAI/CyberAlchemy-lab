"""Create an isolated Docker namespace from an exact selected public artifact.

No host snapshot is written to the WSL filesystem's absolute locations. The
snapshot tree is a Docker image layer; installation runs as a fresh private UID.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat

ROOT=Path(__file__).resolve().parents[4]
TOOLS=ROOT/'implementation/lab-runtime/local-host/t25-integrated-runtime-0004'


def need(value,message):
    if not value:raise ValueError(message)


def sha_file(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        while raw:=stream.read(1024*1024):h.update(raw)
    return h.hexdigest()


def write(path,raw,mode):
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o755)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    path.chmod(mode)


def exact_copy(source,destination,row,mode):
    source=Path(source);info=source.lstat()
    need(stat.S_ISREG(info.st_mode) and not source.is_symlink()
         and info.st_size==row['size_bytes'] and sha_file(source)==row['sha256'],
         'selected public Docker input differs')
    destination.parent.mkdir(parents=True,exist_ok=True,mode=0o755)
    with source.open('rb') as a,destination.open('xb') as b:
        shutil.copyfileobj(a,b,1024*1024);b.flush();os.fsync(b.fileno())
    destination.chmod(mode)
    need(sha_file(destination)==row['sha256'] and sha_file(source)==row['sha256'],
         'Docker input changed during exact copy')


def build(view,archive,archive_pin,package_pin,destination):
    view,archive,destination=map(lambda p:Path(p).absolute(),(view,archive,destination))
    need(not destination.exists() and not destination.is_symlink(),'fresh Docker context required')
    manifest_raw=(view/'PACKAGE-MANIFEST.json').read_bytes()
    need(hashlib.sha256(manifest_raw).hexdigest()==package_pin and sha_file(archive)==archive_pin,
         'independently selected Docker artifact differs')
    manifest=json.loads(manifest_raw);inputs=json.loads((view/'BUILD-INPUTS.json').read_bytes())
    need(inputs['package_manifest_sha256']==package_pin,'Docker input selection differs')
    need(len(manifest['host_inputs'])>=857 and len(manifest['native_payload']['members'])==1010,
         'selected namespace/native closure differs')
    destination.mkdir(mode=0o700)
    audit={'schema_version':'lab-scratch-docker-public-context/v1','package_manifest_sha256':package_pin,
        'archive_sha256':archive_pin,'namespace_snapshots':[],'tool_namespace_aliases':[],'bootstrap_native':[],'controller':[],
        'actual_Docker_boot_or_API_qualified':False,'authority_effect':'none'}
    # Public transport is already independently hash-pinned. The installer
    # validates its exact closed archive members again inside the container.
    exact_copy(archive,destination/'artifact.tar.gz',{'size_bytes':archive.stat().st_size,'sha256':archive_pin},0o444)
    rows={row['path']:row for row in manifest['members']}
    names=('install_from_archive.py','archive.py','materialize.py','native_install.py',
           'configure_installation.py','construction_runner.py')
    for name in names:
        logical='implementation/lab-runtime/local-host/t25-integrated-runtime-0004/'+name
        row=rows[logical];source=inputs['repository_inputs'][logical]['input_path']
        exact_copy(source,destination/'controller'/name,row,0o444)
        audit['controller'].append({'name':name,'sha256':row['sha256']})
    reserved=(Path('/opt/cal'),Path('/home/cal'),Path('/tmp'),Path('/proc'),Path('/dev'),Path('/sys'),Path('/etc/passwd'),Path('/etc/group'))
    for row in manifest['host_inputs']:
        path=Path(row['path'])
        need(path.is_absolute() and '..' not in path.parts
             and not any(path==base or path.is_relative_to(base) for base in reserved),
             'host snapshot collides with controlled Docker namespace')
        source=inputs['host_inputs'][str(path)]['input_path']
        exact_copy(source,destination/'namespace'/str(path).lstrip('/'),row,row['mode'])
        audit['namespace_snapshots'].append({'path':str(path),'sha256':row['sha256'],'mode':row['mode']})
    # Linux executable startup also needs the declared PT_INTERP and SONAME
    # locators. These are exact extra regular copies of selected public bytes,
    # confined to the image; no WSL system path or historical runtime is altered.
    host_rows={row['path']:row for row in manifest['host_inputs']}
    seen_aliases=set()
    for alias in manifest.get('tool_namespace_aliases',[]):
        need(type(alias) is dict and set(alias)=={'path','source_path','sha256','size_bytes','mode'},
             'closed declared tool namespace alias required')
        path=Path(alias['path'])
        need(path.is_absolute() and path.as_posix()==alias['path'] and '..' not in path.parts
             and str(path) not in seen_aliases
             and not any(path==base or path.is_relative_to(base) for base in reserved),
             'unsafe duplicate or controlled tool namespace locator')
        seen_aliases.add(str(path))
        need(alias['source_path'] in host_rows,'tool namespace target is not independently packaged')
        row=host_rows[alias['source_path']]
        need(all(alias[k]==row[k] for k in ('sha256','size_bytes','mode')),
             'tool namespace alias differs from selected canonical bytes')
        source=inputs['host_inputs'][alias['source_path']]['input_path']
        target=destination/'namespace'/str(path).lstrip('/')
        if target.exists():
            need(str(path) in host_rows and host_rows[str(path)]==row,
                 'tool namespace alias collides with another selected member')
            need(sha_file(target)==row['sha256'] and stat.S_IMODE(target.stat().st_mode)==row['mode'],
                 'existing canonical namespace member differs')
        else:exact_copy(source,target,row,row['mode'])
        audit['tool_namespace_aliases'].append(dict(alias))
    native_root=Path(inputs['native_payload_root'])
    for relative,row in manifest['native_payload']['members'].items():
        path=Path(relative);need(not path.is_absolute() and '..' not in path.parts,'closed native Docker member required')
        # This public installer bootstrap has no runtime attestation. The
        # installed private runtime gets its original modes and fresh receipt.
        mode=0o555 if row['mode']&0o111 else 0o444
        exact_copy(native_root/path,destination/'bootstrap-native'/path,row,mode)
        audit['bootstrap_native'].append({'path':relative,'sha256':row['sha256'],'bootstrap_mode':mode})
    write(destination/'identity/passwd',b'root:x:0:0:root:/root:/sbin/nologin\ncal:x:20001:20001:Lab local installer:/home/cal:/sbin/nologin\n',0o644)
    write(destination/'identity/group',b'root:x:0:\ncal:x:20001:\n',0o644)
    write(destination/'private-home/.installation-parent',b'owned empty installation parent\n',0o600)
    write(destination/'temporary/.docker-tmp',b'',0o644)
    # An operator umask must not make the root-owned public interpreter or
    # namespace inaccessible to the container's unprivileged installer.
    for tree in ('namespace','bootstrap-native','controller','identity'):
        top=destination/tree
        if top.exists():
            top.chmod(0o755)
            for folder in top.rglob('*'):
                if folder.is_dir():folder.chmod(0o755)
    entry=['/opt/cal/bootstrap-native/lib/abi/ld-linux-x86-64.so.2','--inhibit-cache',
        '--library-path','/opt/cal/bootstrap-native/lib/abi','/opt/cal/bootstrap-native/bin/python',
        '-I','-B','-S','/opt/cal/controller/install_from_archive.py','/opt/cal/artifact.tar.gz',
        archive_pin,package_pin,'/home/cal/lab']
    dockerfile='\n'.join(['FROM scratch','COPY --chown=20001:20001 namespace/ /',
        'COPY identity/passwd /etc/passwd','COPY identity/group /etc/group',
        'COPY bootstrap-native/ /opt/cal/bootstrap-native/',
        'COPY controller/ /opt/cal/controller/','COPY artifact.tar.gz /opt/cal/artifact.tar.gz',
        'COPY --chown=20001:20001 --chmod=0700 private-home/ /home/cal/',
        'COPY --chmod=1777 temporary/ /tmp/',
        'ENV HOME=/home/cal LC_ALL=C PYTHONDONTWRITEBYTECODE=1',
        'USER 20001:20001','WORKDIR /home/cal','ENTRYPOINT '+json.dumps(entry,separators=(',',':')),''])
    write(destination/'Dockerfile',dockerfile.encode(),0o644)
    write(destination/'.dockerignore',b'CONTEXT-RECEIPT.json\n',0o644)
    raw=(json.dumps(audit,sort_keys=True,indent=2)+'\n').encode()
    write(destination/'CONTEXT-RECEIPT.json',raw,0o600)
    return {'result':'PREPARED-exact-scratch-Docker-context','context':str(destination),
        'context_receipt_sha256':hashlib.sha256(raw).hexdigest(),'package_manifest_sha256':package_pin,
        'native_bootstrap_is_installed_runtime_attestation':False,'Docker_run_qualified':False,'authority_effect':'none'}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for name in ('view','archive','archive-sha256','package-sha256','destination'):parser.add_argument('--'+name,required=True)
    a=parser.parse_args();print(json.dumps(build(a.view,a.archive,a.archive_sha256,a.package_sha256,a.destination),sort_keys=True))
