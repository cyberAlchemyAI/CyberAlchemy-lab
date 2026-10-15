"""Repeat the affected profile only,then bind it to three unchanged actual fresh checks."""
import json,sys
import build_candidate as b
from replay import run
def main():
    first=json.loads((b.UNIT/'fresh-first-three-results.json').read_bytes())
    if [x['check'] for x in first]!=['contract','model','source']:raise ValueError('Wrong unaffected check denominator')
    for x in first:
        if x['exit_code']!=0 or (b.UNIT/x['stderr']).read_bytes():raise ValueError('Unaffected checks lack successful terminal evidence')
    actual=run('profile',[sys.executable,str(b.UNIT/'verify_authority_profile.py')])
    b.put('fresh-first-four-results.json',first+[actual])
    print(json.dumps({'check':'profile','exit_code':actual['exit_code'],'stderr_bytes':(b.UNIT/actual['stderr']).stat().st_size},indent=2))
    if actual['exit_code']!=0:raise SystemExit(actual['exit_code'])
if __name__=='__main__':main()
