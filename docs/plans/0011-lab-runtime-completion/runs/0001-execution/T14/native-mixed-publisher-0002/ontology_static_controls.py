"""Static contract conservation; no original projection or mapper is imported."""
import ast
from pathlib import Path
HERE=Path(__file__).absolute().parent

def main():
    tree=ast.parse((HERE/'ontology_snapshot.py').read_bytes());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='OriginalOntologyColdCapture')
    f=next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name=='capture_selected');calls=[ast.unparse(n.func)for n in ast.walk(f)if isinstance(n,ast.Call)]
    returns=[n for n in ast.walk(f)if isinstance(n,ast.Return)and isinstance(n.value,ast.Dict)];assert len(returns)==1
    fields={k.value for k in returns[0].value.keys};expected={'schema_version','principal_ref','work_ref','source_cut','store_ref','mapping_binding','mapping_policy_original','mapping_original_binding','mapping_original','manifest_binding','manifest_original','head_binding','head_original','native_read_binding','native_read_original','native_files','cold_replay_binding','cold_replay_original','expires_at','authority_effect'}
    assert fields==expected
    assert calls.count('self.projection.mapper.call')==1 and 'self.projection.apply'not in calls
    assert calls.count('self.store.snapshot')==2 and calls.count('self.store.read')>=3
    assert not any(c.endswith(('write','_commit_record','append','unlink','remove','rename','replace'))for c in calls)
    assert 'self.public'in calls and 'self.software.function'in calls
    text=ast.unparse(f);assert "'/proc'"in text and 'os.getpid()'in text and "'fd'"in text
    assert "p != 'request.json'"in text
    return {'result':'PASS-static-contract-only','checks':['closed ontology return fields equal split policy/mapping T31 contract','actual original mapper called once; no producer apply/append/commit redispatch','complete original generation snapshots before and after actual read plus head rechecks','no write/delete/rename in original ontology cold capability','independently captured original projection/mapper callable membership','explicit held-controller-generation descriptor locator adaptation','typed native_files excludes request while actual read still receives captured request'], 'actual_native_calls':0,'dynamic_ontology_provider_qualification':False,'authority_effect':'none'}
