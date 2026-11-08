"""Actual disposable FROM-scratch native bootstrap smoke, not API acceptance."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid

from build_context import ROOT,exact_copy,write,need


def main():
    inventory=ROOT/'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/DECLARED-CLOSURE-0001.json'
    rows=[r for r in json.loads(inventory.read_bytes())['members'] if r['member'].startswith('native-payload/')]
    need(len(rows)==1010,'exact native bootstrap closure required')
    tag='cyberalchemy-lab-bootstrap:probe-'+uuid.uuid4().hex
    result=None;built=False
    with tempfile.TemporaryDirectory(prefix='cal-scratch-bootstrap-') as folder:
        context=Path(folder)
        try:
            for row in rows:
                relative=row['member'][len('native-payload/'):]
                exact_copy(row['input_path'],context/'bootstrap'/relative,row,0o555 if row['mode']&0o111 else 0o444)
            for p in (context/'bootstrap',*(p for p in (context/'bootstrap').rglob('*') if p.is_dir())):p.chmod(0o755)
            code="import sys,os,json,platform;sys.path.insert(0,'/opt/native/deps');import importlib.metadata,ssl,zlib;print(json.dumps({'uid':os.getuid(),'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography'),'bootstrap_only':True,'API_qualified':False},sort_keys=True))"
            command=['/opt/native/lib/abi/ld-linux-x86-64.so.2','--inhibit-cache','--library-path','/opt/native/lib/abi',
                '/opt/native/bin/python','-I','-B','-S','-c',code]
            dockerfile='\n'.join(['FROM scratch','COPY bootstrap/ /opt/native/','USER 20001:20001',
                'ENV PYTHONDONTWRITEBYTECODE=1','ENTRYPOINT '+json.dumps(command,separators=(',',':')),''])
            write(context/'Dockerfile',dockerfile.encode(),0o644)
            build=subprocess.run(['docker','build','--network=none','--pull=false','-t',tag,str(context)],capture_output=True,timeout=300)
            need(build.returncode==0,'actual scratch bootstrap build failed: '+build.stderr.decode()[-2000:]);built=True
            run=subprocess.run(['docker','run','--rm','--network=none','--read-only','--cap-drop=ALL',
                '--security-opt=no-new-privileges',tag],capture_output=True,timeout=120)
            need(run.returncode==0,'actual scratch native bootstrap failed: '+run.stderr.decode()[-3000:])
            observed=json.loads(run.stdout)
            need(observed=={'uid':20001,'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5',
                'bootstrap_only':True,'API_qualified':False},'actual Docker bootstrap environment differs')
            result={'result':'PASS-actual-scratch-unprivileged-native-bootstrap','observed':observed,
                'native_files':1010,'native_inventory_sha256':hashlib.sha256(inventory.read_bytes()).hexdigest(),
                'network':'none','root_filesystem':'read-only','capabilities':'ALL-dropped',
                'native_runtime_installation_attested':False,'Source_Context_or_API_qualified':False,
                'image_tag':tag,'authority_effect':'none'}
        finally:
            if built:
                removed=subprocess.run(['docker','image','rm',tag],capture_output=True,timeout=120)
                need(removed.returncode==0,'owned bootstrap image cleanup failed')
    result['owned_context_removed']=not Path(folder).exists();result['owned_image_removed']=True
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
