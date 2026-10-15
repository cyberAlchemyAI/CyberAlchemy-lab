"""Author exact carrier-aware preparation and explicitly represented connections."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
I=ROOT/'product/lab/release-candidates/v1/interface'
P=I/'api-v37';A=I/'api-v38';OLD=I/'classification-preparation-v2';C=I/'classification-preparation-v3'
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not A.exists() and not C.exists()
    rule=I/'classification-rules-v3';proof=rule/'receipts/proof-0001.json';value=json.loads(proof.read_bytes())
    assert value['result']=='PASS' and value['actual_cases']==35 and value['actual_terminal_exit_code']==0
    assert bind(P/'source-manifest.json')['sha256']=='79920ea00200c5f9146d545a42b565aeed0be66f88c6c07452aea4d4d788a81d'
    shutil.copytree(P,A,ignore=shutil.ignore_patterns('source-manifest.json','contract-profile.json','receipts','__pycache__'))
    shutil.copytree(OLD,C,ignore=shutil.ignore_patterns('receipts','__pycache__'))
    p=A/'classification_preparation.py';s=p.read_text().replace('classification-preparation-v2','classification-preparation-v3').replace('_classification_preparation_v2','_classification_preparation_v3');p.write_text(s)
    p=A/'source_bridge.py';s=p.read_text().replace('_cal_api_v37_custody_context_v8','_cal_api_v38_custody_context_v8');p.write_text(s)
    p=C/'preparation.py';s=p.read_text().replace('classification-rules-v2','classification-rules-v3').replace('838255c60c56c37ecfb8af10edf4708c97efc9b2b42adb51df5e773cdbf934e1',bind(rule/'source-manifest.json')['sha256']).replace('f37815799df1b906c8ba8703c551862f66600cae8948e38c725899e5b65449b3',bind(proof)['sha256']).replace("document['actual_cases']==21","document['actual_cases']==35").replace('_public_classification_preparation_rules_v2','_public_classification_preparation_rules_v3')
    old="            if 'node_id' not in body:continue\n            require(body['scope_ref']==scope,'current classification record scope differs')\n            records[header['version_ref']]=self.rules.ExactRecord(header['version_ref'],raw,header['byte_sha256'])\n            headers[header['version_ref']]=header"
    new="""            headers[header['version_ref']]=header
            # Every current domain instance is retained. Catalog declarations
            # join when explicitly requested, with their own carrier witness.
            requested={message[key]['version_ref'] for key in ('subject','scheme','value')}
            if subject['category'] not in ('artifact-instance','typed-relation') and header['version_ref'] not in requested:continue
            if all(key in body for key in ('node_id','kind','scope_ref')):
                require(body['scope_ref']==scope,'current classification record scope differs')
                records[header['version_ref']]=self.rules.ExactRecord(header['version_ref'],raw,header['byte_sha256'])
            else:
                records[header['version_ref']]=self.rules.TypedRecord(header['version_ref'],raw,header['byte_sha256'],public_artifact_ref(header))"""
    assert s.count(old)==1;s=s.replace(old,new)
    old="            if 'node_id' not in body:continue\n            require(header['scope_ref']==body['scope_ref']==scope,'prospective classification scope differs')\n            require(header['version_ref'] not in records,'prospective classification revision duplicates current source')\n            records[header['version_ref']]=self.rules.ExactRecord(header['version_ref'],raw,header['byte_sha256'])\n            headers[header['version_ref']]=header"
    new="""            require(header['scope_ref']==scope,'prospective classification header scope differs')
            require(header['version_ref'] not in records,'prospective classification revision duplicates current source')
            if all(key in body for key in ('node_id','kind','scope_ref')):
                require(body['scope_ref']==scope,'prospective classification scope differs')
                records[header['version_ref']]=self.rules.ExactRecord(header['version_ref'],raw,header['byte_sha256'])
            else:
                records[header['version_ref']]=self.rules.TypedRecord(header['version_ref'],raw,header['byte_sha256'],public_artifact_ref(header))
            headers[header['version_ref']]=header"""
    assert s.count(old)==1;s=s.replace(old,new)
    s=s.replace("if row.body()['kind']=='classification-assignment'","if row.semantic_kind()=='classification-assignment'")
    p.write_text(s);ast.parse(s)
    p=A/'classification_fixture.py';s=p.read_text()
    s=s.replace("carrier = 'cal.artifact-type.' + kind + '/v1'","carrier = 'cal.artifact-type.' + kind + ('/v3' if kind == 'typed-relation' else '/v1')")
    s=s.replace("'category': 'artifact-instance', 'operation': 'admit'","'category': 'typed-relation' if kind == 'typed-relation' else 'artifact-instance', 'operation': 'admit'")
    s=s.replace("'category': 'artifact-instance', 'decision_ref': runtime['decision_ref']","'category': runtime['category'], 'decision_ref': runtime['decision_ref']")
    needle='    return subject, [scheme, value, assignment] + extra, axis'
    replacement="""    all_bodies=[scheme,value,assignment]+extra
    scheme['relation_refs']=[{'relation_kind_ref':'relation.member-of','direction':'target',
        'counterpart_kind':'classification-value','counterpart_ref':value_ref}]
    for body in all_bodies:
        if body['kind']=='classification-value':
            body['relation_refs']=[{'relation_kind_ref':'relation.member-of','direction':'source',
                'counterpart_kind':'classification-scheme','counterpart_ref':scheme_ref}]
        elif body['kind']=='classification-assignment':
            body['relation_refs']=[{'relation_kind_ref':'relation.governed-by','direction':'source',
                'counterpart_kind':'classification-scheme','counterpart_ref':scheme_ref}]
    return subject, all_bodies, axis"""
    assert s.count(needle)==1;s=s.replace(needle,replacement)
    needle='    if mode == \'bad-core\':'
    insertion="""    connections=[]
    original_targets=list(targets)
    template=P.frame_parse((ROOT/'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/fixtures/valid/record.json').read_bytes())
    scheme_header=targets[0]['artifact']
    from .classification_preparation import selected as composition
    for endpoint in original_targets:
        kind=endpoint['artifact']['carrier_ref'].split('.')[-1].split('/')[0]
        if kind not in ('classification-value','classification-assignment'):continue
        relation_kind='relation.member-of' if kind=='classification-value' else 'relation.governed-by'
        qualifiers={'membership_role':'Explicit candidate Value membership'} if kind=='classification-value' else {'governance_role':'Explicit annotation-rule governance only'}
        body=copy.deepcopy(template)
        body.update(node_id='typed-relation:R03-classification:'+endpoint['artifact']['identity_ref'],
            scope_ref=subject['scope_ref'],relation_refs=[],evidence_refs=['candidate:classification-basis'],successor_refs=[],authority_effect='none')
        body['payload'].update(relation_kind_ref=relation_kind,
            source={'kind':kind,'ref':endpoint['artifact']['identity_ref'],'version_ref':endpoint['artifact']['version_ref']},
            target={'kind':'classification-scheme','ref':scheme_header['identity_ref'],'version_ref':scheme_header['version_ref']},
            qualifiers=qualifiers,relation_evidence_refs=['candidate:classification-basis'])
        targets.append(target(view,body,materials,metadata))
        signature,signature_binding=M.signature(view,relation_kind)
        connections.append({'relation_kind_ref':relation_kind,'signature_sha256':signature_binding['sha256'],
            'axis_ref':signature['payload']['axis_id'],
            'source':{'artifact':composition.public_artifact_ref(endpoint['artifact']),'semantic_kind':kind},
            'target':{'artifact':composition.public_artifact_ref(scheme_header),'semantic_kind':'classification-scheme'},
            'qualifiers':qualifiers})
