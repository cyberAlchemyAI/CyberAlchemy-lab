"""Inventory source capability declarations and import structurally complete candidates."""
import collections
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from jsonschema import ValidationError
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT.parent / 'cyberAlchemy-v2'
HERE = ROOT / 'evidence/migrations/cyberalchemy-v2-to-lab/executions/0008-capability-inventory-import'
sys.path.insert(0, str(ROOT / 'tooling/validators'))
from migration_contracts import load_registry

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'))
def walk(x, ptr=''):
    if isinstance(x,dict):
        yield ptr,x
        for k,v in x.items(): yield from walk(v,ptr+'/'+k.replace('~','~0').replace('/','~1'))
    elif isinstance(x,list):
        for i,v in enumerate(x): yield from walk(v,ptr+'/'+str(i))
def read(p):
    def unique(pairs):
        out={}
        for k,v in pairs:
            if k in out: raise ValueError('duplicate key '+k)
            out[k]=v
        return out
    return json.loads(p.read_text(),object_pairs_hook=unique)
def strings(x): return isinstance(x,list) and bool(x) and all(isinstance(y,str) and y.strip() for y in x)
def text(x): return isinstance(x,str) and bool(x.strip())
def binding(p,ptr=''): return {'path':str(p.relative_to(SOURCE)), 'sha256':sha(p),'selector':ptr}
def identity(row): return next((row.get(k) for k in ['capability_id','id','node_id','artifact_id'] if text(row.get(k))),None)
def classify(row):
    ident=identity(row)
    if not ident:return None
    schema=str(row.get('schema_version','')).lower()
    role=str(row.get('role',row.get('kind',row.get('type','')))).lower()
    if text(row.get('capability_id')):
        if any(text(row.get(k)) for k in ['outcome','purpose']) or ('product-capability' in schema and 'candidate' in schema):
            return 'agent-declaration' if 'agent-capability' in schema else 'declaration'
        return 'reference-or-support'
    if 'capability' in role or ('capability' in schema and any(text(row.get(k)) for k in ['outcome','purpose'])):
        return 'ontology-or-other-capability'
    return None

def discover(source):
    paths=sorted(subprocess.check_output(['rg','--files','--hidden','-g','!.git','-g','*.json',str(source)],text=True).splitlines())
    index=collections.defaultdict(list); inventory=[]; files=[]; errors=[]
    idkeys=['id','node_id','artifact_id','product_id','capability_id','registry_id','obligation_id','contract_id','policy_id','source_id','actor_id']
    for name in paths:
        p=Path(name)
        if not p.resolve().is_relative_to(source.resolve()):
            errors.append({'path':name,'error':'symlink outside source'});continue
        try: data=read(p)
        except (ValueError,UnicodeError,OSError) as exc:
            errors.append({'path':str(p.relative_to(source)),'error':str(exc)[:200]});continue
        digest=sha(p);files.append({'path':str(p.relative_to(source)),'sha256':digest})
        for ptr,row in walk(data):
            ref={'path':str(p.relative_to(source)),'sha256':digest,'selector':ptr}
            item={'source':ref,'record':row}
            for ident in {row[k] for k in idkeys if text(row.get(k))}:
                index[ident].append(item)
            category=classify(row)
            if category:
                inventory.append({**item,'id':identity(row),'category':category})
    return index,inventory,files,errors

def resolve(index,ident,origin,predicate=lambda x:True):
    matches=[m for m in index.get(ident,[]) if predicate(m['record'])]
    if not matches: raise ValueError('unresolved reference '+str(ident))
    # Prefer the closest source package. Tied differing records remain ambiguous.
    parent=Path(origin).parent.parts
    def rank(m):
        parts=Path(m['source']['path']).parent.parts
        common=0
        for a,b in zip(parts,parent):
            if a!=b:break
            common+=1
        return common
    best=max(map(rank,matches));matches=[m for m in matches if rank(m)==best]
    distinct={canonical(m['record']) for m in matches}
    if len(distinct)!=1: raise ValueError('ambiguous reference '+str(ident)+' ('+str(len(matches))+' source records)')
    return sorted(matches,key=lambda m:(m['source']['path'],m['source']['selector']))[0]

