"""Compose source-specific candidate code from exact reviewed fragments."""
from pathlib import Path
import ast,json
p=Path(__file__).resolve().parent;root=Path.cwd();previous=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.coordination-context'
builder='\n'.join((p/name).read_text() for name in ['builder_header.py','theory_body.py','builder_main.py'])
tail='def verify(write=False):'+(previous/'verify_candidate.py').read_text().split('def verify(write=False):',1)[1];tail=tail.replace('definitions/cal.definition.capability-realization-binding/delivery-manifest.json','definitions/cal.definition.coordination-context/delivery-manifest.json').replace('CoordinationContext','Implementation')
tail=tail.replace('Necessary fourteen-coordinate frame, optional anchor cardinality, explicit independent boundary and identity guards checked on supplied models; actual outcomes, fidelity and whole proof pending.','Necessary technical-realization nominations, inclusive posture, explicit interfaces and evidence, separated governance, scoped exact-version uses and noninference guards checked on supplied models; actual outcomes, fidelity and whole proof pending.')
model=(p/'model_body.py').read_text()+'\n'+tail
for name,text in [('build_candidate.py',builder),('verify_candidate.py',model)]:
 ast.parse(text)
 with (p/'prepared'/name).open('x') as f:f.write(text)
with (p/'model_verify_tail.py').open('x') as f:f.write(tail)
print(json.dumps({'result':'Implementation-prepared-code-composed','native_unit_created':False}))
