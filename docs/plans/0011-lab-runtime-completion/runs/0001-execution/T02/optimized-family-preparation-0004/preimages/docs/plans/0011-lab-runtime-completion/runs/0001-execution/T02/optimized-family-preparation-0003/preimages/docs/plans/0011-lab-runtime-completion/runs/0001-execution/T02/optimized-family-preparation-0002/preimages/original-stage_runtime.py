"""Author byte-bound runtime postimages for root's shared API integration.

This does not import a Service, open a resource, freeze an API or confer any
permission. The constructor retains exact independently selected class paths.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
API=HERE.parent/'api-integration-v16'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def replace_once(text,old,new):
    if text.count(old)!=1:raise ValueError('absent/ambiguous runtime selector '+old)
    return text.replace(old,new,1)
def write(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:f.write(value if isinstance(value,str) else json.dumps(value,indent=2,sort_keys=True)+'\n')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--instance',required=True);a=parser.parse_args()
    family=HERE/'instances'/a.instance
    if not family.is_dir() or family.parent!=HERE/'instances':raise ValueError('explicit owned instance required')
    source=family/'source';reader=family/'reader';mapped=family/'mapped';context=family/'context';out=family/'runtime'
    required=[source/'source-manifest.json',source/'packages/0001/manifest.json',reader/'source-manifest.json',mapped/'source-manifest.json',mapped/'packages/0001/manifest.json',context/'source-manifest.json',context/'packages/0001/manifest.json',context/'implementation-binding.json']
    if not all(p.is_file() for p in required):raise ValueError('actual native source/reader/mapper/Context packages required first')
    descriptor={'schema_version':'lab-current-session-runtime-selection/v1-candidate','instance':a.instance,'public_source_name':'completion-current-participation:'+a.instance,'source_binding':binding(required[0]),'source_package_binding':binding(required[1]),'reader_binding':binding(required[2]),'mapper_binding':binding(required[3]),'mapper_package_binding':binding(required[4]),'context_source_binding':binding(required[5]),'context_package_binding':binding(required[6]),'implementation_binding':binding(required[7]),'period_binding':binding(source/'packages/0001/period.json'),'reader_root':reader.relative_to(ROOT).as_posix(),'reader_class':'CurrentFixtureReader','context_entrypoint_ref':context.relative_to(ROOT).as_posix()+'/build.py#generate','fixture_only':True,'actual_human_review':False,'actual_owner_outcome':None,'authority_effect':'none','shared_API_qualified':False}
    template=API/'fixture_context_sessions.py';text=template.read_text()
    text=replace_once(text,'D=source.source8_fixture_delivery()','D=source.current_session_fixture_delivery()')
    text=replace_once(text,"DELIVERY_PIN='0afe7a76c15a26df9f10b0691fb240f6955f772e778e58820cc0d6dc0d0565d3'","DELIVERY_PIN="+repr(descriptor['context_source_binding']['sha256']))
    text=replace_once(text,"MAPPING_PIN='d71e2064fd4c183416bf6f562bd41555ce9047bbbcc5be4bec06821edacb75e1'","MAPPING_PIN="+repr(descriptor['mapper_package_binding']['sha256']))
    for filename in ['reader.py','adapter.py','model.py']:
        text=replace_once(text,"HERE.parent/'source8-lesson-fixture-reader-v4-action-0148/"+filename+"'","ROOT/"+repr((reader/filename).relative_to(ROOT).as_posix()))
    text=replace_once(text,'from .source8_machine_context_scope import generate','from .current_machine_context_scope import generate')
    ast.parse(text);post=out/'postimages/current_context_sessions.py';write(post,text)
    original_scope=API/'source8_machine_context_scope.py';scope=original_scope.read_text()
    scope=replace_once(scope,"Path(C.__file__).name in ('source8_context_sessions.py','fixture_context_sessions.py')","Path(C.__file__).name == 'current_context_sessions.py'")
    ast.parse(scope);scope_post=out/'postimages/current_machine_context_scope.py';write(scope_post,scope)
    descriptor['runtime_postimages']=[binding(post),binding(scope_post)]
    descriptor['original_templates']=[binding(template),binding(original_scope)]
    descriptor['root_required_api_changes']={
        'source_bridge':['exact independent descriptor pin','current_session_fixture_delivery selects actual context/build.py namespace','actual CurrentFixtureReader factory and local SignedSources/Inspection origin','current explicit source/reader/producer markers and cut equivalence'],
        'auth_and_schema':['closed exact public source enum','current new Principal/Assignment/period inputs from descriptor','source-specific private Source8-equivalent policy; fresh nonce/signature/currentness checks'],
        'service':['explicit current_context_sessions module selection','actual runtime class selection in parent borrow/attachment','actual code_files guards for both postimages'],
        'read_and_machine':['guarded_candidate/read actual namespace and source binding selection','Machine runtime filename/origin closed selection','Machine source_facts current producer/read-scope closure'],
        'lesson':['exact current Context implementation/rule/review/native Lesson inventory','current runtime filename allowlist for LessonHost and application preparation; preserve original exclusions']}
    write(out/'runtime-selection.json',descriptor)
    print(json.dumps({'result':'STAGED-runtime-postimages-UNQUALIFIED','selection_binding':binding(out/'runtime-selection.json'),'postimages':descriptor['runtime_postimages']}))
if __name__=='__main__':main()
