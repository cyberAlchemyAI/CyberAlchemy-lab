"""Reversible local installation removal and exact-path native cold restore.

This observer owns no live service. It refuses active selected-native processes,
renames only an explicitly selected private installation, preserves every byte,
and restores its original path before returning (also on ordinary failures).
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import time
import uuid


def need(ok,why):
    if not ok:raise ValueError(why)


def digest(raw):return hashlib.sha256(raw).hexdigest()


def write(path,value):
    raw=(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())


def identity(path):
    s=path.lstat()
    return [s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]


def exact_file(path):
    need(not any(p.is_symlink() for p in path.parents),'linked installation ancestor')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        a=os.fstat(fd)
        need(stat.S_ISREG(a.st_mode) and a.st_uid==os.getuid() and a.st_nlink==1,'owned single-link installation file required')
        h=hashlib.sha256();size=0
        while block:=os.read(fd,1024*1024):h.update(block);size+=len(block)
        b=os.fstat(fd);attached=path.lstat()
        stamp=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mode,x.st_uid,x.st_mtime_ns,x.st_ctime_ns,x.st_nlink)
        need(stamp(a)==stamp(b)==stamp(attached) and size==a.st_size,'installation byte changed during observation')
        return {'identity':identity(path),'size_bytes':size,'sha256':h.hexdigest()}
    finally:os.close(fd)


def inventory(root):
    files={};directories={'.':identity(root)}
    for p in sorted(root.rglob('*')):
        need(not p.is_symlink(),'linked installation member')
        rel=p.relative_to(root).as_posix();s=p.lstat()
        if stat.S_ISDIR(s.st_mode):
            need(s.st_uid==os.getuid(),'installation directory is owned by another user');directories[rel]=identity(p)
        else:files[rel]=exact_file(p)
    return {'files':files,'directories':directories}


def selected(installation,pin):
    installation=Path(installation).absolute()
    need('..'not in installation.parts and installation.resolve()==installation and not installation.is_symlink(),
         'absolute unlinked installation required')
    need(installation.stat().st_uid==os.getuid() and stat.S_IMODE(installation.stat().st_mode)==0o700,
         'owned private installation root required')
    repo=installation/'runtime/repository';private=installation/'runtime/.cal-runtime'
    raw=(repo/'.cal-package-manifest.json').read_bytes()
    need(digest(raw)==pin,'independently selected public package differs')
    receipt=json.loads((private/'installation.json').read_bytes())
    need(receipt['package_manifest_sha256']==pin and receipt['phase']=='ready'
         and receipt['private_root_identity']==identity(private),'actual ready installation differs')
    native=private/'native';n=json.loads((native/'installation.json').read_bytes())
    need(n['identity']==identity(native) and n['file_count']==1010,'actual selected native installation differs')
    return installation,repo,private,native


def idle(native):
    active=[]
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():continue
        try:exe=Path(os.readlink(path/'exe'))
        except (OSError,ValueError):continue
        if exe==native or exe.is_relative_to(native):active.append(int(path.name))
    need(not active,'selected native installation is active: '+str(active))


def probe(repo,stdout,stderr):
    launcher=repo/'implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python'
    script=repo/'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/qualify_installed_api.py'
    with stdout.open('xb') as out,stderr.open('xb') as err:
        child=subprocess.run([str(launcher),'-B',str(script)],stdin=subprocess.DEVNULL,stdout=out,stderr=err,
            cwd=repo,env={'PATH':'/usr/bin:/bin','HOME':str(repo.parent/'.cal-runtime'),'LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1'},timeout=1800,check=False)
    need(child.returncode==0,'actual restored/native API readback refused; logs retained')
    lines=stdout.read_bytes().splitlines();need(bool(lines),'actual cold startup result absent')
    result=json.loads(lines[-1]);need(result['result']=='PASS-installed-cold-source-schemas-grant','actual native API readback result differs')
    return result


def run(installation,pin,output):
    original,repo,private,native=selected(installation,pin)
    output=Path(output).absolute()
    need(not output.exists() and output.parent.is_dir() and not any(p.is_symlink() for p in output.parents)
         and not output.is_relative_to(original),'fresh separate lifecycle evidence directory required')
    output.mkdir(mode=0o700)
    quarantine=original.parent/('.uninstalled-lab-'+uuid.uuid4().hex)
    need(not quarantine.exists(),'exclusive owned quarantine required')
    idle(native)
    before_probe=probe(repo,output/'before.stdout.log',output/'before.stderr.log')
    idle(native);before=inventory(original);before_raw=json.dumps(before,sort_keys=True,separators=(',',':')).encode()
    write(output/'BEFORE-INVENTORY.json',before)
    control={'schema_version':'lab-owned-installation-path-restore/v1','installation':str(original),'quarantine':str(quarantine),
        'installation_identity':identity(original),'package_manifest_sha256':pin,'before_inventory_sha256':digest(before_raw),
        'observer_sha256':digest(Path(__file__).read_bytes()),'live_Session_restored':False,'authority_effect':'none'}
    write(output/'RESTORE-CONTROL.json',control)
    moved=False;restored=False
    try:
        idle(native)
        os.rename(original,quarantine);moved=True
        need(not original.exists() and identity(quarantine)==control['installation_identity'],'actual uninstall namespace differs')
        old_launcher=repo/'implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python'
        try:subprocess.run([str(old_launcher),'-B','-c','raise SystemExit(99)'],capture_output=True,timeout=30,check=False)
        except FileNotFoundError:old_unavailable=True
        else:raise ValueError('removed installation launcher was still reachable')
        write(output/'UNINSTALLED.json',{'result':'PASS-original-path-unavailable','exact_owned_quarantine':str(quarantine),
            'whole_installation_preserved':True,'canonical_or_external_state_changed':False,'authority_effect':'none'})
    finally:
        if moved:
            need(not original.exists() and not original.is_symlink(),'refuse overwriting an unexpected restore destination')
            need(identity(quarantine)==control['installation_identity'],'owned quarantine identity changed')
            os.rename(quarantine,original);restored=True
    need(restored and not quarantine.exists(),'exact original installation path was not restored')
    selected(original,pin);after=inventory(original)
    need(after==before,'restored original file bytes/modes/identities differ')
    write(output/'AFTER-INVENTORY.json',after)
    restored_probe=probe(repo,output/'restored.stdout.log',output/'restored.stderr.log')
    need(restored_probe['source_cut']==before_probe['source_cut'] and restored_probe['source_sha256']==before_probe['source_sha256']
         and restored_probe['profile_sha256']==before_probe['profile_sha256'],'fresh restored API selects different original fixture/code')
    idle(native)
    result={'schema_version':'lab-actual-local-uninstall-restore/v1','result':'PASS-actual-uninstall-exact-original-restore',
        'package_manifest_sha256':pin,'installation_identity':identity(original),'whole_original_inventory_sha256':digest(before_raw),
        'file_count':len(before['files']),'directory_count':len(before['directories']),'original_launcher_unavailable_while_removed':old_unavailable,
        'exact_original_paths_bytes_modes_and_inodes_restored':True,'fresh_native_API_readback':restored_probe,
        'old_Source_or_Session_lease_extended':False,'live_Session_or_private_memory_restored':False,
        'idle_observation_scope':'No executable mapped under this selected native installation was observed in /proc; no global process or memory liveness claim.',
        'canonical_or_external_state_changed':False,'authority_effect':'none'}
    write(output/'RESULT.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--installation',required=True);p.add_argument('--package-sha256',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();print(json.dumps(run(a.installation,a.package_sha256,a.output),sort_keys=True),flush=True)
