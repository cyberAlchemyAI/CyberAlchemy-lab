"""Import revised collectible definition-card candidate with selected collection lock rule."""
import copy,collections,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';PROPOSAL=HERE.parent/'0034-definition-card-editions-proposal';PREV=HERE.parent/'0032-trusted-dataset-product-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
sys.path.insert(0,str(ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
import engine
ID='CA2-CAP-GENERATE-AND-OPTIONALLY-MINT-DEFINITION-NFT'
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,obj):
    text=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=text:raise ValueError('Preserve existing artifact')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def revise_text(s):
    return s.replace('Proposed v1 rule: freeze the collection manifest before its first mint; changed artwork or edition sizes require a new explicitly identified collection.', 'The first mint locks the collection artwork, variants and edition sizes; changed artwork or additional copies require a new explicitly identified collection.')
def prepare():
    for folder in [PREV,PROPOSAL]:
        for b in tool.read(folder/'verification.json')['bindings']:
            if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Previous artifact drift')
    registry=tool.load_registry();proposal=tool.read(PROPOSAL/'proposal.json')
    for b in proposal['source_bindings']:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Source drift')
    selection={'user_answer':'yes','question':'Approve locking image, variants and copy counts at the first mint, with changed artwork or additional copies requiring a new collection, then finish the candidate import?','selected_rule':'First mint locks collection artwork, variants and edition sizes. Changes require a new collection.','prior_user_direction':['configurable visual variants of the same image','collectible cards that can be traded'],'scope':'Product behavior and candidate import only','authority_effect':'none','not_selected':['actual artwork or copy counts','runtime providers or marketplace','mint, payment, deployment or transfer execution']}
    dump(HERE/'selection.json',selection)
    product=copy.deepcopy(proposal['product']);cap=copy.deepcopy(proposal['capability'])
    # This successor changes source Product meaning, so give it a local candidate identity.
    cap['node_id']='lab:definition-card-editions#'+ID
    cap['acceptance_conditions']=[revise_text(s) for s in cap['acceptance_conditions']]
    refs=[]
    for b in proposal['reference_bindings']:
        ref=tool.read(ROOT/b['path']);ref['meaning']=revise_text(ref['meaning']);ref.update(status='candidate-unadmitted',source_or_proposal='Local successor candidate semantic binding; user-directed card variants/trading and selected collection lock. Not a recovered source declaration.')
        path=HERE/'references'/(ref['id']+'.json');dump(path,ref);refs.append(bind(path))
    original=tool.read(SOURCE/'product/definition-nft/product-capability.json')
    needed=[original['product_ref'],original['obligation_registry_ref']]+sum([original[k] for k in ['participant_refs','consumer_refs','input_contract_refs','output_contract_refs','context_policy_refs']],[])
    actual={tool.read(ROOT/b['path'])['id'] for b in refs}
    if actual!=set(needed) or len(refs)!=len(needed):raise ValueError('Incomplete reference bindings')
    engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':[product,cap],'relations':[]})
    entry=next(e for e in registry['entries'] if e['target_id']=='type.product-capability')
    return {'id':ID,'status':'imported-candidate','product':product,'capability':cap,'source_record':original,'source':{**proposal['source_bindings'][0],'selector':''},'source_bindings':proposal['source_bindings'],'proposal_predecessor':bind(PROPOSAL/'proposal.json'),'selection':bind(HERE/'selection.json'),'candidate_dependency_bindings':refs,'contract':entry['contract'],'semantic_dependencies':entry['semantic_definition_bindings'],'authority_effect':'none','operational_use_authorized':False,'scope_change':proposal['scope_change'],'notes':['Local successor changes source one-per-version concept to configurable collectible editions and card transfer. Source record retained verbatim.','First mint locks artwork, variants and edition sizes. Actual artwork and quantities are per-collection inputs, not migration blockers.','Other detailed behavior is retained as the reviewable candidate baseline, not a claim that each detail was separately approved.','Trading mechanics, executable API schemas, runtime implementation and security remain separate.','No mint, trade, payment, publication or deployment performed.']}
if __name__=='__main__':
    result=prepare();prior=tool.read(PREV/'imports.json');assert not any(i['id']==ID for i in prior);combined=prior+[result];nodes={}
    for item in combined:
        for n in [item['product'],item['capability']]:
            if n['node_id'] in nodes and nodes[n['node_id']]!=n:raise ValueError('Identity collision')
            nodes[n['node_id']]=n
    engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
    inventory=tool.read(PREV/'inventory.json');changed=0
    for row in inventory['results']:
        if row['id']==ID and row['category']=='declaration':
            assert row['status']=='blocked';row.update(status='imported-candidate',resolution_state='resolved-local-collectible-card-successor',reason='Local collectible-card Product candidate with 20 semantic bindings; user selected first-mint collection lock.',selection=bind(HERE/'selection.json'));changed+=1
    assert changed==1
    inventory['counts']=dict(collections.Counter(r['status'] for r in inventory['results']));inventory['counts'].setdefault('blocked',0)
    for name,obj in [('result.json',result),('imports.json',combined),('inventory.json',inventory)]:dump(HERE/name,obj)
    dump(ROOT/'.local/capability-inventory-import-0035/imports.json',combined)
    print(json.dumps(inventory['counts']))
