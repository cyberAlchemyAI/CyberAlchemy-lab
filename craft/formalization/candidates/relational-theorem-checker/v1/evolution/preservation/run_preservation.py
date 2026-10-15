#!/usr/bin/env python3
"""Bind sampled data checks separately from universal preservation proofs."""
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import projection as p
s=p.s
BASE=Path(__file__).resolve().parent


def main():
    proposal=s.read(s.BASE/'evolution/proposals/fresh-kind-proposal.json')
    computed=p.g.c.classify(proposal);p.g.source_projection(proposal)
    s.require(computed['profile']=='fresh-kind-extension','unsupported preservation profile')
    fixture=BASE/'CapturedExtension.lean';fixture.write_text(p.extension_fixture(proposal))
    spec=importlib.util.spec_from_file_location('preservation_policy',s.FORMAL/'validate_f0.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
    controls=[]
    with tempfile.TemporaryDirectory(prefix='preservation-replay-') as folder:
        build=Path(folder)
        modules=s.compile_lean(build,p.captured_modules()+[('Preservation',BASE/'Preservation.lean'),('CapturedExtension',fixture)])
        report={**policy.axiom_report(modules[-2]['output']),**policy.axiom_report(modules[-1]['output'])}
        s.require(len(report)==11 and all(set(v)<=policy.ALLOW for v in report.values()),'preservation statement audit failed')
        for name,body,assumed in [
            ('sample cannot substitute for universal theorem','theorem weak : True := True.intro\nexample : RequiredPreservation := weak\n',False),
            ('widened pair still satisfies old invariant','example : Inv Witnesses.base Witnesses.counterexample := by decide\n',False),
            ('assumed generic preservation','theorem assumed : RequiredPreservation := by sorry\n#print axioms assumed\n',True)]:
            path=build/'HostilePreservation.lean';path.write_text('import Preservation\nopen Registry Registry.Evolution\n'+body)
            run=subprocess.run([str(s.lean_path()),str(path)],cwd=build,env={**os.environ,'LEAN_PATH':str(build)},text=True,capture_output=True,timeout=60)
            text=run.stdout+run.stderr
            s.require((run.returncode==0 and not policy.policy_accepts(text)) if assumed else run.returncode!=0,'invalid preservation proof accepted')
            if not assumed:s.require(not any(v in text for v in ['unknown module','Unknown identifier','unexpected token']),'control failed before intended theorem check')
            controls.append({'name':name,'result':'rejected','mechanism':'axiom policy' if assumed else 'required type or kernel semantics'})
        s.compile_lean(build,p.d.core_modules()[1:])
        before=deepcopy(proposal['before']['graph']);after=deepcopy(proposal['after']['graph'])
        for graph in [before,after]:
            for edge in graph['assertions']:edge.pop('kind_version')
        evaluated_before=p.d.check({'schema_version':'relational-checker.normal-form/v1','graph':before},build)
        evaluated_after=p.d.check({'schema_version':'relational-checker.normal-form/v1','graph':after},build)
    s.require(evaluated_before['accepted_result'] and evaluated_after['accepted_result'],'selected data compatibility failed')
    widened=s.read(s.BASE/'evolution/proposals/pair-widening-proposal.json')
    sampled=p.g.c.r.resolve(widened['before']['graph'],widened['after']['registry'])
    s.require(sampled['status']=='supported' and p.g.c.classify(widened)['profile'].startswith('unsupported'),'sample classification obscures weakening')
    s.write(BASE/'data-compatibility-report.json',{'result':'pass','proposal_identity':p.g.c.identity(proposal),
        'selected_before_identity':p.g.c.identity(proposal['before']['graph']),
        'selected_after_identity':p.g.c.identity(proposal['after']['graph']),
        'old_data_compatibility':'compatible','before_evaluation':evaluated_before,'after_evaluation':evaluated_after,
        'structural_before_and_expanded_models':'kernel-checked in CapturedExtension',
        'sample_preserved_but_generic_claim_unsupported':{'proposal':s.binding(s.BASE/'evolution/proposals/pair-widening-proposal.json'),
            'sampled_result':sampled['status'],'general_reflection_countermodel':'Registry.Evolution.Witnesses.widened_invariant_is_weaker'},
        'claim_ceiling':'Exact selected six-node data only; independent general theorem is in preservation-audit.'})
    s.write(BASE/'preservation-audit.json',{'result':'pass','proposal_identity':p.g.c.identity(proposal),
        'profile':'append-only fresh kinds; exact unchanged node inventory and old declarations; both theories valid',
        'theorem':'Registry.Evolution.audited_preservation : RequiredPreservation',
        'quantification':'For arbitrary base/expanded theories satisfying FreshExtension and arbitrary old-language graphs, Inv expanded iff Inv base.',
        'source_interpretation':'Projection and normative correspondence are separately checked host obligations; not proved by the Lean preservation theorem.',
        'full_source_wide_semantics':'unsupported; 263 inherited baseline obligations remain explicit',
        'formal_theorems':report,'modules':modules,'controls':controls,
        'F0_definitions_changed':False,'authority_effect':'none'})
    s.accept('E03',{name:BASE/name for name in ['data-compatibility-report.json','Preservation.lean','preservation-audit.json','projection.py','CapturedExtension.lean']},
        ['The exact selected six-node data are evaluated in the kernel before and after the extension, and typed Registry models are checked separately; those receipts make only sampled compatibility claims.',
         'The exact quantified RequiredPreservation assignment and its axiom closure pass; the captured 41-to-42-kind extension satisfies its structural assumptions and a valid model. Unchanged F0 semantics and unsupported full source meanings remain explicit.'],
        ['A True/sample statement cannot inhabit RequiredPreservation; an assumed theorem fails the axiom policy.',
         'A real pair widening preserves the selected data but a checked countermodel satisfies the widened invariant and fails the old invariant.'],
        [Path(__file__),s.BASE/'evolution/proposals/fresh-kind-proposal.json',s.BASE/'evolution/obligations/generator.py',s.BASE/'registry/build_registry.py',s.BASE/'registry/RegistryChecker.lean',s.FORMAL/'core/RelationalSemantics.lean'])
    print(json.dumps({'task':'E03','result':'accepted','audited_theorems':len(report),'controls':len(controls)}))


if __name__=='__main__':main()
