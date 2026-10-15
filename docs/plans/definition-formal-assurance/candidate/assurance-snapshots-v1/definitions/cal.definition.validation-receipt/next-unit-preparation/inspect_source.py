"""Read-only exact current Artifact source inspection before its native unit exists."""
from pathlib import Path
import sys,json,copy,importlib.util
u=Path(__file__).resolve().parents[1];sys.path.insert(0,str(u));import build_candidate as b
p=u/'next-unit-preparation'
def main():
 snap=b.snapshot();b.r.verify(snap,b.ROOT);source=b.source_ref(snap,'cal.definition.artifact');path=b.ROOT/source['path'];doc=json.loads(path.read_bytes());renderer=b.ROOT/'authority/definitions/v1/render.py'
 if not renderer.exists():renderer=b.ROOT/'authority/definitions/render.py'
 # The exact source generator is selected from the snapshot context rather than guessed.
 context=json.loads((u/'context.json').read_bytes());candidates=[b.ROOT/x['path'] for x in context['sources'] if x['sha256']==doc['source_direction']['generator_sha256']]
 assert len(candidates)==1;candidates[0].read_bytes();renderer=candidates[0]
 spec=importlib.util.spec_from_file_location('artifact_source_renderer',renderer);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 schema=b.ROOT/'authority/artifact-types/definition/v1/schema.json';validator=b.c.Draft202012Validator(json.loads(schema.read_bytes()));b.c.Draft202012Validator.check_schema(validator.schema)
 before=copy.deepcopy(doc);a=(module.render(doc).rstrip()+'\n').encode();z=(module.render(doc).rstrip()+'\n').encode();projection=path.with_name('DEFINITION.md');checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('current-source-exact',source['sha256']=='554dda3aec8fb66fdfd2a910d90defa56235705e482fa24184f31957a2b1d785' and b.ref(path)=={'path':source['path'],'sha256':source['sha256']})
 row=next(x for x in snap['current_entries'] if x['definition_id']=='cal.definition.artifact')
 ck('current-C53-meaning-overlay',row['admission_decision_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION' and row['effective_state']=='admitted-current')
 ck('source-Definition-shape',not list(validator.iter_errors(doc)))
 ck('two-pure-source-projections',before==doc and a==z==projection.read_bytes())
 ck('generator-exact',b.ref(renderer)['sha256']==doc['source_direction']['generator_sha256'])
 ck('D51-local-lineage-exact',doc['source_refs']==[{'admission_posture':'candidate-unadmitted','content_sha256':'3e9d50b1154b58b938c164725ac8fabed16914538dda579cf89c671c13c5becc','selector':'## CAV2-D51: Canonical Artifact','source_admission_ref':None,'source_ref':'cyberalchemy-v2:CAV2-D51'}])
 ck('classification-separate',doc['classification']['artifact_type_ref']=='cal.artifact-type.definition/v1' and doc['classification']['semantic_kind']=='definition')
 ck('origin-three-distinct-assurance-levels',all(x in doc['voices']['scientific_formal']['formal_expression'] for x in ['declared','integrity-bound','actor-attested']))
 ck('kind-origin-owner-assurance-explicit',all(x in doc['voices']['scientific_formal']['formal_expression'] for x in ['canonical_kind(a)','owner_admitted(a)','allowed_origin(a)','origin_assurance(a)']))
 ck('authority-independence-explicit','independent-of   authoritative(a)' in doc['voices']['scientific_formal']['formal_expression'])
 ck('sibling-separation-explicit','semantic.canonical-representation-invariant' in doc['boundaries'][1])
 ck('Artifact-native-unit-not-created',not (b.BASE/'definitions/cal.definition.artifact').exists())
 assert all(x['result'] for x in checks)
 refs=[b.ref(x) for x in [path,projection,renderer,schema,Path(__file__),b.BASE/'current-snapshot.json']];b.unchanged(refs);b.r.verify(snap,b.ROOT)
 report={'schema_version':'definition-assurance-next-Artifact-source-inspection/v1-candidate','source':source,'current_admission_decision_ref':row['admission_decision_ref'],'checks':checks,'selected_inputs':refs,'source_units':len(b.co.inventory(doc)),'projection_bytes':len(a),'projection_sha256':b.r.digest(a),'retained_legacy_source_refs':doc['source_refs'],'primary_consumer_refs':doc['primary_consumer_refs'],'requires_Receipt_full_delivery_audit_first':True,'actual_next_unit_created':False,'interpretation_or_models_created':False,'historical_external_source_bytes_reproduced':False,'repository_identity_authenticated':False,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'authority_effect':'none','claim_ceiling':'Exact current local source,Definition shape,pure source projections and logical design inputs only. Source admission is distinct from translation fidelity and instance authority. Legacy whole-file bytes,process execution,real assurance mechanisms and consumer maps remain unverified.'}
 with (p/'source-inspection.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps({'result':'PASS-for-exact-local-Artifact-source-only','checks':len(checks),'source_units':report['source_units'],'projection_bytes':len(a),'actual_next_unit_created':False},indent=2))
if __name__=='__main__':main()
