"""Preserve the core KEP source graph with explicit external Product closure."""
import json,sys
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';STORE=ROOT/'.local/ontology-context-import-0042';CAPS=HERE.parent/'0035-definition-card-import';PREV=HERE.parent/'0041-encrypted-devnet-context-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
ID='CA2-CAP-HOST-DEVNET-KNOWLEDGE-EXCHANGE'
def bind(p,root=ROOT):return {'path':str(p.relative_to(root)),'sha256':tool.sha(p)}
def dump(p,obj):
    text=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=text:raise ValueError('Existing artifact differs')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def validate_graph(source,external):
    if source['ontology_type']!='business-system-bridge' or set(source['branches'])!={'business','system'} or source['authority_effect']!='none':raise ValueError('Wrong source boundary')
    ns=source['nodes'];rs=source['relations'];ids={n['node_id']:n for n in ns}
    if len(ids)!=len(ns) or len({r['relation_id'] for r in rs})!=len(rs):raise ValueError('Duplicate identity')
    if external:raise ValueError('Unexpected external endpoint')
    for n in ns:
        if n.get('branch') not in ['business','system'] or not tool.text(n.get('role')):raise ValueError('Invalid node branch')
    for r in rs:
        if r['source'] not in ids or r['target'] not in ids:raise ValueError('Dangling endpoint')
        if not tool.text(r.get('type')) or not tool.strings(r.get('evidence_refs')):raise ValueError('Missing relation evidence')
        branches={ids[r['source']]['branch'],ids[r['target']]['branch']}
        if r['branch']=='bridge':
            if branches!={'business','system'}:raise ValueError('Bridge must cross branches')
        elif r['branch'] not in ['business','system'] or branches!={r['branch']}:raise ValueError('Branch mismatch')
    return {'concepts':len(ns),'relations':len(rs),'business_nodes':sum(n['branch']=='business' for n in ns),'system_nodes':sum(n['branch']=='system' for n in ns),'bridge_relations':sum(r['branch']=='bridge' for r in rs),'rules':len(source['rules']),'role_signature_validation':'not-declared-by-source'}

def build():
    for folder in [CAPS,PREV]:
        for b in tool.read(folder/'verification.json')['bindings']:
            if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Predecessor drift')
    registry=tool.load_registry();plan=tool.read(HERE/'plan.json');docs={};snapshots=[]
    for b in plan['sources']:
        path=SOURCE/b['path']
        if tool.sha(path)!=b['sha256']:raise ValueError('Source drift')
        target=HERE/'source'/b['snapshot'];target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=path.read_bytes():raise ValueError('Snapshot drift')
        target.write_bytes(path.read_bytes());snapshots.append(bind(target))
        docs[b['snapshot']]=tool.read(target) if target.suffix=='.json' else target.read_text()
    profile=docs['profile.json'];thesis=docs['product-thesis.record.json']
    source={**profile,'nodes':docs['nodes.json']['nodes'],'relations':docs['relations.json']['relations'],'rules':docs['rules.json']['rules'],'residue':docs['residue.json']}
    for selection in plan['definition_sources']:
        ref=next(v for v in docs['sources.json']['sources'] if v['source_id']==selection['source_id'])
        if ref['sha256']!=tool.sha(HERE/'source'/selection['snapshot']):raise ValueError('Definition binding stale')
    cap=next(i for i in tool.read(CAPS/'imports.json') if i['id']==ID)
    if cap['source_record']!=docs['product-capability.json']:raise ValueError('Capability source drift')
    if profile['ontology_id']!=cap['source_record']['business_ontology_ref']:raise ValueError('Wrong ontology profile')
    evidence_paths={b['source_ref'] for b in plan['sources'] if 'source_ref' in b}
    used={ref for rel in source['relations'] for ref in rel['evidence_refs'] if '/' in ref}
    if used!=evidence_paths:raise ValueError('Implementation reference closure mismatch')
    external={}
    counts=validate_graph(source,external)
    base={'status':'candidate-unadmitted','authority_effect':'none','scope_ref':registry['scope'],'owner_ref':thesis['owner_route']}
    ontology={**base,'node_id':'lab:ontology-contexts/hosted-exchange#ontology','kind':'ontology','name':'Hosted Devnet Knowledge Exchange business-system bridge','version':'source-snapshot-0042','concept_refs':['source/nodes.json#/nodes/'+str(i) for i in range(counts['concepts'])],'relation_ids':[r['relation_id'] for r in source['relations']],'boundaries':['Source Product meaning only; Lab admission and operational authority remain separate.','All relationship endpoints resolve within this source graph; no external concepts merged.']}
    context={**base,'node_id':'lab:ontology-contexts/hosted-exchange#context','kind':'context','purpose':cap['capability']['outcome'],'identity_boundary':'Hosted exchange business/system bridge with explicit branch labels; implementation references are lineage evidence, not verified runtime conformance.','profile_ref':'source/profile.json','relevance':[cap['capability']['node_id'],ontology['node_id']]}
    contracts=[]
    for ident,obj in [('type.context',context),('type.ontology',ontology)]:
        entry=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/entry['binding']['path']).parent/'schema.json';Draft202012Validator(tool.read(schema)).validate(obj);contracts.append({'target_id':ident,'binding':entry['binding'],'schema':bind(schema)})
    bundle={'context':context,'ontology':ontology,'source_graph':source,'implementation_evidence_bindings':[b for b in plan['sources'] if 'source_ref' in b],'external_endpoints':external,'source_bindings':plan['sources'],'snapshots':snapshots,'contracts':contracts,'counts':counts,'capability_binding':{'inventory':bind(CAPS/'imports.json'),'id':ID,'node_id':cap['capability']['node_id']},'authority_effect':'none','limitations':['Source construction and evidence postures remain preserved; not promoted to Lab admission.','Source declares branch labels and evidence references; checks cover endpoint/branch closure, not generic role signatures or runtime conformance.','Source has no separate proof registry declared by this profile. Cited implementation files are copied evidence, not newly executed tests.','Context profile_ref points to source ontology metadata; not an admitted execution profile.']}
    for name,obj in [('context.json',context),('ontology.json',ontology),('bundle.json',bundle)]:dump(HERE/name,obj)
    dump(STORE/'bundle.json',bundle)
    for p in (HERE/'source').iterdir():
        target=STORE/'source'/p.name;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=p.read_bytes():raise ValueError('Store snapshot drift')
        target.write_bytes(p.read_bytes())
    for b in plan['sources']:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Source changed')
    return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
