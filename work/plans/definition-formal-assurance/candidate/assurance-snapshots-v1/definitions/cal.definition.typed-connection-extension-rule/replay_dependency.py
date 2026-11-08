"""One actual fresh dependency check while initial whole inventory runs."""
import json,sys
import build_candidate as b
from replay import run
def main():
    result=run('dependency',[sys.executable,str(b.UNIT/'verify_dependencies.py')])
    b.put('fresh-dependency-command-result.json',result)
    print(json.dumps({'check':result['check'],'exit_code':result['exit_code'],'stderr_bytes':(b.UNIT/result['stderr']).stat().st_size},indent=2))
    if result['exit_code']!=0:raise SystemExit(result['exit_code'])
if __name__=='__main__':main()
