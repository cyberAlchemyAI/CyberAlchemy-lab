"""Installed real-bootstrap proof across child and grandchild processes."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import jsonschema
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT=Path(__file__).resolve().parents[4]

def need(ok,message):
    if not ok:raise ValueError(message)

def main():
    provider=sys.modules.get('cal_installed_runtime_selection_v1')
    need(provider is not None and hasattr(provider,'PROCESS_PROOF_JSON') and callable(getattr(provider,'process_proof',None)),'actual selected bootstrap proof required')
    native=ROOT.parent/'.cal-runtime/native'
    need(Path(sys._base_executable)==native/'bin/python','real interpreter differs from private selected ELF')
    need(Path(sys.executable)==ROOT/'implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python','future children lack exact attested launcher')
    need(Path('/proc/self/exe').resolve()==native/'lib/abi/ld-linux-x86-64.so.2','actual process loader differs')
    need(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,'native child flags weakened')
    key=Ed25519PrivateKey.generate();signature=key.sign(b'installed-child-ABI-proof');key.public_key().verify(signature,b'installed-child-ABI-proof')
    jsonschema.Draft202012Validator({'type':'object','properties':{'value':{'const':1}},'required':['value'],'additionalProperties':False}).validate({'value':1})
    proof=provider.process_proof()
    package=json.loads((ROOT/'.cal-package-manifest.json').read_bytes());members=package['native_payload']['members']
    mapped={}
    for line in Path('/proc/self/maps').read_text().splitlines():
        parts=line.split(None,5)
        if len(parts)!=6 or not parts[5].startswith('/'):continue
        path=Path(parts[5])
        with path.open('rb') as stream:
            if stream.read(4)!=b'\x7fELF':continue
        need(path.is_relative_to(native),'ELF mapping escaped private selected Native')
        relative=path.relative_to(native).as_posix();need(relative in members,'unselected private ELF map')
        digest=hashlib.sha256(path.read_bytes()).hexdigest();need(digest==members[relative]['sha256'],'mapped private ELF original differs')
        mapped[relative]=digest
    depth=int(sys.argv[1]) if len(sys.argv)>1 else 0
    need(0<=depth<=2,'bounded process depth required')
    row={'depth':depth,'actual_python':str(native/'bin/python'),'actual_python_sha256':members['bin/python']['sha256'],
         'launcher':sys.executable,'launcher_is_not_reported_as_python':True,
         'process_executable':str(Path('/proc/self/exe').resolve()),'mapped_ELF_originals':mapped,
         'all_mapped_ELF_private_and_hash_verified':True,'jsonschema':importlib.metadata.version('jsonschema'),
         'cryptography':importlib.metadata.version('cryptography'),'python':sys.version.split()[0],
         'optimization':sys.flags.optimize,'bootstrap_proof':proof}
    need(row['jsonschema']=='4.23.0' and row['cryptography']=='46.0.5' and row['python']=='3.14.4','actual selected dependencies differ')
    if depth<2:
        child=subprocess.run([sys.executable,'-I','-B','-O',str(Path(__file__)),str(depth+1)],capture_output=True,text=True,check=True)
        need(not child.stderr,'unexpected selected child diagnostic')
        row['child']=json.loads(child.stdout)
    print(json.dumps({'result':'PASS-actual-installed-selected-process-tree','process':row},sort_keys=True))

if __name__=='__main__':main()
