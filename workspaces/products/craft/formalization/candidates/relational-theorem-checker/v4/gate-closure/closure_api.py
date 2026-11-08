"""Source-bound original gate reviews and append-only candidate completion log.

The local operator must capture an observed human response. JSON labels are not
authentication. Filesystem ownership, SHA256, Python and cooperating locks are
explicit assumptions; this is not an authority/admission service.
"""
from pathlib import Path
import contextlib
import copy
import fcntl
import hashlib
import json
import os
import re
import uuid
from jsonschema import Draft202012Validator,ValidationError

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'docs/plans/relational-theorem-checker/PLAN-SOURCE.json').is_file())
SCOPE = json.loads((HERE/'scope-manifest.json').read_text())
ROLES = {'R06': ['packet','matrix','pilot','audit'], 'G4':['packet','matrix','alignment','recommendation']}
ANSWERS = {'R06':['meanings','diagnostics'], 'G4':['layers','bounded_use']}
CORE = ['closure_api.py','audit_evidence.py','GateClosure.lean','closure-contract.md','scope-manifest.json',
        'record_feedback.py','accept_r06.py','accept_g4.py','resolve_gate_status.py',
        'human-gate-review.schema.json','gate-status-overlay.schema.json','gate-acceptance.schema.json',
        'review-manifest.schema.json','execution/h00/formal-evidence.json','execution/h00/build/GateClosure.olean']

def require(condition, message):
    if not condition:
        raise ValueError(message)

def decode(raw):
    require(isinstance(raw,bytes) and len(raw)<=64*1024*1024, 'JSON input size')
    def pairs(items):
        result={}
        for key,value in items:
            require(key not in result, 'duplicate JSON field '+key)
            result[key]=value
        return result
    def nonfinite(value):
        raise ValueError('nonfinite JSON number '+value)
    value=json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=nonfinite)
    def depth(x,d=0):
        require(d<=64,'JSON depth ceiling')
        if isinstance(x,dict):
            for child in x.values():depth(child,d+1)
        elif isinstance(x,list):
            for child in x:depth(child,d+1)
    depth(value)
    return value

def read(path):
    return decode(Path(path).read_bytes())

def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()

def identity(value):
    return hashlib.sha256(encoded(value)).hexdigest()

def binding(path):
    path=Path(path).resolve()
    require(path.is_relative_to(ROOT), 'outside repository binding')
    return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def check(ref):
    require(isinstance(ref,dict) and set(ref)=={'path','sha256'}, 'binding fields')
    require(isinstance(ref['path'],str) and isinstance(ref['sha256'],str), 'binding field types')
    rel=Path(ref['path'])
    require(not rel.is_absolute() and '..' not in rel.parts and '\\' not in ref['path'], 'unsafe binding path')
    require(re.fullmatch('[0-9a-f]{64}',ref['sha256']) is not None,'binding digest')
    path=(ROOT/rel).resolve()
    require(path.is_relative_to(ROOT) and path.is_file(),'missing binding '+ref['path'])
    before=path.stat()
    require(binding(path)==ref,'stale binding '+ref['path'])
    after=path.stat()
    require((before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns),'binding changed during read')
    return path

def schema(name,value):
    try:Draft202012Validator(read(HERE/name)).validate(value)
    except ValidationError as error:
        raise ValueError('invalid '+name+': '+error.message[:400]) from error

def durable(path,raw):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as file:
        file.write(raw);file.flush();os.fsync(file.fileno())
    fsync_dir(path.parent)

def fsync_dir(path):
    fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)

def current_sources(refs):
    # Hash each expected identity once; retain stat checks across the read.
    cache={}
    for ref in refs:
        key=(ref['path'],ref['sha256'])
        if key not in cache:
            path=check(ref);st=path.stat();cache[key]=(path,(st.st_ino,st.st_size,st.st_mtime_ns))
    for path,stamp in cache.values():
        st=path.stat();require((st.st_ino,st.st_size,st.st_mtime_ns)==stamp,'source changed during audit')

