"""Preserve failed v1; correct original-schema fixture and source-cut resolution."""
import ast
from pathlib import Path
import shutil
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD=BASE/'checkpoint-owner-verification-v1';NEW=BASE/'checkpoint-owner-verification-v2'
def replace(path,old,new):
    value=path.read_text();assert value.count(old)==1,(path,old);path.write_text(value.replace(old,new,1))
def methods(path):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes()))
        if isinstance(n,ast.FunctionDef) and n.name.startswith('test')}
def main():
    assert not NEW.exists();shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('receipts','source-manifest.json','__pycache__'))
    p=NEW/'owners.py'
    replace(p,"require(c['payload']['authority_basis_refs'] and not c['payload']['limitations'],\n        'claim basis or limitations require an independent admitted semantic adapter')",
        "require(c['payload']['authority_basis_refs'],'claim basis requires an independent admitted semantic adapter')")
    replace(p,"'authority_basis_refs':copy.deepcopy(c['payload']['authority_basis_refs']),",
        "'authority_basis_refs':copy.deepcopy(c['payload']['authority_basis_refs']),\n        'unresolved_semantic_limitations':copy.deepcopy(c['payload']['limitations']),")
    replace(p,"schema=parse((ROOT/'docs/proposals/0007-lab-integrated-schema-package/schemas/common.schema.json').read_bytes())\n        cut_schema={'$schema':schema['$schema'],'$defs':schema['$defs'],**schema['$defs']['source_cut']}",
        "schema=parse((ROOT/'docs/proposals/0006-lab-artifact-storage/schemas/artifact-package-manifest.schema.json').read_bytes())\n        cut_schema={'$schema':schema['$schema'],**schema['properties']['source_cut']}")
    replace(p,'Unknown period semantics and nonempty claim limitations fail closed.',
        'Unknown period semantics fail closed. Claim limitations remain unresolved\n    in the returned join and cannot authorize any live effect.')
    p=NEW/'test_owners.py'
    replace(p,'claimed_permissions=[self.permission],limitations=[]','claimed_permissions=[self.permission],limitations=[\'no consumer activation\']')
    replace(p,"permitted_effects=['admit'],excluded_effects=[]","permitted_effects=['admit'],excluded_effects=['activate-consumer']")
    replace(p,"with self.assertRaises(O.OwnerFault): self.join()", "with self.assertRaises(O.OwnerFault) as caught: self.join()\n        if self._testMethodName not in ('test11_claim_missing_basis','test23_schema_unknown_field'):\n            self.assertNotIn('invalid original',str(caught.exception),'negative case stopped at an unintended schema error')")
    replace(p,"def test10_claim_limitations_need_semantic_adapter(self): self.rows['authority-claim']['payload']['limitations']=['Only after owner approval'];self.rejected()",
        "def test10_claim_limitations_need_semantic_adapter(self):\n        self.rows['authority-claim']['payload']['limitations']=['Only after owner approval']\n        result=self.join();self.assertEqual(result['unresolved_semantic_limitations'],['Only after owner approval'])\n        self.assertFalse(result['live_authority_verified']);self.assertFalse(result['authority_basis_verified'])")
    with p.open('a') as stream:stream.write('''
    def test39_valid_original_schema_fixture_before_mutation(self):
        for kind,record in self.records().items(): O.checked_record(record,kind,self.scope)
    def test40_original_source_cut_hash_shape_enforced(self):
        self.selection_rejected(lambda p:p['source_cut'].update(commit_sha256='caller-text'))
    def test41_hardlinked_policy_refused(self):
        with tempfile.TemporaryDirectory(prefix='cal-checkpoint-owner-selection-') as temporary:
            path=Path(temporary)/'selection.json';raw=O.encoded(self.policy());path.write_bytes(raw);path.chmod(0o600)
            os.link(path,Path(temporary)/'other.json')
            with self.assertRaises(O.OwnerFault): O.Selection(path,O.sha(raw))
    def test42_readable_policy_directory_refused(self):
        with tempfile.TemporaryDirectory(prefix='cal-checkpoint-owner-selection-') as temporary:
            root=Path(temporary);path=root/'selection.json';raw=O.encoded(self.policy());path.write_bytes(raw);path.chmod(0o600);root.chmod(0o755)
            with self.assertRaises(O.OwnerFault): O.Selection(path,O.sha(raw))
    def test43_duplicate_json_key_refused(self):
        with self.assertRaises(O.OwnerFault): O.parse(b'{"revoked":false,"revoked":true}')
''')
    original=methods(OLD/'test_owners.py');new=methods(p)
    assert len(original)==38 and len(new)==43
    assert all(new[name]==body for name,body in original.items() if name!='test10_claim_limitations_need_semantic_adapter')
    p=NEW/'checks.py'
    value=p.read_text().replace('_cal_checkpoint_owner_verification_v1','_cal_checkpoint_owner_verification_v2').replace('==38','==43').replace("'expected_cases':38","'expected_cases':43")
    p.write_text(value)
    p=NEW/'README.md';value=p.read_text().replace('Nonempty claim limitations and unknown boundary\nperiod descriptions require an independent semantic adapter and fail closed.',
        'Claim limitations are retained as unresolved constraints; no live authority is\nverified. Unknown boundary period descriptions fail closed.')
    value=value.replace('The 38 checks','The 43 checks')
    value+='''

The v1 failed run is retained: five errors, no failed assertions, in 38 cases.
The fixture wrongly removed mandatory limitations/exclusions and attempted to
validate an external Source Cut reference without its original storage resource.
Version2 retains nonempty original-schema limitations and exclusions, reads the
exact original storage Source Cut contract, and reports the limitations as
unresolved. No original schema is changed. Thirty-seven original test bodies
remain unchanged. The limitations test now checks retained constraints and
withheld authority. Five extra checks validate the original fixture before any
mutation, Source Cut hashes, hard links, directory privacy and duplicate keys.
Negative joins assert that they reach their intended semantic checks instead of
passing accidentally at an earlier unrelated schema refusal.
'''
    p.write_text(value)
    freeze=(RUN/'freeze-checkpoint-owner-verification-0001.py').read_text().replace('checkpoint-owner-verification-v1','checkpoint-owner-verification-v2')
    freeze=freeze.replace('own=[bind(p) for p in files]+[bind(Path(__file__).resolve())]',
        "own=[bind(p) for p in files]+[bind(Path(__file__).resolve()),bind(RUN/'author-checkpoint-owner-verification-0002.py')]")
    freeze=freeze.replace("'docs/proposals/0007-lab-integrated-schema-package/schemas/common.schema.json',",
        "'docs/proposals/0007-lab-integrated-schema-package/schemas/common.schema.json',\n        'docs/proposals/0006-lab-artifact-storage/schemas/artifact-package-manifest.schema.json',\n        'product/lab/release-candidates/v1/interface/checkpoint-owner-verification-v1/source-manifest.json',\n        'product/lab/release-candidates/v1/interface/checkpoint-owner-verification-v1/receipts/checks-0001.json',\n        'product/lab/release-candidates/v1/interface/checkpoint-owner-verification-v1/receipts/actual-0001.log',")
    with (RUN/'freeze-checkpoint-owner-verification-0002.py').open('x') as stream:stream.write(freeze)
    print('Authored owner verification v2; original schemas and failed proof retained, 37 unchanged original test bodies plus revised limitation test and 5 new cases.',flush=True)
if __name__=='__main__':main()
