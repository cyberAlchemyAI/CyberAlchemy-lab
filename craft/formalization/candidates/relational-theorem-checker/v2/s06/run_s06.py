from pathlib import Path
import sys,copy,json
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import runtime as r
s=r.s;HERE=Path(__file__).resolve().parent
s.context('S06',[(s.BASE/'s03/RecursiveExtension.lean','independent checked structural expansion hypotheses'),(s.BASE/'s03/RecursiveSaturation.lean','complete finite reference saturation proof'),(s.BASE/'s03/normalizer.py','component-local stable old-rule identity'),(s.BASE/'s05/capability-manifest.json','source observation transport and trust ceiling'),(s.BASE/'s15/obligation-catalog.json','generated exact change class inventory'),(s.BASE/'s04/MappingStatements.lean','independent mapping requirements'),(s.V1/'workflow/proof-verifier/Verifier.lean','fixed exact statement replay policy')],[{'decision':'General independent bundle plus actual projection, producer, lineage, closure and extension witnesses; no sampled closure substitutes for model expansion','basis':'S06 requirements'},{'decision':'Saved result validation is structural currentness only; application needs fresh qualification','basis':'metadata alone is not evidence replay'}])
b=r.ext.c.fixture();a=r.ext.example(b);p=r.proposal(b,a);s.write(HERE/'recursive-proposal.json',p)
result=r.qualify(p,HERE/'build');s.write(HERE/'recursive-result.json',result);results=[]
def ctrl(name,fn,pos=False):
 try:fn();s.require(pos,'accepted hostile '+name);results.append({'name':name,'result':'pass','outcome':'checked'})
 except Exception as ex:
  if pos:raise
  s.require(not str(ex).startswith('accepted hostile'),'failed control '+name);results.append({'name':name,'result':'pass','outcome':'blocked','reason':str(ex).splitlines()[0]})
def mutate(fn):
 q=copy.deepcopy(result);fn(q);return r.validate_receipt(p,q)
ctrl('complete-recursive-proposal-fresh-replay',lambda:s.require(result['status']=='qualified-candidate' and result['evidence']['general']['audit']['fresh_kernel_replay'],'missing full replay'),True)
ctrl('exact-generated-inventory',lambda:s.require([o['id'] for o in result['obligations']]==[o['id'] for o in r.ext.c.obligations('rule-only')],'inventory mismatch'),True)
ctrl('nonempty-old-baseline-qualified',lambda:s.require(bool(b['inference']['rules']) and len(result['closure'])>len(result['observations']),'nonempty rules not exercised'),True)
ctrl('structurally-current-result-not-application-authorization',lambda:s.require(r.validate_receipt(p,result)['readiness'].startswith('requires-fresh'),'metadata authorized application'),True)
ctrl('caller-shrunken-inventory',lambda:mutate(lambda q:q['obligations'].pop()))
ctrl('missing-hard-evidence',lambda:mutate(lambda q:q['obligations'][0].update(evidence=[])))
ctrl('wrong-evidence-method',lambda:mutate(lambda q:q['obligations'][0].update(method='metadata-pass')))
ctrl('weakened-obligation-statement',lambda:mutate(lambda q:q['obligations'][-1].update(target='True')))
ctrl('stale-profile-receipt',lambda:mutate(lambda q:q.update(profile_identity='0'*64)))
ctrl('stale-proposal-receipt',lambda:mutate(lambda q:q.update(proposal_identity='0'*64)))
ctrl('v1-fifteen-inventory-assumption',lambda:s.require(len(result['obligations'])!=15,'old inventory retained'),True)
# Independent verifier refuses an actually compiled True theorem against the general bundle.
weak=r.replay_general(HERE/'build',weak=True);s.write(HERE/'weakened-general-rejection.json',weak)
weakArchive=HERE/'build/WeakenedSubmission.lean';weakArchive.write_bytes((HERE/'build/Submitted.lean').read_bytes())
# Restore exact accepted submitted bytes and kernel artifact; source is checked again.
restored=r.replay_general(HERE/'build');s.require(restored['audit']['accepted'],'restore replay failed')
ctrl('compiled-weakened-general-type-rejected',lambda:s.require(weak['result']=='rejected','weak accepted'),True)
# Actual query certificate and partial closure rejections are kernel checked.
d=r.projection.c.f.d;n=result['normal_form'];ev={'closure':result['closure'],'steps':result['certificates']};bad=copy.deepcopy(ev['steps']);s.require(bad[-1]['kind']=='apply','expected actual multi-step derivation');bad[-1]['indices']=[len(bad)-1]
source='import RuntimeProofs\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nnamespace Successor.Runtime.Negative\nopen Inference\ndef theory : Theory := '+r.render.theory_lean(n)+'\ndef facts : List Atom := '+d.rows(n['facts'],r.render.atom_lean)+'\ndef C : List Atom := '+d.rows(ev['closure'][:-1],r.render.atom_lean)+'\ndef good : List Step := '+d.rows(ev['steps'],r.render.step_lean)+'\ndef cyclic : List Step := '+d.rows(bad,r.render.step_lean)+'\ndef query : Atom := '+r.render.atom_lean(ev['closure'][-1])+'\ntheorem cyclic_certificate_blocked : checkDerivation theory facts cyclic query = false := by decide\ntheorem incomplete_closure_blocked : checkClosure theory facts C [good] = false := by decide\n#print axioms cyclic_certificate_blocked\n#print axioms incomplete_closure_blocked\nend Successor.Runtime.Negative\n'
(HERE/'NegativeCertificates.lean').write_text(source);negative=s.compile_modules(HERE/'build',[('NegativeCertificates',HERE/'NegativeCertificates.lean')])
ctrl('cyclic-or-forward-certificate-cannot-prove-query',lambda:s.require(bool(negative),'missing rejection'),True)
ctrl('partial-closure-cannot-claim-completeness',lambda:s.require(bool(negative),'missing partial rejection'),True)
ctrl('currentness-after-negative-controls',lambda:r.validate_receipt(p,result),True)
s.write(HERE/'recursive-workflow-audit.json',{'result':'pass','controls':results,'result_binding':s.binding(HERE/'recursive-result.json'),'required_ids':[o['id'] for o in r.ext.c.obligations('rule-only')],'general_required_type':'Successor.Runtime.Catalog.RequiredGeneralBundle','weakened_type_rejection':s.binding(HERE/'weakened-general-rejection.json'),'negative_kernel_witnesses':negative,'source_trust':'Tested JSON/projected-value boundary; fixed independent types and actual pure proof/value replay; same pinned Lean kernel','authority_effect':'none'})
s.accept('S06',['Actual multi-step/cycle proposal with nonempty old rules has typed, producer, complete-closure and structural extension witnesses plus fresh general-bundle replay.','Kernel checks actual hypotheses separately from exact universal required types; compiled weakened type and cyclic/partial certificate controls reject.','Exact generated ordered inventory has 20 hard obligations; no legacy count constraint.'],controls=results,extra_dependencies=[HERE/'runtime.py',HERE/'RuntimeCatalog.lean',HERE/'RuntimeProofs.lean',HERE/'RuntimeVerifier.lean',HERE/'recursive-proposal.json',HERE/'recursive-result.json',HERE/'NegativeCertificates.lean',HERE/'weakened-general-rejection.json',weakArchive])
print('S06 accepted: 20 actual required obligations, general fresh replay and '+str(len(results))+' workflow controls.')