def implementation_bindings():
    return [binding(HERE/name) for name in CORE]

class Conflict(ValueError):
    pass

class Ledger:
    def __init__(self,directory=None,*,fixture=False,challenges=None):
        self.directory=Path(directory or HERE/'state').resolve();self.fixture=fixture
        allowed=HERE/'execution' if fixture else HERE/'state'
        require(self.directory.is_relative_to(allowed), 'closure log ownership')
        require(challenges is None or fixture,'actual challenges are independently anchored')
        self.fixture_challenges=challenges
        self.directory.mkdir(parents=True,exist_ok=True)

    @contextlib.contextmanager
    def lock(self):
        with (self.directory/'cooperating.lock').open('a+b') as file:
            fcntl.flock(file,fcntl.LOCK_EX)
            try:yield
            finally:fcntl.flock(file,fcntl.LOCK_UN)

    def base(self):
        return read(check(SCOPE['base_plan']))

    def challenge(self,gate):
        require(gate in ROLES,'unknown gate')
        if self.fixture:
            return copy.deepcopy(self.fixture_challenges[gate])
        anchor=HERE/'review-challenges.json'
        accepted=read(HERE/'execution/h03/task-acceptance.json')
        require(accepted['task']=='H03' and accepted['result']=='accepted','review packet not frozen/accepted')
        expected=next(r for r in accepted['artifacts'] if r['path']==str(anchor.relative_to(ROOT)))
        check(expected)
        return read(anchor)[gate]

    def manifest(self,gate,*,sources=True):
        ref=self.challenge(gate);value=read(check(ref));schema('review-manifest.schema.json',value)
        require(value['gate']==gate and value['scope']==SCOPE['scope_ids'][gate],'manifest gate/scope')
        require(value['base_plan']==SCOPE['base_plan'],'manifest base-plan substitution')
        require(list(sorted(value['artifacts']))==sorted(ROLES[gate]),'mandatory artifact inventory')
        require(len({r['path'] for r in value['artifacts'].values()})==len(ROLES[gate]),'duplicate review artifact paths')
        current_sources(value['artifacts'].values())
        require(value['implementation_bindings']==implementation_bindings(),'gate implementation changed')
        current_sources(value['implementation_bindings'])
        audit=read(check(value['source_audit']))
        require(audit['schema']=='relational.closure-predecessor-audit/v4' and audit['result']=='pass','source audit incomplete')
        require(audit['original_counts']=={'tasks':35,'working_units':40,'edges':56,'accepted':33},'base inventory mismatch')
        require(audit['successor_units']==19 and audit['extension_final_witnesses']==19,'successor coverage incomplete')
        if sources:current_sources(audit['source_bindings'])
        return ref,value,audit

    def validate_feedback(self,feedback,*,sources=True):
        schema('human-gate-review.schema.json',feedback)
        gate=feedback['gate'];ref,manifest,audit=self.manifest(gate,sources=sources)
        require(feedback['review_manifest']==ref,'review-manifest substitution')
        require(feedback['reviewed_artifacts']==manifest['artifacts'],'mandatory reviewed identities missing/substituted')
        require(feedback['scope']==manifest['scope'],'feedback scope mismatch')
        require(feedback['capture_kind']==('fixture' if self.fixture else 'actual'),'fixture feedback cannot enter actual closure')
        return manifest,audit

    def record_feedback(self,raw,*,observed_direct_response=False):
        require(observed_direct_response,'operator must observe the direct response before capture')
        require(len(raw)<=4194304,'feedback input size')
        feedback=decode(raw);self.validate_feedback(feedback)
        path=self.directory/'feedback'/(identity(feedback)+'.json')
        with self.lock():
            if path.exists():require(read(path)==feedback,'feedback identity conflict')
            else:durable(path,encoded(feedback))
        return binding(path)

    def verify_receipt(self,gate,receipt,*,sources=True):
        schema('gate-acceptance.schema.json',receipt)
        require(receipt['task_id']==gate and receipt['base_plan']==SCOPE['base_plan'],'receipt gate/base mismatch')
        feedback=read(check(receipt['human_feedback']));manifest,audit=self.validate_feedback(feedback,sources=sources)
        require(receipt['review_manifest']==feedback['review_manifest'],'receipt review-manifest mismatch')
        task=next(t for t in self.base()['tasks'] if t['id']==gate)
        require(receipt['validation_id']==task['validation']['id'],'original validation identity')
        require([x['criterion'] for x in receipt['criteria']]==task['acceptance_criteria'],'original criteria changed/missing')
        require([x['criterion'] for x in receipt['failure_controls']]==task['failure_controls'],'original failure controls changed/missing')
        require(set(receipt['artifacts'])==set(task['outputs']),'original deliverable inventory')
        require(receipt['source_bindings']==[manifest['source_audit'],*audit['source_bindings']],'source inventory missing/substituted')
        require(receipt['implementation_bindings']==manifest['implementation_bindings'],'receipt implementation mismatch')
        require(all(feedback['answers'][name]=='accepted' for name in ANSWERS[gate]),'human assessment requires revisions or is undecided')
        for group in ['criteria','failure_controls']:
            for row in receipt[group]:
                require(row['evidence']==[receipt['review_manifest'],receipt['human_feedback'],*[receipt['artifacts'][k] for k in sorted(receipt['artifacts'])]], 'criterion evidence incomplete/substituted')
        for ref in receipt['artifacts'].values():
            path=check(ref)
            allowed=self.directory if self.fixture else ROOT/SCOPE['r06_output_root' if gate=='R06' else 'g4_output_root']
            require(path.is_relative_to(allowed),'gate output outside original write boundary')
        self.verify_outputs(gate,receipt,feedback,manifest)

    def verify_outputs(self,gate,receipt,feedback,manifest):
        artifacts=receipt['artifacts']
        if gate=='R06':
            pilot=read(check(artifacts['shadow-pilot-report.json']))
            require(pilot==read(check(manifest['artifacts']['pilot'])),'pilot output differs from reviewed pilot')
            matrix=read(check(artifacts['supported-use-matrix.json']))
            original=read(check(manifest['artifacts']['matrix']))
            require(matrix=={**original,'human_use_recommendation':'pending G4; R06 meaning/diagnostics accepted','human_r06_feedback':receipt['human_feedback']},'matrix feedback/status mismatch')
            text=check(artifacts['reviewer-feedback.md']).read_text()
            require(text==feedback_text(feedback),'readable feedback differs from captured response')
        else:
            alignment=read(check(artifacts['alignment-and-layering-audit.json']))
            reviewed=read(check(manifest['artifacts']['alignment']))
            require(alignment=={**reviewed,'r06_acceptance':self.r06_receipt_reference(),'g4_human_feedback':receipt['human_feedback'],'result':'accepted-original-layer-alignment'},'layer alignment receipt mismatch')
            recommendation=check(artifacts['bounded-use-recommendation.md']).read_text()
            require(recommendation==check(manifest['artifacts']['recommendation']).read_text(),'recommendation differs from reviewed recommendation')
            review=read(check(artifacts['l4-review.json']))
            expected={'schema':'relational.l4-review/v4','result':'reviewed-for-bounded-candidate-use', 'human_review':receipt['human_feedback'], 'review_manifest':receipt['review_manifest'],'r06_acceptance':self.r06_receipt_reference(),'alignment_audit':artifacts['alignment-and-layering-audit.json'],'authority_effect':'none','application_authorized':False}
            require(review==expected,'G4 review mismatch')

    def entry_paths(self):
        folder=self.directory/'entries'
        if not folder.exists():return []
        paths=sorted(folder.iterdir())
        require(all(p.is_file() and re.fullmatch(r'[0-9]{4}\.json',p.name) for p in paths),'unrecognized log entry')
        return paths

    def r06_receipt_reference(self):
        paths=self.entry_paths();require(paths,'accepted R06 missing')
        return read(paths[0])['receipt']

    def resolve(self,*,sources=True):
        base=self.base();tasks=copy.deepcopy(base['tasks']);previous=None;accepted=[]
        for generation,path in enumerate(self.entry_paths(),1):
            entry=read(path);schema('gate-status-overlay.schema.json',entry)
            require(entry['generation']==generation and path.name==f'{generation:04}.json','log generation gap')
            require(entry['previous']==previous and entry['base_plan']==SCOPE['base_plan'],'log predecessor/base mismatch')
            expected='R06' if generation==1 else 'G4'
            require(generation<=2 and entry['gate']==expected,'gate ordering/duplicate')
            receipt=read(check(entry['receipt']));self.verify_receipt(expected,receipt,sources=sources)
            task=next(t for t in tasks if t['id']==expected)
            require(task['status']=='not-started','original gate baseline changed')
            require(all(next(t for t in tasks if t['id']==dep)['status']=='accepted' for dep in task['depends_on']),'gate prerequisite incomplete')
            task['status']='accepted';task['validation']={**task['validation'],'acceptance_ref':entry['receipt'],'execution_status':'accepted-overlay'}
            for unit in task['working_units']:unit['status']='accepted'
            previous=binding(path);accepted.append(expected)
        return {'schema':'relational.current-original-task-view/v4','base_plan':SCOPE['base_plan'],
                'overlay_head':previous,'overlay_accepted':accepted,'generation':len(accepted),
                'counts':{'tasks':len(tasks),'working_units':sum(len(t['working_units']) for t in tasks),
                          'edges':sum(len(t['depends_on']) for t in tasks),'accepted':sum(t['status']=='accepted' for t in tasks)},
                'tasks':tasks,'historical_base_accepted':33,'fresh_event':False,'authority_effect':'none','application_authorized':False}

    def recover(self):
        with self.lock():
            view=self.resolve();target=self.directory/'current-original-task-view.json'
            temp=self.directory/('view-'+uuid.uuid4().hex+'.tmp')
            durable(temp,encoded(view));os.replace(temp,target);fsync_dir(self.directory)
            return view

    def accept(self,gate,feedback_ref,*,expected_head,crash_at=None):
        require(crash_at is None or self.fixture,'crash controls only in isolated fixtures')
        with self.lock():
            current=self.resolve()
            if current['overlay_head']!=expected_head:raise Conflict('closure head changed; reread the checked current view')
            require(gate==('R06' if current['generation']==0 else 'G4') and current['generation']<2,'gate prerequisite/order or duplicate acceptance')
            feedback=read(check(feedback_ref));manifest,audit=self.validate_feedback(feedback)
            require(feedback['gate']==gate,'feedback for another gate')
            require(all(feedback['answers'][name]=='accepted' for name in ANSWERS[gate]),'human assessment requires revisions or is undecided')
            parent=self.directory/'preparations' if self.fixture else ROOT/SCOPE['r06_output_root' if gate=='R06' else 'g4_output_root']
            folder=parent/('accepted-'+uuid.uuid4().hex);folder.mkdir(parents=True,exist_ok=False)
            artifact_values={}
            if gate=='R06':
                artifact_values={'shadow-pilot-report.json':encoded(read(check(manifest['artifacts']['pilot']))),
                    'supported-use-matrix.json':encoded({**read(check(manifest['artifacts']['matrix'])),'human_use_recommendation':'pending G4; R06 meaning/diagnostics accepted','human_r06_feedback':feedback_ref}),
                    'reviewer-feedback.md':feedback_text(feedback).encode()}
            else:
                artifact_values={'alignment-and-layering-audit.json':encoded({**read(check(manifest['artifacts']['alignment'])),'r06_acceptance':self.r06_receipt_reference(),'g4_human_feedback':feedback_ref,'result':'accepted-original-layer-alignment'}),
                    'bounded-use-recommendation.md':check(manifest['artifacts']['recommendation']).read_bytes()}
            for name,raw in artifact_values.items():durable(folder/name,raw)
            artifacts={name:binding(folder/name) for name in artifact_values}
            if gate=='G4':
                review={'schema':'relational.l4-review/v4','result':'reviewed-for-bounded-candidate-use','human_review':feedback_ref,'review_manifest':feedback['review_manifest'],'r06_acceptance':self.r06_receipt_reference(),'alignment_audit':artifacts['alignment-and-layering-audit.json'],'authority_effect':'none','application_authorized':False}
                durable(folder/'l4-review.json',encoded(review));artifacts['l4-review.json']=binding(folder/'l4-review.json')
            task=next(t for t in self.base()['tasks'] if t['id']==gate)
            evidence=[feedback['review_manifest'],feedback_ref,*[artifacts[k] for k in sorted(artifacts)]]
            def findings(criteria):
                return [{'criterion':c,'result':'pass','finding':'Exact original criterion supported by current bound machine evidence and the actual scoped human assessment. See reviewed packet and named artifacts.','evidence':evidence} for c in criteria]
            receipt={'schema':'relational.gate-acceptance/v4','task_id':gate,'validation_id':task['validation']['id'],'result':'accepted','review_mode':'Actual human assessment plus current candidate evidence audit','base_plan':SCOPE['base_plan'], 'review_manifest':feedback['review_manifest'],'human_feedback':feedback_ref,'criteria':findings(task['acceptance_criteria']),'failure_controls':findings(task['failure_controls']),'artifacts':artifacts,'source_bindings':[manifest['source_audit'],*audit['source_bindings']],'implementation_bindings':manifest['implementation_bindings'],'authority_effect':'none','application_authorized':False}
            self.verify_receipt(gate,receipt)
            durable(folder/'task-acceptance.json',encoded(receipt));fsync_dir(folder);fsync_dir(folder.parent)
            # Recheck all hard identities after preparation, before the atomic
            # authoritative publication. Uncommitted folders remain historical.
            self.validate_feedback(feedback)
            entry={'schema':'relational.gate-overlay-entry/v4','generation':current['generation']+1,'previous':current['overlay_head'],'base_plan':SCOPE['base_plan'],'gate':gate,'receipt':binding(folder/'task-acceptance.json'),'authority_effect':'none','application_authorized':False}
            schema('gate-status-overlay.schema.json',entry)
            pending=self.directory/('entry-'+uuid.uuid4().hex+'.tmp');durable(pending,encoded(entry))
            entries=self.directory/'entries';entries.mkdir(exist_ok=True);fsync_dir(self.directory)
            if crash_at=='before-publication':os._exit(91)
            target=entries/f"{entry['generation']:04}.json"
            os.link(pending,target);fsync_dir(entries);pending.unlink();fsync_dir(self.directory)
            if crash_at=='after-publication':os._exit(92)
            return {'status':'original-candidate-gate-accepted','gate':gate,'entry':binding(target),
                    'receipt':entry['receipt'],'fresh_event':False,'authority_effect':'none','application_authorized':False}

def feedback_text(feedback):
    return ('# Actual original gate feedback\n\nGate: '+feedback['gate']+'\n\nScope: '+feedback['scope']+
            '\n\nAnswers: '+json.dumps(feedback['answers'],sort_keys=True)+'\n\nActual quote:\n\n'+
            feedback['provenance']['quote']+'\n\nProvenance: '+json.dumps(feedback['provenance'],sort_keys=True)+
            '\n\nCandidate review only; authority_effect: none.\n')
