#!/usr/bin/env python3
"""Validate outcome distinctions and reject inconsistent readiness labels."""
from copy import deepcopy
import json
from pathlib import Path
import jsonschema
import outcomes as o
s=o.s
BASE=Path(__file__).resolve().parent


def main():
    s.context('R01',[(s.PLAN,'R01 explicit commands and separate outcome axes'),
        (s.BASE/'gates/l3/l3-review.json','named supported profile and retained trust'),
        (s.BASE/'interfaces/contracts/L4.md','frozen draft provider/obligation/review mapping'),
        (s.BASE/'interfaces/schemas/obligation-result.schema.json','independent method and freshness draft')],
        [{'classification':'non-blocking','choice':'Local successor contract with explicit adapter to frozen draft interfaces',
          'basis':'No Boolean readiness collapse, historical theorem-only reinterpretation or public truth claim; semantic policy inventory and proof verification remain independent.'}])
    jsonschema.Draft202012Validator.check_schema(o.schema());s.write(BASE/'outcome-schema.json',o.schema())
    catalog={'schema':'relational.diagnostic-catalog/v1-candidate','authority_effect':'none','entries':[]}
    entries=[('input-invalid','input','not-run','Correct the malformed/unknown input fields.'),
        ('profile-unsupported','scope','unsupported','Select a supported profile or supply a separately formalized one.'),
        ('pair-forbidden','semantics','violated','Use an allowed ordered pair or submit an evidenced relation extension.'),
        ('qualifier-invalid','semantics','violated','Correct the exact qualifier shape or resolved evidence role.'),
        ('protected-root-mismatch','semantics','violated','Supply independent evidence matching target version, effect, scope and epoch.'),
        ('protected-lineage-leak','semantics','violated','Remove the unjustified producer or add a legitimate matching root/carrier premise.'),
        ('proof-statement-mismatch','evidence','unknown','Submit a proof of the exact independently required statement.'),
        ('proof-axiom-rejected','evidence','unknown','Remove unfinished/custom assumed conclusions and replay under the selected policy.'),
        ('proof-dependency-substituted','currentness','unknown','Restore the pinned definition/import bytes and rerun proof replay.'),
        ('evidence-stale','currentness','unknown','Recapture the current baseline/profile/rules and rerun affected checks.'),
        ('obligation-missing','aggregation','unknown','Provide verified evidence for every independently required obligation.'),
        ('provider-unavailable','execution','unknown','Install/select the required provider or isolation environment.'),
        ('provider-timeout','execution','unknown','Increase the bounded budget or reduce the selected scope; rerun before negative claims.'),
        ('provider-error','execution','unknown','Inspect the bound provider diagnostic and retry after correcting the failure.'),
        ('bounded-search-inconclusive','evidence','unknown','Supply and independently check a model witness or a complete formal proof.')]
    for code,phase,verdict,action in entries:catalog['entries'].append({'code':code,'phase':phase,'default_verdict':verdict,'next_action':action})
    catalog['exit_code_precedence']=[{'code':code,'meaning':meaning} for code,meaning in [(2,'invalid input'),(6,'timeout'),(5,'unavailable'),
        (8,'provider error'),(7,'stale'),(3,'unsupported'),(1,'violated'),(4,'unknown/unresolved'),(0,'completed/current selected requirements satisfied')]]
    s.write(BASE/'diagnostic-catalog.json',catalog)
    binding=s.binding(s.BASE/'inference/closure/ClosureAdequacy.lean')
    result={'obligation_id':'fixture:obligation','hard':True,'required_statement':{'id':'Inference.RequiredClosureAdequacy','definition_bindings':[binding]},
        'execution':'completed','currentness':'current','evidence_method':'kernel-proof','verdict':'satisfied','evidence_refs':[binding],'diagnostics':[]}
    fixture={'schema_version':'relational.cli-outcome/v1-candidate','command':'check-extension','profile_id':'fixture:contract-validation-only',
        'baseline_identity':'1'*64,'proposal_identity':'2'*64,'execution':'completed','currentness':'current',
        'evidence':{'methods':['kernel-proof'],'policy_identity':'3'*64,'trust_boundary':['Fixture labels test schema/aggregation; no provider run is claimed.']},
        'results':[result],'required_hard_obligation_ids':['fixture:obligation'],'missing_hard_obligation_ids':[],
        'unresolved_hard_obligation_ids':[],'readiness':'ready-for-review',
        'compatibility_dimensions':{dimension:'verified-for-named-scope' for dimension in o.DIMENSIONS},
        'diagnostics':[],'authority_effect':'none'}
    o.validate(fixture,['fixture:obligation']);s.require(o.exit_code(fixture)==0,'valid scoped outcome not successful')
    cases=[]
    for name,execution,currentness,verdict,method,expected_code in [
        ('timeout','timeout','unresolved','unknown','none',6),('provider unavailable','unavailable','unresolved','not-run','none',5),
        ('provider error','provider-error','unresolved','unknown','none',8),('stale evidence','completed','stale','unknown','kernel-proof',7),
        ('unsupported semantics','completed','current','unsupported','none',3),('verified violated constraint','completed','current','violated','verified-checker',1),
        ('bounded no-witness search','completed','current','unknown','bounded-search',4)]:
        outcome=deepcopy(fixture);outcome.update(execution=execution,currentness=currentness,readiness='unresolved',unresolved_hard_obligation_ids=['fixture:obligation'])
        outcome['results'][0].update(execution=execution,currentness=currentness,verdict=verdict,evidence_method=method)
        outcome['evidence']['methods']=[method]
        o.validate(outcome,['fixture:obligation']);s.require(o.exit_code(outcome)==expected_code,'outcome distinctions collapsed: '+name)
        cases.append({'name':name,'exit_code':expected_code,'outcome':outcome})
    controls=[]
    for name,mutate in [('timeout labeled ready',lambda x:x.update(execution='timeout')),
                        ('stale labeled ready',lambda x:x.update(currentness='stale')),
                        ('unsupported obligation labeled ready',lambda x:x['results'][0].update(verdict='unsupported')),
                        ('bounded search satisfies theorem',lambda x:x['results'][0].update(evidence_method='bounded-search')),
                        ('missing result hidden',lambda x:x.update(results=[])),
                        ('weakened required inventory',lambda x:x.update(required_hard_obligation_ids=[])),
                        ('duplicate obligation result',lambda x:x['results'].append(x['results'][0])),
                        ('client all-passed Boolean',lambda x:x.update(all_passed=True)),
                        ('collapsed method inventory',lambda x:x['evidence'].update(methods=[])),
                        ('sample compatibility replaces general dimensions',lambda x:x['compatibility_dimensions'].update({'model-conservativity':'unknown'}))]:
        bad=deepcopy(fixture);mutate(bad)
        try:o.validate(bad,['fixture:obligation'])
        except (ValueError,jsonschema.ValidationError):controls.append({'name':name,'result':'rejected'})
        else:raise ValueError('inconsistent outcome accepted: '+name)
    s.write(BASE/'outcome-controls.json',{'result':'pass','positive_example':fixture,'distinction_cases':cases,'controls':controls,
        'proof_execution_claimed':False,'source_bindings':[s.binding(BASE/'outcomes.py'),s.binding(BASE/'cli-contract.md')],
        'authority_effect':'none'})
    s.accept('R01',{name:BASE/name for name in ['cli-contract.md','outcome-schema.json','diagnostic-catalog.json','outcomes.py','run_contracts.py','outcome-controls.json']},
        ['All four commands specify exact input/profile/definition identities, supported claim ceilings, local artifact boundaries and failure handling. Diagnostic actions, compatibility dimensions, exit-code precedence and frozen-interface adapters are explicit.',
         'Execution, currentness, evidence method, per-obligation verdict and aggregate readiness are separate schema fields. Trusted inventory comparison rejects omitted/duplicated obligations and client flags; readiness requires completed/current allowed evidence with all three compatibility dimensions verified.'],
        ['Timeout, unavailable provider, provider failure, stale evidence, unsupported semantics, verified violation and bounded unknown search have separately validated outcomes and CI exit codes. Invalid ready labels and bounded-search theorem evidence fail schema/aggregation checks.'],
        [s.BASE/'interfaces/contracts/L4.md',s.BASE/'interfaces/schemas/obligation-result.schema.json',s.BASE/'interfaces/schemas/review-report.schema.json'])
    print(json.dumps({'task':'R01','result':'accepted','distinct_failure_cases':len(cases),'rejection_controls':len(controls),'authority_effect':'none'}))


if __name__=='__main__':main()
