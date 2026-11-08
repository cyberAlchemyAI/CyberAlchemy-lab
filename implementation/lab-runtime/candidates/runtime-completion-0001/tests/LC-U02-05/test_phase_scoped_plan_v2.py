"""Pure phase-scoped T35 plan; no Source or Mapper child is launched."""
from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath
import sys
import unittest

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from t35_external_v1 import role_stage, scratch_source_probe as source
from t35_external_v1.phase_scoped_v2 import plan as phase


class PhaseScopedPlanTests(unittest.TestCase):
    def fixture(self):
        layout = role_stage.DisposableLayout(PurePosixPath('/tmp/t35-plan/legacy-phase-fixture'),
                                              PurePosixPath('/tmp/t35-inputs'),
                                              'legacy-phase-fixture')
        rows = []
        for role, original, output in role_stage.entries(layout):
            filename = PurePosixPath(original).name
            if role == 'mapped' and filename in ('base.py', 'build.py'):
                selected = {'path': original, 'sha256': source.ROLE_TEMPLATE_SHA[original]}
                raw = source._held_input(selected)
                generated = role_stage.render_python(raw, layout=layout, role=role,
                                                     name=filename)
            else:
                generated = (role + '/' + filename + '\n').encode()
            rows.append({'role': role,
                         'input': {'path': original,
                                   'sha256': source.ROLE_TEMPLATE_SHA[original]},
                         'output': {'path': output,
                                    'sha256': hashlib.sha256(generated).hexdigest()},
                         'bytes': generated})
        return layout, rows

    def test_full_plan_is_30_but_initial_materialization_is_15(self):
        layout, rows = self.fixture()
        planned = phase.plan(layout, rows, episode_raw=b'episode\n', role_raw=b'role\n')
        self.assertEqual(len(planned.template_rows()), 27)
        self.assertEqual(len(planned.initial_bindings()), 15)
        self.assertEqual(len(planned.deferred_bindings()), 15)
        self.assertEqual(len(planned.initial_inventory()), 15)
        self.assertTrue(all('/mapped/' in r['path'] or '/context/' in r['path']
                            for r in planned.deferred_bindings()))
        planned.check_initial_inventory(planned.initial_inventory())
        selected = planned.source_rows([{'path': 'selected/input.json', 'sha256': 'a'*64}])
        self.assertEqual(len(selected), 16)
        self.assertTrue(set(planned.initial_inventory()) <= {r['path'] for r in selected})
        self.assertTrue({r['path'] for r in selected}.isdisjoint(
            r['path'] for r in planned.deferred_bindings()))
        self.assertEqual(planned.value()['status'], 'planned-unmaterialized')

    def test_future_role_present_early_and_caller_mutation_refuse(self):
        layout, rows = self.fixture()
        planned = phase.plan(layout, rows, episode_raw=b'episode\n', role_raw=b'role\n')
        old = planned.initial_inventory()
        rows[0]['bytes'] = b'mutated caller-owned bytes'
        rows[0]['output']['sha256'] = '0'*64
        self.assertEqual(planned.initial_inventory(), old)
        future = planned.deferred_bindings()[0]
        with self.assertRaises(ValueError):
            planned.check_initial_inventory({**old, future['path']: future['sha256']})
        wrong = dict(old)
        wrong[next(iter(wrong))] = '0'*64
        with self.assertRaises(ValueError):
            planned.check_initial_inventory(wrong)
        with self.assertRaises(ValueError):
            planned.source_rows([{'path': str(layout.family / 'mapped/base.py'),
                                  'sha256': 'a'*64}])

    def test_mapper_phase_rebind_is_pure_and_requires_fresh_pins(self):
        layout, rows = self.fixture()
        planned = phase.plan(layout, rows, episode_raw=b'episode\n', role_raw=b'role\n')
        predecessor = {
            name: {'path': str(layout.family / phase.phase_rebind.PIN_PATHS[name]),
                   'sha256': digit*64}
            for name, digit in (('source', '1'), ('source_package', '2'), ('reader', '3'))
        }
        generated = planned.mapper_bindings(predecessor)
        self.assertEqual(set(generated), {str(layout.family / 'mapped' / name)
                                          for name in role_stage.ROLE_FILES['mapped']})
        planned_sha = {row['path']: row['sha256'] for row in planned.deferred_bindings()}
        self.assertNotEqual(generated[str(layout.family / 'mapped/base.py')]['sha256'],
                            planned_sha[str(layout.family / 'mapped/base.py')])
        self.assertNotEqual(generated[str(layout.family / 'mapped/build.py')]['sha256'],
                            planned_sha[str(layout.family / 'mapped/build.py')])
        self.assertEqual(generated[str(layout.family / 'mapped/policy.json')]['sha256'],
                         planned_sha[str(layout.family / 'mapped/policy.json')])
        with self.assertRaises(ValueError):
            planned.mapper_bindings({**predecessor,
                'reader': {'path': str(layout.family / 'reader/other.json'),
                           'sha256': '3'*64}})


if __name__ == '__main__':
    unittest.main()
