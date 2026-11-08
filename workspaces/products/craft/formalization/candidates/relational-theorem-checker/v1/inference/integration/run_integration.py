#!/usr/bin/env python3
"""Freshly discharge every obligation for the captured rule proposal."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import integration as i
s=i.s;f=i.f;c=i.c;w=i.w;g=i.g
BASE=Path(__file__).resolve().parent


def main():
    proposal=s.read(s.BASE/'evolution/proposals/rule-change-proposal.json');captured=i.capture(proposal);required=g.generate(proposal)
    s.require(required==s.read(s.BASE/'evolution/obligations/required-rule-obligations.json'),'required rule inventory drift')
    s.context('I06',[(s.PLAN,'I06 complete source-bound rule obligations and invalidation'),
        (s.BASE/'evolution/obligations/required-rule-obligations.json','exact nine L2 and six L3 mandatory entries'),
        (s.BASE/'evolution/impact/extension-impact-report.json','three dimensions and no L2 rule authorization'),
        (s.BASE/'inference/protected/lineage-audit.json','generic all-producer root lineage'),
        (s.BASE/'inference/independence/non-entailment-report.json','exact countermodel and coexistence claim ceilings'),
        (s.BASE/'evolution/proposals/rule-change-proposal.json','actual frozen registry/graph and new rule bytes')],
        [{'classification':'non-blocking','choice':'Fresh-head/old-body rule model expansion plus unchanged-registry preservation with exact actual proposal replays',
          'basis':'Every required obligation binds this proposal and inference context. No blanket rule-edit permission; G3 and public R02/R03 remain distinct gates.'}])
    before=captured['before_input'];after=captured['after_input'];normal=captured['after_normal'];audit=c.c.policy()
    reports={};controls=[]
    with tempfile.TemporaryDirectory(prefix='rule-extension-evidence-') as folder:
        build=Path(folder);logs=w.prepare(normal,build)
        logs+=s.compile_lean(build,[('ProtectedLineage',s.BASE/'inference/protected/ProtectedLineage.lean'),
            ('RuleConservativity',BASE/'RuleConservativity.lean'),('RuleStatementAudit',BASE/'StatementAudit.lean')])
        axioms=audit.axiom_report(logs[-1]['output'])
        s.require(len(axioms)==12 and audit.policy_accepts(logs[-1]['output']),'rule extension statement/axiom closure incomplete')
        conservative=i.conservativity_source(captured)
        logs.append(c.c.compile_generated(build,'CapturedRuleConservativity',conservative))
        (BASE/'CapturedRuleConservativity.lean').write_text(conservative)
        (BASE/'InferenceFixture.lean').write_bytes((build/'InferenceFixture.lean').read_bytes())
        computed=c.compute(after);bundle=computed['bundle'];subject=after['facts'][0]['terms'][0]
        query={'predicate':'Admitted','version':'v1','terms':[subject,*after['domain'][-3:]]}
        bundle['negative_query']=query
        reports['closure']=c.check(after,bundle,build)
        s.require(reports['closure']['accepted'] and reports['closure']['non_derivability_proved'],'actual rule closure/absence check failed')
        (BASE/'ActualClosure.lean').write_bytes((build/'ClosureQuery.lean').read_bytes())
        reports['lineage']=i.lineage.check(after,query=query,build=build)
        s.require(reports['lineage']['accepted'] and reports['lineage']['no_unrooted_derivation_proved'],'actual rule root lineage failed')
        (BASE/'ActualLineage.lean').write_bytes((build/'LineageQuery.lean').read_bytes())
        witness={'schema':'relational.inference-model/v1','normal_form_identity':normal['normal_form_identity'],
                 'model':deepcopy(bundle['closure']),'claim':{'kind':'non-entailment','premise':after['facts'][0],'conclusion':query}}
        reports['independence']=w.check(after,witness,build)
        s.require(reports['independence']['non_entailment_proved'],'actual proposal countermodel failed')
        (BASE/'ActualCountermodel.lean').write_bytes((build/'ModelQuery.lean').read_bytes())
        # Replay all 41 registry declarations before invoking the actual
        # zero-kind-change preservation/conservativity instances.
        registry_modules=[(m['module'],s.ROOT/m['source']['path']) for m in s.read(s.BASE/'registry/projection-audit.json')['modules']]
        for _,path in registry_modules:s.require(path.is_file(),'missing captured registry proof module')
        logs+=s.compile_lean(build,registry_modules+[
            ('Preservation',s.BASE/'evolution/preservation/Preservation.lean'),
            ('ConservativeExpansion',s.BASE/'evolution/models/ConservativeExpansion.lean')])
        registry_source=i.registry_identity_source();logs.append(c.c.compile_generated(build,'RegistryIdentity',registry_source))
        (BASE/'RegistryIdentity.lean').write_text(registry_source)
    raw=(s.BASE/'demonstrations/l0/input.json').read_bytes();graph=g.c.r.from_decoder(raw)
    s.require(graph==proposal['before']['graph'],'F0 demonstration graph differs from selected rule proposal')
    formal_normal=dummy=None
    formal_normal=c.d.normalize(c.d.decode(raw));formal_evaluation=c.d.check(formal_normal)
    s.require(formal_evaluation['accepted_result'],'actual selected F0 model invalid')
    s.write(BASE/'selected-data-report.json',{'result':'pass','proposal_identity':captured['proposal_identity'],
        'graph_identity':g.c.identity(graph),'registry_unchanged':True,'before_F0':formal_evaluation,'after_F0':formal_evaluation,
        'after_inference_model':reports['independence'],'after_inference_closure':reports['closure'],
        'general_preservation_claimed_by_sample':False,'authority_effect':'none'})
    s.write(BASE/'formal-audit.json',{'result':'pass','proposal_identity':captured['proposal_identity'],
        'normal_form_identity':normal['normal_form_identity'],'modules':logs,'transitive_axioms':axioms,
        'rule_conservativity':'Every typed/root-constrained base interpretation expands with unchanged old interpretation under FreshHeadExtension; actual structural/ground assumptions kernel checked.',
        'registry_preservation':'Exact same registry; actual FreshExtension added=[] and empty-kind conservativity independently instantiated.',
        'authority_effect':'none'})
    for name,obj in [('captured-profile.json',captured),('before-input.json',before),('after-input.json',after),
                     ('closure-certificate.json',bundle),('countermodel.json',witness),('inference-checks.json',reports)]:s.write(BASE/name,obj)
    carrier=g.carrier(proposal);s.write(BASE/'rule-carrier-schema.json',carrier)
    sys.path.insert(0,str(s.BASE/'coverage/carrier'));from check_coverage import table
    actual_carrier=table(carrier)
    for kind in proposal['after']['registry']['kinds']:
        s.require(actual_carrier[kind['id']]['pairs']==kind['pairs'],'rule carrier projection loses exact pairs')
    logic=s.read(s.FORMAL/'semantic-logic/v1/semantic-logic-audit.json')
    for binding in logic['source_bindings']:s.check_binding(binding)
    s.require('Relational.Logic.admission_roots_do_not_change_instance_meaning' in logic['transitive_axioms'],'missing unchanged semantic root-independence proof')
    manifest=i.dependency_manifest(proposal);s.write(BASE/'dependency-manifest.json',manifest);i.verify_dependencies(proposal,manifest)
    evidence={
        'baseline-current':([BASE/'dependency-manifest.json'],'Full baseline and current inference dependency identities rechecked.'),
        'computed-classification':([BASE/'captured-profile.json'],'Actual registry/graph unchanged; exact rule AST change classified.'),
        'source-profile-projection':([BASE/'captured-profile.json',BASE/'InferenceFixture.lean'],'Exact source AST projected to typed profile; unary conformance abstraction explicitly bound.'),
        'carrier-projection':([BASE/'rule-carrier-schema.json'],'All 41 source kinds and 550 ordered pairs retained.'),
        'selected-data-compatibility':([BASE/'selected-data-report.json'],'Same captured graph remains F0-valid; expanded inference closure/model checked.'),
        'invariant-preservation':([BASE/'formal-audit.json',BASE/'RegistryIdentity.lean'],'General registry preservation theorem applied to actual identical registry.'),
        'conservative-expansion':([BASE/'formal-audit.json',BASE/'RegistryIdentity.lean'],'Every old structural model has unchanged registry expansion; rule-model expansion separately proved.'),
        'inhabited-model':([BASE/'inference-checks.json',BASE/'ActualCountermodel.lean'],'Actual nonempty conformance/review model checked against every Horn axiom.'),
        'protected-root-independence':([BASE/'ActualLineage.lean',s.FORMAL/'semantic-logic/v1/semantic-logic-audit.json'],'Exact derived protected root boundary and unchanged independent F0 semantics checked.'),
        'typed-rule-profile':([BASE/'InferenceFixture.lean',BASE/'captured-profile.json'],'Actual normalized type/domain/rule profile kernel checked.'),
        'derivation-soundness':([BASE/'formal-audit.json',s.BASE/'inference/derivations/DerivationSoundness.lean'],'Exact generic certificate soundness audit reused under captured typed input.'),
        'closure-adequacy':([BASE/'ActualClosure.lean',BASE/'formal-audit.json'],'General complete-grounding/least-closure theorem and actual closure absence replay.'),
        'protected-lineage':([BASE/'ActualLineage.lean',BASE/'formal-audit.json'],'Every producer checked and generic matching-root induction instantiated.'),
        'independence-witnesses':([BASE/'ActualCountermodel.lean',BASE/'inference-checks.json'],'Actual conformance/not-admission countermodel; I05 coexistence evidence retained separately.'),
        'rule-extension-compatibility':([BASE/'RuleConservativity.lean',BASE/'CapturedRuleConservativity.lean',BASE/'formal-audit.json'],'Every base semantic model expands with identical old predicate truth; no sample-only conservativity claim.')}
    submission={'proposal_identity':required['proposal_identity'],'policy_identity':required['policy_identity'],'obligations':[]}
    for obligation in required['obligations']:
        paths,finding=evidence[obligation['name']]
        entry={**obligation,'status':'discharged','proposal_identity':required['proposal_identity'],'normal_form_identity':normal['normal_form_identity'],
            'evidence_kind':i.KINDS[obligation['name']],'evidence':[s.binding(path) for path in paths],'finding':finding}
        target={**i.r.TARGETS,**i.RULE_TARGETS}.get(obligation['name'])
        if target:entry['required_statement']=target
        submission['obligations'].append(entry)
    outcome=i.validate_submission(proposal,submission,normal['normal_form_identity'])
    s.require(not outcome['missing_hard_obligations'],'required actual rule obligation incomplete')
    # Independent L2 still cannot authorize a rule change after its own pass.
    l2=i.r.evaluate(proposal,submission);s.require(l2['status']=='pending-L3' and not l2['rule_scope_ready'],'L2 implicitly authorized new rules')
    controls.append({'name':'G2/L2 cannot authorize the rule extension','result':'pending-L3','outcome':l2})
    def rejected(name,mutate):
        bad=deepcopy(submission);mutate(bad)
        try:i.validate_submission(proposal,bad,normal['normal_form_identity'])
        except ValueError as error:controls.append({'name':name,'result':'rejected','diagnostic':str(error)})
        else:raise ValueError('invalid obligation submission accepted: '+name)
    rejected('omitted required obligation',lambda x:x['obligations'].pop())
    rejected('wrong exact statement',lambda x:next(o for o in x['obligations'] if o['name']=='rule-extension-compatibility').update(required_statement='True'))
    rejected('bounded sample substitutes for rule conservativity',lambda x:next(o for o in x['obligations'] if o['name']=='rule-extension-compatibility').update(evidence_kind='checked-model-witness'))
    rejected('changed scope identity',lambda x:x['obligations'][-1].update(normal_form_identity='0'*64))
    rejected('stale evidence binding',lambda x:x['obligations'][-1]['evidence'][0].update(sha256='0'*64))
    pending=deepcopy(submission);pending['obligations'][-1]['status']='pending';pending['obligations'][-1]['evidence']=[]
    pending_outcome=i.validate_submission(proposal,pending,normal['normal_form_identity'])
    s.require(pending_outcome['status']=='pending' and pending_outcome['missing_hard_obligations'],'unresolved mandatory obligation became ready')
    controls.append({'name':'unresolved mandatory rule obligation','result':'pending','outcome':pending_outcome})
    for name,mutate in [('changed rule version',lambda x:x['after']['rules'][0].update(version='v2'))]:
        changed=deepcopy(proposal);mutate(changed);new=i.capture(changed)
        s.require(new['after_normal']['normal_form_identity']!=normal['normal_form_identity'],'changed rule did not invalidate captured identity')
        try:c.normalize_bundle(new['after_normal'],bundle)
        except ValueError:controls.append({'name':name+' invalidates closure proof','result':'rejected'})
        else:raise ValueError('changed rule reused old closure')
    for name,mutate in [('missing dependency',lambda x:x['bindings'].pop()),('changed proof digest',lambda x:x['bindings'][0].update(sha256='0'*64))]:
        bad=deepcopy(manifest);mutate(bad)
        try:i.verify_dependencies(proposal,bad,executed_at='later-timestamp')
        except ValueError:controls.append({'name':name+' cannot be repaired by timestamp','result':'rejected'})
        else:raise ValueError('dependency invalidation bypassed')
    coupling=deepcopy(proposal);coupling['after']['rules'][0]['head']={'predicate':'Admitted','terms':[
        {'variable':'subject'},*({'constant':v} for v in after['domain'][-3:])]}
    try:i.capture(coupling)
    except ValueError:controls.append({'name':'old protected head cannot reuse fresh-head conservativity','result':'unsupported; new proof obligations remain required'})
    else:raise ValueError('old-head coupling treated as conservative')
    s.write(BASE/'obligation-submission.json',submission)
    s.write(BASE/'integration-controls.json',{'result':'pass','controls':controls,'authority_effect':'none'})
    s.write(BASE/'rule-extension-report.json',{'task':'I06','result':'pass','proposal_identity':required['proposal_identity'],
        'normal_form_identity':normal['normal_form_identity'],'obligation_outcome':outcome,'submission':submission,
        'compatibility_dimensions':l2['dimensions'],'rule_model_conservativity':'verified for captured fresh-head/old-body profile',
        'currentness':{'dependency_identity':manifest['dependency_identity'],'verified':True},
        'next_gate':'G3 remains required before full scoped rule readiness; public untrusted submissions require R02/R03.',
        'inference_scope':'Finite positive typed Horn rules; exact source-bound ReviewSignal extension preserves old truth and independent roots.',
        'projection_boundary':captured['claim_ceiling'],'epoch_boundary':captured['epoch_interpretation'],
        'full_source_semantics':'unsupported; all 263 inherited source-level obligations remain visible',
        'authority_effect':'none','review_mode':'Codex author self-review; candidate obligation acceptance only'})
    artifacts={name:BASE/name for name in ['rule-extension-report.json','integration-controls.json','integration.py','run_integration.py',
        'RuleConservativity.lean','StatementAudit.lean','CapturedRuleConservativity.lean','RegistryIdentity.lean','InferenceFixture.lean',
        'ActualClosure.lean','ActualLineage.lean','ActualCountermodel.lean','formal-audit.json','selected-data-report.json','captured-profile.json',
        'before-input.json','after-input.json','closure-certificate.json','countermodel.json','inference-checks.json','rule-carrier-schema.json',
        'dependency-manifest.json','obligation-submission.json']}
    s.accept('I06',artifacts,
        ['All nine L2 and six L3 independently generated obligations bind the actual proposal and normalized inference snapshot. Current type, generic soundness/adequacy/lineage, exact countermodel and universally quantified rule-model expansion evidence are present; registry preservation remains separate.',
         'Current full baseline and inference dependency manifests are recomputed. Actual before/after data, rule identities, interpretation projection and model impact are captured; changed rule/proof/source/omitted bindings invalidate evidence even with a later timestamp.'],
        ['G2/L2 remains pending-L3 despite all supplied discharge entries. G3 and independent public proof/bundle verification remain required; an old protected head cannot reuse this fresh-head conservativity profile.',
         'Omitted, pending, stale, scope-mismatched or weakened obligations prevent the integrated pass. A model/sample cannot replace the universal rule-model conservativity statement.'],
        [s.FORMAL/'validate_f0.py',s.FORMAL/'toolchain-lock.json',s.BASE/'inference/independence/ModelSemantics.lean',
         s.BASE/'inference/independence/witness_checker.py',s.BASE/'inference/protected/ProtectedLineage.lean',
         s.BASE/'inference/protected/lineage_checker.py',s.BASE/'replay/replay_engine.py'])
    print(json.dumps({'task':'I06','result':'accepted','required_obligations':len(required['obligations']),
        'generic_rule_audit_declarations':len(axioms),'controls':len(controls),'next_gate':'G3'}))


if __name__=='__main__':main()
