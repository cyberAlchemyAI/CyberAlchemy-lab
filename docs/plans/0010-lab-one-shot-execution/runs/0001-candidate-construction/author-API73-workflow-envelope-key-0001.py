"""Preserve production contracts; align preparation test envelope to proposal key."""
import ast,json,shutil
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4];BASE=ROOT/'product/lab/release-candidates/v1/interface'
def main():
    old=BASE/'api-v72';api=BASE/'api-v73'
    assert not api.exists() and not (BASE/'lesson-host-composition-v23').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(old,api,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v22',BASE/'lesson-host-composition-v23',ignore=ignore)
    p=BASE/'lesson-host-composition-v23/host.py';s=p.read_text();assert s.count('api-v72/service.py')==1;p.write_text(s.replace('api-v72/service.py','api-v73/service.py'))
    p=api/'lesson_selection.py';s=p.read_text();assert s.count('lesson-host-composition-v22')==1;p.write_text(s.replace('lesson-host-composition-v22','lesson-host-composition-v23'))
    p=api/'test_workflow_composition.py';s=p.read_text();needle="        call = F.call(service.channel.context, 'lab.status', H.cut(self.view))"
    assert s.count(needle)==1
    s=s.replace(needle,"        if name == 'change.prepare': key = message['idempotency_key']\n"+needle)
    p.write_text(s)
    for p in api.rglob('*.py'):ast.parse(p.read_bytes())
    print(json.dumps({'result':'AUTHORED','version':73,'production_contract_changed':False,'runtime_qualified':False,'authority_effect':'none'}))
if __name__=='__main__':main()
