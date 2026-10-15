#!/usr/bin/env python3
"""Single maintained executable; public prechecks precede the selected runtime."""
import argparse,hashlib,json,os,stat,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
INSTALL=HERE.parent/'runtime-dependencies-v2-completion-0001/installations/0004'
SELECTION=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
SELECTION_SHA='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    p=argparse.ArgumentParser(description='Candidate full34 operator launcher; no network service')
    p.add_argument('--launcher-source-sha256',required=True);p.add_argument('--config',required=True);p.add_argument('--config-sha256',required=True)
    args=p.parse_args()
    try:
        manifest_path=HERE/'source-manifest.json';raw=manifest_path.read_bytes();assert sha(raw)==args.launcher_source_sha256
        manifest=json.loads(raw);assert manifest['authority_effect']=='none'
        for row in manifest['files']:
            relative=Path(row['path']);assert not relative.is_absolute() and '..' not in relative.parts
            path=ROOT/relative;assert path.is_file() and not any(q.is_symlink() for q in [path,*path.parents]) and sha(path.read_bytes())==row['sha256']
        raw=SELECTION.read_bytes();assert sha(raw)==SELECTION_SHA;value=json.loads(raw);assert len(value['inputs'])==720 and len(value['original_bindings'])==5
        expected={r['destination']:{'sha256':r['sha256'],'size_bytes':r['size_bytes'],'mode':0o755 if r['kind'] in {'interpreter','native-executable'} else 0o644} for r in value['inputs']}
        expected.update(value['wheel_members']);expected['lib/abi/ld-linux-x86-64.so.2']['mode']=0o755;assert len(expected)==1010
        for name,row in expected.items():
            path=INSTALL/name;assert not any(q.is_symlink() for q in [path,*path.parents]);s=path.stat();assert s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==row['mode'] and s.st_size==row['size_bytes'] and sha(path.read_bytes())==row['sha256']
        code='import sys;sys.path[:0]=['+repr(str(INSTALL/'deps'))+','+repr(str(HERE))+'];from composite import main;raise SystemExit(main())'
        cmd=[str(INSTALL/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(INSTALL/'lib/abi'),str(INSTALL/'bin/python'),'-I','-X','utf8','-B','-S','-c',code,'--config',args.config,'--config-sha256',args.config_sha256]
        result=subprocess.run(cmd,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'})
        for row in manifest['files']:assert sha((ROOT/row['path']).read_bytes())==row['sha256']
        return result.returncode
    except Exception:
        print('{"schema_version":"lab-composite-startup-error/v1-candidate","code":"selected-bootstrap-refused","authority_effect":"none"}',flush=True);return 2
if __name__=='__main__':raise SystemExit(main())
