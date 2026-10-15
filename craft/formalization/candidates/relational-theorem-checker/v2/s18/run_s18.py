from pathlib import Path
import sys,re,copy
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import transition as t
s=t.s;HERE=Path(__file__).resolve().parent
s.context('S18',[(s.BASE/'s01/requirements.json','all 41 selected/deferred improvements'),(s.BASE/'s02/ContextProjection.lean','contextual source view'),(s.BASE/'s04/field-map.json','exact opaque interpretation qualifiers'),(s.BASE/'s15/baseline-example.json','richer transition frame'),(s.BASE/'s16/SupportedObservations.lean','source meanings and least derivation'),(s.V1/'references/resolver.py','selected literal source meanings')],[{'decision':'Richer migration is append-only graph/domain growth with old initial observation embedding; no model-conservativity claim','basis':'independent initial view target'},{'decision':'Plural conformance_evidence_refs stays one opaque token; multi-token interpretation is deferred','basis':'selected legacy formalization and token binding'}])
b=t.c.fixture();a=t.example(b);selected=t.classify(b,a);s.write(HERE/'migration-before.json',b);s.write(HERE/'migration-after.json',a)
results=[]
def ctrl(name,fn,pos=False):
 try:fn();s.require(pos,'accepted hostile '+name);results.append({'name':name,'result':'pass','outcome':'selected-migration'})
 except Exception as e:
  if pos:raise
  s.require(not str(e).startswith('accepted hostile'),'negative failed '+name);results.append({'name':name,'result':'pass','outcome':'blocked','reason':str(e).splitlines()[0]})
def mut(fn):
 q=copy.deepcopy(a);fn(q);return t.classify(b,q)
ctrl('richer-graph-domain-scope-migration',lambda:t.classify(b,a),True)
ctrl('same-reference-kind-substitution',lambda:mut(lambda q:q['graph']['nodes'][0].update(kind='contract')))
ctrl('same-reference-content-substitution',lambda:mut(lambda q:q['graph']['nodes'][0].update(content_identity='0'*64)))
ctrl('multiple-evidence-tokens-no-split',lambda:mut(lambda q:q['graph']['assertions'][-1]['qualifiers'].update(conformance_evidence_refs='assessment:new-contract,other')))
ctrl('wrong-exact-target-fragment',lambda:mut(lambda q:q['graph']['assertions'][-1]['target'].update(version='other')))
ctrl('missing-context-revision',lambda:mut(lambda q:q['context'].update(version='different')))
ctrl('changed-source-interpretation',lambda:mut(lambda q:q['interpretations'].append({'assertion_id':'edge'})))
ctrl('old-assessment-replacement',lambda:mut(lambda q:q['graph']['assessments'][0].update(accepted=False)))
ctrl('unselected-registry-pair-not-a-semantic-proof',lambda:mut(lambda q:q['graph']['assertions'][-1].update(kind='relation.acts-for')))
ctrl('rule-change-not-migration',lambda:mut(lambda q:q['inference']['rules'][0].update(version='new')))
ctrl('old-domain-removal',lambda:mut(lambda q:q['inference']['domain'].pop(0)))
# Generate a kernel witness for this actual richer graph transition.
d=t.c.f.d;old,new=selected['old_selected_graph'],selected['new_selected_graph']
source='import BaselineTransition\nnamespace Successor.Transition.Actual\nopen Relational\ndef before : Graph := '+d.graph_lean(old)+'\ndef after : Graph := '+d.graph_lean(new)+'\ndef actual : AppendGraph before after := {\n'
source+='newNodes := after.nodes.drop '+str(len(old['nodes']))+', newAssessments := after.assessments.drop '+str(len(old['assessments']))+', newAssertions := after.assertions.drop '+str(len(old['assertions']))+'\n'
source+='nodes_append := by decide, assessments_append := by decide, assertions_append := by decide,after_valid := by decide,references_stable := by unfold Baseline.StableReferences; decide }\n'
source+='theorem initial_view : InitialViewRelation before after := initial_view_preserved actual\n#print axioms initial_view\nend Successor.Transition.Actual\n'
(HERE/'ActualMigration.lean').write_text(source)
reviews=[r for r in s.read(s.BASE/'s01/requirements.json')['rows'] if r['id'].startswith('v2-review:')];s.require(len(reviews)==41,'review coverage omission')
rows=[]
for row in reviews:
 s.check(row['source']);id=row['id'].split('v2-review:')[1];selectedMeaning=id in t.F0|t.MAPPED
 rows.append({'relation':id,'source':row['source'],'improvement':row['improvement'],'selection':'selected-fragment' if selectedMeaning else 'deferred-semantic-improvement','implemented_fragment':'literal selected F0 source meaning/context projection' if id in t.F0 else 'independent token-store mapping; runtime integration S07' if id in t.MAPPED else None,'unsupported_remainder':row['controls'],'external_truth_proved':False})
