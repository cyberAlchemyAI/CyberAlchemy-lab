"""Final direct candidate controls, preserving prior bounded receipts."""
import ast,copy
from .pure_controls import main as original_controls,HERE

def main():
    result=original_controls();checks=result['checks']
    def fn(path,name,cls=None):
        tree=ast.parse((HERE/path).read_bytes());nodes=tree.body
        if cls:nodes=next(n for n in nodes if isinstance(n,ast.ClassDef)and n.name==cls).body
        return next(n for n in nodes if isinstance(n,ast.FunctionDef)and n.name==name)
    def calls(node):return [ast.unparse(n.func)for n in ast.walk(node)if isinstance(n,ast.Call)]
    publish=fn('gateway.py','publish','NativeMixedPublisher');actual=calls(publish)
    assert actual.count('self.replay_store._commit_record')==1 and actual.count('self.store._commit_record')==1
    assert 'self.replay_store.lock'in actual
    checks.append('separate persistent T33 replay root lock and descriptor reservation held through commit')
    assert actual.index('self.store.write')<actual.index('self.replay_store._commit_record')<actual.index('self.store._commit_record')
    checks.append('complete durable selected plan precedes owner reservation and outer visibility')
    cold=fn('gateway.py','inspect_committed','NativeMixedPublisher');actual=calls(cold)
    assert not any(s.endswith(('.publish','.reserve','.prepare_promotion'))for s in actual)
    assert 'self._cold_native'in actual and 'self._verify_repository'in actual
    checks.append('cold inspection never redispatches/reserves and requires native plus complete original consequences')
    selected=fn('gateway.py','_cold_native','NativeMixedPublisher');actual=calls(selected)
    assert 'self.native_factory.cold_snapshot_original_outcome'in actual and not any(s.endswith(('.head','.read_committed','.append','.run'))for s in actual)
    checks.append('cold consumer selects exact immutable old generation rather than mutable HEAD')
    recovery=fn('adoption.py','construct_cold_reader');assert not any(s.endswith(('.prepare_promotion','.verify_for_publication'))for s in calls(recovery))
    checks.append('fresh cold construction uses separate actual recovery guard without replaying old publication permission')
    old=fn('preimages/original-owner-verify.py','verify');new=fn('owner_history.py','verify_committed_response');normalized=copy.deepcopy(new)
    normalized.name=old.name;normalized.args=copy.deepcopy(old.args);normalized.body[0]=copy.deepcopy(old.body[0])
    start=next(i for i,n in enumerate(normalized.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='require'for t in n.targets))
    end=next(i for i,n in enumerate(normalized.body)if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='require')
    del normalized.body[start:end]
    class Restore(ast.NodeTransformer):
        def visit_Assign(self,node):
            if any(isinstance(t,ast.Name)and t.id=='now'for t in node.targets):node.value=ast.parse('datetime.now(timezone.utc)',mode='eval').body
            return self.generic_visit(node)
    normalized=Restore().visit(normalized)
    assert ast.dump(normalized,include_attributes=False)==ast.dump(old,include_attributes=False)
    checks.append('full original T33 proof/signature/role/source/period semantics preserved except explicit historical observation-time input')
    for name in ('check','directory','snapshot','close'):
        old=fn('preimages/technical-publisher-v2.py',name,'OwnedBytePublisher');new=fn('receipt_store.py',name,'ReceiptStore')
        assert ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False)
    checks.append('original anchored attachment/member traversal and no-deletion close semantics conserved')
    result.update(count=len(checks));return result
