"""Close Intent Resolution's required Decision/Effect declarations explicitly."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'current-participation-v9';NEW=BASE/'current-participation-v10'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    assert not NEW.exists()
    shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('packages','receipts','__pycache__','source-manifest.json'))
    p=NEW/'base.py';p.write_text(p.read_text().replace('_0009','_0010'))
    p=NEW/'build.py';s=p.read_text().replace('R03-current-participation-0009','R03-current-participation-0010').replace('cal-R03-workflow-source-0009-','cal-R03-workflow-source-0010-').replace('R03-workflow-source-0009','R03-workflow-source-0010').replace('Source9','Source10')
    s=s.replace("evidence_refs=['protocol:R03-Source10-intent-resolution-approval'],relation_refs=[],successor_refs=[])",
        "evidence_refs=[str((HERE.parent/'current-participation-v9/packages/0001/failure.json').relative_to(ROOT))],relation_refs=[{'relation_kind_ref':'relation.declares-effect-on','direction':'target','counterpart_kind':'decision','counterpart_ref':decision_ref+'@'+records.VERSION}],successor_refs=[])")
    before="""            data=commit('workflow-intent-resolution',[target],{version:original_resolution})
            current.append({**all_rows[-1],'original_binding':binding(out/'workflow-intent-resolution.json'),'encoding':handle.custody.ENCODING})"""
    after="""            decision=integration.fixture('decision');effect=integration.fixture('effect')
            effect_ref='effect:Source10:isolated-workflow-interpretation'
            evidence=str((HERE.parent/'current-participation-v9/packages/0001/failure.json').relative_to(ROOT))
            for body,identity in [(decision,decision_ref),(effect,effect_ref)]:
                body.update(node_id=identity,owner_ref=records.PRINCIPAL,scope_ref=data['config']['scope_ref'],
                    lifecycle_state='candidate',evidence_refs=[evidence],successor_refs=[],
                    challenge_route='protocol:R03-owned-workflow-source-review',
                    claim_ceiling='Actual test-owned candidate interpretation declaration; no human owner outcome, canonical admission or Work completion.')
            decision['payload'].update(decision_maker_ref=records.PRINCIPAL_REFERENCE+'@'+records.VERSION,
                selected_outcome='select-isolated-workflow-source-inspection',subject_refs=[version],
                declared_effect_refs=[effect_ref+'@'+records.VERSION],evidence_basis_refs=[evidence])
            decision['relation_refs']=[integration.role('relation.declares-effect-on','intent-resolution',version),
                integration.role('relation.declares-effect-on','effect',effect_ref+'@'+records.VERSION)]
            effect['payload'].update(effect_kind='select-isolated-workflow-source-inspection',subject_ref=version,
                intended_state='candidate-interpretation-selected',effective_when='Exact independent test-owned approval and original source replay are verified',
                verification_refs=[evidence])
            effect['relation_refs']=[integration.role('relation.declares-effect-on','decision',decision_ref+'@'+records.VERSION,'target')]
            additions=[target];addition_originals={version:original_resolution}
            for body,carrier in [(decision,'cal.artifact-type.decision/v2'),(effect,'cal.artifact-type.effect/v1')]:
                ref=body['node_id']+'@'+records.VERSION;raw=authored_bytes(body)
                additions.append({'category':'artifact-instance','operation':'admit','version_ref':ref,'carrier_ref':carrier,
                    'record':body,'predecessor_ref':None,'decision_ref':'decision:Source10:local-import:'+ref,'contract':None})
                addition_originals[ref]=raw;emit(out/('workflow-'+body['kind']+'.json'),None,raw=raw)
            relation_template=load(ROOT/'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/fixtures/valid/record.json')
            for suffix,body_kind,right in [('resolution','intent-resolution',version),('effect','effect',effect_ref+'@'+records.VERSION)]:
                body=copy.deepcopy(relation_template);identity='typed-relation:Source10:workflow-decision-'+suffix
                body.update(schema_version='cyberalchemy-lab-typed-relation/v4',node_id=identity,scope_ref=data['config']['scope_ref'],
                    owner_ref=records.PRINCIPAL,evidence_refs=[evidence],relation_refs=[],successor_refs=[],
                    challenge_route='protocol:R03-owned-workflow-source-review',claim_ceiling=decision['claim_ceiling'])
                body['payload'].update(relation_kind_ref='relation.declares-effect-on',
                    source={'kind':'decision','ref':decision_ref,'version_ref':decision_ref+'@'+records.VERSION},
                    target={'kind':body_kind,'ref':right.split('@')[0],'version_ref':right},
                    qualifiers={'effect_kind':'select-isolated-workflow-source-inspection','exact_target_version_ref':right},relation_evidence_refs=[evidence])
                ref=identity+'@'+records.VERSION;raw=authored_bytes(body)
                additions.append({'category':'typed-relation','operation':'admit','version_ref':ref,'carrier_ref':'cal.artifact-type.typed-relation/v4',
                    'record':body,'predecessor_ref':None,'decision_ref':'decision:Source10:local-import:'+ref,'contract':None})
                addition_originals[ref]=raw;emit(out/('workflow-relation-'+suffix+'.json'),None,raw=raw)
            data=commit('workflow-intent-resolution',additions,addition_originals)
            for item in additions:
                if item['category']=='typed-relation':handle.operations.validate_relation(item['record'],data['projection'])
            current.extend(all_rows[-len(additions):])"""
    assert s.count(before)==1;s=s.replace(before,after);ast.parse(s);p.write_text(s)
    parent=json.loads((OLD/'source-manifest.json').read_bytes());rows={r['path']:r for r in parent['files']}
    for p in [OLD/'source-manifest.json',OLD/'packages/0001/failure.json',Path(__file__).resolve()]:rows[p.relative_to(ROOT).as_posix()]=bind(p)
    for p in sorted(NEW.glob('*')):
        if p.is_file():
            if p.suffix=='.py':ast.parse(p.read_text())
            rows[p.relative_to(ROOT).as_posix()]=bind(p)
    value={**parent,'schema_version':'lab-current-participation-source/v10-candidate','files':[rows[k] for k in sorted(rows)],
        'failed_parent_source_binding':bind(OLD/'source-manifest.json'),'failed_parent_result_binding':bind(OLD/'packages/0001/failure.json'),
        'expected_original_targets':110,'expected_signed_transactions':6,
        'explicit_resolution_closure':['Exact current test-owned Intent Resolution','Original candidate Decision and Effect','Two exact v4 declared-effect connections'],
        'claim_ceiling':'Frozen isolated source producer; actual signed construction, cold replay, current source adapter and public transition qualification required. No canonical admission or human owner outcome.'}
    with (NEW/'source-manifest.json').open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':'FROZEN','source_binding':bind(NEW/'source-manifest.json')}),flush=True)
if __name__=='__main__':main()
