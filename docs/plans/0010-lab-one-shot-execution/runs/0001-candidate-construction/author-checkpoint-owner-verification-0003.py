"""Separate storage provenance scope from Role Assignment and target domains."""
import ast
from pathlib import Path
import shutil
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD=BASE/'checkpoint-owner-verification-v2';NEW=BASE/'checkpoint-owner-verification-v3'
def replace(path,old,new):
    value=path.read_text();assert value.count(old)==1,(path,old);path.write_text(value.replace(old,new,1))
def methods(path):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes()))
        if isinstance(n,ast.FunctionDef) and n.name.startswith('test')}
def main():
    assert not NEW.exists();shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('receipts','source-manifest.json','__pycache__'))
    p=NEW/'owners.py'
    replace(p,"require(body['kind']==kind and body['scope_ref']==scope,'source kind or domain scope differs')",
        "require(body['kind']==kind,'source kind differs')")
    replace(p,'def verify_join(records,*,principal_ref,role_ref,scope_ref,evaluated_at,permission,targets):',
        'def verify_join(records,*,principal_ref,role_ref,storage_scope_ref,assignment_scope_ref,evaluated_at,permission,targets):')
    replace(p,'checked_record(records[k],k,scope_ref)','checked_record(records[k],k,storage_scope_ref)')
    replace(p,"require(a['role_ref']==role_ref and a['assignee_kind']=='person-reference'",
        "require(type(assignment_scope_ref) is str and assignment_scope_ref and a['scope_ref']==assignment_scope_ref,\n        'Role Assignment domain differs from independently selected authority domain')\n    require(a['role_ref']==role_ref and a['assignee_kind']=='person-reference'")
    replace(p,"set(target)=={'version_ref','identity_ref','kind','operation'}","set(target)=={'version_ref','identity_ref','kind','operation','scope_ref'}")
    replace(p,"require(target['version_ref'] not in seen,'duplicate target grant');seen.add(target['version_ref'])",
        "require(target['scope_ref']==assignment_scope_ref,'target domain outside selected Role Assignment')\n        require(target['version_ref'] not in seen,'duplicate target grant');seen.add(target['version_ref'])")
    replace(p,"'role_ref':role_ref,'scope_ref':scope_ref,'permission':permission,'evaluated_at':evaluated_at,",
        "'role_ref':role_ref,'storage_scope_ref':storage_scope_ref,'assignment_scope_ref':assignment_scope_ref,\n        'permission':permission,'evaluated_at':evaluated_at,")
    value=p.read_text().replace("'accountable_principal_ref','scope_ref','not_before'","'accountable_principal_ref','storage_scope_ref','not_before'")
    value=value.replace("value['scope_ref']","value['storage_scope_ref']").replace("selected['scope_ref']","selected['storage_scope_ref']")
    value=value.replace("'permission','targets','core_bindings'}","'permission','targets','core_bindings','assignment_scope_ref'}")
    value=value.replace("scope_ref=selected['storage_scope_ref'],evaluated_at=clock,permission=owner['permission'],targets=tuple(owner['targets']))",
        "storage_scope_ref=selected['storage_scope_ref'],assignment_scope_ref=owner['assignment_scope_ref'],\n                evaluated_at=clock,permission=owner['permission'],targets=tuple(owner['targets']))")
    p.write_text(value)
    replace(p,"key=(owner['principal_ref'],owner['role_ref']);require(key not in seen,'ambiguous owner recognition');seen.add(key)",
        "key=(owner['principal_ref'],owner['role_ref']);require(key not in seen,'ambiguous owner recognition');seen.add(key)\n            require(type(owner['assignment_scope_ref']) is str and owner['assignment_scope_ref'],'explicit Role Assignment domain required')")
    p=NEW/'test_owners.py'
    replace(p,"self.targets=({'identity_ref':'work:fixture:one','version_ref':'work:fixture:one@1','kind':'work','operation':'admit'},)",
        "self.targets=({'identity_ref':'work:fixture:one','version_ref':'work:fixture:one@1','kind':'work','operation':'admit','scope_ref':self.scope},)")
    replace(p,'role_ref=self.role,scope_ref=self.scope,','role_ref=self.role,storage_scope_ref=self.scope,assignment_scope_ref=self.scope,')
    replace(p,"'accountable_principal_ref':self.principal,'scope_ref':self.scope,","'accountable_principal_ref':self.principal,'storage_scope_ref':self.scope,")
    replace(p,"'owners':[{'principal_ref':self.principal,'role_ref':self.role,'public_key':", "'owners':[{'principal_ref':self.principal,'role_ref':self.role,'assignment_scope_ref':self.scope,'public_key':")
    with p.open('a') as stream:stream.write('''
    def test44_principal_body_scope_is_separate_from_storage(self):
        self.rows['principal']['scope_ref']='scope:principal-registry'
        self.assertTrue(self.join()['join_consistent'])
    def test45_assignment_domain_is_independently_checked(self):
        self.rows['role-assignment']['scope_ref']='scope:other-authority-domain';self.rejected()
    def test46_target_domain_is_not_storage_scope(self):
        self.targets=({**self.targets[0],'scope_ref':'scope:other-target-domain'},);self.rejected()
    def test47_original_header_storage_scope_is_checked(self):
        records=self.records();r=records['principal'];h={**r.header,'scope_ref':'store-scope:other'}
        records['principal']=O.Record(h,r.original,r.source_state)
        with self.assertRaises(O.OwnerFault): self.join(records)
    def test48_one_assignment_does_not_cover_another_domain(self):
        self.targets=(*self.targets,{**self.targets[0],'version_ref':'work:fixture:two@1','scope_ref':'scope:other-domain'})
        self.rejected()
    def test49_distinct_authority_record_body_domains_are_retained(self):
        for kind in ('principal','authority-claim','authority-boundary','decision-scope'):
            self.rows[kind]['scope_ref']='scope:record-domain:'+kind
        result=self.join();self.assertTrue(result['join_consistent'])
        self.assertEqual(result['assignment_scope_ref'],self.scope);self.assertEqual(result['storage_scope_ref'],self.scope)
''')
    assert len(methods(p))==49 and all(methods(p)[k]==v for k,v in methods(OLD/'test_owners.py').items())
    p=NEW/'checks.py';value=p.read_text().replace('_cal_checkpoint_owner_verification_v2','_cal_checkpoint_owner_verification_v3').replace('==43','==49').replace("'expected_cases':43","'expected_cases':49");p.write_text(value)
    p=NEW/'README.md';value=p.read_text().replace('The 43 checks','The 49 checks')
    value+='''

Version3 separates the artifact header's storage scope from the Role Assignment's
authority domain. Principal registry, claim, boundary and Decision Scope bodies
may retain their own semantic domains. The independent owner selection names the
storage scope and each assignment domain explicitly. Each selected target must
belong to that assignment domain; authority does not spread across domains merely
because targets share a storage namespace. All 43 prior test bodies are unchanged;
six cases check these distinctions. Exact target-to-core/package coupling still
requires composition with the checkpoint rule kernel; selected target text alone
does not authorize anything. Version2's passing evidence remains preserved.
''';p.write_text(value)
    freeze=(RUN/'freeze-checkpoint-owner-verification-0002.py').read_text().replace('checkpoint-owner-verification-v2','checkpoint-owner-verification-v3')
    freeze=freeze.replace("bind(RUN/'author-checkpoint-owner-verification-0002.py')","bind(RUN/'author-checkpoint-owner-verification-0003.py')")
    freeze=freeze.replace("'docs/proposals/0007-lab-integrated-schema-package/schemas/common.schema.json',",
        "'docs/proposals/0007-lab-integrated-schema-package/schemas/common.schema.json',\n        'product/lab/release-candidates/v1/interface/checkpoint-owner-verification-v2/source-manifest.json',\n        'product/lab/release-candidates/v1/interface/checkpoint-owner-verification-v2/receipts/checks-0001.json',\n        'product/lab/release-candidates/v1/interface/checkpoint-owner-verification-v2/receipts/actual-0001.log',")
    with (RUN/'freeze-checkpoint-owner-verification-0003.py').open('x') as stream:stream.write(freeze)
    print('Authored owner verification v3; all 43 original test bodies unchanged, six domain/storage distinction cases added.',flush=True)
if __name__=='__main__':main()
