"""Candidate research with predeclared methods, bounded replay and explicit uncertainty."""
from __future__ import annotations
import base64,copy,importlib.util,math,os,statistics,subprocess,sys,tempfile,time
from datetime import datetime,timezone
from pathlib import Path
from dataclasses import replace

sys.path.insert(0,str(Path(__file__).resolve().parent))
import engineering as shared
from engineering import BoundaryFault,HostAuthority,byte_sha,encoded,parse,require,read,carrier,validate_record,ROOT,PACKAGE,SCOPE,CAPABILITY,PAIRS
from dispatch import public_evaluation
from counter import atomic

EXAMPLE=PACKAGE/'examples/research'
INTERFACE='bounded-signed-replay-comparison/v1-candidate'
METHOD_SCHEMA=ROOT/'implementation/lab-bootstrap/candidates/v1/packages/0004/method/schema.json'
ARCHIVE=ROOT/'implementation/lab-work/candidates/v1/packages/0002/branch.snapshot'
BRIDGE=ROOT/'implementation/lab-runtime/candidates/repeatable-operation'
ENGINEERING_INPUTS=PACKAGE/'examples/engineering/packages/0004'
TRIAL_LABELS=('parity','mismatch','rejected','timeout')
VERSION='candidate.1'
OUTPUT_KINDS=frozenset({'experiment-run','research-run','observation','measurement-result','evidence-set','finding',
    'evaluation','implementation','agent-action','generated-output','work','typed-relation'})


def now():return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def ident(value):return value.get('node_id',value.get('method_id',value.get('goal_id',value.get('coordination_context_id',value.get('project_id',value.get('product_id'))))))
def ref(value):return ident(value)+'@'+value.get('version',VERSION)
def kind(value):
    if 'project_id' in value:return 'project'
    if 'product_id' in value:return 'product'
    return value['kind']


def validate(value,semantic_kind):
    if semantic_kind=='method':
        from jsonschema import Draft202012Validator
        require(not list(Draft202012Validator(read(METHOD_SCHEMA)).iter_errors(value)),'invalid candidate Method carrier')
    else:validate_record(value,semantic_kind)


def template(semantic_kind,name):
    value=read(ROOT/f'authority/artifact-types/{semantic_kind}/v1/fixtures/valid/record.json')
    value.update(node_id=semantic_kind+':lab-W09:bc3c50170a404b4ba8d8:research:'+name,authority_effect='none',scope_ref=SCOPE,
        owner_ref='principal:repository-owner@candidate.1',challenge_route='protocol:W04-research-challenge',
        claim_ceiling='Exact isolated candidate research only; no admission, Product SLA or human acceptance.')
    if 'owner_route' in value:value['owner_route']='protocol:deferred-owner-decision:R08'
    if 'status' in value:value['status']='candidate-unadmitted'
    return value


def typed(name,relation_kind,source_ref,target_ref,records,qualifiers):
    require(source_ref in records and target_ref in records,'research exact endpoint unresolved')
    source,target=records[source_ref],records[target_ref]
    for selected,value in [(source_ref,source),(target_ref,target)]:
        require(selected.startswith(ident(value)+'@'),'research endpoint identity differs')
        if 'version' in value:require(selected==ref(value),'research endpoint exact version differs')
    rows=[r for r in read(PAIRS)['exact_pairs'] if
        (r['relation_kind_ref'],r['source_kind'],r['target_kind'])==(relation_kind,kind(source),kind(target))]
    require(len(rows)==1,'research ordered relation pair undeclared')
    contract=rows[0]['qualifier_contract']
    from jsonschema import Draft202012Validator
    qualifier_schema={'type':'object','properties':contract['properties'],'required':contract['required_axes'],'additionalProperties':False}
    require(not list(Draft202012Validator(qualifier_schema).iter_errors(qualifiers)),'research closed qualifier domain differs')
    binding=rows[0]['relation_binding'];require(byte_sha((ROOT/binding['path']).read_bytes())==binding['sha256'],'research Relation Kind bytes drift')
    value=shared.artifact('typed-relation',name,{
        'relation_kind_ref':relation_kind,
        'source':{'ref':ident(source),'version_ref':source_ref,'kind':kind(source)},
        'target':{'ref':ident(target),'version_ref':target_ref,'kind':kind(target)},
        'qualifiers':qualifiers,'relation_lifecycle_state':'candidate',
        'relation_evidence_refs':['protocol:W04-exact-observed-evidence']},[])
    value['node_id']='typed-relation:lab-W09:bc3c50170a404b4ba8d8:research:'+name;validate(value,'typed-relation');return value


