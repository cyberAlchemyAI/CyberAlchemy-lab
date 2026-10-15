"""Author an unfrozen successor; qualification is required before fixture effects."""
import ast
import copy
import hashlib
import json
import shutil
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
PARENT = INTERFACE / 'api-v35'
SELECTED = INTERFACE / 'api-v36'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def replace_exact(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def main():
    assert not SELECTED.exists()
    parent_source = PARENT / 'source-manifest.json'
    assert bind(parent_source)['sha256'] == 'c4e6e226082890da6569acb1175878fa5b3f70e06b1e42cd0a11331ec3c21e11'
    SELECTED.mkdir()
    for path in PARENT.rglob('*'):
        if not path.is_file() or any(part in path.parts for part in ['receipts', '__pycache__']):
            continue
        relative = path.relative_to(PARENT)
        if relative.as_posix() in ['source-manifest.json', 'contract-profile.json']:
            continue
        out = SELECTED / relative
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, out)
    protocol = SELECTED / 'protocol.py'
    text = replace_exact(protocol.read_text(), "SUPPORTED=LEGACY_SUPPORTED+('files.materialize','proposal.review')", "CLASSIFICATION_SUPPORTED=METADATA_SUPPORTED+('classification.prepare',)\nSUPPORTED=LEGACY_SUPPORTED+('files.materialize','proposal.review','classification.prepare')")
    protocol.write_text(text)
    auth = SELECTED / 'auth.py'
    text = auth.read_text()
    text = replace_exact(text, "        review=value['schema_version']=='lab-local-review-candidate-policy/v1-candidate'", "        review=value['schema_version']=='lab-local-review-candidate-policy/v1-candidate'\n        classification=value['schema_version']=='lab-local-classification-candidate-policy/v1-candidate'")
    text = replace_exact(text, "metadata=export or review or value['schema_version']", "metadata=export or review or classification or value['schema_version']")
    text = replace_exact(text, "'lab-local-export-candidate-policy/v1-candidate','lab-local-review-candidate-policy/v1-candidate')", "'lab-local-export-candidate-policy/v1-candidate','lab-local-review-candidate-policy/v1-candidate','lab-local-classification-candidate-policy/v1-candidate')")
    text = replace_exact(text, "EXPORT_SUPPORTED if export else REVIEW_SUPPORTED if review else METADATA_SUPPORTED if metadata else LEGACY_SUPPORTED", "EXPORT_SUPPORTED if export else REVIEW_SUPPORTED if review else CLASSIFICATION_SUPPORTED if classification else METADATA_SUPPORTED if metadata else LEGACY_SUPPORTED")
    text = replace_exact(text, "'durable-metadata-and-exact-review-preparation' if review else 'durable-metadata-and-exact-candidate-preparation'", "'durable-metadata-and-exact-review-preparation' if review else 'durable-metadata-and-exact-classification-preparation' if classification else 'durable-metadata-and-exact-candidate-preparation'")
    ast.parse(text)
    auth.write_text(text)
    schema_path = SELECTED / 'authentication.schema.json'
    schema = json.loads(schema_path.read_bytes())
    policy = copy.deepcopy(next(row for row in schema['oneOf'] if row['properties']['schema_version'].get('const') == 'lab-local-review-candidate-policy/v1-candidate'))
    policy['properties']['schema_version']['const'] = 'lab-local-classification-candidate-policy/v1-candidate'
    policy['properties']['purpose']['const'] = 'durable-metadata-and-exact-classification-preparation'
    operations = ['lab.status', 'catalog.get', 'artifact.inspect', 'artifact.query', 'change.prepare', 'change.validate', 'operation.inspect', 'projection.refresh', 'classification.prepare']
    policy['properties']['allowed_operations'] = {'const': operations}
    schema['oneOf'].append(policy)
    schema_path.write_text(json.dumps(schema, indent=2, sort_keys=True) + '\n')
    proxy = '''"""Select the exact composition whose bytes the host manifest guards."""
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PATH = HERE.parent / 'classification-preparation-v1'
NAME = '_cal_' + HERE.name.replace('-', '_') + '_classification_preparation_v1'
if NAME not in sys.modules:
    spec = importlib.util.spec_from_file_location(NAME, PATH / '__init__.py', submodule_search_locations=[str(PATH)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[NAME] = package
    spec.loader.exec_module(package)
selected = __import__(NAME + '.preparation', fromlist=['ClassificationPreparation'])
assert Path(selected.__file__).resolve() == PATH / 'preparation.py'
ClassificationPreparation = selected.ClassificationPreparation
'''
    with (SELECTED / 'classification_preparation.py').open('x') as stream:
        stream.write(proxy)
    service = SELECTED / 'service.py'
    text = service.read_text()
    text = replace_exact(text, 'from .review_preparation import ReviewPreparation', 'from .review_preparation import ReviewPreparation\nfrom .classification_preparation import ClassificationPreparation')
    text = replace_exact(text, "'review-routing.schema.json')}", "'review-routing.schema.json','classification_preparation.py')}")
    text = replace_exact(text, '    def error(self,call,raw,message_raw,error):', '''    def select_classification(self,message,outer,key):
        selected=self.vault.inputs.get('candidate:classification-routing')
        if selected is None:
            raise ApplicationError('closure-missing','Independently selected exact classification routing is unavailable in this owned workspace.')
        try:
            routing={'ref':selected['ref'],'sha256':selected['sha256']}
            source_path=HERE/'source-manifest.json'
            builder=ClassificationPreparation(self,routing,{'path':str(source_path.relative_to(ROOT)),'sha256':source.sha(source_path.read_bytes())})
            builder.preflight(message,outer,key)
            return builder
        except ApplicationError:raise
        except Exception:
            raise ApplicationError('invalid-contract','Exact classification routing, source cut, Actor, scope, key or original proposal could not be verified.')
    def error(self,call,raw,message_raw,error):''')
    text = replace_exact(text, "'handler_binding':binding(str((HERE/'review_preparation.py')", "'handler_binding':binding(str((HERE/'classification_preparation.py').relative_to(ROOT)),(HERE/'classification_preparation.py').read_bytes()) if call['operation']=='classification.prepare' else binding(str((HERE/'review_preparation.py')")
    text = replace_exact(text, "effectful=name in ('change.prepare','change.validate','session.open','session.close','projection.refresh','files.materialize','proposal.review')", "effectful=name in ('change.prepare','change.validate','session.open','session.close','projection.refresh','files.materialize','proposal.review','classification.prepare')")
    text = replace_exact(text, "elif name=='proposal.review':self.review_builder=self.select_review(message,call['expected_source_cut'])", "elif name=='proposal.review':self.review_builder=self.select_review(message,call['expected_source_cut'])\n                elif name=='classification.prepare':classification_builder=self.select_classification(message,call['expected_source_cut'],call['idempotency_key'])")
    text = replace_exact(text, "elif name=='proposal.review':domain,evidence=self.review_builder.build(message,inner)", "elif name=='proposal.review':domain,evidence=self.review_builder.build(message,inner)\n                elif name=='classification.prepare':domain,evidence=classification_builder.prepare(message,request,call['expected_source_cut'],call['idempotency_key'])")
    ast.parse(text)
    service.write_text(text)
    machine = SELECTED / 'test_machine_transport.py'
    text = replace_exact(machine.read_text(), '        Sessions.setUp(self)\n', "        Sessions.setUp(self)\n        # The parent saves a dict under the same name as this class's helper.\n        assert isinstance(self.__dict__.get('authenticated'),dict)\n        del self.authenticated\n")
    machine.write_text(text)
    inherited = []
    for old in PARENT.rglob('*.py'):
        if any(part in old.parts for part in ['receipts', '__pycache__']):
            continue
        new = SELECTED / old.relative_to(PARENT)
        methods = lambda path: {node.name: ast.dump(node, include_attributes=False) for node in ast.walk(ast.parse(path.read_bytes())) if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}
        assert methods(old) == methods(new), old.name
        inherited.extend(old.name + ':' + name for name in methods(old))
    assert len(inherited) == 259
    design = '''# Classification API successor construction

Status: authored, unfrozen, unexecuted, unqualified. No fixture effects may start before the exact host source/profile, classification composition and rule proofs are frozen.

Add classification.prepare to the dispatcher, its original ChangeProposal result and original fingerprint/journal/deadline/uncertainty rules. A distinct closed Operator candidate policy grants the exact metadata preparation subset plus classification.prepare. It grants no owner authority or Machine permission. Existing policy variants and Machine read operation set are retained.

The composition requires the complete selected current records plus every validated prospective target. The candidate assignment is excluded from its own cardinality count; other assignments stay present. Header, schema, stable Decision core, Actor, scope, source cut, idempotency key, basis and all declared rules must agree. Unknown rules remain unevaluated; unresolved general domain closure remains visible.

All259 inherited test method ASTs remain exact. Machine setUp removes only the parent fixture dictionary that shadows its existing authentication helper; no test method, source callback, clock, permission or900second limit changes.

Context8 full50 and independent qualification are required before rebinding this successor's source/Context selection. Preserve all previous successful and failed evidence. Add actual public classification positive/refusal/retry/prospective transition/uncertainty cases, full inherited suites and independent integrated audit before qualification. Original34 contracts, remaining21 qualifications and all46 tasks/S02/R08 remain.
'''
    (SELECTED / 'CLASSIFICATION.md').open('x').write(design)
    report = {'schema_version': 'lab-classification-API-construction/v1-candidate',
              'parent_source_binding': bind(parent_source), 'unchanged_inherited_test_methods': 259,
              'authored_operation': 'classification.prepare', 'frozen': False,
              'Context_selection_rebound': False, 'fixture_effects_started': False,
              'public_handlers_qualified': False, 'authority_effect': 'none', 'actual_owner_outcome': None,
              'files': [bind(path) for path in sorted(SELECTED.rglob('*')) if path.is_file()]}
    with (RUN / 'classification-API-construction-0036.json').open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'AUTHORED', 'unchanged_methods': len(inherited), 'owned_fixture_effects': 0, 'frozen': False}), flush=True)


if __name__ == '__main__':
    main()
