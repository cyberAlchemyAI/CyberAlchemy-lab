"""Check exact declared contract identities; do not infer aliases from similar names."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
SOURCE=ROOT.parent/'cyberAlchemy-v2'
sys.path.insert(0,str(ROOT/'tooling/importers'))
from capability_inventory_import import read,walk,sha

def run():
    cap_path=SOURCE/'commercial-agent-access/product-capability.json'
    cap=read(cap_path);nodes=read(SOURCE/'commercial-agent-access/nodes.json')['nodes']
    bindings=[]
    for name in ['product-capability.json','nodes.json','product-capability-support.json','residue.json','README.md']:
        p=SOURCE/'commercial-agent-access'/name
        bindings.append({'path':str(p.relative_to(SOURCE)),'sha256':sha(p)})
    results=[];searched={};errors=[]
    for field in ['input_contract_refs','output_contract_refs','context_policy_refs']:
        for ident in cap[field]:
            search=subprocess.run(['rg','-l','--hidden','-g','!.git','-g','*.json','-F',ident,str(SOURCE)],capture_output=True,text=True)
            if search.returncode not in [0,1]:raise ValueError(search.stderr)
            exact=[]
            for file in sorted(search.stdout.splitlines()):
                p=Path(file)
                if not p.resolve().is_relative_to(SOURCE.resolve()):raise ValueError('Source escapes repository')
                try:data=read(p)
                except (ValueError,UnicodeError) as exc:errors.append({'path':str(p.relative_to(SOURCE)),'error':str(exc)});continue
                searched[str(p.relative_to(SOURCE))]=sha(p)
                for ptr,row in walk(data):
                    if any(row.get(key)==ident for key in ['id','node_id','contract_id','policy_id']):
                        exact.append({'path':str(p.relative_to(SOURCE)),'sha256':sha(p),'selector':ptr,'record':row})
            # Similar names are review leads only, never admitted aliases.
            local_id=ident.replace('CA2-CAP-CONTRACT-','CAA-CONTRACT-').replace('CA2-CAP-POLICY-','CAA-POLICY-')
            related=[n for n in nodes if n['node_id']==local_id]
            results.append({'field':field,'requested_id':ident,'exact_definitions':exact,'status':'exact-identity-found' if exact else 'missing-exact-contract','local_review_leads':related,'alias_established':False})
    for path,digest in searched.items():
        if sha(SOURCE/path)!=digest:raise ValueError('Searched source changed: '+path)
    for ref in bindings:
        if sha(SOURCE/ref['path'])!=ref['sha256']:raise ValueError('Source changed')
    result={'capability_id':cap['capability_id'],'result':'CHECK-COMPLETE','import_status':'blocked','references_checked':len(results),'missing_exact_contracts':sum(not x['exact_definitions'] for x in results),'references':results,'search_scope':'Exact identity declarations in all non-ignored JSON files found by rg, including hidden files except .git. Similar names and string references do not establish aliases.','parse_errors':errors,'source_bindings':bindings,'searched_files':searched,'authority_effect':'none','existing_imported_candidates':24,'remaining_blocked_declarations':21,'finding':'Local candidate concept descriptions use different IDs. The source explicitly records missing KEP service-exchange and request/response contracts; this is not repaired by silently equating the names.','next_work':'Construct the missing candidate contract bundle with explicit identity mappings and request/response/failure, authorization, containment and receipt boundaries; preserve the separate KEP semantic-admission prerequisite.'}
    (HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['result','references_checked','missing_exact_contracts','import_status']}))
if __name__=='__main__':run()