def resolve(directory,selection_sha):
    directory=Path(directory);raw=(directory/'selection.json').read_bytes()
    require(byte_sha(raw)==selection_sha,'independent research selection pin differs')
    selection=parse(raw);require(selection['authority_effect']=='none' and selection['actual_owner_outcome'] is None,'research inputs cannot supply owner outcome')
    require(selection['scope_ref']==SCOPE,'research Project differs');records={}
    for row in selection['records']:
        require(Path(row['path']).name==row['path'],'research input outside selected scope')
        p=directory/row['path'];require(p.is_file() and not p.is_symlink(),'research input missing or unsafe')
        value=read(p);require(byte_sha(p.read_bytes())==row['sha256'],'research original input bytes changed')
        validate(value,row['kind']);require(ident(value)==row['identity_ref'],'research input identity differs')
        require(row['version_ref'].startswith(ident(value)+'@'),'research input revision differs')
        if 'version' in value:require(row['version_ref']==ref(value),'research body version differs')
        require(row['version_ref'] not in records,'duplicate research revision');records[row['version_ref']]=value
    method_row=selection['procedure'];require(Path(method_row['path']).name==method_row['path'],'procedure path outside selected scope')
    p=directory/method_row['path'];require(p.is_file() and not p.is_symlink(),'procedure unsafe')
    raw=p.read_bytes();require(byte_sha(raw)==method_row['sha256'],'research method bytes changed');procedure=parse(raw)
    required={'schema_version','authority_effect','method_ref','design_ref','archive_sha256','source_bindings','samples','order',
        'timeout_seconds','ratio_threshold','residue_labels','claim_ceiling','actual_owner_outcome'}
    require(set(procedure)==required and procedure['authority_effect']=='none' and procedure['actual_owner_outcome'] is None,'closed research procedure required')
    require(procedure['method_ref']==selection['method_ref'] and procedure['design_ref']==selection['design_ref'],'research method/design differs')
    require(procedure['samples']==3 and procedure['order']==[['direct','facade'],['facade','direct'],['direct','facade']]
        and type(procedure['timeout_seconds']) is int and procedure['timeout_seconds']==45
        and procedure['ratio_threshold']==0.8 and procedure['residue_labels']==list(TRIAL_LABELS),'research predeclared procedure differs')
    require(byte_sha(ARCHIVE.read_bytes())==procedure['archive_sha256'],'selected signed archive differs')
    for row in procedure['source_bindings']:require(byte_sha((ROOT/row['path']).read_bytes())==row['sha256'],'research selected implementation bytes differ')
    design=records[selection['design_ref']];hypothesis=records[selection['hypothesis_ref']]
    require(design['protocol_ref']=='protocol:W04-pinned-replay-comparison' and design['design_state']=='ready','research design not ready')
    require(records[selection['inquiry_ref']]['method_ref']==selection['method_ref'],'Inquiry Method differs')
    require(hypothesis['payload']['disposition']=='open' and hypothesis['payload']['falsification_conditions'],'hypothesis must be open with falsifiers')
    context=design['product_evaluation_context'];require(context is not None and context['product_capability_refs']==[selection['capability_ref']]
        and context['product_ref']==selection['product_ref'],'research Product evaluation context differs')
    require(design['project_ref']==SCOPE and design['goal_refs']==[selection['goal_ref']],'research design Project/Goal differs')
    require(records[selection['work_ref']]['payload']['project_ref']==SCOPE,'research Work scope differs')
    # Product experiments may omit Research links. Every declared Inquiry must resolve exactly.
    require(all(r in records and kind(records[r])=='research-inquiry' for r in design['research_refs']),'declared Inquiry revision unresolved')
    return selection,records,procedure


def fixture(selection,records):
    sys.path.insert(0,str(PACKAGE/'examples/engineering'));from behavior import Fixture
    f=Fixture();f.by_kind['agent-assignment']['payload']['work_ref']=ident(records[selection['work_ref']])
    f.by_kind['delegation']['payload']['allowed_action_kinds']=['compare-signed-replay']
    f.by_kind['agent-profile']['payload']['tool_class_refs']=['tool-class:signed-replay-comparison']
    f.by_kind['agent-profile']['payload']['allowed_output_kinds']=sorted(OUTPUT_KINDS)
    f.by_kind['tool']['payload'].update(tool_name='signed-replay-comparison',interface_version=INTERFACE,
        input_contract_ref='protocol:W04-pinned-procedure-input',output_contract_ref='protocol:W04-original-comparison-receipts',
        failure_boundary_refs=['protocol:W04-indeterminate-no-redispatch'],evidence_route_ref='protocol:W04-comparison-journal')
    for k in ['agent-assignment','delegation','agent-profile','tool']:f.reselect(k)
    f.status['selected_work_ref']=ident(records[selection['work_ref']]);f.status['tool_classes'][f.ref('tool')]='tool-class:signed-replay-comparison'
    sha=byte_sha(Path(__file__).read_bytes());f.adapter_sha256=sha
    permission=encoded({'scope':'Explicit owned isolated W04 signed replay comparison and unadmitted evidence staging',
        'authorization_ref':'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json',
        'fixture_only':True,'actual_owner_outcome':None,'excluded_effects':['canonical admission','live stores','private signing keys']})
    f.grant=replace(f.grant,action_kinds=frozenset({'compare-signed-replay'}),max_actions=1,max_output_bytes=262144,adapter_sha256=sha,
        evidence_ref='protocol:W04-explicit-fixture-development-permission',evidence_original=permission,evidence_sha256=byte_sha(permission),recovery_allowed=False)
    f.request['action_kind']='compare-signed-replay'
    module=shared.load_registered(ENGINEERING_INPUTS/'registered_evaluator.py',read(ENGINEERING_INPUTS/'input-manifest.json')['output_source_sha256'])
    f.authority=module.HostAuthority(f.session,lambda r:f.records.get(r),lambda:copy.deepcopy(f.status),lambda:f.grant,
        adapter_sha256=sha,environment_sha256=f.environment_sha256,registered_interfaces=frozenset({INTERFACE}))
    return f


