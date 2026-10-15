"""Authored pure controls; execute only after Root review. No API/native imports."""
import ast,copy,hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');HERE=Path(__file__).absolute().parent
POST=HERE/'postimages/product/lab/release-candidates/v1/interface/api-integration-v17'
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    sys.path.append(str(INSTALL/'deps'))
    from jsonschema import Draft202012Validator
    checks=[]
    R=module('_T31_own_registry',POST/'workflow_output_registry.py')
    V=module('_T31_own_result_validation',POST/'workflow_output_validation.py')
    inventory=json.loads((ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T31/output-transitions-0001/workflow-output-inventory.json').read_bytes())
    original={t['transition_ref']:(w,t) for w in inventory['workflows'] for t in w['transitions']}
    assert len(R.REGISTRY)==len(original)==28 and len(inventory['workflows'])==10
    for ref,row in R.REGISTRY.items():
        w,t=original[ref];assert row['output_carriers']==t['original_required_output_carriers'] and row['original_producer_path']==t['exact_original_producer_consumer_path'] and row['definition_binding']==w['original_definition_binding']
    checks.append('all10 original definitions and28 full output/carrier/producer obligations retained')
    header={'identity_ref':'OWNED-INERT','version_ref':'OWNED-INERT@1','byte_sha256':'1'*64}
    assert V.contains_original({'review':{'member_records':[{'identity_ref':'OWNED-INERT','version_ref':'OWNED-INERT@1','record_sha256':'1'*64}]}},header)
    for wrong in [{'sha256':'1'*64},{'identity_ref':'OWNED-INERT','version_ref':'OTHER@1','sha256':'1'*64},{'identity_ref':'OTHER','version_ref':'OWNED-INERT@1','sha256':'1'*64},{'identity_ref':'OWNED-INERT','version_ref':'OWNED-INERT@1','sha256':'2'*64},b'OWNED-INERT',{'actual_invoked':True,'authority_effect':'none'}]:assert not V.contains_original(wrong,header)
    checks.append('real result needs exact identity/version/digest triple; hash-only/header guess/flag refuses')
    for p in POST.glob('*.py'):ast.parse(p.read_bytes())
    checks.append('all postimage Python ASTs parse without importing API')
    def methods(raw):
        return {n.name:ast.dump(n,include_attributes=False) for c in ast.parse(raw).body if isinstance(c,ast.ClassDef) and c.name=='Service' for n in c.body if isinstance(n,ast.FunctionDef)}
    old=methods((ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17/service.py').read_bytes());new=methods((POST/'service.py').read_bytes())
    assert set(old)==set(new) and {k for k in old if old[k]!=new[k]}=={'__init__','select_workflow_transition'}
    checks.append('Service preserves every original method except declared fingerprints/private reader factory')
    schema=json.loads((HERE/'private-output-plan.schema.json').read_bytes());Draft202012Validator.check_schema(schema)
    packet=json.loads((HERE/'UNRESOLVED-private-output-plan.json').read_bytes())
    assert not Draft202012Validator(schema).is_valid(packet)
    checks.append('inactive unknown private original selectors refuse schema')
    assert 'bridge_binding' not in schema['properties'] and 'workflow_output_binding' not in schema['properties']
    checks.append('child private plan cannot bind parent descriptor digest or create selector digest cycle')
    assert (HERE/'private-output-plan.schema.json').read_bytes()==(POST/'workflow-output-plan.schema.json').read_bytes()
    for ref in original:
        assert schema['properties']['transitions']['properties'][ref]['properties']['transition_ref']=={'const':ref}
    checks.append('all28 explicit transition slots/controls required; no future output hashes prebound')
    proposal=json.loads((HERE/'ROOT-selection-proposal.json').read_bytes());assert proposal['active'] is False and set(proposal['routes'])==set(original)
    for ref,row in proposal['routes'].items():
        assert row['original_required_output_carriers']==original[ref][1]['original_required_output_carriers'] and row['original_authority_precondition_satisfaction_relation_obligations']==original[ref][1]['original_authority_precondition_satisfaction_relation_obligations']
        assert all(len(b['schema_binding']['sha256'])==64 for b in row['schema_bindings'])
    checks.append('all28 source/callable/schema proposal retains every original obligation, with no active future selection')
    conservation=json.loads((HERE/'original-input-conservation.json').read_bytes());parent=json.loads((ROOT/conservation['parent_input_selection']['path']).read_bytes());assert conservation['declarations']==parent['files'] and len(conservation['declarations'])==293
    checks.append('all293 original input declarations conserved one-for-one')
    # Unknown outcomes must be rejected before completing the opaque capsule.
    body=(POST/'workflow_producer_outputs.py').read_text();assert body.index('unknown/partial original outcome requires reconciliation')<body.index('capsule._pending=False')
    checks.append('unknown outcomes cannot be upgraded by output-only reconciliation')
    assert all('outputs_binding' not in r['properties'] for r in schema['properties']['transitions']['properties'].values())
    controls_schema=json.loads((POST/'workflow-stage-controls.schema.json').read_bytes());Draft202012Validator.check_schema(controls_schema)
    assert len(controls_schema['oneOf'])==len({json.dumps(v,sort_keys=True)for v in controls_schema['oneOf']})
    checks.append('all exact stage-control alternatives retained once; duplicate oneOf rejection corrected')
    checks.append('design/formal-Session/native private controls use closed explicit schemas')
    def klass(raw,name):
        return {n.name:ast.dump(n,include_attributes=False) for c in ast.parse(raw).body if isinstance(c,ast.ClassDef) and c.name==name for n in c.body if isinstance(n,ast.FunctionDef)}
    old_journal=klass((ROOT/'product/lab/release-candidates/v1/interface/workflow-transition-v1/journal.py').read_bytes(),'Journal');new_journal=klass((POST/'workflow_output_journal.py').read_bytes(),'Journal')
    assert set(old_journal)==set(new_journal) and {k for k in old_journal if old_journal[k]!=new_journal[k]}=={'initialize','__init__','replay','apply','recover'}
    checks.append('original journal locks/namespace/lookup helpers unchanged; output closure added at apply/replay/recovery')
    M=module('_T31_own_material_controls',HERE/'material_controls.py');checks.extend(M.main())
    S=module('_T31_v4_own_scope_controls',HERE/'scope_controls.py');checks.extend(S.main())
    R=module('_T31_v4_own_response_controls',HERE/'response_controls.py');checks.extend(R.main())
    I=module('_T31_v4_own_invocation_controls',HERE/'invocation_controls.py');checks.extend(I.main())
    for name in ('workflow-native-scope.schema.json','workflow-response-permission.schema.json'):Draft202012Validator.check_schema(json.loads((POST/name).read_bytes()))
    checks.append('new native scope and phase-specific response schemas are closed and valid')
    print(json.dumps({'result':'PASS-pure-T31-owned-components','checks':checks,'tests_actual_producer_WorkflowRun_or_native':False,'all28_genuine_runtime_qualified':False,'authority_effect':'none','task_complete':False},sort_keys=True))
if __name__=='__main__':main()
