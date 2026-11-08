"""Build and run one exact portable artifact in an owned Docker namespace.

Successful runs remove only their unique container, image, volume and context.
Failed runs retain the actual private installation for diagnosis.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import uuid

HERE=Path(__file__).resolve().parent


def need(value,message):
    if not value:raise ValueError(message)


def write(path,value):
    raw=(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())


def command(arguments,path,*,timeout):
    with path.open('xb') as stream:
        result=subprocess.run(arguments,stdout=stream,stderr=subprocess.STDOUT,timeout=timeout,check=False)
    need(result.returncode==0,'Docker command failed; actual command log retained: '+str(path))


def execute(args):
    out=Path(args.output).absolute()
    need(not out.exists() and not out.is_symlink(),'fresh qualification output directory required')
    need(out.parent.is_dir() and not any(p.is_symlink() for p in out.parents),'existing unlinked output parent required')
    out.mkdir(mode=0o700)
    token=uuid.uuid4().hex
    image='cyberalchemy-lab-portable:qualification-'+token
    container='cal-portable-qualification-'+token
    volume='cal-portable-private-'+token
    started=time.monotonic()
    resources={'image':image,'container':container,'volume':volume,'context':str(out/'context')}
    write(out/'OWNED-RESOURCES.json',resources)
    result=None
    try:
        spec=importlib.util.spec_from_file_location('_cal_scratch_build_context',HERE/'build_context.py')
        builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
        context=builder.build(args.view,args.archive,args.archive_sha256,args.package_sha256,out/'context')
        write(out/'CONTEXT-PREPARED.json',context)
        print(json.dumps({'phase':'docker-build','image':image}),flush=True)
        command(['docker','build','--network','none','--pull=false','--tag',image,str(out/'context')],out/'docker-build.log',timeout=args.timeout)
        made=subprocess.run(['docker','volume','create','--label','cyberalchemy.lab.qualification='+token,volume],capture_output=True,check=True)
        need(made.stdout.decode().strip()==volume,'unique owned Docker volume creation differs')
        print(json.dumps({'phase':'fresh-artifact-installation','container':container}),flush=True)
        command(['docker','run','--name',container,'--network','none','--read-only','--cap-drop','ALL',
            '--security-opt','no-new-privileges:true','--pids-limit','256','--shm-size','64m',
            '--tmpfs','/tmp:rw,nosuid,nodev,size=512m,mode=1777',
            '--mount','type=volume,source='+volume+',target=/home/cal',image],out/'installation.log',timeout=args.timeout)
        lines=(out/'installation.log').read_text().splitlines()
        need(bool(lines),'actual Docker installation output missing')
        observation=json.loads(lines[-1])
        need(observation['result']=='PASS-fresh-installed-API-cold'
             and observation['archive_sha256']==args.archive_sha256
             and observation['package_manifest_sha256']==args.package_sha256,
             'actual selected artifact/API result differs')
        inspected=subprocess.run(['docker','inspect',container],capture_output=True,check=True)
        state=json.loads(inspected.stdout)[0]
        need(state['State']['ExitCode']==0 and state['Config']['User']=='20001:20001'
             and state['HostConfig']['NetworkMode']=='none' and state['HostConfig']['ReadonlyRootfs']
             and state['HostConfig']['CapDrop']==['ALL']
             and any(m['Type']=='volume' and m['Name']==volume and m['Destination']=='/home/cal' for m in state['Mounts']),
             'actual Docker isolation/owned volume differs')
        result={'schema_version':'lab-portable-scratch-docker-installation/v1','result':'PASS-actual-unprivileged-Docker-artifact-installation',
            'archive_sha256':args.archive_sha256,'package_manifest_sha256':args.package_sha256,
            'actual_installation':observation,'uid':20001,'network':'none','read_only_root':True,
            'capabilities':'ALL-dropped','no_new_privileges':True,'native_runtime_is_fresh_installation':True,
            'full_regression_qualified':False,'authority_effect':'none'}
    except BaseException as error:
        write(out/'FAILED-RETAINED.json',{'result':'FAIL-resources-retained-for-diagnosis','error':type(error).__name__,
            'message':str(error),'resources':resources,'authority_effect':'none'})
        raise
    # Cleanup follows the completed actual installation observation. Never
    # generalize these exact resource identities into a Docker prune operation.
    for name,argv in [('container',['docker','rm',container]),('volume',['docker','volume','rm',volume]),('image',['docker','image','rm',image])]:
        done=subprocess.run(argv,capture_output=True,check=False)
        need(done.returncode==0,'successful qualification cleanup failed for own '+name)
    shutil.rmtree(out/'context')
    result.update(owned_resources_removed=True,elapsed_seconds=round(time.monotonic()-started,3),
        docker_runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        context_builder_sha256=hashlib.sha256((HERE/'build_context.py').read_bytes()).hexdigest())
    write(out/'RESULT.json',result)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for name in ('view','archive','archive-sha256','package-sha256','output'):parser.add_argument('--'+name,required=True)
    parser.add_argument('--timeout',type=int,default=3600)
    arguments=parser.parse_args()
    need(60<=arguments.timeout<=14400,'bounded Docker qualification timeout required')
    print(json.dumps(execute(arguments),sort_keys=True),flush=True)