def entropy(labels):
    require(labels and all(v in TRIAL_LABELS for v in labels),'undeclared residue label')
    probabilities=[labels.count(v)/len(labels) for v in TRIAL_LABELS if v in labels]
    return -sum(p*math.log(p) for p in probabilities)


def evaluate(trials,procedure):
    require(len(trials)==procedure['samples'],'missing declared research samples')
    ratios=[];labels=[]
    for i,row in enumerate(trials):
        require(row['sample']==i+1 and row['order']==procedure['order'][i],'research sample/order differs')
        require(set(row['observations'])=={'direct','facade'},'missing replay observation')
        a,b=row['observations']['direct'],row['observations']['facade']
        for observation in [a,b]:
            require(observation['posture'] in ['completed','rejected','timeout'],'invalid observed replay posture')
            require(type(observation['seconds']) in [float,int] and math.isfinite(observation['seconds']) and observation['seconds']>=0,'invalid observed timing')
        label=('timeout' if any(v['posture']=='timeout' for v in [a,b]) else
            'rejected' if any(v['posture']=='rejected' for v in [a,b]) else
            'parity' if a['projection_sha256']==b['projection_sha256'] and a['head']==b['head'] else 'mismatch')
        labels.append(label)
        if label=='parity' and a['seconds']>0:ratios.append(b['seconds']/a['seconds'])
    if 'mismatch' in labels:disposition='negative';support='contradicted'
    elif len(ratios)!=procedure['samples']:disposition='inconclusive';support='indeterminate'
    elif all(r<=procedure['ratio_threshold'] for r in ratios):disposition='positive';support='supported'
    elif all(r>procedure['ratio_threshold'] for r in ratios):disposition='negative';support='not-supported'
    else:disposition='inconclusive';support='indeterminate'
    return {'authority_effect':'none','disposition':disposition,'support_state':support,'labels':labels,
        'ratios':ratios,'median_ratio':statistics.median(ratios) if ratios else None,'residue_entropy_nats':entropy(labels),
        'actual_owner_outcome':None,'claim_ceiling':'Only the three declared finite comparisons; no population inference, cache improvement, SLA or Product acceptance.'}


