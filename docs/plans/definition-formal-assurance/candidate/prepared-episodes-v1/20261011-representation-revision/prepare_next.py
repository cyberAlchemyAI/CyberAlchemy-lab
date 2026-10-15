"""Source-only Schema Evolution Invariant preparation; no next native unit."""
from pathlib import Path
import ast
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.representation-revision');d=u/'next-unit-preparation';d.mkdir()
prev=u.with_name('cal.definition.projection-specification')
s=(prev/'verify_source_checks.py').read_text();s=s[:s.index("\n ck('native-exact-source-and22units'")]
s=s.replace('import build_candidate as b',"P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent));import build_candidate as b")
s=s.replace("'cal.definition.projection-specification'","'cal.definition.schema-evolution-invariant'").replace('ProjectionSpecification','SchemaEvolutionInvariant').replace('cal.definition.projection-specification@','cal.definition.schema-evolution-invariant@').replace('semantic.projection-specification','semantic.schema-evolution-invariant')
s=s.replace('42cff2435ac4e732bf0ea45a2e0f5d6fcdf2921f17b18bbd1b1adcc4e643eb24','e1c996eda39fa109bc0b689570ce1a6cdeb72796e667125a365679ad4da26088').replace('b90efb80d4f8a497b49168a3db804626ecf52e3524141c98aa42725c9f52897c','c847e55136201777b89c5cdb6ad7e538e033e730538e143535d7edf65283d935').replace('CAV2-D44: View-Bearing Concept','CAV2-D25: Schema Amendment Witness').replace('D44','D25')
s=s.replace("'checker':b.UNIT/'verify_source_checks.py'","'checker':P/'inspect_source.py'")
i=s.index(" f=doc['voices']['scientific_formal']");j=s.index('\n admissions=',i)
s=s[:i]+''' f=doc['voices']['scientific_formal'];expr=f['formal_expression'];norm=f['normative_statement'];ck('normalized-invariant-own-D25-classification',all(x in norm for x in ['semantic.schema-evolution-invariant','scope.shared-authority','type.invariant','CAV2-D25','without silently merging']))
 ck('authority-affecting-seven-shape-surfaces',all(x in norm for x in ['schema,','frontmatter,','taxonomy,','ontology,','ledger,','event,','machine-view','validation or authority interpretation']))
 ck('amendment-record-seven-components',all(x in norm for x in ['owner, scope, reason, changed shape, source','evidence, compatibility effect, and rollout or rollback route']))
 ck('witness-record-five-alternatives',all(x in norm for x in ['validator, runtime observation, fixture, review check,','or typed residue']))
 ck('formal-seven-position-amendment-tuple','A = (owner, scope, source, delta, compatibility, witness, residue)' in expr)
 ck('deterministic-hybrid-review-and-owned-absence',all(x in expr for x in ['deterministic, hybrid, review-based','absent only when','typed as residue with owner and effect']))
 ck('downstream-governance-requires-enforcement-or-residue',all(x in expr for x in ['not','complete','govern downstream work','declared','enforcement or residue path']))
 ck('change-rule-not-generic-schema',all(x in f['boundary_conditions'][0] for x in ['CAV2-D56','change','not its content','fully automated validator','Review and typed residue are acceptable']))
 ck('one-boundary-four-tests-two-notations',len(f['boundary_conditions'])==1 and len(f['testable_conditions'])==4 and len(f['notation'])==2)
 ck('candidate-body-current-overlay-separated','It is not admitted' in doc['claim_ceiling'] and row['effective_state']=='admitted-current')
'''+s[j:]
s+='''
 ck('next-native-unit-absent',not (b.BASE/'definitions/cal.definition.schema-evolution-invariant').exists());ck('all-201-source-bytes-still-current',b.r.verify(snap,b.ROOT)['files']==201)
 report={'schema_version':'definition-assurance-next-source-inspection/v1-candidate','authority_effect':'none','source':source,'source_units':len(b.co.inventory(doc)),'checks':checks,'selected_inputs':refs,'upstream_observations':[{'embedded_source_ref':embedded,'admitted_for_use_selection':admitted,'current_external_file_ref':external_ref,'current_selection_sha256':b.r.digest(selected),'current_selection_bytes':len(selected),'coordinate_equivalence_accepted':False}],'projection_bytes':len(one),'projection_sha256':b.r.digest(one),'external_file_refs':[external_ref],'requires_RepresentationRevision_full_delivery_audit_first':True,'actual_next_unit_created':False,'interpretation_or_models_created':False,'native_or_live_consumer_executed':False,'semantic_ready':False,'mechanized_proof':False}
 if write:
  with (P/'source-inspection.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\\n')
 else:assert b.r.same_json(report,json.loads((P/'source-inspection.json').read_bytes()))
 return report
if __name__=='__main__':
 x=verify('--write' in sys.argv);print(json.dumps({'result':'PASS-next-SchemaEvolutionInvariant-source-only','checks':len(x['checks']),'source_units':x['source_units'],'projection_bytes':x['projection_bytes'],'external_D25_bytes':x['upstream_observations'][0]['current_selection_bytes'],'source_sha256':x['source']['sha256'],'actual_next_unit_created':False},indent=2))
'''
ast.parse(s)
with (d/'inspect_source.py').open('x') as f:f.write(s)
s=(p.with_name('20261011-projection-specification')/'capture_next_source.py').read_text().replace('cal.definition.projection-specification','cal.definition.representation-revision').replace("str(u/'inspect_source.py')","str(u/'inspect_source.py'),'--write'")
with (p/'capture_next_source.py').open('x') as f:f.write(s)
print('Prepared exact C53 D25 source-only inspector.')
