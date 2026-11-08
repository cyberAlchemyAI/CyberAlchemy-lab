"""Validate UX source parity, carrier requests and cross-record references."""
from pathlib import Path
import hashlib,json
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=load(ROOT/'design/source.json');index=load(ROOT/'design/index.json')
assert src['authority_effect']==index['authority_effect']=='none'
assert index['source_sha256']==sha(ROOT/'design/source.json')
assert index['count']==sum(len(x) for x in src['families'].values())==55
assert index['counts']=={k:len(v) for k,v in src['families'].items()}
ids={r['id'] for rows in src['families'].values() for r in rows}
assert len(ids)==55
seen=set()
for family,rows in src['families'].items():
    base=ROOT/'model/carriers'/family/'v1'
    schema=load(base/'schema.json'); descriptor=load(base/'artifact.json');request=load(base/'request.json')
    assert request['status']=='candidate-unadmitted' and request['authority_effect']=='none'
    assert descriptor['instance_contract']['schema_sha256']==sha(base/'schema.json')
    assert descriptor['semantic_definition_sha256']==sha(ROOT/'model/definition-records'/family/'definition.json')
    validator=Draft202012Validator(schema)
    for i,row in enumerate(rows):
        p=ROOT/'design/records'/row['id']/'record.json'; rec=load(p)
        assert not list(validator.iter_errors(rec)),(row['id'],list(validator.iter_errors(rec)))
        assert rec['source_row']==row and rec['source_index']==i
        assert rec['source_sha256']==index['source_sha256']
        assert rec['source_excerpt_sha256']==hashlib.sha256(json.dumps(row,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        seen.add(str(p.relative_to(ROOT)))
        for key in ('component_refs','screen_refs','flow_ref'):
            value=row.get(key,[])
            for ref in value if isinstance(value,list) else [value]: assert ref in ids,(row['id'],ref)
assert seen==set(index['record_refs'])
assert set(index['type_request_refs'])=={f'model/carriers/{f}/v1/request.json' for f in src['families']}
names=[e['event_name'] for e in src['families']['analytics-event-spec']]
assert len(names)==len(set(names))==27
assert all(not set(e['required_properties']+e['optional_properties'])&set(e['forbidden_properties']) for e in src['families']['analytics-event-spec'])
tokens=load(ROOT/'design/tokens.json')['color']
def luminance(value):
    rgb=[int(value[i:i+2],16)/255 for i in (1,3,5)]
    linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    return sum(a*b for a,b in zip(linear,[.2126,.7152,.0722]))
for foreground,background in [('ink','canvas'),('mutedInk','canvas'),('actionInk','action'),('cautionInk','cautionSurface'),('errorInk','errorSurface')]:
    a,b=[luminance(tokens[k]['$value']) for k in (foreground,background)]
    assert (max(a,b)+.05)/(min(a,b)+.05)>=4.5,(foreground,background)
print('PASS: 55 source-bound UX records, six closed candidate carriers, type requests and references')
