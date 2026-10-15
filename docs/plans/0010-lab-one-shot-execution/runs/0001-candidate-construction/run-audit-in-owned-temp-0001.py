"""Run the exact audit in its own process-owned temporary-directory namespace."""
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True);args=parser.parse_args()
    inputs=RUN/'current-source-adapter-audit-source-0004.json';assert sha(inputs)==args.source_sha256
    selection=json.loads(inputs.read_bytes())
    def guard():
        for row in selection['files']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
    guard()
    with tempfile.TemporaryDirectory(prefix='cal-R03-source-audit-owned-0004-') as temporary:
        own=Path(temporary);own.chmod(0o700)
        environment=dict(os.environ);environment['TMPDIR']=str(own)
        completed=subprocess.run([sys.executable,'-B',str(RUN/'audit-R03-current-source-adapter-0004.py'),'--source-sha256',args.source_sha256],env=environment)
        assert not any(own.iterdir()),'actual audit left a child temporary workspace'
    assert not own.exists(),'actual audit parent workspace remains'
    guard()
    value={'schema_version':'lab-owned-source-audit-process/v1-candidate','result':'PASS' if completed.returncode==0 else 'FAIL','actual_child_exit_code':completed.returncode,'parent_temporary_root_removed':True,'original_source_callbacks_replaced':False,'original_clock_replaced':False,'permission_changed':False,'inputs_sha256':args.source_sha256,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    with (RUN/'current-source-adapter-owned-process-0004.json').open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
    raise SystemExit(completed.returncode)
if __name__=='__main__':main()
