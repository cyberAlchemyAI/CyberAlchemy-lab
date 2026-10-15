from pathlib import Path
import sys,copy
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import fixtures as f
s=f.s;a=f.a;HERE=Path(__file__).resolve().parent
s.context('S07',[(s.BASE/'s04/field-map.json','exact legacy stress qualifiers'),(s.BASE/'s04/ConditionSemantics.lean','unknown/false/conflicting status meaning'),(s.BASE/'s05/capability-manifest.json','transport identity/budget posture'),(s.BASE/'s18/source-map.json','all unselected source meanings remain deferred'),(s.V1/'relation-stress/v1/implementation/stress_cli.py','strict typed stress backend'),(s.V1/'relation-stress/v1/implementation/examples/acts-for.json','direct declaration example'),(s.V1/'relation-stress/v1/implementation/examples/inherits-contract.json','fixed norm example')],[{'decision':'One exact source assertion per mapped query; source registry endpoint kind checks outside F0 are a tested boundary','basis':'acts-for agent-instance/principal lie outside F0 NodeKind enumeration'},{'decision':'Condition reference revision comes from an explicit source-bound interpretation record; no arbitrary condition execution','basis':'S00/S04 activation requirements'}])
results=[];outputs=[]
def case(name,q,expected,condition=None,potential=None,active=None,conflicts=None):
 out=a.evaluate(q,HERE/'build');s.require(out['status']==expected,'unexpected '+name+' status '+str(out))
 if condition is not None:s.require(out['condition_status']==condition,'condition mismatch '+name)
 if potential is not None:s.require(len(out['potential_norms'])==potential,'potential count '+name)
 if active is not None:s.require(len(out['active_norms'])==active,'active count '+name)
 if conflicts is not None:s.require(len(out['active_conflicts'])==conflicts,'conflict count '+name)
 path=HERE/'cases'/(name+'.json');s.write(path,{'request':q,'result':out});outputs.append(s.binding(path));results.append({'name':name,'result':'pass','outcome':out['status'],'condition_status':out.get('condition_status')});return out

def negative(name,q):
 try:a.evaluate(q,HERE/'build');raise ValueError('hostile accepted '+name)
 except Exception as ex:
  s.require(not str(ex).startswith('hostile accepted'),'negative failed');results.append({'name':name,'result':'pass','outcome':'invalid','reason':str(ex).splitlines()[0]})
