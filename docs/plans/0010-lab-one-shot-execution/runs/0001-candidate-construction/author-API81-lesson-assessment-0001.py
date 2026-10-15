"""Wire original lesson.assess under a separately selected private candidate policy."""
import ast
import copy
import json
import shutil
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-v80'
API = BASE / 'api-v81'
KIND = 'lab-local-lesson-assessment-policy/v1-candidate'


def replace(path, old, new):
    text = path.read_text()
    assert text.count(old) == 1, (path, old)
    path.write_text(text.replace(old, new, 1))


def main():
    assert not API.exists() and not (BASE / 'lesson-host-composition-v31').exists()
    ignore = shutil.ignore_patterns('receipts', '__pycache__', 'source-manifest.json', 'contract-profile.json')
    shutil.copytree(OLD, API, ignore=ignore)
    shutil.copytree(BASE / 'lesson-host-composition-v30', BASE / 'lesson-host-composition-v31', ignore=ignore)
    replace(BASE / 'lesson-host-composition-v31/host.py', 'api-v80/service.py', 'api-v81/service.py')
    replace(API / 'lesson_selection.py', 'lesson-host-composition-v30', 'lesson-host-composition-v31')
    (API / 'lesson_assessment.py').write_text(
        '"""Select the exact lesson assessment implementation in this host closure."""\n'
        'import importlib.util,sys\nfrom pathlib import Path\n'
        'HERE=Path(__file__).resolve().parent\nPATH=HERE.parent/"lesson-assessment-v1"\n'
        'NAME="_cal_"+HERE.name.replace("-","_")+"_lesson_assessment_v1"\n'
        'if NAME not in sys.modules:\n'
        '    spec=importlib.util.spec_from_file_location(NAME,PATH/"__init__.py",submodule_search_locations=[str(PATH)])\n'
        '    module=importlib.util.module_from_spec(spec);sys.modules[NAME]=module;spec.loader.exec_module(module)\n'
        'selected=__import__(NAME+".preparation",fromlist=["LessonAssessment"])\n'
        'assert Path(selected.__file__).resolve()==PATH/"preparation.py"\n'
        'LessonAssessment=selected.LessonAssessment\nLessonAssessmentFailure=selected.RuleFailure\n')
    path = API / 'protocol.py'
    replace(path, "WORKFLOW_SUPPORTED=CHALLENGE_SUPPORTED+('proposal.review',)",
            "ASSESSMENT_SUPPORTED=METADATA_SUPPORTED+('lesson.assess',)\nWORKFLOW_SUPPORTED=CHALLENGE_SUPPORTED+('proposal.review',)")
    replace(path, "'package.import','package.export')", "'package.import','package.export','lesson.assess')")
    path = API / 'auth.py'
    replace(path, "        failure=value['schema_version']=='lab-local-failure-candidate-policy/v1-candidate'",
            "        assessment=value['schema_version']=='" + KIND + "'\n        failure=value['schema_version']=='lab-local-failure-candidate-policy/v1-candidate'")
    replace(path, 'metadata=export or review or challenge or classification or failure or typed',
            'metadata=assessment or export or review or challenge or classification or failure or typed')
    replace(path, "        if failure:fields+=['failure_control']",
            "        if failure:fields+=['failure_control']\n        if assessment:fields+=['assessment_control']")
    replace(path, "'lab-local-reference-closed-review-policy/v1-candidate')",
            "'lab-local-reference-closed-review-policy/v1-candidate','" + KIND + "')")
    replace(path, 'list(WORKFLOW_SUPPORTED if workflow', 'list(ASSESSMENT_SUPPORTED if assessment else WORKFLOW_SUPPORTED if workflow')
    replace(path, '        if failure:\n            from .workspace import read_private',
            "        if assessment:\n            from .workspace import read_private\n            selected=value['assessment_control']['routing_binding']\n            source.require(selected['ref']=='workspace-object:'+selected_manifest['workspace_ref']+':'+selected['sha256'],'assessment routing namespace differs')\n            selected_raw=read_private(selected_root/'objects'/(selected['sha256']+'.json'))\n            source.require(source.sha(selected_raw)==selected['sha256'],'assessment routing bytes changed')\n            method=HERE.parent/'lesson-assessment-v1/preparation.py'\n            source.require(value['assessment_control']['method_binding']==binding(str(method.relative_to(ROOT)),method.read_bytes()),'assessment method selection differs')\n        if failure:\n            from .workspace import read_private")
    replace(path, "'durable-metadata-and-exact-failure-preparation' if failure",
            "'durable-metadata-and-exact-lesson-assessment' if assessment else 'durable-metadata-and-exact-failure-preparation' if failure")
    path = API / 'authentication.schema.json'
    schema = json.loads(path.read_bytes())
    branch = copy.deepcopy(next(b for b in schema['oneOf'] if b.get('properties', {}).get('schema_version', {}).get('const') == 'lab-local-failure-candidate-policy/v1-candidate'))
    branch['properties']['schema_version'] = {'const': KIND}
    branch['properties']['purpose'] = {'const': 'durable-metadata-and-exact-lesson-assessment'}
    branch['properties']['allowed_operations']['const'][-1] = 'lesson.assess'
    control = branch['properties'].pop('failure_control')
    control['properties']['method_binding'] = {'$ref': 'urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/binding'}
    control['required'].append('method_binding')
    branch['properties']['assessment_control'] = control
    branch['required'] = ['assessment_control' if key == 'failure_control' else key for key in branch['required']]
    schema['oneOf'].append(branch)
    path.write_text(json.dumps(schema, indent=2, sort_keys=True) + '\n')
    path = API / 'service.py'
    replace(path, '    def select_failure(self,message,outer,key):',
            "    def select_assessment(self,message,outer,key):\n        from .lesson_assessment import LessonAssessment\n        selected=self.channel.policy_guard().get('assessment_control')\n        if selected is None:raise ApplicationError('closure-missing','Independently selected lesson assessment method and routing are unavailable.')\n        path=HERE/'source-manifest.json'\n        builder=LessonAssessment(self,selected['routing_binding'],{'path':str(path.relative_to(ROOT)),'sha256':source.sha(path.read_bytes())})\n        builder.preflight(message,outer,key)\n        return builder\n    def select_failure(self,message,outer,key):")
    replace(path, "'carrier_references.py','carrier-reference-check.schema.json')",
            "'carrier_references.py','carrier-reference-check.schema.json','lesson_assessment.py')")
    replace(path, "'package.import','package.export')", "'package.import','package.export','lesson.assess')")
    replace(path, "                elif name=='failure.assess':failure_builder=self.select_failure(message,call['expected_source_cut'],call['idempotency_key'])",
            "                elif name=='failure.assess':failure_builder=self.select_failure(message,call['expected_source_cut'],call['idempotency_key'])\n                elif name=='lesson.assess':assessment_builder=self.select_assessment(message,call['expected_source_cut'],call['idempotency_key'])")
    replace(path, "                elif name=='classification.prepare':\n                    try:",
            "                elif name=='lesson.assess':\n                    from .lesson_assessment import LessonAssessmentFailure\n                    try:domain,evidence=assessment_builder.prepare(message,request,call['expected_source_cut'],call['idempotency_key'])\n                    except LessonAssessmentFailure as error:\n                        self.channel.guard();self.schemas.guard()\n                        source.require(self.handlers.current(),'lesson assessment source changed before failure recording')\n                        for item in error.evidence:self.vault.object_read(item)\n                        domain=self.error_domain(call,raw,inner,ApplicationError(error.code,error.message,error.evidence))\n                        self.vault.finish(namespace,domain,error.evidence,posture='failed')\n                        return self.deliver_recorded(call,raw,domain,'failed',ceiling,effective)\n                elif name=='classification.prepare':\n                    try:")
    # Counts are exact current registry expectations, not weaker assertions.
    for path in API.rglob('*.py'):
        text = path.read_text().replace('self.assertEqual(len(SUPPORTED),21)', 'self.assertEqual(len(SUPPORTED),22)')
        ast.parse(text)
        path.write_text(text)
    print(json.dumps({'result': 'AUTHORED', 'authored_handlers': 22, 'remaining_handlers': 12,
                      'runtime_qualified': False, 'authority_effect': 'none'}), flush=True)


if __name__ == '__main__':
    main()
