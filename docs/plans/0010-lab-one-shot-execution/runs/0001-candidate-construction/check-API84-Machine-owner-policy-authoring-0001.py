"""Check exact composition structure without transferring runtime qualification."""
import ast
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD,API=BASE/'api-v83',BASE/'api-v84'
COMPONENT=BASE/'machine-context-scope-v1'


def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())


def methods(path):
    return {node.name:ast.dump(node,include_attributes=False) for node in ast.walk(ast.parse(path.read_text()))
            if isinstance(node,ast.FunctionDef) and node.name.startswith('test_')}


def main():
    checks=[];count=0
    for old in OLD.glob('*.py'):
        assert methods(old)==methods(API/old.name),old.name
        count+=len(methods(old))
    assert count==323
    checks.append({'check':'all323-original-test-method-ASTs-unchanged','result':'PASS'})
    for name in ('machine_transport.py','auth.py','workspace.py','guarded_reads.py','guarded_candidate.py','protocol.py'):
        assert (OLD/name).read_bytes()==(API/name).read_bytes(),name
    checks.append({'check':'original-Machine-auth-permission-allowlist-clock-vault-and-protocol-bytes-unchanged','result':'PASS'})
    text=(COMPONENT/'generation.py').read_text();ast.parse(text)
    assert 'class OwnerPolicyScope(K.ReadScope)' in text and 'super().check()' in text
    assert 'G._generate(custodian.source,custodian.bridge,message,request_raw' in text
    assert 'self.policy_channel=owner.channel' in text and 'return self.policy_channel' in text
    assert 'require(value is self.policy_peer' in text
    checks.append({'check':'original-sealed-copy-and-generator-with-exact-parent-policy-host-and-Machine-Actor','result':'PASS'})
    for fragment in ['custodian.parent is owner.sessions','peer.resource is owner.sessions.live.get',
                     'peer.resource.bridge.channel is owner.channel','custodian.bridge.channel is peer',
                     'not peer.closed and not peer.resource.closed','Machine policy custody changed during fact scope']:
        assert fragment in text,fragment
    checks.append({'check':'actual-owner-source-live-resource-and-private-custodian-identity-chain-closed','result':'PASS'})
    assert 'K.require_outside_scope()' in text and 'del K._active.value' in text
    assert text.count('source.guard()')>=2 and 'checked(source.guard)' in text
    assert 'checked(channel.guard)' in text and 'scope.closed=True' in text
    checks.append({'check':'complete-source-policy-boundaries-and-registry-cleanup-surround-pure-calculation','result':'PASS'})
    for node in ast.walk(ast.parse(text)):
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Attribute) and isinstance(target.value,ast.Name) and target.value.id in ('D','G','K'):
                    raise AssertionError('original selected module assignment forbidden')
    checks.append({'check':'no-original-source-kernel-generator-or-permission-callback-assignment','result':'PASS'})
    profile=load(API/'contract-profile.json');assert len(profile['implemented_operations'])==23
    for row in profile['files']:assert bind(ROOT/row['path'])==row,row['path']
    checks.append({'check':'full-selected-repository-profile-bytes-current','result':'PASS'})
    paths=[API/'source-manifest.json',API/'contract-profile.json',COMPONENT/'generation.py',COMPONENT/'DESIGN.md',
           RUN/'context-R03-Machine-owner-policy-scope-0084.json',
           RUN/'API83-original-Machine-generation-diagnosis-0001.json',Path(__file__).resolve()]
    value={'schema_version':'lab-Machine-owner-policy-authoring-checks/v1-candidate','result':'PASS',
           'checks':checks,'files':[bind(path) for path in paths],'original_inherited_methods':323,
           'unchanged_method_ASTs':323,'authored_handlers':23,'remaining_handlers':11,
           'actual_runtime_qualified':False,'actual_owner_outcome':None,'authority_effect':'none',
           'claim_ceiling':'Exact source/structure checks and separately observed original mismatch only. Actual repaired Machine and complete API qualification remain.'}
    output=RUN/'API84-Machine-owner-policy-authoring-checks-0001.json'
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','checks':len(checks),'binding':bind(output)}),flush=True)


if __name__=='__main__':main()
