"""Version the added inspection case with its original required read budget.

Classification requests have no budget field. The added inspection request uses
the actual authenticated context's limits, with zero permitted actions. Host and
all sixteen prior classification case bodies stay immutable.
"""
import ast
import hashlib
import json
from pathlib import Path
import shutil

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD=BASE/'api57-classification-checks-v1';CHECK=BASE/'api57-classification-checks-v2'
API=BASE/'api-v57'
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def methods(path):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes()))
        if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not CHECK.exists()
    shutil.copytree(OLD,CHECK,ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json'))
    path=CHECK/'test_classification_api.py';text=path.read_text()
    before="'budget':{**request['message']['budget'],'max_actions':0},'authority_effect':'none',"
    after="""'budget':{'max_actions':0,
                'max_input_bytes':host.channel.context['limits']['max_request_bytes'],
                'max_output_bytes':host.channel.context['limits']['max_response_bytes'],
                'deadline':host.channel.context['limits']['deadline']},'authority_effect':'none',"""
    assert text.count(before)==1;path.write_text(text.replace(before,after,1))
    original=methods(OLD/'test_classification_api.py');revised=methods(path)
    changed=[name for name in original if original[name]!=revised[name]]
    assert changed==['test_17_pending_native_evidence_is_inspectable_and_tamper_refused']
    files=sorted(p for p in CHECK.rglob('*') if p.is_file())
    files += [API/'source-manifest.json',API/'contract-profile.json',API/'test_classification_api.py',
        OLD/'source-manifest.json',Path(__file__).resolve()]
    selected={'schema_version':'lab-separate-classification-check-source/v1-candidate',
        'files':[bind(p) for p in files],'original_classification_methods':16,
        'previous16_successor_methods_unchanged':True,'changed_methods':changed,
        'actual_runtime_qualified':False,'authority_effect':'none','actual_owner_outcome':None}
    with (CHECK/'source-manifest.json').open('x') as stream:json.dump(selected,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'FROZEN-CHECK-SUCCESSOR','check_source_binding':bind(CHECK/'source-manifest.json'),
        'host_source_binding':bind(API/'source-manifest.json'),'changed_methods':changed,
        'previous16_methods_unchanged':True,'actual_runtime_qualified':False}),flush=True)

if __name__=='__main__':main()
