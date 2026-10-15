"""Preserve API59; construct authenticated candidate challenge submission."""
import copy
import json
from pathlib import Path
import shutil
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v59';API=BASE/'api-v60'
def replace(path,before,after):
    text=path.read_text();assert text.count(before)==1,(path,before);path.write_text(text.replace(before,after,1))
def main():
    assert not API.exists() and not (BASE/'lesson-host-composition-v10').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(OLD,API,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v9',BASE/'lesson-host-composition-v10',ignore=ignore)
    replace(BASE/'lesson-host-composition-v10/host.py','api-v59/service.py','api-v60/service.py')
    replace(API/'lesson_selection.py','lesson-host-composition-v9','lesson-host-composition-v10')
    p=API/'protocol.py'
    replace(p,"SUPPORTED=LEGACY_SUPPORTED+('files.materialize'", "CHALLENGE_SUPPORTED=METADATA_SUPPORTED+('challenge.submit',)\nSUPPORTED=LEGACY_SUPPORTED+('challenge.submit','files.materialize'")
    p=API/'auth.py'
    replace(p,"review=value['schema_version']=='lab-local-review-candidate-policy/v1-candidate'", "review=value['schema_version']=='lab-local-review-candidate-policy/v1-candidate'\n        challenge=value['schema_version']=='lab-local-challenge-candidate-policy/v1-candidate'")
    replace(p,'metadata=export or review or classification or failure or typed or package or package_export or', 'metadata=export or review or challenge or classification or failure or typed or package or package_export or')
    replace(p,"if classification:fields+=['classification_control']", "if challenge:fields+=['challenge_control']\n        if classification:fields+=['classification_control']")
    replace(p,"'lab-local-package-export-policy/v1-candidate')", "'lab-local-package-export-policy/v1-candidate','lab-local-challenge-candidate-policy/v1-candidate')")
    replace(p,'else REVIEW_SUPPORTED if review else', 'else CHALLENGE_SUPPORTED if challenge else REVIEW_SUPPORTED if review else')
    replace(p,"else 'durable-metadata-and-exact-review-preparation' if review else", "else 'durable-metadata-and-exact-challenge-preparation' if challenge else 'durable-metadata-and-exact-review-preparation' if review else")
    replace(p,'        if package_export:\n            from .package_export import validate_control',
        '        if challenge:\n            from .challenge_submission import validate_control\n            validate_control(value,self.schemas)\n        if package_export:\n            from .package_export import validate_control')
    p=API/'service.py'
    replace(p,'from .package_export import PackageExport','from .package_export import PackageExport\nfrom .challenge_submission import ChallengeSubmission')
    replace(p,"'package_import.py','package_export.py')}","'package_import.py','package_export.py','challenge_submission.py','challenge-routing.schema.json')}")
    replace(p,'    def select_review(self,message,outer):', '''    def select_challenge(self,message,outer,key):
        selected=self.channel.policy_guard().get('challenge_control')
        if selected is None:raise ApplicationError('closure-missing','Independent challenger eligibility and exact routing are unavailable.')
        builder=ChallengeSubmission(self,copy.deepcopy(selected['routing_binding']))
        builder.preflight(message,outer,key)
        return builder
    def select_review(self,message,outer):''')
    replace(p,"effectful=name in ('change.prepare'", "effectful=name in ('challenge.submit','change.prepare'")
    replace(p,"elif name=='proposal.review':self.review_builder=self.select_review(message,call['expected_source_cut'])",
        "elif name=='challenge.submit':challenge_builder=self.select_challenge(message,call['expected_source_cut'],call['idempotency_key'])\n                elif name=='proposal.review':self.review_builder=self.select_review(message,call['expected_source_cut'])")
    replace(p,"elif name=='proposal.review':domain,evidence=self.review_builder.build(message,inner)",
        "elif name=='challenge.submit':domain,evidence=challenge_builder.prepare(message,request,call['expected_source_cut'],call['idempotency_key'],inner)\n                elif name=='proposal.review':domain,evidence=self.review_builder.build(message,inner)")
    schema=json.loads((API/'authentication.schema.json').read_bytes())
    branch=copy.deepcopy(next(b for b in schema['oneOf'] if b.get('properties',{}).get('schema_version',{}).get('const')=='lab-local-review-candidate-policy/v1-candidate'))
    branch['properties']['schema_version']['const']='lab-local-challenge-candidate-policy/v1-candidate'
    branch['properties']['purpose']['const']='durable-metadata-and-exact-challenge-preparation'
    branch['properties']['challenge_control']={'additionalProperties':False,'type':'object','properties':{'routing_binding':{'type':'object','additionalProperties':False,'properties':{'ref':{'type':'string','minLength':1},'sha256':{'type':'string','pattern':'^[a-f0-9]{64}$'}},'required':['ref','sha256']}},'required':['routing_binding']}
    branch['required'].append('challenge_control');schema['oneOf'].append(branch)
    (API/'authentication.schema.json').write_text(json.dumps(schema,indent=2,sort_keys=True)+'\n')
    print('Authored unfrozen API60 routing/policy skeleton; challenge implementation and exact qualification remain required.',flush=True)
if __name__=='__main__':main()
