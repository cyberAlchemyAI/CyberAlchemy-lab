"""Cold anchor and provenance tests; no native build or Docker process."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import tempfile
import textwrap
import unittest
from unittest.mock import patch
from jsonschema import Draft202012Validator

import stage_learning
from transform import LESSON_CONSTRUCTION, TransformFault, transform

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SELECTED = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-947e6c2a5b3d10f8'
PREDECESSOR = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/fresh-legacy-current-runtime-preparation-0009/construct_legacy_v3.py'
CASES = [('source', 'records.py'), ('source', 'build.py'), ('mapped', 'build.py'),
         ('context', 'generation.py'), ('context', 'build.py')]
MANIFEST_SHA = stage_learning.digest(stage_learning.NATIVE_MANIFEST)


class NativeSuccessorTransform(unittest.TestCase):
    def test_01_all_five_exact_source_transforms_parse_and_leave_old_bytes(self):
        for role, name in CASES:
            with self.subTest(role=role, name=name):
                path = SELECTED / role / name
                before = path.read_bytes()
                generated = transform(role, name, before.decode())
                self.assertNotEqual(generated.encode(), before)
                ast.parse(generated)
                self.assertEqual(path.read_bytes(), before)

    def test_02_closed_anchors_refuse_changed_or_reapplied_source(self):
        for role, name in CASES:
            with self.subTest(role=role, name=name):
                generated = transform(role, name, (SELECTED / role / name).read_text())
                with self.assertRaises(TransformFault):
                    transform(role, name, generated)
        with self.assertRaises(TransformFault):
            transform('mapped', 'build.py', 'changed native builder')

    def test_03_single_constructor_semantic_change(self):
        before = PREDECESSOR.read_text()
        after = (HERE / 'construct_learning.py').read_text()
        self.assertEqual(before.count("'complete_current_Lesson_inventory':0"), 1)
        self.assertEqual(after, before.replace("'complete_current_Lesson_inventory':0",
                                               "'complete_current_Lesson_inventory':1", 1))
        ast.parse(after)

    def test_04_new_lesson_inventory_requires_live_selection(self):
        source = transform('source', 'records.py', (SELECTED / 'source/records.py').read_text())
        mapping = transform('mapped', 'build.py', (SELECTED / 'mapped/build.py').read_text())
        context = transform('context', 'generation.py', (SELECTED / 'context/generation.py').read_text())
        self.assertIn("LESSON = 'operational-lesson:' + PREFIX", source)
        self.assertIn("'operational-lesson': lesson", source)
        self.assertIn('records.LESSON', mapping)
        self.assertIn("'current_catalog_lessons':1", context)
        self.assertIn("'selected_lesson_refs':[]", context)
        self.assertIn('live independent lesson.select must decide applicability', context)
        self.assertIn('len(bodies)==31', context)

    def test_05_native_constructor_manifest_closed_and_exact(self):
        manifest = stage_learning.verify_manifest(MANIFEST_SHA)
        self.assertEqual(len(manifest['files']), 5)
        self.assertEqual(len(manifest['input_bindings']), 11)
        self.assertIn(stage_learning.LESSON_FIXTURE.relative_to(ROOT).as_posix(),
                      {row['path'] for row in manifest['input_bindings']})

    def test_06_missing_or_changed_constructor_selection_refuses(self):
        manifest = json.loads(stage_learning.NATIVE_MANIFEST.read_bytes())
        for variant in ('missing', 'changed'):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory(prefix='t03-native-manifest-') as temp:
                altered = json.loads(json.dumps(manifest))
                if variant == 'missing':
                    altered['files'].pop(0)
                else:
                    altered['input_bindings'][-1]['sha256'] = '0' * 64
                path = Path(temp) / 'manifest.json'
                path.write_text(json.dumps(altered))
                with patch.object(stage_learning, 'NATIVE_MANIFEST', path):
                    with self.assertRaises(ValueError):
                        stage_learning.verify_manifest(MANIFEST_SHA)

    def test_07_unreviewed_or_wrong_constructor_manifest_pin_refuses(self):
        with self.assertRaisesRegex(ValueError, 'independent native constructor manifest pin required'):
            stage_learning.verify_manifest('')
        with self.assertRaisesRegex(ValueError, 'independent native constructor manifest pin differs'):
            stage_learning.verify_manifest('0' * 64)
        self.assertEqual(stage_learning.verify_manifest(MANIFEST_SHA)['schema_version'],
                         'lab-t03-native-learning-constructor/v1')

    def test_08_constructed_lesson_satisfies_selected_artifact_schema(self):
        fixture_path = stage_learning.LESSON_FIXTURE
        namespace = {
            '__file__': str(SELECTED / 'source/records.py'),
            'Path': Path, 'json': json,
            'fixture': lambda kind: json.loads(fixture_path.read_bytes()),
            'LESSON': 'operational-lesson:completion-legacy-cold-probe',
            'PRINCIPAL': 'principal:completion-legacy-cold-probe',
            'T03_EVIDENCE': stage_learning.EVIDENCE.relative_to(ROOT).as_posix(),
            'T03_RETENTION': 'protocol:T03-retain-public-technical-evidence-exclude-session-memory/v1',
            'T03_FAMILY': 'family:api33-native-disposition-review',
            'scope': 'project:cyberalchemy-v2-to-lab-migration',
        }
        exec(textwrap.dedent(LESSON_CONSTRUCTION), namespace)
        lesson = namespace['lesson']
        schema = json.loads(stage_learning.LESSON_SCHEMA.read_bytes())
        Draft202012Validator(schema).validate(lesson)
        self.assertEqual(lesson['payload']['evidence_refs'], [namespace['T03_EVIDENCE']])
        self.assertEqual(lesson['payload']['applicability'], namespace['T03_FAMILY'])


if __name__ == '__main__':
    unittest.main()
