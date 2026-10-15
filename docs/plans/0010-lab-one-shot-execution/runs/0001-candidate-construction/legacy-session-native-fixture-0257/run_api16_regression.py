"""Observe only assigned whole-class workers 1 and 8 and their actual exits."""
import hashlib,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent;RUN=OUT.parent;ROOT=RUN.parents[4]
PLAN=RUN/'final-api-regression-plan-0274.json';PIN='b04c3f6a9953765b807adf4f8ef72b480c6c51985a1b1c563535395f86b8ac40';PREFIX='final-api-regression-0173-0274'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 proof=OUT/'api16-proof.json';v=json.loads(proof.read_bytes());assert v['result']=='PASS' and v['full16entry'] and v['full16exit'] and v['owned_private_root_absent'];assert sha(PLAN)==PIN
 for bucket in ['worker:1','worker:8']:
  label=bucket.replace(':','-');report=RUN/(PREFIX+'.'+label+'.json');command=RUN/(PREFIX+'.'+label+'.command.json');log=RUN/(PREFIX+'.'+label+'.log')
  assert not report.exists() and not command.exists() and not log.exists()
  args=['flock','-s',str(RUN/'final-api-regression-0173-0190.execution.lock'),sys.executable,'-B',str(RUN/'final-api-regression-0270.py'),'--api-directory',str(ROOT/'product/lab/release-candidates/v1/interface/api-integration-v16'),'--source','8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7','--profile','8cc29da16d3881d8816cdc45c55358d9229fcaf226d1b9a757402ebc8675d18c','--plan',str(PLAN),'--plan-sha256',PIN,'--output-prefix',PREFIX,'--worker',bucket]
  started=datetime.now(timezone.utc).isoformat()
  with log.open('xb') as f:r=subprocess.run(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  value={'schema_version':'lab-actual-regression-command-observation/v1-candidate','bucket':bucket,'started_at':started,'ended_at':datetime.now(timezone.utc).isoformat(),'actual_os_exit_code':r.returncode,'argv':args,'plan_sha256':PIN,'log_sha256':sha(log),'report_binding':{'path':str(report.relative_to(ROOT)),'sha256':sha(report)} if report.exists() else None,'authority_effect':'none'}
  with command.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
  print(json.dumps({'bucket':bucket,'actual_os_exit_code':r.returncode,'report_exists':report.exists()}),flush=True)
if __name__=='__main__':main()
