"""Install, restore and regress one exact artifact in an owned Docker namespace.

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


def isolated_run(name,volume,image,entrypoint,arguments):
    return ['docker','run','--name',name,'--network','none','--read-only','--cap-drop','ALL',
        '--security-opt','no-new-privileges:true','--pids-limit','256','--shm-size','64m',
        '--ulimit','nofile=65536:65536','--tmpfs','/tmp:rw,nosuid,nodev,size=512m,mode=1777',
        '--mount','type=volume,source='+volume+',target=/home/cal','--entrypoint',entrypoint,
        image,*arguments]


def inspect_isolation(name,volume):
    inspected=subprocess.run(['docker','inspect',name],capture_output=True,check=True)
    state=json.loads(inspected.stdout)[0]
    need(state['State']['ExitCode']==0 and state['Config']['User']=='20001:20001'
         and state['HostConfig']['NetworkMode']=='none' and state['HostConfig']['ReadonlyRootfs']
         and state['HostConfig']['CapDrop']==['ALL']
         and 'no-new-privileges:true' in state['HostConfig']['SecurityOpt']
         and any(r['Name']=='nofile' and r['Soft']==65536 and r['Hard']==65536 for r in state['HostConfig']['Ulimits'])
         and any(m['Type']=='volume' and m['Name']==volume and m['Destination']=='/home/cal' for m in state['Mounts']),
         'actual Docker isolation/owned volume differs: '+name)


def copy_owned(name,source,destination):
    need(not destination.exists(),'fresh Docker evidence destination required')
    copied=subprocess.run(['docker','cp',name+':'+source,str(destination)],capture_output=True,check=False)
    need(copied.returncode==0,'actual Docker evidence copy failed: '+copied.stderr.decode()[-1000:])
    need(destination.is_dir() and not destination.is_symlink(),'copied Docker evidence directory differs')
    need(not any(p.is_symlink() for p in destination.rglob('*')),'copied Docker evidence contains a link')


def execute(args):
    out=Path(args.output).absolute()
    need(not out.exists() and not out.is_symlink(),'fresh qualification output directory required')
    need(out.parent.is_dir() and not any(p.is_symlink() for p in out.parents),'existing unlinked output parent required')
    out.mkdir(mode=0o700)
    token=uuid.uuid4().hex
    image='cyberalchemy-lab-portable:qualification-'+token
    container='cal-portable-qualification-'+token
    lifecycle_container=container+'-lifecycle'
    regression_container=container+'-regression'
    volume='cal-portable-private-'+token
    started=time.monotonic()
    runner_digest=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    builder_digest=hashlib.sha256((HERE/'build_context.py').read_bytes()).hexdigest()
    resources={'image':image,'containers':[container,lifecycle_container,regression_container],
        'volume':volume,'context':str(out/'context')}
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
            '--security-opt','no-new-privileges:true','--pids-limit','256','--shm-size','64m','--ulimit','nofile=65536:65536',
            '--tmpfs','/tmp:rw,nosuid,nodev,size=512m,mode=1777',
            '--mount','type=volume,source='+volume+',target=/home/cal',image],out/'installation.log',timeout=args.timeout)
        lines=(out/'installation.log').read_text().splitlines()
        need(bool(lines),'actual Docker installation output missing')
        observation=json.loads(lines[-1])
        need(observation['result']=='PASS-fresh-installed-API-cold'
             and observation['archive_sha256']==args.archive_sha256
             and observation['package_manifest_sha256']==args.package_sha256,
             'actual selected artifact/API result differs')
        inspect_isolation(container,volume)
        repo='/home/cal/lab/runtime/repository'
        native='/opt/cal/bootstrap-native'
        observer=repo+'/implementation/lab-runtime/local-host/t25-integrated-runtime-0004/uninstall_restore.py'
        native_entry=native+'/lib/abi/ld-linux-x86-64.so.2'
        lifecycle_args=['--inhibit-cache','--library-path',native+'/lib/abi',native+'/bin/python',
            '-I','-B','-S',observer,'--installation','/home/cal/lab',
            '--package-sha256',args.package_sha256,'--output','/home/cal/uninstall-restore-final-0001']
        print(json.dumps({'phase':'idle-exact-installation-restore','container':lifecycle_container}),flush=True)
        command(isolated_run(lifecycle_container,volume,image,native_entry,lifecycle_args),
                out/'lifecycle.log',timeout=args.timeout)
        inspect_isolation(lifecycle_container,volume)
        copy_owned(lifecycle_container,'/home/cal/uninstall-restore-final-0001',out/'lifecycle')
        lifecycle=json.loads((out/'lifecycle/RESULT.json').read_bytes())
        need(lifecycle['result']=='PASS-actual-uninstall-exact-original-restore'
             and lifecycle['package_manifest_sha256']==args.package_sha256
             and lifecycle['fresh_native_API_readback']['source_sha256']==observation['API_observation']['source_sha256']
             and lifecycle['fresh_native_API_readback']['profile_sha256']==observation['API_observation']['profile_sha256']
             and lifecycle['fresh_native_API_readback']['source_cut']==observation['API_observation']['source_cut']
             and lifecycle['original_launcher_unavailable_while_removed'] is True
             and lifecycle['exact_original_paths_bytes_modes_and_inodes_restored'] is True
             and lifecycle['old_Source_or_Session_lease_extended'] is False
             and lifecycle['live_Session_or_private_memory_restored'] is False,
             'actual Docker uninstall/restore or cold selected API differs')
        launcher=repo+'/implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python'
        regression=repo+'/implementation/lab-runtime/local-host/t25-integrated-runtime-0004/regression.py'
        run_id='docker-t19-final-0001'
        bucket='sequential:test_installation_release.py:InstallationReleaseAPI'
        print(json.dumps({'phase':'actual-installation-upgrade-rollback-bucket','container':regression_container}),flush=True)
        command(isolated_run(regression_container,volume,image,launcher,['-B',regression,
            '--run-id',run_id,'--workers','1','--timeout-seconds','3600','--only-bucket',bucket]),
            out/'regression.log',timeout=args.timeout)
        inspect_isolation(regression_container,volume)
        copy_owned(regression_container,'/home/cal/lab/runtime/.cal-runtime/regression/'+run_id,out/'regression')
        release=json.loads((out/'regression/REGRESSION-RESULT.json').read_bytes())
        selection_raw=(out/'regression/SELECTION.json').read_bytes();selection=json.loads(selection_raw)
        need(release['result']=='PASS' and release['selected_bucket_count']==1
             and release['selected_method_count']==release['executed_method_count']==release['pass_method_count']==22
             and release['source_sha256']==observation['API_observation']['source_sha256']
             and release['profile_sha256']==observation['API_observation']['profile_sha256']
             and release['selection_sha256']==hashlib.sha256(selection_raw).hexdigest()
             and selection['package_manifest_sha256']==args.package_sha256
             and selection['api_source_sha256']==release['source_sha256']
             and selection['api_profile_sha256']==release['profile_sha256']
             and selection['inventory_sha256']==release['inventory_sha256']
             and selection['selected_buckets']==1 and selection['selected_methods']==22
             and selection['full_suite_selected'] is False
             and release['exact_case_set'] is True and release['selection_unchanged'] is True
             and release['full_suite_selected'] is False
             and len(release['bucket_results'])==1 and release['bucket_results'][0]['bucket']==bucket
             and release['bucket_results'][0]['status']=='PASS'
             and release['bucket_results'][0]['entry_guard_passed'] is True
             and release['bucket_results'][0]['exit_guard_passed'] is True
             and release['bucket_results'][0]['exit_code']==0
             and release['bucket_results'][0]['timed_out'] is False,
             'actual Docker installation release bucket differs')
        result={'schema_version':'lab-portable-scratch-docker-complete-installation/v1','result':'PASS-actual-unprivileged-Docker-install-restore-release',
            'archive_sha256':args.archive_sha256,'package_manifest_sha256':args.package_sha256,
            'actual_installation':observation,'actual_uninstall_restore':lifecycle,
            'installation_release_bucket':{'bucket':bucket,'selected_method_count':22,
                'receipt_sha256':hashlib.sha256((out/'regression/REGRESSION-RESULT.json').read_bytes()).hexdigest()},
            'uid':20001,'network':'none','read_only_root':True,
            'capabilities':'ALL-dropped','no_new_privileges':True,'nofile_soft':65536,'nofile_hard':65536,'native_runtime_is_fresh_installation':True,
            'full_regression_qualified':False,'authority_effect':'none'}
    except BaseException as error:
        try:
            write(out/'FAILED-RETAINED.json',{'result':'FAIL-resources-retained-for-diagnosis','error':type(error).__name__,
                'message':str(error),'resources':resources,'authority_effect':'none'})
        except OSError:
            pass
        raise
    # Cleanup follows the completed actual installation observation. Never
    # generalize these exact resource identities into a Docker prune operation.
    try:
        for name,argv in [*[(n,['docker','rm',n]) for n in resources['containers']],
                          ('volume',['docker','volume','rm',volume]),('image',['docker','image','rm',image])]:
            done=subprocess.run(argv,capture_output=True,check=False)
            need(done.returncode==0,'successful qualification cleanup failed for own '+name)
        shutil.rmtree(out/'context')
    except BaseException as error:
        try:
            write(out/'FAILED-CLEANUP-RETAINED.json',{'result':'FAIL-owned-resource-cleanup-incomplete',
                'error':type(error).__name__,'message':str(error),'resources':resources,'authority_effect':'none'})
        except OSError:
            pass
        raise
    need(hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==runner_digest
         and hashlib.sha256((HERE/'build_context.py').read_bytes()).hexdigest()==builder_digest,
         'qualification code changed during actual Docker run')
    result.update(owned_resources_removed=True,elapsed_seconds=round(time.monotonic()-started,3),
        docker_runner_sha256=runner_digest,context_builder_sha256=builder_digest)
    write(out/'RESULT.json',result)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for name in ('view','archive','archive-sha256','package-sha256','output'):parser.add_argument('--'+name,required=True)
    parser.add_argument('--timeout',type=int,default=3600)
    arguments=parser.parse_args()
    need(60<=arguments.timeout<=14400,'bounded Docker qualification timeout required')
    print(json.dumps(execute(arguments),sort_keys=True),flush=True)
