"""Pure AST/byte review; no API, runner, observer, Session or lease imports."""
import ast, hashlib, json, os, types
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T05'
P=BASE/'machine-read-diagnostic-preparation-0004'
OLD=BASE/'machine-read-development-preparation-0003'
OWN=Path(__file__).parent
HH='1801946a1c5489961d7223b6888bccd93ed628e984c6a147e6ff0010f595306e'
MF='42320284eecba299e39f4aa7cba6993eaf89921fd703cb7ae36c69619bf351c9'
sha=lambda b:hashlib.sha256(b).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def main():
    fd0=len(os.listdir('/proc/self/fd'))
    raw=(P/'capture.py').read_bytes()
    need(sha(raw)=='b41f1914e0d6a9be125e228525ca92d1b28d853be79c118adffc040bcf01f0fa','capture bootstrap differs')
    cap=types.ModuleType('_T05_review_capture');cap.__file__=str(P/'capture.py')
    exec(compile(raw,cap.__file__,'exec'),cap.__dict__)
    capture=cap.capture_path
    handoff=capture(P/'HANDOFF.json',HH);manifest=capture(P/'source-manifest.json',MF)
    rows=json.loads(manifest)['files'];need(len(rows)==21,'exact21 rows required')
    cache={}
    for row in rows:
        raw=capture(ROOT/row['path'],row['sha256']);need(len(raw)==row['size_bytes'],'size differs')
        cache[row['path']]=raw
    original=capture(ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17/test_machine_transport.py')
    helpers=['capture.py','owned_observer.py','owned_parent_sessions.py','owned_output.py','owned_machine_tests.py']
    for leaf in helpers:need(cache[str((P/leaf).relative_to(ROOT))]==cache[str((OLD/leaf).relative_to(ROOT))],'original helper changed')
    tests=ast.parse(cache[str((P/'owned_machine_tests.py').relative_to(ROOT))])
    def methods(tree):
        return {n.name:ast.dump(n,include_attributes=False)for c in tree.body if isinstance(c,ast.ClassDef)and c.name=='MachineTransport'for n in c.body if isinstance(n,ast.FunctionDef)and n.name.startswith('test_')}
    need(methods(tests)==methods(ast.parse(original))and len(methods(tests))==14,'original14 AST differs')
    new=ast.parse(cache[str((P/'run_machine_diagnostic_v4.py').relative_to(ROOT))])
    old=ast.parse(cache[str((OLD/'run_machine_development_v3.py').relative_to(ROOT))])
    functions=lambda t:{n.name:n for n in t.body if isinstance(n,ast.FunctionDef)}
    n=functions(new);o=functions(old)
    unchanged=[]
    for name in o:
        if name not in {'shape','execute'}:
            need(ast.dump(n[name],include_attributes=False)==ast.dump(o[name],include_attributes=False),'unchanged function differs:'+name)
            unchanged.append(name)
    need([ast.dump(x,include_attributes=False)for x in n['shape'].body[2:]]==[ast.dump(x,include_attributes=False)for x in o['shape'].body[2:]],'shape guards beyond explicit mode changed')
    # Entry/exit guard construction and all statements before nested Result are identical.
    nt=next(v for v in n['execute'].body if isinstance(v,ast.Try));ot=next(v for v in o['execute'].body if isinstance(v,ast.Try))
    until_result=lambda t:[ast.dump(v,include_attributes=False)for v in t.body[:next(i for i,v in enumerate(t.body)if isinstance(v,ast.ClassDef)and v.name=='Result')]]
    need(until_result(nt)==until_result(ot),'runtime entry guard/helper import path changed')
    need(ast.dump(nt.finalbody[1],include_attributes=False)==ast.dump(ot.finalbody[1],include_attributes=False),'full exit guards changed')
    resultclass=next(v for v in nt.body if isinstance(v,ast.ClassDef)and v.name=='Result')
    save=next(v for v in resultclass.body if isinstance(v,ast.FunctionDef)and v.name=='save_case')
    need(any(isinstance(v,ast.Call)and isinstance(v.func,ast.Attribute)and v.func.attr=='write'for v in ast.walk(save)),'per-test durable output absent')
    for row in rows:need(capture(ROOT/row['path'],row['sha256'])==cache[row['path']],'selected input changed')
    need(capture(P/'HANDOFF.json',HH)==handoff and capture(P/'source-manifest.json',MF)==manifest,'frozen metadata changed')
    need(capture(ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17/test_machine_transport.py')==original,'original test changed')
    need(len(os.listdir('/proc/self/fd'))==fd0,'descriptor imbalance')
    value={'result':'PASS-pure-static-review','authority_effect':'none','handoff_sha256':HH,'manifest_sha256':MF,'entry_exit_rows':21,'five_helper_bytes_unchanged':True,'original_test_AST_count':14,'unchanged_top_level_functions':unchanged,'entry_and_full_exit_guards_AST_identical':True,'FD_delta':0,'runner_API_native_Session_or_lease_called':False,'full14_or_diagnostic_runtime_qualified':False,'original_test_sha256':sha(original)}
    with (OWN/'static-result-0001.json').open('x')as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(value,sort_keys=True))
if __name__=='__main__':main()
