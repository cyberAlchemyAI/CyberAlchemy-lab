"""Three fresh checks for the typed Representation Revision draft; full delivery replay remains pending."""
import subprocess,sys,json
from concurrent.futures import ThreadPoolExecutor
import build_candidate as b
def run(stem,argv):
 result=subprocess.run(argv,cwd=b.ROOT,capture_output=True)
 for suffix,raw in [('stdout',result.stdout),('stderr',result.stderr)]:
  with (b.UNIT/('fresh-types-'+stem+'-'+suffix+'.txt')).open('xb') as f:f.write(raw)
 return {'check':stem,'argv':argv,'exit_code':result.returncode,'stdout':'fresh-types-'+stem+'-stdout.txt','stderr':'fresh-types-'+stem+'-stderr.txt'}
def main():
 jobs=[('contract',[sys.executable,str(b.IMPL/'contracts.py'),'validate','--kind','interpretation','--input',str(b.UNIT/'t.json')])]+[(stem,[sys.executable,str(b.UNIT/script)]) for stem,script in [('model','verify_candidate.py'),('source','verify_source_checks.py')]]
 with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(lambda job:run(*job),jobs))
 b.put('fresh-types-logic-results.json',results);print(json.dumps([{'check':x['check'],'exit_code':x['exit_code'],'stderr_bytes':(b.UNIT/x['stderr']).stat().st_size} for x in results],indent=2))
 if any(x['exit_code']!=0 for x in results):raise SystemExit(1)
if __name__=='__main__':main()
