"""Pure AST/metadata checks. Never import or call the capture writer."""
import ast,hashlib,json
from pathlib import Path

HERE=Path(__file__).absolute().parent
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')

def run():
    old=ast.parse((HERE/'preimages/capture_v5.py').read_bytes())
    new=ast.parse((HERE/'capture_v6.py').read_bytes())
    funcs=lambda t:{n.name:n for n in t.body if isinstance(n,ast.FunctionDef)}
    a,b=funcs(old),funcs(new);checks=[]
    changed={'publish','activate','main'}
    for name,node in a.items():
        if name not in changed:assert ast.dump(node,include_attributes=False)==ast.dump(b[name],include_attributes=False),name
    checks.append('all original capture5 helpers/family/closed-path/accounting functions retained except explicit main/activation/publication suffix')
    global_names={n.id for n in new.body if isinstance(n,ast.Assign)for n in n.targets if isinstance(n,ast.Name)}
    for name,fn in b.items():
        local={n.arg for n in fn.args.args}|{n.id for n in ast.walk(fn)if isinstance(n,ast.Name)and isinstance(n.ctx,ast.Store)}
        if name=='publish':assert 'lineage'in local and 'publication_predecessor'not in local
    checks.append('publication predecessor is a held function parameter; no stale outer lineage variable')
    text=ast.unparse(b['main'])
    for n in ('28597','28596','4125','3961','24497','24496','25','24472'):assert n in text,n
    checks.append('all capture5/current and original historical counts remain explicit')
    assert "old['path'] not in parent_by_path"in text and "set(prior_rows) <= set"in text
    checks.append('original24497 rows cannot be replacement targets; every28597 predecessor path retained')
    assert "predecessor['source-manifest.json']['snapshot_binding']"in text
    assert "predecessor['INPUT-ACCOUNTING.json']['snapshot_binding']"in text
    checks.append('new baseline is exact capture5 snapshots, historical capture4 metadata stays historical')
    activation=ast.unparse(b['activate'])
    assert "lab-T07-capture6-selection/v1-candidate"in activation and 'CAPTURE5_RESULT_SHA'in activation
    assert "'inputs', 'final_root_packet_binding', 'final_peer_review_binding'"in activation
    checks.append('unknown Root/component/peer selections refuse before capture6 activation')
    publication=ast.unparse(b['publish'])
    assert '.capture-0006-new'in publication
    assert publication.index("'SCHEMA-EXECUTION-DEPENDENCIES.json', 'contract-profile.json', 'INPUT-ACCOUNTING.json', 'source-manifest.json'")>=0
    checks.append('publication uses new exclusive suffix and Source-last order; no atomic multi-file transaction claim')
    source=(ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17/source-manifest.json').read_bytes()
    assert hashlib.sha256(source).hexdigest()=='ee969cc8c6b539aa3247d81c82322cb9e7aefd42188d63db0195e381cdad4cb1'
    checks.append('current shared Source metadata unchanged; no full row guard run')
    return {'result':'PASS-pure-capture6-plan-AST-controls','checks':checks,'count':len(checks),
        'writer_imported_or_executed':False,'API_Source_native_installed_guard_or_lease_executed':False,'authority_effect':'none','task_complete':False}

if __name__=='__main__':print(json.dumps(run(),sort_keys=True))
