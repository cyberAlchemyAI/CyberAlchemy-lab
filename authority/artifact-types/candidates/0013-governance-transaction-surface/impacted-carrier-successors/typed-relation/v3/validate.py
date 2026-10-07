#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,jsonschema,sys
R=Path(__file__).resolve().parent
L=lambda p:json.loads(p.read_text())
S=L(R/'schema.json');A=L(R/'artifact.json');V=jsonschema.Draft202012Validator(S)
checks=[]
def add(i,p,d):checks.append({'check_id':i,'result':'PASS' if p else 'BLOCK','detail':d})
w=L(R/'fixtures/valid/record.json');errs=[e.message for e in V.iter_errors(w)];add('positive-witness',not errs,errs)
neg=[]
for rel in A['validation_contract']['negative_witnesses']:
 e=[x.message for x in V.iter_errors(L(R/rel))];neg.append({'path':rel,'rejected':bool(e),'errors':e})
add('hostile-rejections',len(neg)==4 and all(x['rejected'] for x in neg),neg)
rels=S['properties']['payload']['properties']['relation_kind_ref']['enum'];add('41-relation-conditions',len(rels)==41 and len(S['allOf'])==41 and 'relation.materializes-consequence' in rels,{'enum':len(rels),'conditions':len(S['allOf'])})
add('schema-current',A['schema_digest']==hashlib.sha256((R/'schema.json').read_bytes()).hexdigest(),A['schema_digest'])
result='PASS' if all(x['result']=='PASS' for x in checks) else 'BLOCK';out={'schema_version':'cyberalchemy-lab-typed-relation-v3-validation/v1','subject':A['artifact_type_ref'],'result':result,'authority_effect':'none','checks':checks};(R/'receipts').mkdir(exist_ok=True);(R/'receipts/validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'subject':A['artifact_type_ref'],'result':result,'checks':len(checks)},sort_keys=True));sys.exit(0 if result=='PASS' else 1)