class ResearchWorkflow:
    def __init__(self,inputs,selection_sha,output):
        self.inputs=Path(inputs);self.selection_sha=selection_sha
        self.selection,self.records,self.procedure=resolve(inputs,selection_sha)
        self.output=Path(output);require(not self.output.exists(),'research output already exists');self.output.mkdir(mode=0o700)
        self.state='prepared';self.events=[];self.trials=None;self.assessment=None;self.receipt=None
        self.evidence_pin=None;self.journal=self.output/'journal.json';self.journal_pin=None
        self._authority=None;self._request=None

    def transition(self,expected,new,detail):
        require(self.state==expected,'research transition differs')
        self.events.append({'from':expected,'to':new,'detail':detail,'authority_effect':'none',
            'admission':'candidate-unadmitted','carrier_lifecycle':'candidate','outcome_satisfaction':None})
        self.state=new

    def current_inputs(self):
        s,r,p=resolve(self.inputs,self.selection_sha)
        require(p==self.procedure and r==self.records,'research inputs changed after selection')

    def current_authority(self):
        require(isinstance(self._authority,HostAuthority),'trusted research host authority required')
        evaluation=self._authority.check(self._request)
        require(evaluation['posture']=='permitted','current research authority denied')
        selected=self._authority.resolver(evaluation['request']['profile_ref'])
        require(isinstance(selected,shared.SelectedRecord),'selected research Profile unresolved')
        profile=selected.record('agent-profile')
        require(OUTPUT_KINDS<=set(profile['payload']['allowed_output_kinds']),'research Profile denies planned output kinds')
        return evaluation

    def design(self):
        self.current_inputs();s=self.selection;r=self.records
        # Check exact existing connections before executing any selected procedure.
        signatures=[('relation.tests-hypothesis',s['design_ref'],s['hypothesis_ref'],
            {'hypothesis_version_ref':s['hypothesis_ref'],'test_role':'bounded-replay-comparison'}),
            ('relation.evaluates',s['design_ref'],s['capability_ref'],
             {'evaluation_role':'candidate-replay-comparison','evaluation_purpose':'bounded-correctness-and-overhead'})]
        for i,args in enumerate(signatures):typed('preflight-'+str(i),*args[:3],r,args[3])
        planned=[('relation.realizes','experiment-run','experiment-design'),('relation.evaluates','experiment-run','product-capability'),
            ('relation.evaluates','evaluation','product-capability'),('relation.uses-method','experiment-run','method'),
            ('relation.uses-method','research-run','method'),('relation.uses-method','observation','method'),
            ('relation.uses-method','measurement-result','method'),('relation.derives-from','observation','experiment-run'),
            ('relation.derives-from','measurement-result','experiment-run'),('relation.derives-from','evidence-set','experiment-run'),
            ('relation.derives-from','finding','evidence-set'),('relation.engages-inquiry','finding','research-inquiry'),
            ('relation.engages-inquiry','research-run','research-inquiry'),('relation.member-of','experiment-run','project'),
            ('relation.realizes','implementation','product-capability'),('relation.produces','agent-action','generated-output'),
            ('relation.successor-of','work','work')]
        planned.append(('relation.evidence-bears-on','observation','hypothesis'))
        pairs=read(PAIRS)['exact_pairs']
        for signature in planned:
            matches=[p for p in pairs if (p['relation_kind_ref'],p['source_kind'],p['target_kind'])==signature]
            require(len(matches)==1,'planned research ordered pair undeclared')
            b=matches[0]['relation_binding'];require(byte_sha((ROOT/b['path']).read_bytes())==b['sha256'],'planned research Relation Kind drift')
        self.transition('prepared','designed',{'method_ref':s['method_ref'],'procedure_sha256':s['procedure']['sha256'],
            'design_ref':s['design_ref'],'samples':self.procedure['samples'],'ratio_threshold':self.procedure['ratio_threshold']})

    def execute(self,authority,request,original_input,*,interrupt_after_observations=False):
        require(self.state=='designed','research design required before execution');self.current_inputs()
        require(isinstance(authority,HostAuthority),'trusted research host authority required')
        self._authority=authority;self._request=request;evaluation=self.current_authority()
        contract=evaluation['tool_contract'];grant=evaluation['grant']
        require(contract['interface_version']==INTERFACE and contract['input_contract_ref']=='protocol:W04-pinned-procedure-input'
            and contract['output_contract_ref']=='protocol:W04-original-comparison-receipts'
            and contract['failure_boundary_refs']==['protocol:W04-indeterminate-no-redispatch']
            and contract['evidence_route_ref']=='protocol:W04-comparison-journal','selected research Tool contract differs')
        require(grant.adapter_sha256==byte_sha(Path(__file__).read_bytes()),'research adapter bytes differ')
        require(grant.max_actions>=1 and len(original_input)<=grant.max_input_bytes,'research action/input budget exceeded')
        require(byte_sha(original_input)==evaluation['request']['input_sha256'],'research Tool input binding differs')
        require(parse(original_input)=={'selection_sha256':self.selection_sha,'procedure_sha256':self.selection['procedure']['sha256']},'closed selected research input differs')
        require(not self.journal.exists(),'research journal already exists; no redispatch')
        atomic(self.journal,{'authority_effect':'none','posture':'pending','request_sha256':byte_sha(request),
            'input_sha256':byte_sha(original_input),'evaluation':public_evaluation(evaluation),
            'procedure_sha256':self.selection['procedure']['sha256'],'retry_allowed':False})
        self.journal_pin=byte_sha(self.journal.read_bytes());self.started_at=now();trials=[]
        try:
            for i,order in enumerate(self.procedure['order']):
                row={'sample':i+1,'order':order,'observations':{}}
                for approach in order:
                    self.current_authority()
                    self.current_inputs()
                    start=time.perf_counter()
                    try:
                        with tempfile.TemporaryDirectory(prefix='lab-W04-owned-child-') as owned:
                            command=[sys.executable,str(EXAMPLE/'replay_child.py'),approach,self.procedure['archive_sha256'],owned]
                            child=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=self.procedure['timeout_seconds'])
                        seconds=time.perf_counter()-start
                        observation={'posture':'completed' if child.returncode==0 else 'rejected','seconds':seconds,
                            'returncode':child.returncode,'stdout_sha256':byte_sha(child.stdout),'stderr_sha256':byte_sha(child.stderr)}
                        if child.returncode==0:
                            actual=parse(child.stdout);require(actual['approach']==approach and actual['archive_sha256']==self.procedure['archive_sha256'],'unselected replay child result')
                            require(set(actual)=={'authority_effect','approach','archive_sha256','projection_sha256','head','actual_owner_outcome','cache_enabled','owned_store_removed_on_return'}
                                and actual['authority_effect']=='none' and actual['actual_owner_outcome'] is None
                                and actual['cache_enabled'] is False and actual['owned_store_removed_on_return'] is True,'replay child contract differs')
                            require(actual['head']==read(ARCHIVE)['project_pins']['expected_head']
                                and type(actual['projection_sha256']) is str and len(actual['projection_sha256'])==64
                                and all(v in '0123456789abcdef' for v in actual['projection_sha256']),'replay child exact cut/digest differs')
                            observation.update(projection_sha256=actual['projection_sha256'],head=actual['head'])
                        (self.output/f'sample-{i+1}-{approach}.stdout').write_bytes(child.stdout)
                        (self.output/f'sample-{i+1}-{approach}.stderr').write_bytes(child.stderr)
                    except subprocess.TimeoutExpired as exc:
                        seconds=time.perf_counter()-start
                        stdout=exc.stdout or b'';stderr=exc.stderr or b''
                        (self.output/f'sample-{i+1}-{approach}.stdout').write_bytes(stdout)
                        (self.output/f'sample-{i+1}-{approach}.stderr').write_bytes(stderr)
                        observation={'posture':'timeout','seconds':seconds,'returncode':None,'stdout_sha256':byte_sha(stdout),'stderr_sha256':byte_sha(stderr)}
                    row['observations'][approach]=observation
                trials.append(row)
                (self.output/f'sample-{i+1}.json').write_bytes(encoded(row))
            self.trials=trials;self.ended_at=now()
            evidence={'authority_effect':'none','selection_sha256':self.selection_sha,'procedure_sha256':self.selection['procedure']['sha256'],
                'archive_sha256':self.procedure['archive_sha256'],'trials':trials,'actual_owner_outcome':None}
            raw=encoded(evidence);require(len(raw)<=grant.max_output_bytes,'research Tool output budget exceeded')
            (self.output/'observed.json').write_bytes(raw);self.evidence_pin=byte_sha(raw)
            if interrupt_after_observations:
                self.transition('designed','indeterminate',{'retry_allowed':False,'reconciliation_required':True});return {'posture':'indeterminate','retry_allowed':False}
            self.receipt={'authority_effect':'none','posture':'completed','request_sha256':byte_sha(request),
                'evaluation':public_evaluation(evaluation),'evidence_sha256':self.evidence_pin,'actual_owner_outcome':None,'retry_allowed':False}
            atomic(self.journal,self.receipt);self.journal_pin=byte_sha(self.journal.read_bytes())
            self.transition('designed','executed',{'execution':'completed','hypothesis_support':None,'evidence_sha256':self.evidence_pin})
            return self.receipt
        except Exception as exc:
            self.transition('designed','indeterminate',{'error':str(exc),'retry_allowed':False,'reconciliation_required':True})
            return {'posture':'indeterminate','retry_allowed':False,'reconciliation_required':True}

    def assess(self):
        require(self.state=='executed','research observations required before assessment');self.current_inputs()
        self.current_authority()
        require(byte_sha(self.journal.read_bytes())==self.journal_pin,'research action journal bytes differ')
        raw=(self.output/'observed.json').read_bytes();require(byte_sha(raw)==self.evidence_pin,'research observed bytes changed')
        evidence=parse(raw);require(evidence['trials']==self.trials and evidence['procedure_sha256']==self.selection['procedure']['sha256'],'research observation method differs')
        for row in self.trials:
            require(read(self.output/f'sample-{row["sample"]}.json')==row,'research sample evidence changed')
            for approach,observation in row['observations'].items():
                for channel in ['stdout','stderr']:
                    raw=(self.output/f'sample-{row["sample"]}-{approach}.{channel}').read_bytes()
                    require(byte_sha(raw)==observation[channel+'_sha256'],'research original process evidence changed')
        self.assessment=evaluate(self.trials,self.procedure)
        self.transition('executed','evaluated',{'hypothesis_disposition':self.assessment['disposition'],'actual_owner_outcome':None})
        (self.output/'assessment.json').write_bytes(encoded(self.assessment));return self.assessment

    def materialize(self):
        require(self.state=='evaluated','research assessment required before review');self.current_inputs()
        permission=self.current_authority()
        require(not (self.output/'review-effects.json').exists(),'research review output already exists')
        require(byte_sha((self.output/'observed.json').read_bytes())==self.evidence_pin,'research original evidence drift before review')
        require(self.assessment==evaluate(self.trials,self.procedure) and read(self.output/'assessment.json')==self.assessment,'research assessment altered after evaluation')
        s=self.selection;r=copy.deepcopy(self.records);assessment=self.assessment;timestamp=self.ended_at
        evidence=template('evidence-set','replay-comparison');evidence['name']='Candidate replay comparison evidence'
        evidence['payload']={'source_refs':[s['method_ref'],s['design_ref'],'protocol:C12-original-signed-archive:'+self.procedure['archive_sha256']],
            'item_refs':['protocol:W04-original-observations:'+self.evidence_pin],
            'coverage_statement':'All three declared paired comparisons, including every timeout/rejection/mismatch and original subprocess outputs.',
            'limitations':['Three paired observations on one archived signed branch','No CPU isolation or population inference','No cache enabled','No owner outcome']}
        evidence['relation_refs']=[{'relation_kind_ref':'relation.derives-from','direction':'source','counterpart_kind':'experiment-run','counterpart_ref':'experiment-run:lab-W09:bc3c50170a404b4ba8d8:research:replay-comparison'}]
        validate(evidence,'evidence-set');r[ref(evidence)]=evidence
        experiment=template('experiment-run','replay-comparison');design=r[s['design_ref']]
        experiment.update(design_ref=ident(design),design_version_ref=s['design_ref'],project_ref=SCOPE,goal_refs=design['goal_refs'],
            research_refs=design['research_refs'],product_evaluation_context=copy.deepcopy(design['product_evaluation_context']),
            environment='Python '+sys.version.split()[0]+'; local bounded archived candidate branch',
            input_refs=[s['method_ref'],'protocol:C12-original-signed-archive:'+self.procedure['archive_sha256']],
            interventions=['direct full_replay versus read-only facade replay, both uncached'],deviations=[],
            observation_refs=['observation:lab-W09:bc3c50170a404b4ba8d8:research:replay-comparison@candidate.1'],measurement_result_refs=['measurement-result:lab-W09:bc3c50170a404b4ba8d8:research:verification-residue@candidate.1'],
            evidence_set_ref=ref(evidence),run_state='completed',stop_reason=None,period={'start':self.started_at,'end':timestamp})
        validate(experiment,'experiment-run');r[ref(experiment)]=experiment
        research_run=template('research-run','replay-comparison')
        research_run.update(inquiry_ref=ident(r[s['inquiry_ref']]),inquiry_version_ref=s['inquiry_ref'],project_ref=SCOPE,
            goal_refs=design['goal_refs'],inspected_sources=[{'source_ref':b['path'],'observed_sha256':b['sha256'],'selector':'whole-file'} for b in self.procedure['source_bindings']],
            method_performed={'method_ref':s['method_ref'],'procedure_summary':'Inspect exact uncached direct/facade sources and execute the declared finite signed archive comparisons.','deviation_refs':[]},
            observation_refs=experiment['observation_refs'],counterevidence_refs=['protocol:W04-all-original-negative-or-inconclusive-rows:'+self.evidence_pin],
            evidence_set_ref=ref(evidence),run_state='completed',stop_reason=None,receipt_ref='protocol:W04-original-action-receipt',
            period={'start':self.started_at,'end':timestamp},limitations=['Selected source inspection and three paired runs only','No evidence of cache or population performance improvement'])
        validate(research_run,'research-run');r[ref(research_run)]=research_run
        observation=template('observation','replay-comparison')
        observation.update(run_ref=ref(experiment),subject_ref=s['capability_ref'],
            statement='Observed verification labels '+str(assessment['labels'])+' and facade/direct timing ratios '+str(assessment['ratios'])+'.',
            method_ref=s['method_ref'],conditions=['One fixed archived signed branch','AB/BA/AB paired order','Both paths fully replay; fresh child namespace per call'],
            observed_at=timestamp,observer_ref=self.receipt['evaluation']['request']['instance_record_ref'],
            provenance_refs=['protocol:W04-original-observations:'+self.evidence_pin,s['procedure']['sha256']],
            uncertainty='Three shared-host samples; subprocess/module staging included; OS caches, load and scheduling not controlled; no population uncertainty estimate.',
            evidence_ref=ref(evidence),limitations=['Raw timing seconds are protocol evidence and are not residue entropy','Finite observations do not establish a Product SLA'])
        validate(observation,'observation');r[ref(observation)]=observation
        measurement=template('measurement-result','verification-residue')
        measurement.update(method_ref=s['measurement_method_ref'],subject_ref=ref(experiment),
            residue_ref='protocol:W04-declared-verification-residue-labels',source_operation_ref='protocol:W04-replay-comparison',
            entropy_register='finite-probabilistic',observable_kind='shannon-entropy',scope_kind='probabilistic',
            mathematical_reading='H(R) = -sum p(label)*ln p(label) over the three observed parity/mismatch/rejected/timeout residue labels; not timing entropy.',
            value=assessment['residue_entropy_nats'],unit='nats',uncertainty={'value':0,'interpretation':'Exact calculation over this finite observed label multiset; no population uncertainty estimated.'},
            claim_status='review',authority_treatment='non-governing',observed_at=timestamp,evidence_ref=ref(evidence),receipt_ref='protocol:W04-original-observations:'+self.evidence_pin)
        validate(measurement,'measurement-result');r[ref(measurement)]=measurement
        finding=template('finding','replay-comparison')
        finding.update(inquiry_ref=ident(r[s['inquiry_ref']]),question=r[s['inquiry_ref']]['question'],research_run_refs=[ref(research_run)],
            statement='The predeclared finite replay comparison is '+assessment['disposition']+' for the 0.8 facade/direct threshold with exact verification parity.',
            evidence_set_refs=[ref(evidence)],evidence_refs=[ref(observation),ref(measurement)],
            counterevidence_refs=['protocol:W04-all-original-sample-rows:'+self.evidence_pin],
            support_assessment={'support_state':assessment['support_state'],'rationale':assessment['claim_ceiling']},
            finding_state='draft',created_at=timestamp,last_updated_at=timestamp,successor_refs=[],revision_history=[],
            limitations=['Both selected paths use the same uncached independent full verifier','Timing observations cannot establish algorithmic reuse or general Product benefit','Negative and inconclusive rows remain in original evidence'])
        validate(finding,'finding');r[ref(finding)]=finding
        evaluation=template('evaluation','replay-comparison');evaluation['name']='Candidate bounded replay capability evaluation'
        evaluation['payload']={'profile_ref':'protocol:W04-pinned-replay-comparison:'+s['procedure']['sha256'],
            'subject_ref':s['capability_ref'],'input_state_ref':'sha256:'+self.evidence_pin,
            'outcomes':[{'check_id':'finite-replay-hypothesis','result':assessment['disposition'],'evidence_refs':[ref(finding),ref(evidence)],
                'blocker_ref':'none' if assessment['disposition']=='positive' else 'protocol:W04-hypothesis-not-confirmed'}]}
        evaluation['relation_refs']=[{'relation_kind_ref':'relation.evaluates','direction':'source','counterpart_kind':'product-capability','counterpart_ref':CAPABILITY}]
        validate(evaluation,'evaluation');r[ref(evaluation)]=evaluation
        implementation=shared.artifact('implementation','replay-comparison',{
            'implementation_kind':'bounded-local-research-and-experiment-adapter',
            'conforms_to_schema_refs':['protocol:W04-pinned-procedure-input','protocol:W04-original-comparison-receipts'],
            'realizes_capability_refs':[s['capability_ref']],
            'execution_entrypoint_ref':'protocol:W04-ResearchWorkflow:'+byte_sha(Path(__file__).read_bytes()),
            'environment_contract_ref':'protocol:W04-closed-local-Python-subprocesses'},
            [{'relation_kind_ref':'relation.realizes','direction':'source','counterpart_kind':'product-capability','counterpart_ref':CAPABILITY}])
        implementation['node_id']='implementation:lab-W09:bc3c50170a404b4ba8d8:research:replay-comparison';validate(implementation,'implementation');r[ref(implementation)]=implementation
        request=self.receipt['evaluation']['request']
        action=shared.artifact('agent-action','replay-comparison',{
            'agent_instance_ref':request['instance_record_ref'],'session_ref':request['session_record_ref'],'assignment_ref':request['assignment_ref'],
            'action_kind':request['action_kind'],'posture':'completed','input_refs':[s['design_ref'],s['method_ref']],
            'output_refs':['generated-output:lab-W09:bc3c50170a404b4ba8d8:research:original-comparison-bytes@candidate.1'],
            'tool_refs':[request['tool_ref']],'implementation_refs':[ref(implementation)],
            'authority_evidence_refs':[b['ref'] for b in self.receipt['evaluation']['evidence_bindings']],
            'receipt_refs':['protocol:W04-original-action-receipt'],'residue_refs':['protocol:deferred-owner-decision:R08']},
            [{'relation_kind_ref':'relation.uses-tool','direction':'source','counterpart_kind':'tool','counterpart_ref':request['tool_ref']}])
        action.update(node_id='agent-action:lab-W09:bc3c50170a404b4ba8d8:research:replay-comparison',owner_ref=request['principal_ref']);validate(action,'agent-action');r[ref(action)]=action
        output=shared.artifact('generated-output','original-comparison-bytes',{
            'generator_ref':ref(implementation),'input_refs':[s['method_ref'],s['design_ref']],
            'output_digest':'sha256:'+self.evidence_pin,'reproducibility_receipt_ref':'protocol:W04-original-action-receipt'},
            [{'relation_kind_ref':'relation.produces','direction':'target','counterpart_kind':'agent-action','counterpart_ref':ident(action)}])
        output['node_id']='generated-output:lab-W09:bc3c50170a404b4ba8d8:research:original-comparison-bytes';validate(output,'generated-output');r[ref(output)]=output
        work=copy.deepcopy(r[s['work_ref']]);work['payload']['completion_state']='candidate-evaluated'
        work['payload']['output_refs']=[ref(v) for v in [experiment,research_run,observation,measurement,evidence,finding,evaluation,implementation,action,output]]
        work['evidence_refs']=[ref(evidence)];work_ref=ident(work)+'@evaluated-candidate.1';validate(work,'work');r[work_ref]=work
        relations=[]
        def add(name,k,a,b,q):relations.append(typed(name,k,a,b,r,q))
        add('design-hypothesis','relation.tests-hypothesis',s['design_ref'],s['hypothesis_ref'],{'hypothesis_version_ref':s['hypothesis_ref'],'test_role':'bounded-replay-comparison'})
        for a in [s['design_ref'],ref(experiment),ref(evaluation)]:
            add('capability-evaluation-'+str(len(relations)),'relation.evaluates',a,s['capability_ref'],{'evaluation_role':'candidate-replay-comparison','evaluation_purpose':'bounded-correctness-and-overhead'})
        add('run-design-realization','relation.realizes',ref(experiment),s['design_ref'],{'realization_role':'exact-predeclared-procedure-execution','exact_target_version_ref':s['design_ref']})
        for a in [ref(experiment),ref(research_run),ref(observation),ref(measurement)]:add('method-usage-'+str(len(relations)),'relation.uses-method',a,s['method_ref'],{'usage_role':'exact-declared-replay-comparison-procedure'})
        for a in [ref(observation),ref(measurement)]:
            add('run-derivation-'+str(len(relations)),'relation.derives-from',a,ref(experiment),{'derivation_role':'original-comparison-observation'})
        add('evidence-run-derivation','relation.derives-from',ref(evidence),ref(experiment),{'derivation_role':'complete-original-comparison-evidence'})
        add('finding-evidence-derivation','relation.derives-from',ref(finding),ref(evidence),{'derivation_role':'independent-predeclared-threshold-assessment'})
        add('finding-inquiry','relation.engages-inquiry',ref(finding),s['inquiry_ref'],{'inquiry_role':'bounded-finite-comparison-result'})
        add('research-run-inquiry','relation.engages-inquiry',ref(research_run),s['inquiry_ref'],{'inquiry_role':'source-inspection-and-declared-procedure'})
        add('observation-hypothesis-evidence','relation.evidence-bears-on',ref(observation),s['hypothesis_ref'],{'polarity':assessment['disposition']})
        for a in design['research_refs']:
            add('design-inquiry-'+str(len(relations)),'relation.engages-inquiry',s['design_ref'],a,{'inquiry_role':'declared-experiment-question'})
            add('run-inquiry-'+str(len(relations)),'relation.engages-inquiry',ref(experiment),a,{'inquiry_role':'declared-experiment-question'})
        add('experiment-project','relation.member-of',ref(experiment),s['project_ref'],{'membership_role':'bounded-candidate-replay-experiment'})
        add('research-adapter-realization','relation.realizes',ref(implementation),s['capability_ref'],{'realization_role':'bounded-candidate-research-evidence-subset','exact_target_version_ref':s['capability_ref']})
        add('research-action-production','relation.produces',ref(action),ref(output),{'action_receipt_ref':'protocol:W04-original-action-receipt','production_role':'original-finite-comparison-bytes','output_posture':'candidate-unadmitted'})
        add('research-work-succession','relation.successor-of',work_ref,s['work_ref'],{'succession_effect':'candidate-exact-research-evidence-and-evaluation-recording'})
        candidates={'experiment-run':experiment,'research-run':research_run,'observation':observation,'measurement-result':measurement,
            'evidence-set':evidence,'finding':finding,'evaluation':evaluation,'implementation':implementation,'agent-action':action,'generated-output':output,'work':work}
        require(sum(len(encoded(v)) for v in list(candidates.values())+relations)<=permission['grant'].max_output_bytes,'candidate research output budget exceeded')
        for name,value in candidates.items():(self.output/(name+'.json')).write_bytes(encoded(value))
        for value in relations:(self.output/(ident(value).split(':')[-1]+'.json')).write_bytes(encoded(value))
        review={'authority_effect':'none','actual_owner_outcome':None,'canonical_effects_applied':0,
            'hypothesis_disposition':assessment['disposition'],'process_completed':True,
            'selected_candidate_members':[{'kind':kind(v),'identity_ref':ident(v),'version_ref':work_ref if v is work else ref(v),'sha256':byte_sha(encoded(v))}
                for v in list(candidates.values())+relations],
            'input_dependencies':[{'version_ref':row['version_ref'],'sha256':row['sha256'],'posture':'selected-source-or-isolated-candidate; resolve independently for admission'} for row in s['records']],
            'method_type_admission':'separate-S01/C10/R08-member; candidate Method schema grants no type admission',
            'exclusions':['private Session notes','automatic hypothesis confirmation','canonical admission','Product acceptance','cache improvement']}
        (self.output/'review-effects.json').write_bytes(encoded(review));(self.output/'transitions.json').write_bytes(encoded(self.events))
        return {'candidates':candidates,'relations':relations,'review':review,'assessment':assessment,'receipt':self.receipt}
