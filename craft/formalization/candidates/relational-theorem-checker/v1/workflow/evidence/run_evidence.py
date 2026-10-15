#!/usr/bin/env python3
"""End-to-end scoped bundle cases and actual hostile proof/model controls."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import aggregate as a
b=a.b;s=b.s;sem=a.sem;v=b.v;HERE=Path(__file__).resolve().parent


def source_controls():
 proposal=s.read(s.BASE/'evolution/proposals/fresh-kind-proposal.json')
 original=(s.ROOT/proposal['after']['registry']['kinds'][-1]['source']['path']).read_bytes()
 controls=[]
 def reject(name,proposal):
  result=a.verify(proposal)
  s.require(a.o.exit_code(result)==2 and result['execution']=='not-run' and result['readiness']!='ready-for-review','unsafe declaration source accepted: '+name)
  controls.append({'name':name,'result':'rejected','outcome':result})
 with tempfile.TemporaryDirectory(prefix='source-boundary-outside-') as external,tempfile.TemporaryDirectory(prefix='source-boundary-',dir=HERE) as local:
  external_file=Path(external)/'declaration.json';external_file.write_bytes(original)
  link=Path(local)/'escaped-source.json';link.symlink_to(external_file)
  bad=deepcopy(proposal);bad['after']['registry']['kinds'][-1]['source']={'path':str(link.relative_to(s.ROOT)),'sha256':s.digest(external_file)}
  reject('declaration source symlink outside workspace rejected before projection',bad)
  duplicate=Path(local)/'duplicate-source.json';duplicate.write_bytes(b'{"schema":"ambiguous",'+original.lstrip()[1:])
  bad=deepcopy(proposal);row=bad['after']['registry']['kinds'][-1];row['source']=s.binding(duplicate);row['version']='sha256:'+row['source']['sha256']
  reject('duplicate declaration JSON keys rejected before legacy parser',bad)
  oversized=Path(local)/'oversized-source.json';oversized.write_bytes(original+b' '*(4*1024*1024))
  bad=deepcopy(proposal);row=bad['after']['registry']['kinds'][-1];row['source']=s.binding(oversized);row['version']='sha256:'+row['source']['sha256']
  reject('oversized declaration source rejected before unbounded read',bad)
 s.write(HERE/'source-boundary-controls.json',{'schema':'relational.declaration-source-controls/v1-candidate','result':'pass','controls':controls,'validation_script':s.binding(Path(__file__)),'authority_effect':'none'})
 print('source-boundary controls passed',len(controls),flush=True)
 return controls


def main():
 rules=s.read(s.BASE/'evolution/proposals/rule-change-proposal.json')
 unchanged=deepcopy(rules);unchanged['proposal_id']='proposal:bundle-unchanged';unchanged['after']=deepcopy(unchanged['before'])
 addition=deepcopy(unchanged);addition['proposal_id']='proposal:bundle-addition'
 edge=deepcopy(addition['after']['graph']['assertions'][0]);edge['id']='assertion:bundle-additional-conformance';addition['after']['graph']['assertions'].append(edge)
 fresh=s.read(s.BASE/'evolution/proposals/fresh-kind-proposal.json');kind=fresh['after']['registry']['kinds'][-1]
 fresh['proposal_id']='proposal:bundle-fresh-kind-with-instance'
 nodes=fresh['after']['graph']['nodes'];source=next(n for n in nodes if n['kind']=='capability-instance');target=next(n for n in nodes if n['kind']=='contract')
 fresh['after']['graph']['assertions'].append({'id':'assertion:bundle-trace','kind':kind['id'],'kind_version':kind['version'],
  'source':source['ref'],'target':target['ref'],'qualifiers':{'trace_label':'candidate:static-trace'}})
 empty=s.read(s.BASE/'evolution/proposals/fresh-kind-proposal.json');empty['proposal_id']='proposal:bundle-empty-pairs'
 empty_row=empty['after']['registry']['kinds'][-1];source_doc=s.read(s.ROOT/empty_row['source']['path'])
 empty_row['id']='relation.trace-empty-for';empty_row['pairs']=[]
 source_doc['declaration']['id']=empty_row['id'];source_doc['declaration']['pairs']=[]
 s.write(HERE/'empty-pairs-source.json',source_doc);empty_row['source']=s.binding(HERE/'empty-pairs-source.json');empty_row['version']='sha256:'+empty_row['source']['sha256']
 empty['after']['registry']['ordered_pair_count']=empty['before']['registry']['ordered_pair_count']
 controls=source_controls();reports={};cases={'unchanged':unchanged,'instance-only':addition,'fresh-kind-extension':fresh,'fresh-kind-empty-pairs':empty,'rule-only-extension':rules}
 with tempfile.TemporaryDirectory(prefix='source-collision-build-') as build,tempfile.TemporaryDirectory(prefix='source-collision-',dir=HERE) as output:
  replay=sem.Replay(rules,Path(build),Path(output));module=Path(build)/'Collision.lean';module.write_text('first checked statement\n')
  replay.persist_source('Collision');module.write_text('second checked statement\n');replay.persist_source('Collision')
  try:replay.audit_generated()
  except ValueError as error:controls.append({'name':'generated evidence source overwrite prevents readiness','result':'rejected','diagnostic':str(error)})
  else:raise ValueError('generated source overwrite was not detected')
 carrier=sem.compile_carrier(empty);validator=b.g.c.jsonschema.Draft202012Validator(carrier)
 sample_path=s.ROOT/'authority/admissions/governance-transaction-surface/v1/instances/typed-relations/materializes-generated-output.json'
 if not sample_path.is_file():
  sample_path=next(p for p in (sample_path.parent.parent).rglob('*.json') if s.read(p).get('payload',{}).get('relation_kind_ref')=='relation.materializes-consequence')
 sample=s.read(sample_path);sample['schema_version']='relational-checker.extension-carrier/v1-candidate'
 s.require(not list(validator.iter_errors(sample)),'empty-kind carrier damaged existing valid envelope')
 sample['payload']['relation_kind_ref']=empty_row['id'];sample['payload']['qualifiers']={field:'candidate:opaque' for field in empty_row['fields']}
 s.require(list(validator.iter_errors(sample)),'empty-pair declaration admitted an instance')
 controls.append({'name':'valid empty-pair carrier rejects all new-kind instances and preserves existing carrier instances','result':'pass','compiled_schema_valid':True})
 for name,proposal in cases.items():
  print('case starting',name,flush=True);bundle=b.make_bundle(proposal)
  # The rule case rechecks actual external proof and exact source-bound countermodel.
  if name=='rule-only-extension':
   proof=next(o for o in bundle['obligations'] if o['name']=='derivation-soundness')
   proof.update(method='proof-submission',artifacts={'proof-submission':s.binding(s.BASE/'workflow/proof-verifier/examples/derivation-submission.json')})
   wrapper=HERE/'case-countermodel-evidence.json'
   s.write(wrapper,{'schema':b.ROLE_SCHEMA['model-witness'],'proposal_identity':b.g.c.identity(proposal),
    'witness':s.binding(s.BASE/'inference/integration/countermodel.json')})
   model=next(o for o in bundle['obligations'] if o['name']=='independence-witnesses')
   model.update(method='checked-model-witness',artifacts={'model-witness':s.binding(wrapper)})
  s.write(HERE/(name+'-proposal.json'),proposal);s.write(HERE/(name+'-bundle.json'),bundle)
  outcome=a.verify(proposal,bundle);s.write(HERE/(name+'-result.json'),outcome)
  s.require(outcome['readiness']=='ready-for-review' and a.o.exit_code(outcome)==0,'positive full bundle failed: '+name+' '+json.dumps(outcome['diagnostics'])+' '+str([(r['required_statement']['id'],r['verdict'],r['diagnostics']) for r in outcome['results'] if r['verdict']!='satisfied']))
  reports[name]=outcome;print('case passed',name,flush=True)
  if name=='rule-only-extension':
   sources=[]
   for row in outcome['results']:
    if row['obligation_id'].endswith((':inhabited-model',':independence-witnesses')):
     evidence=s.read(s.ROOT/row['evidence_refs'][0]['path']);source=evidence['detail']['source'];s.check_binding(source);sources.append(source['path'])
   s.require(len(set(sources))==2,'scoped model sources still share an output path')
   controls.append({'name':'inhabited and independence model proofs retain distinct current source snapshots','result':'pass','source_paths':sources})
 # A real selected-data violation does not erase valid general preservation/conservativity.
 invalid=deepcopy(addition);invalid['proposal_id']='proposal:bundle-wrong-target-version'
 invalid['after']['graph']['assertions'][0]['qualifiers']['exact_version_ref']='wrong-target-version'
 outcome=a.verify(invalid);s.write(HERE/'invalid-data-result.json',outcome)
 s.require(outcome['readiness']=='blocked' and outcome['compatibility_dimensions']['selected-data-compatibility']=='violated' and outcome['compatibility_dimensions']['invariant-preservation']=='verified-for-named-scope' and outcome['compatibility_dimensions']['model-conservativity']=='verified-for-named-scope','selected data and universal properties collapsed')
 controls.append({'name':'actual selected-data violation separate from universally valid extension properties','result':'blocked','outcome':s.binding(HERE/'invalid-data-result.json')})
 good=b.make_bundle(rules)
 def rejected(name,mutate):
  bad=deepcopy(good);mutate(bad);result=a.verify(rules,bad)
  s.require(result['readiness']!='ready-for-review' and a.o.exit_code(result)!=0,'invalid complete bundle became ready: '+name)
  controls.append({'name':name,'result':result['readiness'],'diagnostics':result['diagnostics'],'missing':result['missing_hard_obligation_ids']})
 rejected('omitted required obligation',lambda x:x['obligations'].pop())
 rejected('substituted dependency digest',lambda x:x['dependencies']['bindings'][0].update(sha256='0'*64))
 rejected('old proposal binding',lambda x:x.update(proposal_identity='0'*64))
 rejected('self-authorized weaker policy',lambda x:x.update(policy_identity='0'*64))
 rejected('mislabeled bounded search as universal proof',lambda x:next(o for o in x['obligations'] if o['name']=='conservative-expansion').update(method='bounded-search'))
 rejected('client all-passed flag',lambda x:x.update(accepted=True))
 # Real proof and supplied model checks in the captured typed theory, independent
 # of transport metadata. Each failure then blocks a complete aggregate.
 with tempfile.TemporaryDirectory(prefix='bundle-hostile-typed-') as temp:
  build=Path(temp);output=HERE/'targeted-controls';output.mkdir(exist_ok=True)
  replay=sem.Replay(rules,build,output);replay.core()
  bad_proof=HERE/'targeted-weak-proof.lean';bad_proof.write_text('import DerivationSoundness\ntheorem submitted : True := True.intro\n')
  submission=v.make_submission(rules,'derivation-soundness',bad_proof,'submitted')
  entry={'method':'proof-submission'}
  verdict,method,detail=replay.execute('derivation-soundness',entry,{'proof-submission':submission})
  s.require(verdict=='violated','actual weakened proof accepted by R03')
  rows=deepcopy(reports['rule-only-extension']['results']);row=next(r for r in rows if r['obligation_id'].endswith(':derivation-soundness'));row.update(verdict=verdict,evidence_method=method)
  blocked=a.aggregate_results(rules,rows);s.require(blocked['readiness']=='blocked','failed required proof aggregated as ready')
  controls.append({'name':'actual weak theorem cannot discharge required derivation statement','result':'blocked','detail':detail})
  rule=replay.rule_checks();bad_model=deepcopy(s.read(s.BASE/'inference/integration/countermodel.json'));bad_model['model']=[]
  verdict,method,detail=replay.execute('independence-witnesses',{'method':'checked-model-witness'},{'model-witness':{'witness':bad_model}})
  s.require(verdict=='violated' and not detail['accepted'],'typed invalid model accepted by checker')
  controls.append({'name':'actual missing-facts countermodel rejected by fresh semantic checker','result':'violated','detail':detail})
  wrong=deepcopy(s.read(s.BASE/'inference/integration/countermodel.json'))
  wrong['claim']['conclusion']['terms'][0]=deepcopy(next(x for x in rule['after']['domain'] if x['kind']=='reference' and x!=wrong['claim']['conclusion']['terms'][0]))
  try:replay.execute('independence-witnesses',{'method':'checked-model-witness'},{'model-witness':{'witness':wrong}})
  except ValueError as error:controls.append({'name':'valid countermodel for another ground implication cannot weaken required formula','result':'rejected','diagnostic':str(error)})
  else:raise ValueError('wrong scoped non-entailment formula accepted')
  verdict,method,detail=replay.execute('independence-witnesses',{'method':'bounded-search'},{'search-result':{'schema':b.ROLE_SCHEMA['search-result'],'proposal_identity':b.g.c.identity(rules),'provider_status':'completed','found':True,'accepted':True}})
  s.require(verdict=='unknown' and method=='bounded-search','provider flags became theorem evidence')
  rows=deepcopy(reports['rule-only-extension']['results']);row=next(r for r in rows if r['obligation_id'].endswith(':independence-witnesses'));row.update(verdict=verdict,evidence_method=method)
  pending=a.aggregate_results(rules,rows);s.require(pending['readiness']=='unresolved' and a.o.exit_code(pending)==4,'bounded search inferred readiness')
  controls.append({'name':'provider completion/found flags without checked witness remain unknown','result':'unresolved','detail':detail})
  rows=deepcopy(reports['rule-only-extension']['results']);row=next(r for r in rows if r['obligation_id'].endswith(':rule-extension-compatibility'));row.update(verdict='unknown',evidence_method='none')
  pending=a.aggregate_results(rules,rows);s.require(pending['compatibility_dimensions']['model-conservativity']=='unknown','rule conservativity omitted from model dimension')
  controls.append({'name':'missing actual rule-model conservativity cannot hide behind registry conservativity','result':'unresolved'})
  rows=deepcopy(reports['rule-only-extension']['results']);rows.pop();pending=a.aggregate_results(rules,rows)
  s.require(pending['missing_hard_obligation_ids'] and pending['readiness']=='unresolved','missing verifier result silently dropped')
  controls.append({'name':'complete aggregation detects missing server result','result':'unresolved'})
 widened=s.read(s.BASE/'evolution/proposals/pair-widening-proposal.json');unsupported=a.verify(widened)
 s.require(a.o.exit_code(unsupported)==3 and unsupported['readiness']!='ready-for-review','unsupported widening became ready')
 controls.append({'name':'endpoint widening remains unsupported despite old selected sample compatibility','result':'unsupported'})
 oldhead=deepcopy(rules);oldhead['after']['rules'][0]['head']['predicate']='Admitted';unsupported=a.verify(oldhead)
 s.require(a.o.exit_code(unsupported)==3 and unsupported['readiness']!='ready-for-review','old protected head reused fresh-head model construction')
 controls.append({'name':'old protected head requires another extension profile','result':'unsupported'})
 malformed=HERE/'targeted-malformed.json';malformed.write_text('{"schema":1,"schema":2}')
 run=subprocess.run([str(HERE/'bundle-verifier'),str(malformed),'--proposal',str(HERE/'rule-only-extension-proposal.json')],text=True,capture_output=True,timeout=60)
 result=b.i.c.d.decode(run.stdout)
 s.require(run.returncode==2 and result['execution']=='not-run' and 'Traceback' not in run.stderr,'malformed public transport did not return a safe input outcome')
 controls.append({'name':'duplicate JSON input returns normalized not-run outcome and nonzero exit','result':'rejected','exit_code':run.returncode,'outcome':result})
 s.write(HERE/'evidence-controls.json',{'schema':'relational.bundle-controls/v1-candidate','result':'pass',
  'positive_full_profiles':{name:s.binding(HERE/(name+'-result.json')) for name in reports},
  'controls':controls,'validation_script':s.binding(Path(__file__)),'authority_effect':'none',
  'review_mode':'Codex author self-review; candidate bundle verification only',
  'claim_ceiling':'Five complete cases across four computed profiles, including an empty-denotation fresh kind; exact captured structural/F0 projection and fresh-head/old-body finite inference. Full source semantics, authenticated admission and deployment are outside this evidence.'})
 print('R03 full controls passed:',len(reports),'profiles;',len(controls),'hostile controls',flush=True)

if __name__=='__main__':main()
