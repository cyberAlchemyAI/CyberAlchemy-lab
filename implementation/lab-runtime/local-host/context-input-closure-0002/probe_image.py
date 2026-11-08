"""One no-mount, disposable selected-image version probe; records actual subprocess argv/results."""
from __future__ import annotations
import hashlib
import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE_ID = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
CODE = ('import json,os,platform,importlib.metadata as m;'
        'print(json.dumps({"python":platform.python_version(),'
        '"versions":{k:m.version(k) for k in '
        '("jsonschema","cryptography","referencing")},'
        '"uid":os.getuid(),"euid":os.geteuid(),'
        '"gid":os.getgid(),"egid":os.getegid()},sort_keys=True))')

def record(argv):
    # Retain argv verbatim: no post-hoc reconstruction or display placeholder.
    try:
        p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=60, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError('bounded Docker command timed out') from exc
    if len(p.stdout) > 65536 or len(p.stderr) > 65536:
        raise RuntimeError('Docker diagnostic exceeds 64 KiB')
    return {'argv':argv, 'os_exit_code':p.returncode,
            'stdout':p.stdout.decode('utf-8',errors='strict'),
            'stderr':p.stderr.decode('utf-8',errors='strict'),
            'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),
            'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()}

def main():
    name='cal-context-env-closure2-'+uuid.uuid4().hex[:16]
    inspect_image=record(['docker','image','inspect',IMAGE_ID])
    if inspect_image['os_exit_code'] != 0:
        raise RuntimeError('selected image inspect failed')
    image=json.loads(inspect_image['stdout'])
    if len(image)!=1 or image[0]['Id']!=IMAGE_ID:
        raise RuntimeError('selected image ID differs')
    config=image[0]['Config']
    if config.get('Entrypoint') not in (None,[]) or config.get('Cmd')!=['python3']:
        raise RuntimeError('selected image command configuration differs')
    pre=record(['docker','container','inspect',name])
    if pre['os_exit_code']==0:
        raise RuntimeError('probe name already exists')
    argv=['docker','run','--rm','--name',name,'--network','none','--read-only',
          '--cap-drop','ALL','--security-opt','no-new-privileges',
          '--pids-limit','16','--user','1000:1000','--workdir','/',
          IMAGE_ID,'python3','-B','-c',CODE]
    run=record(argv)
    post=record(['docker','container','inspect',name])
    if post['os_exit_code']==0:
        # Only this newly unique probe name is eligible for emergency cleanup.
        record(['docker','container','rm','-f',name])
        raise RuntimeError('probe container remained after --rm')
    if run['os_exit_code']!=0 or run['stderr']!='':
        raise RuntimeError('Docker run failed or emitted stderr')
    data=json.loads(run['stdout'])
    if data!={'python':'3.14.4',
              'versions':{'jsonschema':'4.23.0','cryptography':'46.0.5',
                          'referencing':'0.37.0'},
              'uid':1000,'euid':1000,'gid':1000,'egid':1000}:
        raise RuntimeError('image version or identity differs')
    receipt={'schema_version':'lab-context-image-environment-probe/v2',
             'observed_at_utc':datetime.now(timezone.utc).isoformat(),
             'wrapper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'image_id':IMAGE_ID,'image_config':{
                 'entrypoint':config.get('Entrypoint'),'cmd':config.get('Cmd'),
                 'user':config.get('User')},'container_name':name,
             'image_inspect':inspect_image,'before_container_inspect':pre,
             'run':run,'after_container_inspect':post}
    target=HERE/'image-environment-probe.json'
    with target.open('x') as f:
        json.dump(receipt,f,sort_keys=True,indent=2)
        f.write('\n')
    print(target)

if __name__=='__main__':
    main()
