"""Connect independently reconstructed challenge outputs to original validation."""
from pathlib import Path
import shutil
import json
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v68';API=BASE/'api-v69'
def replace(p,a,b):
    s=p.read_text();assert s.count(a)==1,(p,a);p.write_text(s.replace(a,b,1))
def main():
    assert not API.exists() and not (BASE/'lesson-host-composition-v19').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(OLD,API,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v18',BASE/'lesson-host-composition-v19',ignore=ignore)
    replace(BASE/'lesson-host-composition-v19/host.py','api-v68/service.py','api-v69/service.py')
    replace(API/'lesson_selection.py','lesson-host-composition-v18','lesson-host-composition-v19')
    p=API/'challenge_submission.py';s=p.read_text()
    start=s.index("            plan=self._plan(message,outer,key);targets=[]")
    tail=s[start:];assert tail.endswith('        return domain,evidence\n')
    lines=tail.splitlines();lines[0]='            targets=[]'
    render='\n'.join(line[4:] if line.startswith('    ') else line for line in lines[:-1])+'\n        return domain,evidence\n'
    p.write_text(s[:start]+"            plan=self._plan(message,outer,key)\n            return self.render(plan,message,outer,key,original,writer)\n    def render(self,plan,message,outer,key,original,writer):\n"+render)
    p=API/'service.py'
    replace(p,'from .candidate import CandidateHandlers','from .candidate import CandidateHandlers\nfrom .generated_candidate import GeneratedCandidateHandlers')
    replace(p,'self.candidates=CandidateHandlers(self.handlers,self.vault,schemas)','self.candidates=GeneratedCandidateHandlers(self)')
    replace(p,"'challenge_submission.py','challenge-routing.schema.json')", "'challenge_submission.py','challenge-routing.schema.json','generated_candidate.py')")
    shutil.copyfile(RUN/'API69-generated_candidate.py',API/'generated_candidate.py')
    print(json.dumps({'result':'AUTHORED','successor':'api-v69','authority_effect':'none'}))
if __name__=='__main__':main()
