"""Compose the new prepared candidate from reviewed fragments; never create its native unit."""
from pathlib import Path
import ast,json
p=Path(__file__).resolve().parent;root=Path.cwd();prepared=p/'prepared';prepared.mkdir(exist_ok=True)
previous=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-realization-binding'
header=(p/'builder_header.py').read_text().replace('Prepared Capability Instance source-qualified tuple,owner,contexts,claims and recursion guards.','Prepared Coordination Context source-qualified frame, optional anchors, boundaries and identity guards.')
builder=header+'\n'+(p/'theory_body.py').read_text()+'\n'+(p/'builder_main.py').read_text()
tail=(previous/'verify_candidate.py').read_text().split('def verify(write=False):',1)[1]
tail='def verify(write=False):'+tail
tail=tail.replace('definitions/cal.definition.capability-instance/delivery-manifest.json','definitions/cal.definition.capability-realization-binding/delivery-manifest.json').replace('CapabilityRealizationBinding','CoordinationContext')
tail=tail.replace('Necessary exact association/endpoints/single-authority/evidence-purpose/optional-projection/change-succession guards checked on supplied models;actual outcomes,fidelity andwhole proof pending.','Necessary fourteen-coordinate frame, optional anchor cardinality, explicit independent boundary and identity guards checked on supplied models; actual outcomes, fidelity and whole proof pending.')
model=(p/'model_body.py').read_text()+'\n'+tail
for name,text in [('build_candidate.py',builder),('verify_candidate.py',model)]:
 ast.parse(text)
 with (prepared/name).open('x') as f:f.write(text)
with (p/'model_verify_tail.py').open('x') as f:f.write(tail)
print(json.dumps({'result':'prepared-code-composed','native_unit_created':False}))
