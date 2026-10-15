"""Recorded actual replay checks and owned-fixture negative checks, no owner outcome."""
import argparse
import tempfile
from common import *
from scope import governed_scope,VerifiedScope,_FACTORY
from materialize import request,cases,STATE,CAPABILITY
from model import Model
from selection import verify
from jsonschema import ValidationError

def run(out,pin):
    verify(pin);out=Path(out);require(out.is_relative_to(PACKAGE/'coverage'),'test outputs outside scope');out.mkdir(parents=True,exist_ok=False);checks=[]
    def ok(name,value):require(value,name);checks.append({'name':name,'result':'PASS'})
    def rejected(name,fn):
        try:fn()
        except (ValueError,ValidationError,FileNotFoundError):checks.append({'name':name,'result':'PASS'});return
        raise QueryFault('negative guard accepted: '+name)
    with governed_scope('historical-d73-slice') as selected:
        model=Model(selected);requests=cases(selected.scope_ref,model);life=model.query(requests['lifecycle']);prov=model.query(requests['provenance']);authority=model.query(requests['authority'])
        ok('three-written-questions-have-explicit-obligations',len(requests)==3 and all(v['obligations'] for v in requests.values()))
        ok('authority-actual-exact-authorization',any(e['predicate']=='authorizes-recorded-effect' for e in authority['connections']))
        effects=next(v for v in authority['claims'] if v['obligation']=='effect-scope')['basis']['recorded_effects']
        ok('recorded-22-artifacts-23-relations-zero-activation',effects['artifact_instances_admitted']==22 and effects['typed_relation_instances_admitted']==23 and effects['runtime_activations']==0)
        ok('state-content-epoch-not-admission-epoch',life['source_snapshot']['admission_epoch']=='decision:0073' and next(c for c in life['claims'] if c['obligation']=='current-state')['basis']['content_cursor']=='decision:0072')
        ok('historical-not-current',life['freshness']['state']=='historical')
        ok('invalid-predecessor-excluded-and-explained',life['result_status']=='partial' and any(v['kind']=='unresolved-global-connection' for v in life['gaps']))
        ok('Project-node-exact-version-gap-kept',any(v['kind']=='unresolved-represented-revision' for v in life['gaps']))
        lineage=next(e for e in prov['connections'] if e['predicate']=='relation.derives-from')
        ok('one-hop-derivation-complete',prov['result_status']=='complete' and lineage['qualifiers']=={'derivation_role':'thesis-outcome-realization'})
        ok('capability-domain-draft-despite-admission',next(v for v in prov['subjects'] if v['version_ref']==CAPABILITY)['axes']['domain_state']=='draft')
        ok('nine-independent-axes',all(set(v['axes'])==set(model.profile['independent_axes']) for v in model.nodes.values() if 'axes' in v))
        ok('byte-source-node-and-kind-identity-separated',node_key('a','x','id','v','0'*64)!=node_key('b','x','id','v','0'*64) and node_key('a','x','id','v','0'*64)!=node_key('a','x','id','v','1'*64))
        ok('carrier-and-instance-postures-separate',all(v['axes']['carrier_contract']['posture'] is not None and v['axes']['instance_admission'] for v in model.nodes.values() if 'axes' in v))
        ok('source-symbol-presence-does-not-establish-realization',any(v['kind']=='unresolved-implementation-bridge' for v in model.gaps) and not any(v['predicate']=='implemented-by' for v in model.edges.values()))
        broad=copy.deepcopy(requests['provenance']);broad['obligations']+=['implementation-bridge','effectiveness','new-action-permission'];b=model.query(broad)
        ok('broad-capability-obligations-partial',b['result_status']=='partial' and all(not b['coverage']['required_obligations'][o] for o in ['implementation-bridge','effectiveness','new-action-permission']))
        incoming=copy.deepcopy(requests['provenance']);incoming['root']='product-thesis:cyberalchemy-lab-governed-work@foundation.1';incoming['direction']='incoming';i=model.query(incoming)
        actual=next(e for e in i['connections'] if e['edge_id']==lineage['edge_id']);ok('incoming-retains-exact-source-target-and-qualifiers',actual==lineage)
        ok('incoming-path-marks-navigation-only',any(step['navigation']=='incoming' for p in i['explanation_paths'] for step in p['steps']))
        bounded=copy.deepcopy(requests['lifecycle']);bounded['limits']={'depth':0,'nodes':1,'edges':1};tr=model.query(bounded)
        ok('depth-node-limit-is-partial-with-stable-frontier',tr['result_status']=='partial' and tr['coverage']['truncated'] and tr['coverage']['omitted_frontier'])
        ok('continuation-is-same-cut',tr['coverage']['continuation']['source_cut_digest']==life['source_snapshot']['source_cut_digest'])
        edge_limit=copy.deepcopy(requests['lifecycle']);edge_limit['limits']['edges']=1;er=model.query(edge_limit)
        ok('edge-limit-truncation',er['coverage']['truncated'] and len(er['connections'])<=1)
        ok('coverage-partition-no-omission',sum(life['coverage']['partition'].values())==len(selected.data['projection']['subjects'])==len(life['coverage']['subject_rows']))
        ok('coverage-includes-unresolved-and-excluded-areas',life['coverage']['partition']['unresolved']>0 and life['coverage']['excluded_areas'])
        wrong=copy.deepcopy(requests['lifecycle']);wrong['view']='current';rejected('historical-D73-cannot-answer-current',lambda:model.query(wrong))
        for name,edit in [('wrong-admission-epoch',lambda q:q.update(admission_as_of='decision:0075')),
            ('wrong-selected-scope',lambda q:q.update(scope_ref='d75-selected-source')),
            ('negative-depth',lambda q:q['limits'].update(depth=-1)),('boolean-depth',lambda q:q['limits'].update(depth=True)),
            ('too-many-nodes',lambda q:q['limits'].update(nodes=1001)),('undeclared-edge',lambda q:q.update(edge_selection=['relation.invented'])),
            ('owner-outcome-in-request',lambda q:q.update(owner_outcome='admitted')),('projection-in-request',lambda q:q.update(projection=selected.data)),
            ('undeclared-obligation',lambda q:q.update(obligations=['complete-repository']))]:
            q=copy.deepcopy(requests['lifecycle']);edit(q);rejected(name,lambda:model.query(q))
        missing=copy.deepcopy(requests['provenance']);missing['root']=CAPABILITY.replace('@foundation.1','@wrong.1');mr=model.query(missing)
        ok('exact-version-never-aliased',mr['result_status']=='blocked' and not mr['subjects'])
        rejected('scope-factory-rejects-unverified-input',lambda:VerifiedScope({},selected.scope_ref,lambda:{},None,object()))
        altered=copy.deepcopy(selected.data);altered['projection']['subjects'][STATE]['effective_state']='owner-admitted-truth'
        probe=VerifiedScope(selected.data,selected.scope_ref,selected.source_guard,selected.validate_relation,_FACTORY,schema_validator=selected.validate_schema,endpoint_mapper=selected.endpoint_mapper)
        probe.data=altered;rejected('scope-data-mutation-detected',probe.guard)
        probe=VerifiedScope(selected.data,selected.scope_ref,selected.source_guard,selected.validate_relation,_FACTORY,schema_validator=selected.validate_schema,endpoint_mapper=selected.endpoint_mapper)
        probe.expires=time.monotonic()-1;rejected('expired-scope-rejected',probe.guard)
        probe.close();rejected('closed-scope-rejected',probe.guard)
        first=next(iter(model.edges.values()))
        rejected('closed-local-signature-no-generic-pair',lambda:model.edge(first['source'],first['target'],'implemented-by','profile-local',[],{'source_binding':{},'selector':'x','alignment_evidence_binding':{}}))
        rejected('closed-local-qualifiers',lambda:model.edge(first['source'],first['target'],first['predicate'],'profile-local',[],{'invented':True}))
        rejected('duplicate-request-key',lambda:parse(b'{"root":"a","root":"b"}'))
        rejected('nonfinite-request-value',lambda:parse(b'{"limits":NaN}'))
        rejected('unsafe-path-traversal',lambda:original({'path':'../outside','sha256':'0'*64}))
        # Freshness negative evidence uses a physically altered owned copy, never historical source bytes.
        with tempfile.TemporaryDirectory(prefix='cal-O03-source-fixture-') as temp:
            path=Path(temp)/'selected-source.json';raw=encoded({'candidate_owned_observation':1});path.write_bytes(raw);expected=sha(raw)
            def observed_guard():
                f=selected.source_guard();f['checked_count']+=1
                if not path.exists():f['missing'].append('owned-fixture:selected-source.json')
                elif path.is_symlink():f['unsafe'].append('owned-fixture:selected-source.json')
                elif sha(path.read_bytes())!=expected:f['changed'].append('owned-fixture:selected-source.json')
                return f
            fixture=VerifiedScope(selected.data,selected.scope_ref,observed_guard,selected.validate_relation,_FACTORY,schema_validator=selected.validate_schema,endpoint_mapper=selected.endpoint_mapper)
            fm=Model(fixture);ok('owned-selected-source-initially-current',fm.query(requests['provenance'])['result_status']=='complete')
            path.write_bytes(encoded({'candidate_owned_observation':2}));changed=fm.query(requests['provenance'])
            ok('actual-owned-source-change-invalidates-confirmed-paths',changed['freshness']['state']=='stale' and changed['result_status']=='blocked' and not changed['connections'])
            ok('stale-keeps-original-subject-observation',bool(changed['subjects']) and all(c['status']=='historical-source-observation' for c in changed['claims']))
            path.unlink();missing=fm.query(requests['provenance']);ok('actual-owned-source-missing-is-explicit',missing['freshness']['missing'] and missing['result_status']=='blocked')
            path.symlink_to(Path(temp)/'outside');unsafe=fm.query(requests['provenance']);ok('unsafe-owned-source-never-current',unsafe['result_status']=='blocked')
            fixture.close()
        ok('owned-source-fixture-removed',not Path(temp).exists())
        unknown=lambda:{'changed':[],'missing':[],'unsafe':[],'unchecked':['unverified-independent-source'],'checked_count':0}
        fixture=VerifiedScope(selected.data,selected.scope_ref,unknown,selected.validate_relation,_FACTORY,schema_validator=selected.validate_schema,endpoint_mapper=selected.endpoint_mapper)
        unknown_model=Model(fixture);u=unknown_model.query(requests['provenance']);ok('unchecked-source-blocks-confirmed-traversal',u['freshness']['state']=='unknown' and u['result_status']=='blocked' and not u['connections']);fixture.close()
        # Control drift uses the own scope's independent expected pin, with no source mutation.
        fixture=VerifiedScope(selected.data,selected.scope_ref,selected.source_guard,selected.validate_relation,_FACTORY,schema_validator=selected.validate_schema,endpoint_mapper=selected.endpoint_mapper)
        fixture.control_bindings[0]['sha256']='0'*64;cm=Model(fixture);c=cm.query(requests['provenance']);ok('control-pin-change-invalidates-current',c['result_status']=='blocked' and c['freshness']['changed']);fixture.close()
        ok('no-new-authority-no-replay-source',all(v['authority_effect']=='none' and v['replay_source'] is False for v in [life,prov,authority,b,u,c,changed]))
        ok('Project-history-never-claims-ontology-cut',life['source_snapshot']['canonical_ontology_cut'] is False and life['source_snapshot']['histories']['ontology-semantic'] is None)
        ok('same-scope-query-exact-original-byte-reproducibility',encoded(prov)==encoded(model.query(copy.deepcopy(requests['provenance']))))
    ok('actual-query-scope-closed',selected.closed);verify(pin)
    emit(out/'result.json',{'result':'PASS','checks':checks,'checks_count':len(checks),'selection_binding':pin,'authority_effect':'none','actual_owner_outcome':None,
        'negative_source_mutation':'owned physical selected-source fixture only; historical/admitted/control originals unchanged','canonical_admission':False})
    return bind(out/'result.json')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output');p.add_argument('selection_path');p.add_argument('selection_sha256');a=p.parse_args()
    print(json.dumps(run(a.output,{'path':a.selection_path,'sha256':a.selection_sha256}),sort_keys=True))
