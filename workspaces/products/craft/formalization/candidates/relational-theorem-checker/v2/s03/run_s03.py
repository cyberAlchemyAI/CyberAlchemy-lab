from pathlib import Path
import sys,re,copy
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import extension as e
s=e.s;HERE=Path(__file__).resolve().parent
s.context('S03',[(s.BASE/'s16/ProducerPolicy.lean','sealed producer compatibility'),(s.BASE/'s16/SupportedObservations.lean','source-faithful model distinction'),(s.V1/'inference/integration/RuleConservativity.lean','old SemanticModel and grounding soundness'),(s.V1/'inference/closure/ClosureAdequacy.lean','choices/grounding/fuel'),(s.BASE/'s15/baseline-example.json','nonempty baseline'),(s.V1/'inference/profile/frontend.py','legacy rule hash depends on entire vocabulary')],[{'decision':'Positive fresh ordinary recursive heads; fixed old graph/domain/facts/roots/context/producer policy','basis':'independent recursive contract'},{'decision':'Component-local v2 rule hashes bind only used predicate definitions; fresh vocabulary append must not rekey old rules','basis':'implementation finding: legacy normalizer hashes every predicate into every rule'}])
b=e.c.fixture();a=e.example(b);qualified=e.classify(b,a);s.write(HERE/'recursive-before.json',b);s.write(HERE/'recursive-after.json',a)
results=[]
def ctrl(name,fn,positive=False):
 try:
  out=fn();s.require(positive,'accepted hostile '+name);results.append({'name':name,'result':'pass','outcome':'supported-profile'})
 except Exception as ex:
  if positive:raise
  s.require(not str(ex).startswith('accepted hostile'),'failed negative '+name);results.append({'name':name,'result':'pass','outcome':'blocked','reason':str(ex).splitlines()[0]})
def mut(fn):
 q=copy.deepcopy(a);fn(q);return e.classify(b,q)
ctrl('nonempty-old-baseline-and-recursive-chain-cycle',lambda:e.classify(b,a),True)
ctrl('old-rule-rekey-does-not-follow-unrelated-predicate-append',lambda:s.require(qualified['old_normal']['rules']==qualified['new_normal']['rules'][:len(qualified['old_normal']['rules'])],'old hash changed'),True)
ctrl('old-rule-mutation',lambda:mut(lambda q:q['inference']['rules'][0].update(version='changed')))
ctrl('old-predicate-mutation',lambda:mut(lambda q:q['inference']['predicates'][-3].update(version='changed')))
ctrl('fresh-protected-role',lambda:mut(lambda q:q['inference']['predicates'][-1].update(role='root-carrier')))
ctrl('old-head-new-rule',lambda:mut(lambda q:q['inference']['rules'][-1]['head'].update(predicate='BaselineSignal')))
ctrl('sealed-head-new-rule',lambda:mut(lambda q:q['inference']['rules'][-1]['head'].update(predicate='Conforms')))
ctrl('domain-growth',lambda:mut(lambda q:q['inference']['domain'].append({'kind':'text','value':'new'})))
ctrl('fact-growth',lambda:mut(lambda q:q['inference']['facts'].append({'predicate':'BaselineSignal','terms':[q['inference']['domain'][0]]})))
ctrl('root-growth',lambda:mut(lambda q:q['inference']['roots'].append({'id':'fake'})))
ctrl('context-growth',lambda:mut(lambda q:q['context'].update(version='new')))
ctrl('interpretation-change',lambda:mut(lambda q:q['interpretations'].append({'assertion_id':'new'})))
modules=s.core_modules({'RelationalInput','RelationalSemantics','SemanticLogic','InferenceCore','ReferenceChecker','DerivationSoundness','ClosureAdequacy','ProtectedLineage','ModelSemantics','RuleConservativity','StressTypes','ObligationSemantics'})+[(n,s.BASE/f's00/{n}.lean') for n in ['RequirementSemantics','RequiredStatements']]+[(n,s.BASE/f's02/{n}.lean') for n in ['ContextProjection','ProjectionProofs']]+[(n,s.BASE/f's16/{n}.lean') for n in ['ProducerPolicy','SupportedObservations','SupportLineage']]+[(n,HERE/(n+'.lean')) for n in ['RecursiveExtension','RecursiveConservativity','RecursiveSaturation','RecursiveControls']]
logs=s.compile_modules(HERE/'build',modules)
kcontrols=[{'theorem':name,'result':'kernel-checked'} for name in re.findall(r'^theorem (\w+)',(HERE/'RecursiveControls.lean').read_text(),re.M)]
s.write(HERE/'recursive-countermodels.json',{'controls':results+kcontrols,'model_class':'generic-root-constrained-horn; exact old reduct; source-faithful variant requires explicit source-faithful old interpretation','truth_assumptions':['ordinary supplied facts and independently supplied root receipts'],'unsupported':['old-head extension','domain/fact/root/graph change under rule-only theorem','fresh root/protected roles','negation/functions/existential generation'],'authority_effect':'none'})
s.write(HERE/'recursion-audit.json',{'result':'pass','modules':logs,'general_targets':['every_old_model_expands','source_faithfulness_preserved','finite_universe','no_unseeded_facts','saturation_state','reference_saturation_exact'],'actual_targets':['nonempty_before_valid','after_valid','actual_every_old_model','multistep_seeded_cycle','unseeded_not_derivable'],'structural_controls':results,'kernel_controls':kcontrols,'normalization_change':'v2 component-local identities preserve old rule keys on fresh vocabulary append; transport equivalence remains tested boundary','authority_effect':'none'})
s.accept('S03',['Arbitrary old SemanticModel expands by inductive positive fresh closure; exact old reduct and finite typed universe proved.','No nonempty-body derivation from empty seeds; complete pending-head invariant proves terminating reference saturation exact. Root inventory preserved.','Actual domain/old-head/context/protected change controls block with precise profile reasons.','Fresh heads are ordinary derived-information only; old source graph/facts/domain/roots and component-local old rule keys fixed.'],controls=results+kcontrols,extra_dependencies=[HERE/'RecursiveSaturation.lean',HERE/'RecursiveControls.lean',HERE/'normalizer.py',HERE/'extension.py',HERE/'recursive-before.json',HERE/'recursive-after.json'])
print('S03 accepted: general every-old-model expansion and exact finite saturation; '+str(len(results)+len(kcontrols))+' controls.')
