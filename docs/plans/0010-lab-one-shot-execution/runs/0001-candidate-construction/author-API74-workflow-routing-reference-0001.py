"""Preserve production contracts; use the exact original private review protocol namespace."""
import ast,json,shutil
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4];BASE=ROOT/'product/lab/release-candidates/v1/interface'
def main():
    old=BASE/'api-v73';api=BASE/'api-v74'
    assert not api.exists() and not (BASE/'lesson-host-composition-v24').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(old,api,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v23',BASE/'lesson-host-composition-v24',ignore=ignore)
    p=BASE/'lesson-host-composition-v24/host.py';s=p.read_text();assert s.count('api-v73/service.py')==1;p.write_text(s.replace('api-v73/service.py','api-v74/service.py'))
    p=api/'lesson_selection.py';s=p.read_text();assert s.count('lesson-host-composition-v23')==1;p.write_text(s.replace('lesson-host-composition-v23','lesson-host-composition-v24'))
    p=api/'workflow_fixture.py';s=p.read_text();needle="'protocol:R03-composed-workflow:'"
    assert s.count(needle)==1;s=s.replace(needle,"'protocol:R03-review-workflow:'")
    needle="        raw = P.compact(routing)"
    assert s.count(needle)==1
    s=s.replace(needle,"        schema = P.frame_parse((Path(__file__).resolve().parent / 'review-routing.schema.json').read_bytes())\n        P.Draft202012Validator(schema, registry=schemas.registry, format_checker=schemas.checker).validate(routing)\n"+needle)
    p.write_text(s)
    for p in api.rglob('*.py'):ast.parse(p.read_bytes())
    print(json.dumps({'result':'AUTHORED','version':74,'production_contract_changed':False,'runtime_qualified':False,'authority_effect':'none'}))
if __name__=='__main__':main()
