"""Bind six actual terminal fresh observations; execute no replacement checks."""
import json,sys
import build_candidate as b
def main():
    results=json.loads((b.UNIT/'fresh-first-four-results.json').read_bytes())
    if len(results)!=4:raise ValueError('Wrong first-four denominator')
    results += [json.loads((b.UNIT/n).read_bytes()) for n in ['fresh-dependency-command-result.json','fresh-inventory-command-result.json']]
    names=['contract','model','source','profile','dependency','inventory']
    expected=[['validate','--kind','interpretation','--input',str(b.UNIT/'t.json')]]
    scripts=[b.IMPL/'contracts.py']+[b.UNIT/n for n in ['verify_candidate.py','verify_source_checks.py','verify_authority_profile.py','verify_dependencies.py','verify_current_inventory.py']]
    for i,(name,row,script) in enumerate(zip(names,results,scripts)):
        argv=[sys.executable,str(script)]+(expected[0] if i==0 else [])
        if row['check']!=name or row['argv']!=argv or row['exit_code']!=0 or (b.UNIT/row['stderr']).read_bytes() or not (b.UNIT/row['stdout']).read_bytes():raise ValueError('Missing or substituted fresh observation: '+name)
    b.put('fresh-command-results.json',results)
    print(json.dumps([{'check':x['check'],'exit_code':x['exit_code'],'stderr_bytes':(b.UNIT/x['stderr']).stat().st_size} for x in results],indent=2))
if __name__=='__main__':main()
