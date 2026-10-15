"""Compile isolated reader against the selected existing candidate native library."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'session-participation-v2'))
from base import ROOT,sha,encoded,load,require,binding,original
import subprocess,os,json
OUT=Path('/tmp/cal-R03-mapped-native-build-0001')
def main(pin):
    require(sha((HERE/'source-manifest.json').read_bytes())==pin,'native build producer pin differs')
    m=load(HERE/'source-manifest.json')
    for row in m['files']:original(row)
    require(not OUT.exists(),'owned native build target exists');OUT.mkdir(mode=0o700)
    for row in m['copies']:
        p=OUT/row['target'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(original(row['binding']))
    receipts=HERE/'receipts';receipts.mkdir(mode=0o700)
    env=dict(os.environ);env['CARGO_TARGET_DIR']=str(OUT/'target')
    observations=[]
    for label,args in [('build',['build','--offline','--frozen','--manifest-path',str(OUT/'reader/Cargo.toml')]),
                       ('tests',['test','--offline','--frozen','--manifest-path',str(OUT/'ontology/Cargo.toml')])]:
        p=subprocess.run(['cargo',*args],capture_output=True,env=env,timeout=240)
        for name,raw in [('stdout',p.stdout),('stderr',p.stderr)]: (receipts/(label+'.'+name)).open('xb').write(raw)
        require(p.returncode==0,'native '+label+' failed: '+p.stderr.decode(errors='replace')[-1800:])
        observations.append({'producer':label,'exit_code':p.returncode,'terminal_observed':True})
    exe=OUT/'target/debug/lab-context-native-reader';require(exe.is_file(),'compiled native reader missing')
    for row in m['files']:original(row)
    result={'result':'PASS','source_sha256':pin,'executable_binding':{'path':str(exe),'sha256':sha(exe.read_bytes())},
        'observations':observations,'owned_compile_root':str(OUT),'existing_runtime_changed':False,
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    (receipts/'result.json').open('xb').write(encoded(result));print(json.dumps(result),flush=True)
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);a=p.parse_args();main(a.source_sha256)
