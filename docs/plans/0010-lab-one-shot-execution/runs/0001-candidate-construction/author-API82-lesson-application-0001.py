"""Wire original lesson.apply under a separately selected private candidate policy."""
import ast
import copy
import json
import shutil
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-v81'
API = BASE / 'api-v82'
KIND = 'lab-local-lesson-application-policy/v1-candidate'


def replace(path, old, new):
    text = path.read_text()
    assert text.count(old) == 1, (path, old)
    path.write_text(text.replace(old, new, 1))


def main():
    assert not API.exists() and not (BASE / 'lesson-host-composition-v32').exists()
    ignore = shutil.ignore_patterns('receipts', '__pycache__', 'source-manifest.json', 'contract-profile.json')
    shutil.copytree(OLD, API, ignore=ignore)
    shutil.copytree(BASE / 'lesson-host-composition-v31', BASE / 'lesson-host-composition-v32', ignore=ignore)
    replace(BASE / 'lesson-host-composition-v32/host.py', 'api-v81/service.py', 'api-v82/service.py')
    replace(API / 'lesson_selection.py', 'lesson-host-composition-v31', 'lesson-host-composition-v32')
    (API / 'lesson_application.py').write_text(
        '"""Select the exact lesson application implementation in this host closure."""\n'
        'import importlib.util,sys\nfrom pathlib import Path\n'
        'HERE=Path(__file__).resolve().parent\nPATH=HERE.parent/"lesson-application-v1"\n'
        'NAME="_cal_"+HERE.name.replace("-","_")+"_lesson_application_v1"\n'
        'if NAME not in sys.modules:\n'
        '    spec=importlib.util.spec_from_file_location(NAME,PATH/"__init__.py",submodule_search_locations=[str(PATH)])\n'
        '    module=importlib.util.module_from_spec(spec);sys.modules[NAME]=module;spec.loader.exec_module(module)\n'
        'selected=__import__(NAME+".preparation",fromlist=["LessonApplication"])\n'
        'assert Path(selected.__file__).resolve()==PATH/"preparation.py"\n'
        'LessonApplication=selected.LessonApplication\nLessonApplicationFailure=selected.RuleFailure\n')
    path = API / 'protocol.py'
    replace(path, "WORKFLOW_SUPPORTED=CHALLENGE_SUPPORTED+('proposal.review',)",
            "APPLICATION_SUPPORTED=METADATA_SUPPORTED+('lesson.apply',)\nWORKFLOW_SUPPORTED=CHALLENGE_SUPPORTED+('proposal.review',)")
    replace(path, "'package.import','package.export','lesson.assess')", "'package.import','package.export','lesson.assess','lesson.apply')")
    path = API / 'auth.py'
    replace(path, "        failure=value['schema_version']=='lab-local-failure-candidate-policy/v1-candidate'",
            "        application=value['schema_version']=='" + KIND + "'\n        failure=value['schema_version']=='lab-local-failure-candidate-policy/v1-candidate'")
    replace(path, 'metadata=assessment or export or review or challenge or classification or failure or typed',
            'metadata=application or assessment or export or review or challenge or classification or failure or typed')
    replace(path, "        if failure:fields+=['failure_control']",
            "        if failure:fields+=['failure_control']\n        if application:fields+=['application_control']")
    replace(path, "'lab-local-reference-closed-review-policy/v1-candidate','lab-local-lesson-assessment-policy/v1-candidate')",
            "'lab-local-reference-closed-review-policy/v1-candidate','lab-local-lesson-assessment-policy/v1-candidate','" + KIND + "')")
    replace(path, 'list(ASSESSMENT_SUPPORTED if assessment else WORKFLOW_SUPPORTED if workflow', 'list(APPLICATION_SUPPORTED if application else ASSESSMENT_SUPPORTED if assessment else WORKFLOW_SUPPORTED if workflow')
    replace(path, '        if failure:\n            from .workspace import read_private',
            "        if application:\n            from .workspace import read_private\n            selected=value['application_control']['routing_binding']\n            source.require(selected['ref']=='workspace-object:'+selected_manifest['workspace_ref']+':'+selected['sha256'],'application routing namespace differs')\n            selected_raw=read_private(selected_root/'objects'/(selected['sha256']+'.json'))\n            source.require(source.sha(selected_raw)==selected['sha256'],'application routing bytes changed')\n            method=HERE.parent/'lesson-application-v1/preparation.py'\n            source.require(value['application_control']['method_binding']==binding(str(method.relative_to(ROOT)),method.read_bytes()),'application method selection differs')\n        if failure:\n            from .workspace import read_private")
    replace(path, "'durable-metadata-and-exact-failure-preparation' if failure",
            "'durable-metadata-and-exact-lesson-application' if application else 'durable-metadata-and-exact-failure-preparation' if failure")
    path = API / 'authentication.schema.json'
    schema = json.loads(path.read_bytes())
    branch = copy.deepcopy(next(b for b in schema['oneOf'] if b.get('properties', {}).get('schema_version', {}).get('const') == 'lab-local-failure-candidate-policy/v1-candidate'))
    branch['properties']['schema_version'] = {'const': KIND}
    branch['properties']['purpose'] = {'const': 'durable-metadata-and-exact-lesson-application'}
    branch['properties']['allowed_operations']['const'][-1] = 'lesson.apply'
    control = branch['properties'].pop('failure_control')
    control['properties']['method_binding'] = {'$ref': 'urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/binding'}
    control['required'].append('method_binding')
    branch['properties']['application_control'] = control
    branch['required'] = ['application_control' if key == 'failure_control' else key for key in branch['required']]
    schema['oneOf'].append(branch)
    path.write_text(json.dumps(schema, indent=2, sort_keys=True) + '\n')
    path = API / 'service.py'
    replace(path, '    def select_failure(self,message,outer,key):',
            "    def select_application(self,message,outer,key):\n        from .lesson_application import LessonApplication\n        selected=self.channel.policy_guard().get('application_control')\n        if selected is None:raise ApplicationError('closure-missing','Independently selected lesson application method and routing are unavailable.')\n        path=HERE/'source-manifest.json'\n        builder=LessonApplication(self,selected['routing_binding'],{'path':str(path.relative_to(ROOT)),'sha256':source.sha(path.read_bytes())})\n        builder.preflight(message,outer,key)\n        return builder\n    def select_failure(self,message,outer,key):")
    replace(path, "'carrier_references.py','carrier-reference-check.schema.json','lesson_assessment.py')",
            "'carrier_references.py','carrier-reference-check.schema.json','lesson_assessment.py','lesson_application.py')")
    replace(path, "'package.import','package.export','lesson.assess')", "'package.import','package.export','lesson.assess','lesson.apply')")
    replace(path, "                elif name=='failure.assess':failure_builder=self.select_failure(message,call['expected_source_cut'],call['idempotency_key'])",
            "                elif name=='failure.assess':failure_builder=self.select_failure(message,call['expected_source_cut'],call['idempotency_key'])\n                elif name=='lesson.apply':application_builder=self.select_application(message,call['expected_source_cut'],call['idempotency_key'])")
    replace(path, "                elif name=='classification.prepare':\n                    try:",
            "                elif name=='lesson.apply':\n                    from .lesson_application import LessonApplicationFailure\n                    try:domain,evidence=application_builder.prepare(message,request,call['expected_source_cut'],call['idempotency_key'])\n                    except LessonApplicationFailure as error:\n                        self.channel.guard();self.schemas.guard()\n                        source.require(self.handlers.current(),'lesson application source changed before failure recording')\n                        for item in error.evidence:self.vault.object_read(item)\n                        domain={'schema_version':'lab-error-result/v1-candidate','request_binding':request,'code':error.code,'message':error.message,'gaps':[],'retry_policy':'no-retry','evidence_bindings':error.evidence,'authority_effect':'none'}\n                        self.vault.finish(namespace,domain,error.evidence,posture='failed')\n                        return self.deliver_recorded(call,raw,domain,'failed',ceiling,effective)\n                elif name=='classification.prepare':\n                    try:")
    # Counts are exact current registry expectations, not weaker assertions.
    for path in API.rglob('*.py'):
        text = path.read_text().replace('self.assertEqual(len(SUPPORTED),22)', 'self.assertEqual(len(SUPPORTED),23)')
        ast.parse(text)
        path.write_text(text)
    print(json.dumps({'result': 'AUTHORED', 'authored_handlers': 23, 'remaining_handlers': 11,
                      'runtime_qualified': False, 'authority_effect': 'none'}), flush=True)


if __name__ == '__main__':
    main()
