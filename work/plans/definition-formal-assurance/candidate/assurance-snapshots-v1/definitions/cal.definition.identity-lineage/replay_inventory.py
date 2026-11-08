"""Fresh whole98-definition inventory after initial actual terminal success."""
import json,sys
import build_candidate as b
from replay import run
def main():
    terminal=json.loads((b.UNIT/'inventory-command-result.json').read_bytes())
    if terminal['exit_code']!=0 or (b.UNIT/terminal['stderr']).read_bytes():raise ValueError('Initial inventory did not complete successfully')
    result=run('inventory',[sys.executable,str(b.UNIT/'verify_current_inventory.py')])
    b.put('fresh-inventory-command-result.json',result)
    print(json.dumps({'check':result['check'],'exit_code':result['exit_code'],'stderr_bytes':(b.UNIT/result['stderr']).stat().st_size},indent=2))
    if result['exit_code']!=0:raise SystemExit(result['exit_code'])
if __name__=='__main__':main()
