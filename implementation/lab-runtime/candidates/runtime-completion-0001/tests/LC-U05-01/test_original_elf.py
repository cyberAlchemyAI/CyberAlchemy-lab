"""Inspect all77 exact selected public ELF inputs without executing any member."""
import bootstrap
from bootstrap import R,E,checked
import argparse,json,os,unittest
from pathlib import Path
from lab_contracts.codec import sha
from lab_selectors.anchors import AnchoredReader,RootAnchor,identity
from environment.elf import inspect_elf,compare_abi_versions

SELECTED=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
SELECTED_SHA='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
PUBLIC_ROOT=R/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
OBSERVATION={}

class OriginalElfTests(unittest.TestCase):
    def test_every_original_elf_origin_and_declared_transitive_version_requirement(self):
        raw=checked(SELECTED,SELECTED_SHA);selection=json.loads(raw)
        rows={r['destination']:r for r in selection['inputs']};rows.update(selection['wheel_members'])
        bindings=[{'kind':'execution','root_id':'public-original-runtime','relative_path':name,
            'sha256':rows[name]['sha256'],'size_bytes':rows[name]['size_bytes']} for name in selection['elf_graph']]
        reader=AnchoredReader([RootAnchor('public-original-runtime',str(PUBLIC_ROOT),identity(os.stat(PUBLIC_ROOT)))],bindings)
        observations={}
        for b in bindings:
            member=reader.read(b);observations[b['relative_path']]=inspect_elf(member,b['sha256'])
        self.assertEqual(len(observations),77)
        for name,value in observations.items():
            original=selection['elf_graph'][name]
            self.assertEqual(set(value['needed']),set(original['needed']))
            self.assertEqual(Path(value['interpreter']).name if value['interpreter'] else None,original['interpreter'])
            libraries={needed:observations['lib/abi/'+needed] for needed in value['needed']}
            self.assertFalse(compare_abi_versions(value,libraries)['runtime_abi_verified'])
        for b in bindings:reader.read(b)
        checked(SELECTED,SELECTED_SHA)
        OBSERVATION.update({'schema_version':'lab-u0501-original-elf-observation/v1','selection_sha256':SELECTED_SHA,
            'root_posture':'read-only public original installation bytes; no actual custody or mode qualification',
            'bindings':bindings,'observations':observations,'elf_members':77,
            'selected_member_execution':0,'runtime_qualification':False,'authority_effect':'none'})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--temp-root',type=Path,required=True);p.add_argument('--report',type=Path);a=p.parse_args()
    if a.temp_root!=E or not E.is_dir():raise ValueError('owned root')
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(OriginalElfTests))
    if a.report and result.wasSuccessful():
        if a.report.parent!=E or not a.report.name.startswith('original-elf-observation-'):raise ValueError('owned report')
        with a.report.open('x') as f:json.dump(OBSERVATION,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS' if result.wasSuccessful() else 'FAIL',
        'checks':result.testsRun,'effect_state':'owned-inert','cleanup':'clean'}))
    raise SystemExit(0 if result.wasSuccessful() else 1)
