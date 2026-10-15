"""Wire challenge.resolve under a separately selected exact private policy."""
import ast
import copy
import json
from pathlib import Path
import shutil

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD,API=BASE/'api-v85',BASE/'api-v86'
KIND='lab-local-challenge-resolution-policy/v1-candidate'


def replace(path,old,new):
    value=path.read_text();assert value.count(old)==1,(path,old)
    path.write_text(value.replace(old,new,1))


def main():
    assert not API.exists() and not (BASE/'lesson-host-composition-v36').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(OLD,API,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v35',BASE/'lesson-host-composition-v36',ignore=ignore)
    replace(BASE/'lesson-host-composition-v36/host.py','api-v85/service.py','api-v86/service.py')
    replace(API/'lesson_selection.py','lesson-host-composition-v35','lesson-host-composition-v36')
    (API/'challenge_resolution.py').write_text('''"""Select the exact challenge resolution implementation in this host closure."""
import importlib.util,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
PATH=HERE.parent/'challenge-resolution-v1'
NAME='_cal_'+HERE.name.replace('-','_')+'_challenge_resolution_v1'
if NAME not in sys.modules:
    spec=importlib.util.spec_from_file_location(NAME,PATH/'__init__.py',submodule_search_locations=[str(PATH)])
    module=importlib.util.module_from_spec(spec);sys.modules[NAME]=module;spec.loader.exec_module(module)
selected=__import__(NAME+'.preparation',fromlist=['ChallengeResolution'])
assert Path(selected.__file__).resolve()==PATH/'preparation.py'
ChallengeResolution=selected.ChallengeResolution
ChallengeResolutionFailure=selected.RuleFailure
''')
    path=API/'protocol.py'
    replace(path,"APPLICATION_SUPPORTED=METADATA_SUPPORTED+('lesson.apply',)",
            "RESOLUTION_SUPPORTED=METADATA_SUPPORTED+('challenge.resolve',)\nAPPLICATION_SUPPORTED=METADATA_SUPPORTED+('lesson.apply',)")
    replace(path,"'package.import','package.export','lesson.assess','lesson.apply')",
            "'package.import','package.export','lesson.assess','lesson.apply','challenge.resolve')")
    path=API/'auth.py'
    replace(path,"        failure=value['schema_version']=='lab-local-failure-candidate-policy/v1-candidate'",
            "        resolution=value['schema_version']=='"+KIND+"'\n        failure=value['schema_version']=='lab-local-failure-candidate-policy/v1-candidate'")
    replace(path,'metadata=(application and not application_session) or assessment',
            'metadata=resolution or (application and not application_session) or assessment')
    replace(path,"        if failure:fields+=['failure_control']",
            "        if resolution:fields+=['resolution_control']\n        if failure:fields+=['failure_control']")
    replace(path,"'lab-local-lesson-application-policy/v2-candidate')",
            "'lab-local-lesson-application-policy/v2-candidate','"+KIND+"')")
    replace(path,'list(APPLICATION_SESSION_SUPPORTED if application_session',
            'list(RESOLUTION_SUPPORTED if resolution else APPLICATION_SESSION_SUPPORTED if application_session')
    replace(path,'        if failure:\n            from .workspace import read_private',
            "        if resolution:\n            from .workspace import read_private\n            selected=value['resolution_control']['routing_binding']\n            source.require(selected['ref']=='workspace-object:'+selected_manifest['workspace_ref']+':'+selected['sha256'],'resolution routing namespace differs')\n            selected_raw=read_private(selected_root/'objects'/(selected['sha256']+'.json'))\n            source.require(source.sha(selected_raw)==selected['sha256'],'resolution routing original changed')\n            method=HERE.parent/'challenge-resolution-v1/preparation.py'\n            source.require(value['resolution_control']['method_binding']==binding(str(method.relative_to(ROOT)),method.read_bytes()),'resolution method selection differs')\n        if failure:\n            from .workspace import read_private")
    replace(path,"value['purpose']==('durable-metadata-and-exact-reference-closed-review' if references",
            "value['purpose']==('durable-metadata-and-exact-challenge-resolution' if resolution else 'durable-metadata-and-exact-reference-closed-review' if references")
    path=API/'authentication.schema.json';schema=json.loads(path.read_bytes())
    branch=copy.deepcopy(next(b for b in schema['oneOf'] if b.get('properties',{}).get('schema_version',{}).get('const')=='lab-local-lesson-assessment-policy/v1-candidate'))
    branch['properties']['schema_version']={'const':KIND}
    branch['properties']['purpose']={'const':'durable-metadata-and-exact-challenge-resolution'}
    branch['properties']['allowed_operations']['const'][-1]='challenge.resolve'
    branch['properties']['resolution_control']=branch['properties'].pop('assessment_control')
    branch['required']=['resolution_control' if field=='assessment_control' else field for field in branch['required']]
    schema['oneOf'].append(branch)
    path.write_text(json.dumps(schema,indent=2,sort_keys=True)+'\n')
    path=API/'service.py'
    replace(path,'    def select_failure(self,message,outer,key):',
            "    def select_resolution(self,message,outer,key):\n        from .challenge_resolution import ChallengeResolution\n        from .guarded_candidate import selection\n        with selection(self):\n            selected=self.channel.policy_guard().get('resolution_control')\n            if selected is None:raise ApplicationError('closure-missing','Independent exact challenge resolution method and routing are unavailable.')\n            path=HERE/'source-manifest.json'\n            try:\n                builder=ChallengeResolution(self,selected['routing_binding'],{'path':str(path.relative_to(ROOT)),'sha256':source.sha(path.read_bytes())})\n                builder.preflight(message,outer,key)\n                return builder\n            except ApplicationError:raise\n            except Exception as error:raise ApplicationError('invalid-contract','Exact challenge authority, response obligations or consequence closure could not be verified.') from error\n    def select_failure(self,message,outer,key):")
    replace(path,"'lesson_assessment.py','lesson_application.py','machine_context_scope.py')",
            "'lesson_assessment.py','lesson_application.py','machine_context_scope.py','challenge_resolution.py')")
    replace(path,"'package.import','package.export','lesson.assess','lesson.apply')",
            "'package.import','package.export','lesson.assess','lesson.apply','challenge.resolve')")
    replace(path,"                elif name=='lesson.apply':application_builder=self.select_application(message,call['expected_source_cut'],call['idempotency_key'])",
            "                elif name=='lesson.apply':application_builder=self.select_application(message,call['expected_source_cut'],call['idempotency_key'])\n                elif name=='challenge.resolve':resolution_builder=self.select_resolution(message,call['expected_source_cut'],call['idempotency_key'])")
    replace(path,"                elif name=='classification.prepare':\n                    try:",
            "                elif name=='challenge.resolve':\n                    from .challenge_resolution import ChallengeResolutionFailure\n                    try:domain,evidence=resolution_builder.prepare(message,request,call['expected_source_cut'],call['idempotency_key'])\n                    except ChallengeResolutionFailure as error:\n                        self.channel.guard();self.schemas.guard()\n                        source.require(self.handlers.current(),'challenge resolution source changed before failure recording')\n                        for item in error.evidence:self.vault.object_read(item)\n                        domain={'schema_version':'lab-error-result/v1-candidate','request_binding':request,'code':error.code,'message':error.message,'gaps':[],'retry_policy':'no-retry','evidence_bindings':error.evidence,'authority_effect':'none'}\n                        self.vault.finish(namespace,domain,error.evidence,posture='failed')\n                        return self.deliver_recorded(call,raw,domain,'failed',ceiling,effective)\n                elif name=='classification.prepare':\n                    try:")
    revised=[]
    for path in API.rglob('*.py'):
        value=path.read_text();changed=value.replace('self.assertEqual(len(SUPPORTED),23)','self.assertEqual(len(SUPPORTED),24)')
        if changed!=value:revised.append(path.relative_to(API).as_posix());path.write_text(changed)
        ast.parse(changed)
    assert revised==['test_current_controls.py','test_custody_sessions.py'] or set(revised)=={'test_current_controls.py','test_custody_sessions.py'}
    print(json.dumps({'result':'AUTHORED','authored_handlers':24,'remaining_handlers':10,
                      'explicit_registry_count_revisions':revised,'runtime_qualified':False,'authority_effect':'none'}),flush=True)


if __name__=='__main__':main()
