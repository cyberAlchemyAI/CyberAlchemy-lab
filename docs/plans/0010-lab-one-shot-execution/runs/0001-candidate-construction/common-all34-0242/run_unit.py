"""One actual OS process per declared bounded unit; retain observed exit status."""
import argparse,hashlib,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser()
 for k in ('api-directory','source','profile','caller-sha256','plan-sha256','plan','unit'):p.add_argument('--'+k,required=True)
 a=p.parse_args();plan=Path(a.plan).resolve();assert plan.is_relative_to(HERE) and sha(plan)==a.plan_sha256;value=json.loads(plan.read_bytes());assert a.unit in value['units'] and value['source_sha256']==a.source and value['profile_sha256']==a.profile and value['api_directory']==str(Path(a.api_directory).resolve().relative_to(ROOT));assert value['runner_binding']['sha256']==sha(Path(__file__));assert sha(HERE/'caller.py')==a.caller_sha256
 external=Path('/tmp/cal-common-all34-0242');external.mkdir(exist_ok=True,mode=0o700);copy=external/'caller.py'
 if copy.exists():assert copy.read_bytes()==(HERE/'caller.py').read_bytes()
 else:
  with copy.open('xb') as f:f.write((HERE/'caller.py').read_bytes())
  copy.chmod(0o600)
 units=HERE/'units';units.mkdir(exist_ok=True);name=a.unit.replace(':','--').replace('.','-');report=units/(name+'.command.json');log=units/(name+'.log');assert not report.exists() and not log.exists();started=datetime.now(timezone.utc).isoformat();argv=[sys.executable,'-B',str(copy)]
 for k in ('api_directory','source','profile','caller_sha256','plan_sha256','plan','unit'):argv.extend(['--'+k.replace('_','-'),str(getattr(a,k))])
 with log.open('xb') as f:result=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 data={'schema_version':'lab-bounded-common-command/v1-candidate','unit':a.unit,'started_at':started,'ended_at':datetime.now(timezone.utc).isoformat(),'actual_os_exit_code':result.returncode,'caller_sha256':a.caller_sha256,'plan_sha256':a.plan_sha256,'source_sha256':a.source,'profile_sha256':a.profile,'log_sha256':sha(log),'caller_report_sha256':sha(units/(name+'.json')) if (units/(name+'.json')).exists() else None,'original_clock_changed':False,'authority_effect':'none'}
 with report.open('x') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps(data),flush=True);return result.returncode
if __name__=='__main__':raise SystemExit(main())