d=f.example('delegation');i=f.example('inheritance');s.write(HERE/'delegation-request.json',d);s.write(HERE/'inheritance-request.json',i)
case('mapped-direct-delegation',d,'yes')
expired=copy.deepcopy(d);expired['typed']['snapshot']['epoch']=10;expired['baseline']['context']['epoch']=10;expired['baseline']['inference']['snapshot_epoch']=10;case('half-open-expiry-boundary',f.refresh(expired),'no')
revoked=copy.deepcopy(d);revoked['typed']['delegations'][0]['revokedAt']=5;revoked['typed']['edge']['revokedAt']=5;revoked['interpretation']['fields']['revocation_state']=5;case('revoked-at-snapshot',f.refresh(revoked),'no')
missing=copy.deepcopy(d);missing['typed']['delegations'][0]['policies']=[{'id':'required-policy','version':'v1'}];case('missing-policy-remains-unknown',f.refresh(missing),'unknown')
chain=copy.deepcopy(d);chain['typed']['redelegated']=True;chain['typed']['delegations'][0]['redelegationAllowed']=True;case('permitted-chain-unimplemented',f.refresh(chain),'unknown')
case('inherited-potential-with-unknown-condition',i,'yes','unknown',1,0,0)
case('held-condition-activates-with-origin',f.holds(i),'yes','yes',1,1,0)
case('false-condition-keeps-potential',f.holds(i,'does-not-hold'),'yes','no',1,0,0)
case('explicit-unknown-not-false',f.holds(i,'unknown'),'yes','unknown',1,0,0)
contradiction=f.holds(i);row=copy.deepcopy(contradiction['evaluations'][0]);row['id']='evaluation-2';row['status']='does-not-hold';contradiction['evaluations'].append(row);case('conflicting-selected-status-blocks-activation',contradiction,'yes','invalid',1,0,0)
unknownplus=f.holds(i);row=copy.deepcopy(unknownplus['evaluations'][0]);row['id']='evaluation-2';row['status']='unknown';unknownplus['evaluations'].append(row);case('selected-unknown-holds-conflict',unknownplus,'yes','invalid',1,0,0)
wrongEpoch=f.holds(i);wrongEpoch['evaluations'][0]['key']['epoch']=6;case('wrong-epoch-evaluation-not-selected',wrongEpoch,'yes','unknown',1,0,0)
wrongVersion=f.holds(i);wrongVersion['evaluations'][0]['key']['condition']['version']='wrong';case('wrong-condition-revision-not-selected',wrongVersion,'yes','unknown',1,0,0)
conflict=f.holds(i);conflict['typed']['graph']['contracts'][0]['norms'].append({'mode':'forbid','action':'receipt'});case('active-conflict-has-two-active-origins',f.refresh(conflict),'yes','yes',2,2,1)
inactive=copy.deepcopy(conflict);inactive['evaluations']=[];case('potential-conflict-is-not-active-conflict',inactive,'yes','unknown',2,0,0)
override=copy.deepcopy(i);override['typed']['graph']['bindings'][0]['overrides']=[{'id':'override','version':'v1'}];case('override-remains-unknown',f.refresh(override),'unknown','unknown',0,0,0)
conforming=f.holds(i);e=conforming['typed']['graph']['inheritances'][0];conforming['typed']['graph']['conformance']=[{'subject':e['subject'],'contract':e['contract'],'scope':e['scope'],'accepted':True}];out=case('conformance-does-not-create-fulfillment-or-admission',f.refresh(conforming),'yes','yes',1,1,0);s.require(out['fulfilled']=='not-established' and out['admission']=='not-derived','meaning upgraded')
invalidPeriod=copy.deepcopy(d);invalidPeriod['interpretation']['fields']['effective_period']='0..10';negative('opaque-period-cannot-be-guessed',invalidPeriod)
wrongKind=copy.deepcopy(d);wrongKind['baseline']['graph']['nodes'][0]['kind']='principal';negative('source-pair-outside-declared-signature',f.refresh(wrongKind))
stale=copy.deepcopy(i);stale['baseline']['context']['epoch']=6;stale['baseline']['inference']['snapshot_epoch']=6;negative('stale-source-context-interpretation',stale)
wrongMap=copy.deepcopy(i);wrongMap['interpretation']['fields']['binding_ref']['version']='wrong';negative('wrong-binding-revision',wrongMap)
absent=copy.deepcopy(d);absent['assertion_id']='absent';negative('nonmember-valid-shaped-edge',absent)
extra=copy.deepcopy(i);extra['typed']['graph']['inheritances'].append({**extra['typed']['graph']['inheritances'][0],'id':'unmapped'});negative('unmapped-typed-extra-edge',f.refresh(extra))
# Original typed examples and source records agree on successful direct/fixed profiles;
# every exported mapping/verdict/norm/activation/conflict has a current kernel witness.
s.write(HERE/'mapping-audit.json',{'result':'pass','controls':results,'cases':outputs,'dependencies':s.binding(HERE/'build/dependencies.json'),'semantic_ledger_advance':[{'relation':'relation.acts-for','fields':['delegation_ref','scope_ref','effective_period','revocation_state'],'status':'selected-explicit-source-bound-map','external_truth_proved':False},{'relation':'relation.inherits-contract','fields':['binding_ref','contract_version_ref'],'status':'selected-explicit-source-bound-map','external_truth_proved':False}],'unselected_meanings':'unchanged/unsupported; v1 ledger not mutated','outside_f0':'agent-instance/principal source kind/pair checks are tested registry boundary, not F0 Graph Inv theorem','certificate_ceiling':'propagation/forward origin witnesses alone do not establish whole-graph/complete-query qualification; actual typed query checks and complete potential enumeration are separate kernel witnesses','authority_effect':'none'})
s.accept('S07',['Each selected qualifier maps via a source/context/assertion/typed identity envelope to a finite functional store; exact maps and scalar verdicts compile.','Original direct/fixed typed cases agree; outside-F0 source kind checks and supplied truth remain explicit tested boundaries.','Potential/active norm outputs never claim fulfillment or admission, including supplied conformance cases.','Unknown/false/wrong-context/conflicting conditions emit no active norms; potential output retained separately; active conflicts have sound/complete kernel witnesses within the mapped query.'],controls=results,extra_dependencies=[HERE/'stress_adapter.py',HERE/'KernelMapping.lean',HERE/'fixtures.py',HERE/'build/dependencies.json',HERE/'delegation-request.json',HERE/'inheritance-request.json']+[s.ROOT/b['path'] for b in outputs])
print('S07 accepted: '+str(len(results))+' source/condition/norm/expiry controls; exact mapped query scope.')
