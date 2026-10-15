"""Reuse checked generic scaffolding and compose source-specific fragments."""
from pathlib import Path
import ast,json
p=Path(__file__).resolve().parent;root=Path.cwd();previous=p.parent/'20261013-implementation';prepared=p/'prepared';prepared.mkdir()
header=(previous/'builder_header.py').read_text();tail=(previous/'model_verify_tail.py').read_text().replace('definitions/cal.definition.coordination-context/delivery-manifest.json','definitions/cal.definition.intent/delivery-manifest.json').replace('Implementation','IntentResolution')
tail=tail.replace('Necessary technical-realization nominations, inclusive posture, explicit interfaces and evidence, separated governance, scoped exact-version uses and noninference guards checked on supplied models; actual outcomes, fidelity and whole proof pending.','Necessary owner-decision, exact Intent, governed output and satisfaction-test links with scope and independent outcomes; fidelity and whole proof pending.')
builder=header+'\n'+(p/'theory_body.py').read_text()+'\n'+(p/'builder_main.py').read_text();model=(p/'model_body.py').read_text()+'\n'+tail
for name,text in [('build_candidate.py',builder),('verify_candidate.py',model)]:
    ast.parse(text)
    with(prepared/name).open('x') as f:f.write(text)
for name,text in [('builder_header.py',header),('model_verify_tail.py',tail)]:
    with(p/name).open('x') as f:f.write(text)
print(json.dumps({'result':'IntentResolution-prepared-code-composed','native_unit_created':False}))
