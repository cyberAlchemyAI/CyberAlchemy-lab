"""Select actual mapped Project endpoint and actual signed Typed Relation body."""
import json
from pathlib import Path
import shutil
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v63';API=BASE/'api-v64'
def replace(p,a,b):
    value=p.read_text();assert value.count(a)==1,(p,a);p.write_text(value.replace(a,b,1))
def main():
    assert not API.exists() and not (BASE/'lesson-host-composition-v14').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(OLD,API,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v13',BASE/'lesson-host-composition-v14',ignore=ignore)
    replace(BASE/'lesson-host-composition-v14/host.py','api-v63/service.py','api-v64/service.py')
    replace(API/'lesson_selection.py','lesson-host-composition-v13','lesson-host-composition-v14')
    replace(API/'challenge_fixture.py',"project=pick(view,'project')", "project=pick_endpoint(view,'project')")
    replace(API/'challenge_fixture.py','def current_body(view,subject):', '''def pick_endpoint(view,kind):
    rows=[s for s in view.subjects.values() if s['effective_state'] in ('admitted-current','local-admitted-current')
        and view.handle.operations.endpoint_kind(s,view.data['projection'])==kind]
    P.source.require(rows,'actual mapped current challenge endpoint missing: '+kind)
    return sorted(rows,key=lambda s:s['version_ref'])[0]
def current_body(view,subject):''')
    replace(API/'challenge_submission.py', """        template_path='authority/relation-kinds/candidates/0006-definition-complete-instances/instances/typed-relations/challenges.json'
        template=copy.deepcopy(self.view.data['projection']['documents'][template_path])""", """        typed_rows=[s for s in self.view.subjects.values() if s['kind']=='typed-relation'
            and s['carrier_ref']==typed_carrier and s['effective_state'] in ('admitted-current','local-admitted-current')]
        require(typed_rows,'actual current Typed Relation template missing')
        template=P.frame_parse(M.record_bytes(self.view,sorted(typed_rows,key=lambda s:s['version_ref'])[0])[0])""")
    print(json.dumps({'result':'AUTHORED','successor':'api-v64','authority_effect':'none'}))
if __name__=='__main__':main()
