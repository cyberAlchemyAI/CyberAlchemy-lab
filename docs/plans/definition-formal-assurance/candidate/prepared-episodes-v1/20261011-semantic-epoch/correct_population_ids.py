"""Retain native build failure; distinguish required and unresolved population identities."""
from pathlib import Path
import json,hashlib,shutil,ast
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.semantic-epoch');a=u/'attempts/001-duplicate-population-identities';a.mkdir(parents=True)
names=['build_candidate.py','build-command-result.json','build-stdout.txt','build-stderr.txt'];refs=[]
for n in names:
 shutil.copyfile(u/n,a/n);refs.append({'path':str(a/n),'sha256':hashlib.sha256((a/n).read_bytes()).hexdigest()})
with (a/'attempt.json').open('x') as f:json.dump({'status':'retained-actual-native-build-failure','exit_code':json.loads((a/'build-command-result.json').read_text())['exit_code'],'reason':'Required demonstration and unresolved map populations shared ten POP identities; correspondence contract rejected duplicate identities before outputs','files':refs,'semantic_theory_change':'none','scope_change':'none','checker_limits_changed':False,'interpretation_created_in_failed_attempt':False},f,indent=2);f.write('\n')
assert not (u/'t.json').exists();s=(u/'build_candidate.py').read_text();old="{'population_id':'POP-'+n,'carrier':args[0]";new="{'population_id':'POP-UNRESOLVED-'+n,'carrier':args[0]";assert s.count(old)==1;s=s.replace(old,new).replace("assert account['character_accounting_complete'],account","assert account.get('character_accounting_complete') is True,account");ast.parse(s);(u/'build_candidate.py').write_text(s)
for n in ['build-command-result.json','build-stdout.txt','build-stderr.txt']:(u/n).unlink()
print('Retained actual native build failure; disjoint required/unresolved population identities; theory unchanged.')
