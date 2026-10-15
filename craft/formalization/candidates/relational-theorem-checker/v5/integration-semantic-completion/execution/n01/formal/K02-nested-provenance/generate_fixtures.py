"""Generate complete coherent synthetic nested catalogs; no provider authenticity."""
from pathlib import Path
import copy, hashlib, json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[9]
def read(p):return json.loads(p.read_text())
def raw(v):return json.dumps(v,separators=(',',':'),ensure_ascii=False).encode()
def hash_bytes(b):return hashlib.sha256(b).hexdigest()
def ref(v):return {'key':v['binding_revision_key'],'digest':hash_bytes(raw(v))}
def lean_ref(v):return '⟨⟨'+','.join(json.dumps(v['key'][k]) for k in ['owner','artifact','revision'])+'⟩,'+json.dumps(v['digest'])+'⟩'
def expected():
    old=HERE.parent/'K02-catalog-snapshots/fixtures'
    metadata,payload,owned=[read(old/(n+'.json')) for n in ['metadata','payload','owned']]
    body_refs={}
    for artifact in payload['context']['records']:
        artifact['content']=list(raw(artifact['body']))
        artifact['ref']['digest']=hash_bytes(bytes(artifact['content']))
        body_refs[artifact['ref']['key']['artifact']]=artifact['ref']
    def substitute(value):
        if isinstance(value,dict):
            if set(value)=={'key','digest'} and value['key']['artifact'] in body_refs:
                return copy.deepcopy(body_refs[value['key']['artifact']])
            return {k:substitute(v) for k,v in value.items()}
        if isinstance(value,list):return [substitute(v) for v in value]
        return value
    payload=substitute(payload)
    for approval in payload['context']['roots']:
        a=approval['artifact'];a['content']=list(raw(a['body']))
    frame=copy.deepcopy(metadata['context']['frame'])
    frame['subject']=copy.deepcopy(body_refs[frame['subject']['key']['artifact']])
    frame['target']=copy.deepcopy(body_refs[frame['target']['key']['artifact']])
    def frames(value):
        if isinstance(value,dict):return {k:copy.deepcopy(frame) if k=='frame' else frames(v) for k,v in value.items()}
        if isinstance(value,list):return [frames(v) for v in value]
        return value
    metadata,payload,owned=[frames(substitute(v)) for v in [metadata,payload,owned]]
    for kind,version in [('resolutions','cyberalchemy-lab-intent-resolution-qualifier-binding/candidate-v1'),('roles','cyberalchemy-lab-intent-addressing-role-binding/candidate-v1')]:
        catalog=owned['context'][kind]
        for artifact in catalog['records']+catalog['roots']:
            record={'schema_version':version,'binding_revision_key':artifact['ref']['key'],'kind':artifact['sourceKind'],'body':artifact['body'],'owner_review_ref':artifact['ownerReview']}
            artifact['content']=list(raw(record));artifact['ref']['digest']=hash_bytes(bytes(artifact['content']))
    prior=HERE.parent/'K02-profile-evidence/fixtures'
    declaration,selection,authority=[read(prior/(n+'.json')) for n in ['declaration','selection','authority-positive']]
    old_refs=[{'key':v['binding_revision_key'],'digest':hash_bytes((prior/(n+'.json')).read_bytes())} for n,v in [('declaration',declaration),('selection',selection)]]
    declaration['body']['frame']=frame;selection['body']['frame']=frame
    declaration_ref=ref(declaration);selection['body']['target']['declaration_ref']=declaration_ref;selection_ref=ref(selection)
    authority['body']['frame']=frame;t=authority['body']['target'];t['declaration_manifest']=[declaration_ref];t['selection_manifest']=[selection_ref]
    for issue in t['issuances']:
        index=old_refs.index(issue['source_ref']);value=[declaration,selection][index]
        issue.update(source_ref=ref(value),source_bytes=list(raw(value)))
    for review in t['reviews']:review['source_ref']=[declaration_ref,selection_ref][old_refs.index(review['source_ref'])]
    for grant in t['entitlements']:grant['scope']=frame['scope']
    source=bytes(metadata['context']['records'][0]['artifact']['content'])
    # Check primary source exact original bytes/body before returning fixtures.
    assert json.loads(source)==metadata['context']['records'][0]['artifact']['body']
    assert hash_bytes(source)==metadata['context']['records'][0]['artifact']['ref']['digest']
    result={'metadata':metadata,'payload':payload,'owned':owned,'declaration':declaration,'selection':selection,'authority-positive':authority}
    return result,source

def artifacts(values):
    m,p,o=[values[n]['context'] for n in ['metadata','payload','owned']]
    return [r['artifact'] for r in m['records']+m['roots']]+p['records']+[r['artifact'] for r in p['roots']]+o['resolutions']['records']+o['resolutions']['roots']+o['roles']['records']+o['roles']['roots']
def lean_source(values,source):
    selected_ref=ref(values['declaration'])
    lines=['import NestedPipeline','import SelectedRelationControls','set_option autoImplicit false','set_option maxRecDepth 65536','set_option maxHeartbeats 10000000',
           'namespace RelationalSuccessor.CandidateNestedProvenance.GeneratedFixture','open CandidateBindingCapture (Envelope)','open CandidateProfileEvidence.Controls (bootstrap root)',
           'def declarationRef : RevisionRef := '+lean_ref(selected_ref),'def authorityRef : RevisionRef := '+lean_ref(ref(values['authority-positive']))]
    def literal(data,profile):return '⟨('+json.dumps(data.decode('utf-8'),ensure_ascii=False)+').toUTF8.toList,'+str(len(data))+','+profile+','+json.dumps(hash_bytes(data))+'⟩'
    for name in ['declaration','selection','authority-positive','metadata','payload','owned']:
        ident={'authority-positive':'authority'}.get(name,name)
        profile='bootstrap.ref' if name in ['declaration','selection','authority-positive'] else 'declarationRef'
        lines.append('def '+ident+' : Envelope := '+literal(raw(values[name]),profile))
    lines.append('def source : Envelope := '+literal(source,'declarationRef'))
    lines.append('def qualifiers : Envelope := {CandidateOriginalBytePipeline.RuntimeControls.qualifiers with digestProfile := declarationRef}')
    lines.append('def nested : List Envelope := ['+','.join(literal(bytes(a['content']),'declarationRef') for a in artifacts(values))+']')
    lines.append('end RelationalSuccessor.CandidateNestedProvenance.GeneratedFixture')
    return '\n'.join(lines)+'\n'
def run():
    values,source=expected();files=HERE/'fixtures';files.mkdir(exist_ok=True)
    for name,value in values.items():(files/(name+'.json')).write_bytes(raw(value))
    (files/'source.json').write_bytes(source)
    (HERE/'NestedFixture.lean').write_text(lean_source(values,source))
    print('Generated complete coherent catalogs, three profile/evidence sources and',len(artifacts(values)),'ordered nested occurrences.')
if __name__=='__main__':run()