"""
    assert s.count(needle)==1;s=s.replace(needle,insertion+needle)
    s=s.replace("'connection_proposals': [], 'evidence_bindings': []","'connection_proposals': connections, 'evidence_bindings': []")
    p.write_text(s);ast.parse(s)
    p=A/'test_classification_api.py';s=p.read_text();old="self.assertEqual(len(reply['message']['targets']), 3)";assert s.count(old)==1;p.write_text(s.replace(old,"self.assertEqual(len(reply['message']['targets']), 5)"))
    retained=[];revised=[]
    for path in P.rglob('*.py'):
        if 'receipts' in path.parts or '__pycache__' in path.parts:continue
        old=methods(path);new=methods(A/path.relative_to(P));assert old.keys()==new.keys()
        for name in old:
            key=str(path.relative_to(P))+':'+name
            (retained if old[name]==new[name] else revised).append(key)
    assert len(retained)==274 and revised==['test_classification_api.py:test_01_exact_original_ChangeProposal_result']
    output=RUN/'API38-carrier-classification-construction-0001.json'
    value={'schema_version':'lab-successor-construction/v1-candidate','result':'AUTHORED','parent_source_binding':bind(P/'source-manifest.json'),
        'rule_source_binding':bind(rule/'source-manifest.json'),'rule_proof_binding':bind(proof),
        'retained_exact_method_ASTs':274,'explicit_revised_method_ASTs':revised,'total_original_test_methods':275,
        'fixture_revision_reason':'Schema-valid declared role endpoints and two separately represented Typed Relations require five independent baseline target cores.',
        'changes':['Explicit original carrier identity/scope witnesses; original bytes are never rewritten.','All current domain instances and explicitly requested catalog declarations enter the classification selection.','Every declared fixture connection has its own Typed Relation target and exact signature/endpoint/qualifier proposal.'],
        'original_contracts':34,'remaining_qualified_operations':21,'original_plan_tasks':46,
        'source_frozen':False,'runtime_qualified':False,'new_fixture_effects':0,'authority_effect':'none','actual_owner_outcome':None}
    with output.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':'AUTHORED','retained_exact_methods':274,'explicit_revision':revised,'source_frozen':False}),flush=True)
if __name__=='__main__':main()
