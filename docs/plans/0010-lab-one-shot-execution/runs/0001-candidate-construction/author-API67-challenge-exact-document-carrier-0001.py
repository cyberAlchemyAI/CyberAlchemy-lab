"""Select historical document carrier by its captured exact discriminator."""
import json
from pathlib import Path
import shutil
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v66';API=BASE/'api-v67'
def replace(p,a,b):
    value=p.read_text();assert value.count(a)==1,(p,a);p.write_text(value.replace(a,b,1))
def main():
    assert not API.exists() and not (BASE/'lesson-host-composition-v17').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(OLD,API,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v16',BASE/'lesson-host-composition-v17',ignore=ignore)
    replace(BASE/'lesson-host-composition-v17/host.py','api-v66/service.py','api-v67/service.py')
    replace(API/'lesson_selection.py','lesson-host-composition-v16','lesson-host-composition-v17')
    replace(API/'challenge_submission.py', """        projection=self.view.data['projection'];carrier='cal.artifact-type.'+row['kind']+'/v1'
        require(carrier in projection['contracts'],'original document carrier absent from captured source')
        c=projection['contracts'][carrier]
        require(c['semantic_kind']==row['kind'] and c['lifecycle_state'] in
            ('admitted-current','local-admitted-current','admitted-historical','local-admitted-historical'),
            'original document carrier withdrawn, unadmitted or wrong kind')""", """        projection=self.view.data['projection'];matches=[]
        for carrier,c in projection['contracts'].items():
            if c['semantic_kind']!=row['kind']:continue
            if c['lifecycle_state'] not in ('admitted-current','local-admitted-current','admitted-historical','local-admitted-historical'):continue
            discriminator=c.get('instance_discriminator')
            if discriminator and self.view.handle.common.pointer(body,discriminator['path'])==discriminator['value']:
                matches.append((carrier,c))
        require(len(matches)==1,'exact original document discriminator carrier missing or ambiguous')
        carrier,c=matches[0]""")
    print(json.dumps({'result':'AUTHORED','successor':'api-v67','authority_effect':'none'}))
if __name__=='__main__':main()
