"""Validate bound-original historical Decisions without promoting authority."""
import json
from pathlib import Path
import shutil
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v64';API=BASE/'api-v65'
def replace(p,a,b):
    value=p.read_text();assert value.count(a)==1,(p,a);p.write_text(value.replace(a,b,1))
def main():
    assert not API.exists() and not (BASE/'lesson-host-composition-v15').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(OLD,API,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v14',BASE/'lesson-host-composition-v15',ignore=ignore)
    replace(BASE/'lesson-host-composition-v15/host.py','api-v64/service.py','api-v65/service.py')
    replace(API/'lesson_selection.py','lesson-host-composition-v14','lesson-host-composition-v15')
    replace(API/'challenge_submission.py',
        "        self.view.handle.operations.validate_record(body,'cal.artifact-type.'+row['kind']+'/v1',self.view.data['projection'])",
        """        # Bound-original is a historical document posture, never signed/current
        # membership or live authority. Retained carrier validation does not
        # authorize an endpoint or an owner outcome.
        self.view.handle.operations.validate_record(body,'cal.artifact-type.'+row['kind']+'/v1',
            self.view.data['projection'],allow_historical_carrier=True)""")
    print(json.dumps({'result':'AUTHORED','successor':'api-v65','authority_effect':'none'}))
if __name__=='__main__':main()
