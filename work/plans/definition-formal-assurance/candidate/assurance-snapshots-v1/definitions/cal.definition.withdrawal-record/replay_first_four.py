"""Run four ready independent full checks while the initial inventory computes."""
import json,sys
from concurrent.futures import ThreadPoolExecutor
import build_candidate as b
from replay import run
def main():
 jobs=[('contract',[sys.executable,str(b.IMPL/'contracts.py'),'validate','--kind','interpretation','--input',str(b.UNIT/'t.json')])]+[(stem,[sys.executable,str(b.UNIT/script)]) for stem,script in [('model','verify_candidate.py'),('source','verify_source_checks.py'),('profile','verify_authority_profile.py')]]
 with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(lambda job:run(*job),jobs))
 b.put('fresh-first-four-results.json',results)
 print(json.dumps([{'check':x['check'],'exit_code':x['exit_code'],'stderr_bytes':(b.UNIT/x['stderr']).stat().st_size} for x in results],indent=2))
 if any(x['exit_code']!=0 for x in results):raise SystemExit(1)
if __name__=='__main__':main()