s.write(HERE/'source-map.json',{'schema':'relational.v2-source-map/v1','relations':rows,'selected_field_map':s.binding(s.BASE/'s04/field-map.json'),'conformance_evidence':'one exact opaque token; no comma/reference fragment splitting or list coercion','endpoint_reference':'exact id/version pair, not opaque qualifier token','condition_revision':'must bind to per-assertion interpretation; legacy stress label alone cannot supply revision','richer_transition':'append-only source graph/domain; initial view embedding only','unselected_registry_pairs':'structural declaration alone does not prove selected typed semantics','authority_effect':'none'})
modules=s.core_modules({'RelationalInput','RelationalSemantics','SemanticLogic','InferenceCore','ReferenceChecker','DerivationSoundness','ClosureAdequacy','ProtectedLineage','StressTypes','DelegationSemantics','ObligationSemantics','StressLaws'})+[(n,s.BASE/f's00/{n}.lean') for n in ['RequirementSemantics','RequiredStatements']]+[('RequirementControls',s.BASE/'s01/RequirementControls.lean')]+[(n,s.BASE/f's02/{n}.lean') for n in ['ContextProjection','ProjectionProofs']]+[('BaselineContract',s.BASE/'s15/BaselineContract.lean')]+[(n,s.BASE/f's16/{n}.lean') for n in ['ProducerPolicy','SupportedObservations','SupportLineage']]+[(n,s.BASE/f's04/{n}.lean') for n in ['ConditionSemantics','InterpretationSemantics','MappingStatements']]+[(n,HERE/(n+'.lean')) for n in ['SourceInterpretation','BaselineTransition','TransitionControls','ActualMigration']]
logs=s.compile_modules(HERE/'build',modules)
controls=[{'theorem':n,'result':'kernel-checked'} for n in re.findall(r'^theorem (\w+)',(HERE/'TransitionControls.lean').read_text(),re.M)]
s.write(HERE/'transition-controls.json',{'result':'pass','controls':results+controls,'modules':logs,'actual_migration':{'before':s.binding(HERE/'migration-before.json'),'after':s.binding(HERE/'migration-after.json'),'target':'InitialViewRelation','model_conservativity':'not claimed'},'all_41_selected_or_deferred':True,'inherited_unsupported':'retained; no discharge by review','authority_effect':'none'})
s.accept('S18',['Literal exact-token conformance bindings and independently interpreted stress fields have universal mapping proofs and explicit coverage.','Actual graph/domain/scope growth compiles an append-graph InitialViewRelation witness; fixed-domain every-model expansion is not asserted.','All 41 relation improvements remain selected fragments or explicit deferred meanings; inherited unsupported obligations persist.'],controls=results+controls,extra_dependencies=[HERE/'transition.py',HERE/'TransitionControls.lean',HERE/'ActualMigration.lean',HERE/'migration-before.json',HERE/'migration-after.json'])
print('S18 accepted: actual richer migration kernel witness; '+str(len(results)+len(controls))+' controls; 41 source improvements retained.')
