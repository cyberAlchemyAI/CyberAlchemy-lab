"""Run the six independent read-only checks, retaining actual terminal results."""
import subprocess,sys,json
from concurrent.futures import ThreadPoolExecutor
import build_candidate as b
def run(stem,argv):
 result=subprocess.run(argv,cwd=b.ROOT,capture_output=True)
 for suffix,raw in [('stdout',result.stdout),('stderr',result.stderr)]:
  with (b.UNIT/('fresh-'+stem+'-'+suffix+'.txt')).open('xb') as f:f.write(raw)
 return {'check':stem,'argv':argv,'exit_code':result.returncode,'stdout':'fresh-'+stem+'-stdout.txt','stderr':'fresh-'+stem+'-stderr.txt'}
def main():
 jobs=[('contract',[sys.executable,str(b.IMPL/'contracts.py'),'validate','--kind','interpretation','--input',str(b.UNIT/'t.json')])]+[(stem,[sys.executable,str(b.UNIT/script)]) for stem,script in [('model','verify_candidate.py'),('source','verify_source_checks.py'),('profile','verify_authority_profile.py'),('dependency','verify_dependencies.py'),('inventory','verify_current_inventory.py')]]
 prepared=b.UNIT/'fresh-first-four-results.json'
 if prepared.exists():
  results=json.loads(prepared.read_bytes())
  if len(results)!=4 or [x['check'] for x in results]!=['contract','model','source','profile']:raise ValueError('Wrong first-four denominator')
  for x,(stem,argv) in zip(results,jobs[:4]):
   if x['argv']!=argv or x['exit_code']!=0 or (b.UNIT/x['stderr']).read_bytes():raise ValueError('First-four checks lack passing terminal evidence')
  with ThreadPoolExecutor(max_workers=2) as pool:results+=list(pool.map(lambda job:run(*job),jobs[4:]))
 else:
  with ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(lambda job:run(*job),jobs))
 b.put('fresh-command-results.json',results)
 print(json.dumps([{'check':x['check'],'exit_code':x['exit_code'],'stderr_bytes':(b.UNIT/x['stderr']).stat().st_size} for x in results],indent=2))
 if any(x['exit_code']!=0 for x in results):raise SystemExit(1)
if __name__=='__main__':main()
