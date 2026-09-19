"""Preserve explicit NFT requirements and audit unresolved source identities."""
import collections,copy,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';PREV=HERE.parent/'0023-governed-domain-model-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
ID='CA2-CAP-GENERATE-AND-OPTIONALLY-MINT-DEFINITION-NFT'
def bind(p,root=ROOT):return {'path':str(p.relative_to(root)),'sha256':tool.sha(p)}
def dump(p,obj):
    text=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=text:raise ValueError('Preserve existing artifact')
    p.write_text(text)
def review():
    for b in tool.read(PREV/'verification.json')['bindings']:
        if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Historical drift')
    old=tool.read(PREV/'inventory.json');row=next(r for r in old['results'] if r['id']==ID and r['category']=='declaration');path=SOURCE/row['source']['path']
    if tool.sha(path)!=row['source']['sha256']:raise ValueError('Capability drift')
    cap=tool.read(path);candidate_path=path.parent/'product-capability-candidate.json';candidate=tool.read(candidate_path)
    if candidate['capability']['sha256']!=tool.sha(path):raise ValueError('Candidate binding drift')
    pred=candidate['predecessors']['definition_pack'];pack_path=(path.parent/pred['path']).resolve()
    if tool.sha(pack_path)!=pred['sha256']:raise ValueError('Definition pack drift')
    pack=tool.read(pack_path)
    refs=[cap['product_ref'],cap['obligation_registry_ref']]
    for f in ['participant_refs','consumer_refs','input_contract_refs','output_contract_refs','context_policy_refs']:refs+=cap[f]
    cmd=['rg','-l','--hidden','-g','!.git','-g','*.json','-F']
    for ident in refs:cmd+=['-e',ident]
    cmd+=[str(SOURCE)]
    files=subprocess.check_output(cmd,text=True).splitlines();bindings=[];declarations={ident:[] for ident in refs};errors=[]
    for f in sorted(files):
        p=Path(f);bindings.append(bind(p,SOURCE))
        try:doc=tool.read(p)
        except ValueError as exc:errors.append({'path':str(p.relative_to(SOURCE)),'error':str(exc)});continue
        for ptr,obj in tool.walk(doc):
            for k in ['id','node_id','product_id','registry_id','contract_id','policy_id','actor_id','identity_id']:
                ident=obj.get(k)
                if isinstance(ident,str) and ident in declarations:declarations[ident].append({'path':str(p.relative_to(SOURCE)),'selector':ptr,'key':k})
    for b in bindings:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Search source drift')
    registry=tool.load_registry();prepared={'node_id':'cav2:'+row['source']['path']+'#'+ID,'kind':'product-capability','status':'candidate-unadmitted','scope_ref':registry['scope'],'authority_effect':'none','owner_ref':tool.owner(cap),'outcome':cap['outcome'],'exclusions':cap['exclusions'],'acceptance_conditions':pack['goal_limits']}
    return {'id':ID,'status':'prepared-not-importable','imported':False,'authority_effect':'none','source_record':cap,'prepared_fields':prepared,'mapping':{'acceptance_conditions':'Exact definition pack /goal_limits; no resolution of open choices implied'},'source_bindings':[bind(path,SOURCE),bind(candidate_path,SOURCE),bind(pack_path,SOURCE)],'declared_construction_state':candidate['construction_state'],'source_blockers':candidate['blockers'],'open_product_questions':pack['open_questions_and_conflicts'],'reference_audit':declarations,'unresolved_identities':[k for k,v in declarations.items() if not v],'search_bindings':bindings,'parse_errors':errors,'search_scope':'Nonignored JSON files matching exact reference IDs; identity-key declarations only. This does not prove absence of prose proposals.'}
if __name__=='__main__':
    result=review();dump(HERE/'result.json',result);old=tool.read(PREV/'inventory.json');new=copy.deepcopy(old)
    for row in new['results']:
        if row['id']==ID and row['category']=='declaration':row.update(resolution_state='reviewed-needs-product-and-contract-decisions',reason='Source explicitly lacks Product thesis and complete contract meanings; candidate requirements preserved, unresolved identities audited.',review=bind(HERE/'result.json'))
    assert new['counts']==old['counts']
    dump(HERE/'inventory.json',new)
    print(json.dumps({'status':result['status'],'unresolved_identities':len(result['unresolved_identities']),'search_files':len(result['search_bindings']),'prepared_requirements':len(result['prepared_fields']['acceptance_conditions'])}))
