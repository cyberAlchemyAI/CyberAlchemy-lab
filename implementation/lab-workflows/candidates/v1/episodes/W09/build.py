"""Build run-scoped prospective constructors and inputs from frozen sources."""
import ast
import hashlib
import json
from pathlib import Path
import uuid

HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parents[1]
ROOT=PACKAGE.parents[3]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'

def require(v,msg):
    if not v:raise ValueError(msg)
def encoded(v):return (json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(p):return {'path':str(Path(p).relative_to(ROOT)),'sha256':sha(Path(p).read_bytes())}
def load(p):return json.loads(Path(p).read_bytes())
def emit(p,v):
    with Path(p).open('xb') as f:f.write(encoded(v))
def mapped(value,prefix):
    if isinstance(value,str):
        for old,family in [(':lab-engineering:',':engineering:'),(':lab-research:',':research:'),(':lab-W06:',':learning:')]:
            value=value.replace(old,':lab-W09:'+prefix+family)
        return value
    if isinstance(value,list):return [mapped(v,prefix) for v in value]
    if isinstance(value,dict):return {mapped(k,prefix):mapped(v,prefix) for k,v in value.items()}
    return value


def build():
    context=load(RUN/'context-W09.json');files={}
    def capture(b):
        p=ROOT/b['path'];require(sha(p.read_bytes())==b['sha256'],'selected source changed: '+b['path'])
        require(b['path'] not in files or files[b['path']]==b['sha256'],'source conflict');files[b['path']]=b['sha256']
    for b in context['source_bindings']:
        capture(b)
        if b['path'].endswith('.json'):
            v=load(ROOT/b['path'])
            for r in v.get('files',[]):capture({'path':r['path'],'sha256':r['sha256']})
    source_proofs={k:load(ROOT/next(b['path'] for b in context['source_bindings'] if '/receipts/'+k+'/' in b['path'])) for k in ['C13']}
    require(source_proofs['C13']['task_complete'],'C13 candidate criteria incomplete')
    native=Path(context['available_native_reader']['path']);require(sha(native.read_bytes())==context['available_native_reader']['sha256'],'native executable changed')
    prefix=uuid.uuid4().hex[:20];output=HERE/'packages'/prefix;output.mkdir(parents=True,exist_ok=False)
    sources=output/'sources';sources.mkdir();changes=[]
    # Constructor transformations change only new instance namespaces and bound source locations.
    originals={'engineering.py':PACKAGE/'workflows/engineering.py','research.py':PACKAGE/'workflows/research.py',
        'adapter.py':PACKAGE/'learning/adapter.py','application.py':PACKAGE/'learning/application.py',
        'run_learning.py':PACKAGE/'examples/learning-loop/run_episode.py'}
    for name,p in originals.items():
        capture(bind(p));raw=p.read_bytes();text=raw.decode();edits=[]
        for old,family in [('lab-engineering:','engineering:'),('lab-research:','research:'),('lab-W06:','learning:')]:
            count=text.count(old)
            if count:
                new='lab-W09:'+prefix+':'+family;edits.append({'before':old,'after':new,'occurrences':count});text=text.replace(old,new)
        parent_tokens={
            'engineering.py':'PACKAGE = Path(__file__).resolve().parents[1]',
            'adapter.py':'PACKAGE = Path(__file__).resolve().parents[1]',
            'run_learning.py':'PACKAGE = Path(__file__).resolve().parents[2]'}
        if name in parent_tokens:
            before=parent_tokens[name];require(text.count(before)==1,'exact PACKAGE binding pattern changed')
            after='PACKAGE = Path('+repr(str(PACKAGE))+')';text=text.replace(before,after);edits.append({'before':before,'after':after,'occurrences':1})
        if name=='adapter.py':
            before='own = list((PACKAGE/\'learning\').glob(\'*.py\')) + [AUTHORIZATION, OLD, CORRECTED]';require(text.count(before)==1,'actual learning source closure pattern changed')
            after=before+' + list(Path(__file__).resolve().parent.glob(\'*.py\'))';text=text.replace(before,after);edits.append({'before':before,'after':after,'occurrences':1})
        if name=='run_learning.py':
            before="source = PACKAGE/'learning'/filename";require(text.count(before)==1,'exact descriptor source selector changed')
            after="source = Path(__file__).resolve().parent/filename if filename in {'adapter.py','application.py'} else PACKAGE/'learning'/filename"
            text=text.replace(before,after);edits.append({'before':before,'after':after,'occurrences':1})
        ast.parse(text);dest=sources/name;dest.write_bytes(text.encode())
        changes.append({'original_binding':bind(p),'generated_binding':bind(dest),'ordered_edits':edits,
            'claim_ceiling':'Fresh prospective object namespace/source provenance only; original schemas, typed axes, checks, thresholds and action guards remain selected.'})
    # Package-specific loaders select constructors explicitly before original helper imports.
    input_rows={}
    for domain,parent,manifest_name in [('engineering',PACKAGE/'examples/engineering/packages/0004','input-manifest.json'),
        ('research',PACKAGE/'examples/research/packages/0007','selection.json')]:
        dest=output/domain;dest.mkdir();manifest=load(parent/manifest_name);prospective=mapped(manifest,prefix);copied=[]
        for r,new in zip(manifest['records'],prospective['records']):
            p=parent/r['path'];capture(bind(p));original=load(p);value=mapped(original,prefix)
            target=dest/r['path'];emit(target,value);new['sha256']=sha(target.read_bytes())
            copied.append({'original_binding':bind(p),'prospective_binding':bind(target),'original_version_ref':r['version_ref'],'prospective_version_ref':new['version_ref']})
        if domain=='engineering':
            for name in ('define','design','plan'):
                p=parent/manifest[name]['path'];capture(bind(p));target=dest/p.name;emit(target,mapped(load(p),prefix));prospective[name]['sha256']=sha(target.read_bytes())
            for name in ('registered_evaluator.py',):
                p=parent/name;capture(bind(p));(dest/name).write_bytes(p.read_bytes())
        else:
            p=parent/manifest['procedure']['path'];capture(bind(p));target=dest/p.name;procedure=mapped(load(p),prefix)
            procedure['source_bindings'] += [bind(sources/'research.py'),bind(sources/'engineering.py')]
            emit(target,procedure);prospective['procedure']['sha256']=sha(target.read_bytes())
        p=dest/manifest_name;emit(p,prospective);input_rows[domain]={'selection_binding':bind(p),'original_selection_binding':bind(parent/manifest_name),
            'prospective_records':copied,'source_family':'frozen-selected-blueprint','domain_execution_started':False}
        capture(bind(parent/manifest_name))
    selection={'schema_version':'lab-W09-execution-selection/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
        'run_namespace':prefix,'source_context_binding':bind(RUN/'context-W09.json'),'constructor_recipes':changes,'inputs':input_rows,
        'native_executable_binding':context['available_native_reader'],'workflow_review_binding':next(b for b in context['source_bindings'] if b['path'].endswith('W08/packages/0001/preparation.json')),
        'historical_Lesson_binding':load(PACKAGE/'review/W08/lesson-expiry-observation.json')['source_binding'],
        'fresh_learning_rule':'New run-scoped Lesson identity and actual-clock expiry; exact separate local signature/review and subsequent new Agent application. Historical expired record never modified.',
        'execution_authorization_binding':next(b for b in context['source_bindings'] if b['path'].endswith('/authorization.json')),
        'source_files':[{'path':p,'sha256':s} for p,s in sorted(files.items())],'canonical_effects_applied':0,'runtime_activation':False}
    emit(output/'selection.json',selection);print(encoded({'result':'PASS','selection':bind(output/'selection.json'),'run_namespace':prefix,'source_files':len(files),'constructors':5,'domain_execution_started':False}).decode(),end='')


if __name__=='__main__':build()
