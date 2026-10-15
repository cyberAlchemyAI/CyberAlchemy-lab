"""Correct one original fixture's opaque connection reference; retain guards."""
import ast
import json
from pathlib import Path
import shutil

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD,API=BASE/'api-v84',BASE/'api-v85'


def replace(path,before,after):
    text=path.read_text();assert text.count(before)==1,(path,before)
    path.write_text(text.replace(before,after,1))


def main():
    assert not API.exists() and not (BASE/'lesson-host-composition-v35').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(OLD,API,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v34',BASE/'lesson-host-composition-v35',ignore=ignore)
    replace(BASE/'lesson-host-composition-v35/host.py','api-v84/service.py','api-v85/service.py')
    replace(API/'lesson_selection.py','lesson-host-composition-v34','lesson-host-composition-v35')
    replace(API/'test_machine_transport.py',"        request=self.inspection(context['session_ref'])",
            "        request=self.inspection(context['session_ref'])\n        request['caller_context_ref']=context['context_ref']")
    for path in API.glob('*.py'):ast.parse(path.read_text())
    print(json.dumps({'result':'AUTHORED','authored_handlers':23,'remaining_handlers':11,
                      'runtime_qualified':False,'test_fixture_binding_revisions':1,'authority_effect':'none'}),flush=True)


if __name__=='__main__':main()
