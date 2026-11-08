"""Check exact submitted structure/rows/bytes; do not self-grant readiness."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1'
sys.path.insert(0,str(IMPL))
import contracts as c
import resolver as r
import obligations as o

SCHEMA_PATH=IMPL/'schemas/evidence.json'
FINITE_BRIDGE={
 'witness-found':('completed','supported','model-witness'),
 'countermodel-found':('completed','counterexample','model-witness'),
 'bounded-supported':('completed','supported','finite-exhaustion'),
 'bounded-no-theory-model':('completed','unknown','finite-exhaustion'),
 'bounded-no-admissible-model':('completed','vacuous','finite-exhaustion'),
 'bounded-no-witness':('completed','unknown','finite-exhaustion'),
 'bounded-no-countermodel':('completed','unknown','finite-exhaustion'),
 'resource-limit':('completed','unknown','none'),
 'timeout':('timeout','unknown','none'),
 'cancelled':('cancelled','unknown','none'),
 'provider-error':('error','unknown','none'),
 'unsupported':('completed','unsupported','none'),
 'malformed':('completed','malformed','none'),
 'unresolved-input-or-binding':('completed','unknown','none')}


class EvidenceFault(ValueError):
    def __init__(self,code,path=''):self.code=code;self.path=path


def digest(value):return r.digest(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode())


def schema():
    value=r.parse(SCHEMA_PATH.read_bytes(),str(SCHEMA_PATH));c.bounded_tree(value);stack=[value]
    while stack:
        node=stack.pop()
        if isinstance(node,dict):
            if '$ref' in node and not node['$ref'].startswith('#/$defs/'):raise EvidenceFault('nonlocal-evidence-schema-reference')
            stack.extend(node.values())
        elif isinstance(node,list):stack.extend(node)
    return value


def artifact_refs(bundle):
    """Derive the closed input manifest only from defined contract fields."""
    rows=[]
    def add(ref):
        if ref is not None:rows.append({'path':ref['path'],'sha256':ref['sha256']})
    for key in ['snapshot_ref','dependency_graph_ref','theory_ref','assumption_set_ref','required_set_ref']:add(bundle[key])
    for row in bundle['sources']:add(row)
    for row in bundle['interpretations']:
        for key in ['correspondence_ref','typed_ir_ref']:add(row[key])
    for ref in bundle['coupling_refs']:add(ref)
    for row in bundle['logical_results']:
        for key in ['native_input_ref','profile_ref','toolchain_ref']:add(row[key])
        if row['native_result'] is not None:add(row['native_result']['binding'])
        add(row['result']['source_fidelity']['review_ref'])
        for ref in row['result']['evidence_refs']:add(ref)
    for row in bundle['gate_results']:
        if row['native_result'] is not None:add(row['native_result']['binding'])
        for ref in row['evidence_refs']:add(ref)
    unique={}
    for row in rows:
        r.components(row['path'])
        if row['path'] in unique and unique[row['path']]['sha256']!=row['sha256']:raise EvidenceFault('conflicting-artifact-byte-binding',row['path'])
        unique[row['path']]=row
    return [unique[path] for path in sorted(unique)]


def finite_dimensions(native):
    if not isinstance(native,dict) or native.get('schema_version')!='definition-assurance-finite-result/v1-candidate' or native.get('authority_effect')!='none' or native.get('semantic_ready') is not False or native.get('unbounded_conclusion') is not None:raise EvidenceFault('invalid-finite-native-boundary')
    status=native.get('status')
    if status not in FINITE_BRIDGE:raise EvidenceFault('unsupported-finite-native-status')
    strength={'model-witness':'model-witness','bounded-exhaustion':'finite-exhaustion','none':'none'}.get(native.get('evidence_strength'))
    dimensions=FINITE_BRIDGE[status]
    if strength!=dimensions[2]:raise EvidenceFault('finite-native-strength-mismatch')
    if status in {'witness-found','countermodel-found'}:
        if not isinstance(native.get('witness'),dict) or native.get('exhaustion_complete') is not False:raise EvidenceFault('finite-native-witness-shape')
    elif strength=='finite-exhaustion':
        if native.get('exhaustion_complete') is not True or native.get('witness') is not None or not isinstance(native.get('space'),dict):raise EvidenceFault('finite-native-exhaustion-shape')
    elif native.get('exhaustion_complete') is not False or native.get('witness') is not None:raise EvidenceFault('execution-state-promoted-to-finite-evidence')
    return dimensions


def check(bundle,expected_required,root=None,captured=None):
    try:
        c.bounded_tree(bundle)
        if c.Draft202012Validator is None:raise EvidenceFault('missing-jsonschema-runtime')
        local=schema();c.Draft202012Validator.check_schema(local);errors=list(c.Draft202012Validator(local).iter_errors(bundle))
        if errors:return {'status':'malformed','diagnostics':[{'code':'schema-'+str(error.validator),'path':c.pointer(error.absolute_path)} for error in errors[:30]],'semantic_ready':False,'authority_effect':'none','claim_ceiling':'Structural evidence contract rejected; no logical/fidelity verdict.'}
        o.compare_required(expected_required,bundle['required_set'])
        required=expected_required['logical_manifest']['obligations'];gates=expected_required['administrative_and_semantic_gates'];results=bundle['logical_results'];gate_results=bundle['gate_results']
        for values,key in [(required,'obligation_id'),(gates,'gate_id')]:
            if len({row[key] for row in values})!=len(values):raise EvidenceFault('duplicate-independent-required-identity')
        ids=[row['obligation']['obligation_id'] for row in results];gate_ids=[row['gate']['gate_id'] for row in gate_results]
        if len(set(ids))!=len(ids) or set(ids)!={row['obligation_id'] for row in required}:raise EvidenceFault('logical-result-denominator-mismatch')
        if len(set(gate_ids))!=len(gate_ids) or set(gate_ids)!={row['gate_id'] for row in gates}:raise EvidenceFault('gate-result-denominator-mismatch')
        by_id={row['obligation_id']:row for row in required};by_gate={row['gate_id']:row for row in gates};sources={}
        for obligation in required:
            for source in obligation['source_refs']:
                old=sources.get(source['version_ref'])
                if old is not None and not r.same_json(old,source):raise EvidenceFault('conflicting-required-source-binding')
                sources[source['version_ref']]=source
        if not r.same_json(sorted(bundle['sources'],key=lambda row:row['version_ref']),[sources[key] for key in sorted(sources)]):raise EvidenceFault('selected-source-denominator-mismatch')
        interpretations=bundle['interpretations'];selection=[row['source']['version_ref'] for row in interpretations]
        if len(set(selection))!=len(selection) or set(selection)!=set(sources):raise EvidenceFault('interpretation-denominator-mismatch')
        for row in interpretations:
            if not r.same_json(row['source'],sources[row['source']['version_ref']]):raise EvidenceFault('interpretation-source-binding-mismatch')
        native_pairs=[(bundle['required_set_ref'],bundle['required_set'])]
        for row in results:
            identity=row['obligation']['obligation_id'];obligation=by_id[identity];result=row['result']
            if not r.same_json(row['obligation'],obligation):raise EvidenceFault('required-obligation-substituted',identity)
            if result['obligation_id']!=identity or result['statement_sha256']!=digest(obligation['statement']) or result['theory_sha256']!=expected_required['logical_manifest']['theory_sha256']:raise EvidenceFault('result-statement-or-theory-binding-mismatch',identity)
            if row['native_result'] is not None:
                native_pairs.append((row['native_result']['binding'],row['native_result']['data']))
                if row['native_result']['binding'] not in result['evidence_refs']:raise EvidenceFault('native-result-not-in-evidence-refs',identity)
                if row['provider_kind']=='finite-static':
                    dimensions=finite_dimensions(row['native_result']['data'])
                    if dimensions!=(result['execution'],result['verdict'],result['strength']):raise EvidenceFault('finite-native-dimension-substitution',identity)
        for row in gate_results:
            identity=row['gate']['gate_id']
            if not r.same_json(row['gate'],by_gate[identity]):raise EvidenceFault('required-gate-substituted',identity)
            if row['native_result'] is not None:
                native_pairs.append((row['native_result']['binding'],row['native_result']['data']))
                if row['native_result']['binding'] not in row['evidence_refs']:raise EvidenceFault('gate-native-result-not-in-evidence-refs',identity)
        refs=artifact_refs(bundle)
        if captured is not None and (not isinstance(captured,dict) or set(captured)!={row['path'] for row in refs}):raise EvidenceFault('captured-artifact-denominator-mismatch')
        if root is not None or captured is not None:
            resolved={}
            for ref in refs:
                raw=captured[ref['path']] if captured is not None else r.read_bytes(root,ref['path'])
                if not isinstance(raw,bytes) or r.digest(raw)!=ref['sha256']:raise EvidenceFault('stale-or-substituted-artifact',ref['path'])
                resolved[ref['path']]=raw
            for ref,data in native_pairs:
                actual=r.parse(resolved[ref['path']],ref['path'])
                if not r.same_json(actual,data):raise EvidenceFault('native-data-byte-binding-mismatch',ref['path'])
        pending=[row['obligation']['obligation_id'] for row in results if row['result']['execution']!='completed' or row['result']['verdict']!='supported' or row['result']['strength']!=row['obligation']['minimum_strength'] or row['result']['currentness']!='current' or row['result']['source_fidelity']['status']!='reviewed']
        pending_gates=[row['gate']['gate_id'] for row in gate_results if row['reported_status']!='reported-supported' or row['currentness']!='current' or row['execution']!='completed']
        return {'status':'candidate-accounted','authority_effect':'none','semantic_ready':False,'readiness':'not-assessed','evidence_verified':False,'native_bytes':'bound' if root is not None or captured is not None else 'not-resolved','required_logical_obligations':len(required),'required_gates':len(gates),'artifact_refs':len(refs),'pending_logical_reports':pending,'pending_gate_reports':pending_gates,'claim_ceiling':'Exact structural required-set/row and optional artifact byte/native-data binding only. Claimed dimensions, source fidelity, actual model/proof semantics and readiness require independent verification.'}
    except (EvidenceFault,o.ObligationFault,r.CaptureFault,c.InputError) as error:return {'status':'evidence-contract-invalid','authority_effect':'none','semantic_ready':False,'diagnostics':[{'code':error.code,'path':error.path}],'claim_ceiling':'No evidence acceptance or readiness from invalid/unresolved bindings.'}
    except (OSError,ValueError,KeyError,TypeError,IndexError,c.SchemaError) as error:return {'status':'unresolved-contract-runtime-or-shape','authority_effect':'none','semantic_ready':False,'diagnostics':[{'code':type(error).__name__}],'claim_ceiling':'No evidence acceptance or readiness from this execution outcome.'}