def owner(row):
    direct=row.get('owner_route',row.get('owner'))
    if text(direct):return direct
    routes=row.get('owner_routes',[])
    if strings(routes):return '; '.join(routes)
    if isinstance(routes,list):
        preferred=[x.get('owner') for x in routes if isinstance(x,dict) and x.get('responsibility') in ['product-meaning','product and capability meaning'] and text(x.get('owner'))]
        if len(set(preferred))==1:return preferred[0]
    return None

def normalize(item,index,engine,scope):
    row=item['record'];path=item['source']['path'];refs=[];notes=[]
    ancestor=row;seen={row.get('capability_id')}
    while not text(ancestor.get('product_ref')):
        parent_ref=ancestor.get('parent_capability_ref',ancestor.get('extends_capability_ref'))
        if not text(parent_ref):raise ValueError('missing explicit Product reference in Capability or its parent chain')
        if parent_ref in seen:raise ValueError('cyclic parent Capability references')
        seen.add(parent_ref)
        parent=resolve(index,parent_ref,path,lambda x:text(x.get('capability_id')) and (text(x.get('outcome')) or text(x.get('purpose'))))
        refs.append(parent['source']);ancestor=parent['record']
    if not text(row.get('product_ref')):
        row={**row,'product_ref':ancestor['product_ref']}
        notes.append('Product link inherited through explicit parent Capability references; no product inferred from directory.')
    product=resolve(index,row['product_ref'],'ontology/product/capability.json' if row['product_ref'] in ['CA2-PRODUCT-CYBERALCHEMY','CA2-PRODUCT-AGENT-REASONING-ENGINE'] else path,lambda x: x.get('role') in ['product','product_projection','parent_product'] or ('product_id' in x and any(k in x for k in ['purpose','plain_language'])))
    refs.append(product['source']);p=product['record']
    if row['product_ref'] in ['CA2-PRODUCT-CYBERALCHEMY','CA2-PRODUCT-AGENT-REASONING-ENGINE']: notes.append('Explicit candidate Product source selection: ontology/product/nodes.json; projections do not override the parent Product description.')
    name=p.get('name',p.get('label',p.get('display_name')));purpose=p.get('purpose',p.get('plain_language',p.get('meaning')));boundary=p.get('identity_boundary',p.get('forbidden_collapse'));powner=owner(p)
    if row['product_ref']=='CA2-PRODUCT-KNOWLEDGE-EXCHANGE-PROTOCOL' and (not boundary or not powner):
        thesis_path=SOURCE/'product/knowledge-exchange-protocol/product-thesis.record.json'
        thesis=read(thesis_path)
        if thesis['product_ref']!=row['product_ref']:raise ValueError('Thesis Product mismatch')
        boundary=boundary or '; '.join(thesis['boundaries']);powner=powner or thesis['owner_route']
        refs.append(binding(thesis_path));notes.append('Product boundary and declared owner completed from its explicit source Product Thesis.')
    if not all(map(text,[name,purpose,boundary,powner])):raise ValueError('Product lacks name, purpose, identity boundary or owner route')
    own=owner(row)
    if not own:raise ValueError('missing unambiguous Capability owner route')
    outcome=row.get('outcome',row.get('purpose'));exclusions=row.get('exclusions',row.get('non_goals',row.get('excluded_effects')))
    if not text(outcome) or not strings(exclusions):raise ValueError('missing outcome or exclusions')
    conditions=row.get('acceptance_conditions',row.get('acceptance_criteria',row.get('invariants')))
    if not strings(conditions):
        if not text(row.get('obligation_registry_ref')):raise ValueError('missing acceptance conditions or linked obligations')
        obligations=resolve(index,row['obligation_registry_ref'],path,lambda x:isinstance(x.get('obligations'),list) or strings(x.get('checks')) or (x.get('kind',x.get('role')) in ['obligation-registry','obligation_registry'] and text(x.get('meaning'))))
        if obligations['record'].get('capability_ref',row['capability_id'])!=row['capability_id']:raise ValueError('obligations belong to another Capability')
        conditions=[o if isinstance(o,str) else o.get('statement') if isinstance(o,dict) else None for o in obligations['record']['obligations']] if 'obligations' in obligations['record'] else obligations['record']['checks'] if strings(obligations['record'].get('checks')) else [obligations['record']['meaning']]
        if obligations['record'].get('role')=='obligation_registry':
            container=read(SOURCE/obligations['source']['path'])
            rules=container.get('rules',[])
            if rules and all(isinstance(rule,dict) and text(rule.get('statement')) for rule in rules):
                conditions=[rule['statement'] for rule in rules]
                notes.append('Acceptance conditions use rules in the business ontology named by its obligation registry.')
            else:raise ValueError('obligation registry describes rules but supplies no structured statements')
        if not strings(conditions):raise ValueError('linked obligations lack acceptance statements')
        refs.append(obligations['source'])
    for field in ['participant_refs','consumer_refs','input_contract_refs','output_contract_refs','context_policy_refs']:
        if field not in row:notes.append(field+' not declared by this source shape');continue
        if not strings(row[field]):raise ValueError('empty or malformed '+field)
        for ident in row[field]:
            resolved=resolve(index,ident,'ontology/product/capability.json' if ident in ['CA2-ACTOR-HUMAN-PARTICIPANT','CA2-ACTOR-MACHINE-COLLABORATOR','CA2-ACTOR-WORK-OWNER'] else path,lambda x: any(k in x for k in ['role','node_id','statement','contract_id','policy_id','purpose','actor_id','meaning']))
            refs.append(resolved['source'])
    posture=row.get('lifecycle_posture',{});status=posture.get('status',row.get('status')) if isinstance(posture,dict) else None
    notes.append('Source lifecycle preserved verbatim; candidate storage does not activate it.')
    notes.append('Realization references preserved as unverified source metadata; no realization asserted.')
    base={'status':'candidate-unadmitted','authority_effect':'none','scope_ref':scope}
    pid='cav2:'+product['source']['path']+product['source']['selector']+'#'+row['product_ref']
    product_record={**base,'node_id':pid,'kind':'product','name':name,'purpose':purpose,'identity_boundary':boundary,'owner_ref':powner,'owner_route':powner}
    record={**base,'node_id':'cav2:'+path+item['source']['selector']+'#'+row['capability_id'],'kind':'product-capability','product_ref':pid,'owner_ref':own,'outcome':outcome,'exclusions':exclusions,'acceptance_conditions':conditions}
    engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':[product_record,record],'relations':[]})
    return {'product':product_record,'capability':record,'resolved_sources':refs,'notes':notes,'source_lifecycle':status}

