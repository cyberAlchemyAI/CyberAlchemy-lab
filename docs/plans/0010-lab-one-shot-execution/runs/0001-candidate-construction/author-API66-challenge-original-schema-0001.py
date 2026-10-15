"""Bound-original document validation uses its captured historical schema only."""
import json
from pathlib import Path
import shutil
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v65';API=BASE/'api-v66'
def replace(p,a,b):
    value=p.read_text();assert value.count(a)==1,(p,a);p.write_text(value.replace(a,b,1))
def main():
    assert not API.exists() and not (BASE/'lesson-host-composition-v16').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(OLD,API,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v15',BASE/'lesson-host-composition-v16',ignore=ignore)
    replace(BASE/'lesson-host-composition-v16/host.py','api-v65/service.py','api-v66/service.py')
    replace(API/'lesson_selection.py','lesson-host-composition-v15','lesson-host-composition-v16')
    replace(API/'challenge_submission.py', """        # Bound-original is a historical document posture, never signed/current
        # membership or live authority. Retained carrier validation does not
        # authorize an endpoint or an owner outcome.
        self.view.handle.operations.validate_record(body,'cal.artifact-type.'+row['kind']+'/v1',
            self.view.data['projection'],allow_historical_carrier=True)""", """        # A bound original is document evidence, not source membership or an
        # eligible current endpoint. Never use the Typed Relation correction
        # adapter to confer a current Decision carrier or live authority.
        projection=self.view.data['projection'];carrier='cal.artifact-type.'+row['kind']+'/v1'
        require(carrier in projection['contracts'],'original document carrier absent from captured source')
        c=projection['contracts'][carrier]
        require(c['semantic_kind']==row['kind'] and c['lifecycle_state'] in
            ('admitted-current','local-admitted-current','admitted-historical','local-admitted-historical'),
            'original document carrier withdrawn, unadmitted or wrong kind')
        require(projection['documents'].get(c['artifact_path'])==c['artifact'],
            'original document descriptor differs from captured source')
        discriminator=c.get('instance_discriminator')
        if discriminator:
            require(self.view.handle.common.pointer(body,discriminator['path'])==discriminator['value'],
                'original historical document discriminator differs')
        self.view.handle.operations.validate_schema(body,c['schema_path'],c.get('schema_selector'),projection['documents'])""")
    print(json.dumps({'result':'AUTHORED','successor':'api-v66','authority_effect':'none'}))
if __name__=='__main__':main()
