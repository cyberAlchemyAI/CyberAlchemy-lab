from pathlib import Path
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'execution'));import support as s
HERE=Path(__file__).resolve().parent
measurement=s.read(s.BASE/'s11/stage-measurements.json')
comparison=[{'mode':m['mode'],'evaluator_seconds':m['inclusive_stages']['grounding_and_saturation']['seconds'],'largest_inclusive_proof_stage_seconds':max(m['inclusive_stages']['compile_and_actual_witness_checks']['seconds'],m['inclusive_stages']['fresh_general_kernel_replay']['seconds'])} for m in measurement['full_qualification']]
s.require(all(m['largest_inclusive_proof_stage_seconds']>m['evaluator_seconds'] for m in comparison),'measured costs do not support optional fallback decision')
s.write(HERE/'measurement-decision.json',{'result':'pass','observed_comparison':comparison,'method':'Compare inclusive stage observations without adding overlapping times; no speedup or general scale claim','source':s.binding(s.BASE/'s11/stage-measurements.json'),'selected':'qualified-reference','authority_effect':'none'})
s.context('S12',[(s.BASE/'s11/stage-measurements.json','observed bottleneck and reference selection'),(HERE/'measurement-decision.json','actual inclusive cost comparison without summing overlapping timers'),(s.BASE/'s11/benchmark-profile.json','bounded qualified benchmark'),(s.PROPOSAL,'optional optimization and S13 fallback')],[{'decision':'Do not select an optimized evaluator; retain required fresh proof replay and current qualified reference','basis':'measured bounded workload and conditional S12 branch'}])
# Independent exact grounding contract for the retained reference. No optimized
# variant or performance equivalence is asserted.
mods=s.core_modules({'RelationalInput','RelationalSemantics','SemanticLogic','InferenceCore','ReferenceChecker','DerivationSoundness','ClosureAdequacy','ProtectedLineage','ModelSemantics','RuleConservativity','StressTypes','ObligationSemantics'})+[(n,s.BASE/f's00/{n}.lean') for n in ['RequirementSemantics','RequiredStatements']]+[(n,s.BASE/f's02/{n}.lean') for n in ['ContextProjection','ProjectionProofs']]+[(n,s.BASE/f's16/{n}.lean') for n in ['ProducerPolicy','SupportedObservations','SupportLineage']]+[('RecursiveExtension',s.BASE/'s03/RecursiveExtension.lean'),('OptimizationEquivalence',HERE/'OptimizationEquivalence.lean')]
logs=s.compile_modules(HERE/'build',mods)
s.write(HERE/'optimization-audit.json',{'status':'not-needed','selection':'qualified-reference','optimized_evaluator_enabled':False,'reason':s.read(s.BASE/'s11/stage-measurements.json')['selection']['reason'],'proof_claim':'exact reference grounding contract only; no unimplemented optimized equivalence or speedup','performance_comparison':'not-applicable; no optimized variant selected','modules':logs,'conditional_edge_to_S13':'inactive; pilot uses reference fallback','human_review':None,'authority_effect':'none'})
receipt={'schema':'relational.v2-optional-task-resolution/v1','task':'S12','result':'not-needed','basis':s.binding(s.BASE/'s11/stage-measurements.json'),'artifacts':[s.binding(HERE/name) for name in ['optimized-grounding.py','OptimizationEquivalence.lean','optimization-audit.json','context-pack.json','measurement-decision.json']],'reason':'Optional optimization branch not selected; reference fallback retained; required replay not removed','authority_effect':'none'}
s.write(HERE/'task-acceptance.json',receipt);plan=s.read(s.PLAN);task=next(t for t in plan['tasks'] if t['id']=='S12');task['status']='not-needed';task['receipt']=s.binding(HERE/'task-acceptance.json')
for u in task['working_units']:u['status']='not-needed'
s.write(s.PLAN,plan);s.sync();print('S12 resolved: optional optimization not needed; qualified reference retained.')