def main():
    registry=load_registry();scope=registry['scope']
    sys.path.insert(0,str(ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
    import engine
    index,inventory,files,errors=discover(SOURCE)
    results=[];imports=[]
    for item in inventory:
        result={k:item[k] for k in ['id','category','source']}
        if item['category']!='declaration':
            result.update(status='listed-not-product-instance',reason='Reference, ontology concept or other capability family; no Product Capability instance inferred.')
        elif any(part in ['fixtures','tests','test','generated','gen'] for part in Path(item['source']['path']).parts):
            result.update(status='example-not-imported',reason='Explicit example/test/generated path retained in inventory.')
        else:
            try:
                normalized=normalize(item,index,engine,scope)
                result.update(status='imported-candidate',reason='Required candidate fields and declared reference checks passed.')
                entry=next(e for e in registry['entries'] if e['target_id']=='type.product-capability')
                imports.append({**result,**normalized,'contract':entry['contract'],'semantic_dependencies':entry['semantic_definition_bindings'],'source_record':item['record'],'authority_effect':'none','operational_use_authorized':False})
            except (ValueError,ValidationError,KeyError,TypeError) as exc:
                result.update(status='blocked',reason=str(exc).split('\n')[0])
        results.append(result)
    used={x['source']['path'] for x in imports} | {ref['path'] for x in imports for ref in x['resolved_sources']}
    changed=[]
    for ref in files:
        if not (SOURCE/ref['path']).exists() or sha(SOURCE/ref['path'])!=ref['sha256']:
            if ref['path'] in used:raise ValueError('Imported source drift: '+ref['path'])
            changed.append(ref['path'])
    for result in results:
        if result['source']['path'] in changed:result.update(status='changed-during-scan',reason='Source changed after observation; rerun this selection before import.')
    counts=dict(collections.Counter(x['status'] for x in results))
    report={'scope':scope,'registry_binding':{'path':'authority/decisions/migration-contracts/v1/registry.json','sha256':sha(ROOT/'authority/decisions/migration-contracts/v1/registry.json')},'scan':'All JSON files returned by rg --files --hidden -g !.git -g *.json; repository ignore rules apply. JSON objects recursively inspected. Markdown-only capabilities are outside machine-instance coverage.', 'json_files':len(files),'parse_errors':errors,'unrelated_files_changed_during_scan':changed,'counts':counts,'unique_ids':len({x['id'] for x in results}),'declaration_ids':len({x['id'] for x in results if x['category']=='declaration'}),'results':results,'operational_use_authorized':False}
    HERE.mkdir(parents=True,exist_ok=True)
    store=ROOT/'.local/capability-inventory-import-0008'
    if store.exists():raise ValueError('Store exists; preserve it and create successor')
    store.mkdir(parents=True)
    for name,value in [('inventory.json',report),('source-manifest.json',files),('imports.json',imports)]:
        payload=json.dumps(value,indent=2,sort_keys=True)+'\n';(HERE/name).write_text(payload)
        if name=='imports.json':(store/name).write_text(payload)
    summaries='; '.join(str(v)+' '+k for k,v in counts.items())
    cards=[]
    for x in results:
        cards.append('<article><h2>'+html.escape(x['id'])+'</h2><p>'+html.escape(x['status'])+' -> '+html.escape(x['reason'])+'</p><small>'+html.escape(x['source']['path']+x['source']['selector'])+'</small></article>')
    (HERE/'REVIEW.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Capability inventory and import</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:20px;background:#f3f5f7}article{background:white;padding:15px;margin:12px 0;border-radius:8px}h2{font-size:18px}input{padding:12px;width:90%}small{overflow-wrap:anywhere}</style><h1>Capability inventory and import</h1><p>'+html.escape(summaries)+'</p><p>Source declarations -> required data and reference checks -> isolated candidate import. No Team instance or implementation is required. Variants retain separate source identities.</p><p>'+html.escape(report['scan'])+'</p><input id="q" placeholder="Filter by capability, status or source" aria-label="Filter results">'+''.join(cards)+'<script>document.getElementById("q").oninput=e=>document.querySelectorAll("article").forEach(a=>a.hidden=!a.textContent.toLowerCase().includes(e.target.value.toLowerCase()))</script></html>')
    table=['| Capability | Result | Source |','|---|---|---|']
    table += ['| '+x['id'].replace('|','\\|')+' | '+x['status']+': '+x['reason'].replace('|','\\|')+' | '+x['source']['path']+x['source']['selector']+' |' for x in results]
    (HERE/'README.md').write_text('# Capability inventory and import\n\nSource declarations -> required data and reference checks -> isolated candidate import.\n\n'+summaries+'.\n\n'+report['scan']+' Parse errors: '+str(len(errors))+'.\n\n[Searchable review](REVIEW.html). [Exact results](inventory.json). [Imported candidates and original source records](imports.json).\n\nNo Team instance or implementation is required. Product references and acceptance conditions are required. Candidate Definitions retain their status; no operational use is authorized. Different source versions are not merged or selected as globally current. source-manifest.json records observed bytes; inventory.json identifies unrelated files that changed during the scan. Every imported source and resolved dependency was rechecked unchanged.\n\n## Remaining gaps\n\nBlocked rows state their first actionable gap. Non-instance references are listed for completeness and are not silently converted to instances. Full source lifecycle and realization claims are retained as metadata, not activated.\n\n'+'\n'.join(table)+'\n')
    print(json.dumps({'json_files':len(files),'counts':counts,'unique_ids':report['unique_ids'],'declaration_ids':report['declaration_ids'],'parse_errors':len(errors)}))
if __name__=='__main__':main()
