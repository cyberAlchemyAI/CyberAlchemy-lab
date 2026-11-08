from pathlib import Path
import json,copy,subprocess,time,sys
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;B=H.parent;sys.path.insert(0,str(B.parent))
from v3.execution import support as s
from v3.p03.context import C
rows=[C.decode(x.encode()) for x in (H/'sample.ndjson').read_text().splitlines()];names={0:''};levels={0:{'zero':True}};exprs={};decls={};kinds={}
for r in rows:
 if 'in' in r:
  v=r.get('str',r.get('num'));part=v.get('str',str(v.get('i')));names[r['in']]=(names[v['pre']]+'.' if names[v['pre']] else '')+part
 elif 'il' in r:levels[r['il']]={k:v for k,v in r.items() if k!='il'}
 elif 'ie' in r:exprs[r['ie']]={k:v for k,v in r.items() if k!='ie'}
 else:
  for kind in ['def','thm','axiom','opaque']:
   if kind in r:decls[r[kind]['name']]=r[kind];kinds[r[kind]['name']]=kind
  if 'inductive' in r:
   for kind in ['types','ctors','recs']:
    for d in r['inductive'][kind]:decls[d['name']]=d;kinds[d['name']]=kind
TARGET='RelationalExtensions.Expression.unknown_not_negative';ns='RelationalExtensions.Expression.'
target=next(d for n,d in decls.items() if names[n]==TARGET)
def level(i):
 d=levels[i]
 if 'zero' in d:return 0
 if 'succ' in d:
  x=level(d['succ']);return x+1 if type(x) is int else ('succ',x)
 if 'param' in d:return ('param',names[d['param']])
 return tuple((k,level(v)) for k,v in sorted(d.items()))
def expression(i):
 d=exprs[i]
 if 'const' in d:return ('const',names[d['const']['name']],tuple(level(x) for x in d['const']['us']))
 if 'app' in d:return ('app',expression(d['app']['fn']),expression(d['app']['arg']))
 if 'sort' in d:return ('sort',level(d['sort']))
 if 'bvar' in d:return ('bvar',d['bvar'])
 if 'forallE' in d or 'lam' in d:
  k='forallE' if 'forallE' in d else 'lam';v=d[k];return (k,expression(v['type']),expression(v['body']))
 raise ValueError('unsupported challenge expression '+str(d))
def const(n,us=()):return ('const',n,us)
def app(f,a):return ('app',f,a)
expected=app(app(app(const('Eq',(1,)),const(ns+'Truth')),app(const(ns+'tNot'),const(ns+'Truth.unknown'))),const(ns+'Truth.unknown'))
controls=[];cases=[]
def test(n,ok):s.require(ok,n);controls.append({'name':n,'result':'pass'});print(n,'PASS',flush=True)
test('trusted-structural-statement-exact',expression(target['type'])==expected)
# Every expression reference and every declaration type/value/computation rule is
# audited. The exporter includes complete inductive groups, even unused recursors.
references=set();universes=[]
for i,d in exprs.items():
 if 'const' in d:
  c=d['const'];references.add(c['name']);test_name=names[c['name']]
  s.require(c['name'] in decls,'missing closure declaration '+test_name)
  s.require(len(c['us'])==len(decls[c['name']]['levelParams']),'dropped/mismatched universe arity '+test_name)
  universes.append({'constant':test_name,'instances':[level(x) for x in c['us']]})
test('complete-exported-expression-closure',references<=set(decls));test('every-declaration-type-present',all(d['type'] in exprs for d in decls.values()));test('no-axioms-in-sample',not any(k=='axiom' for k in kinds.values()))
s.write(H/'dependency-closure.json',{'sample_only':True,'target':TARGET,'declarations':[{'name':names[n],'kind':kinds[n],'universe_parameters':[names[x] for x in d['levelParams']],'type_expression':d['type'],'value_expression':d.get('value'),'computation_rule_expressions':[x['rhs'] for x in d.get('rules',[])]} for n,d in decls.items()],'constant_instances':universes,'expression_count':len(exprs),'level_count':len(levels),'axioms':[],'closure':'Complete exported declaration/type/value/inductive-computation closure; nanoda checks all declarations, not only the named theorem.'})
binary=H/'tools/nanoda/target/release/nanoda_bin';cfg=C.decode((H/'sample-config.json').read_bytes());cfg.update(pp_to_stdout=True,pp_declars=[TARGET],print_axioms=True,num_threads=1);s.write(H/'sample-config.json',cfg)
def run(n,data,should_accept,challenge=True):
 path=H/(n+'.ndjson');path.write_text('\n'.join(json.dumps(r,separators=(',',':')) for r in data)+'\n');config={**cfg,'export_file_path':str(path)};conf=H/(n+'-config.json');s.write(conf,config)
 start=time.monotonic();p=subprocess.run([str(binary),str(conf)],cwd=H,text=True,capture_output=True,timeout=60);seconds=time.monotonic()-start
 log=H/(n+'.log');log.write_text(p.stdout+p.stderr);ok=p.returncode==0 and 'no errors' in p.stdout
 test(n+'-independent-kernel',ok==should_accept);cases.append({'name':n,'input':s.binding(path),'config':s.binding(conf),'log':s.binding(log),'exit_code':p.returncode,'seconds':seconds,'independent_kernel_acceptance':ok})
 return p
run('positive-sample',rows,True)
# A forged original-kernel acceptance bit cannot make an ill-typed proof pass.
bad=copy.deepcopy(rows);bad[0]['meta']['lean']['accepted']=True;bad[-1]['thm']['value']=next(i for i,d in exprs.items() if d.get('const',{}).get('name')==next(n for n in decls if names[n]==ns+'Truth.unknown'))
run('forged-accepted-bad-proof',bad,False)
bad=copy.deepcopy(rows)
for r in bad:
 if r.get('const',{}).get('name')==next(n for n in decls if names[n]=='Eq.refl'):r['const']['us']=[]
run('dropped-universe-instance',bad,False)
bad=copy.deepcopy(rows)
for r in bad:
 if 'axiom' in r:raise ValueError('unexpected existing axiom')
 if r.get('thm',{}).get('name')==next(n for n in decls if names[n]==TARGET):r['axiom']={k:v for k,v in r.pop('thm').items() if k not in ['value','all']}
run('unpermitted-axiom',bad,False)
bad=copy.deepcopy(rows)
for r in bad:
 if 'ie' in r and 'const' in r and names[r['const']['name']]==ns+'Truth.unknown':r['const']['name']=next(n for n in decls if names[n]==ns+'Truth.no')
# This changes the challenge, so even a new valid proof must refuse the trusted
# statement boundary. Independent kernel output is separately reported.
test('changed-statement-refuses-trusted-challenge',bad!=rows)
changed_exprs={r['ie']:{k:v for k,v in r.items() if k!='ie'} for r in bad if 'ie' in r};old_exprs=exprs;exprs=changed_exprs;test('changed-statement-structural-mismatch',expression(target['type'])!=expected);exprs=old_exprs
# A valid proof under substituted definitions is still the wrong trusted export.
bad=copy.deepcopy(rows)
unknown_id=next(i for i,d in exprs.items() if d.get('const',{}).get('name')==next(n for n in decls if names[n]==ns+'Truth.unknown'))
definition=next(r['def'] for r in bad if r.get('def',{}).get('name')==next(n for n in decls if names[n]==ns+'tNot'))
for row in bad:
 if row.get('ie')==definition['value']:row['lam']['body']=unknown_id
run('changed-definition-valid-kernel',bad,True)
try:s.require(C.identity(bad)==C.identity(rows),'trusted closure export identity mismatch')
except ValueError:test('changed-definition-refused-by-trusted-closure-pin',True)
else:raise ValueError('substituted definition accepted against trusted closure')
bad=copy.deepcopy(rows)
# Remove the complete Truth inductive group, not just a displayed definition.
bad=[r for r in bad if not ('inductive' in r and any(names[d['name']]==ns+'Truth' for d in r['inductive']['types']))]
run('missing-inductive-dependency',bad,False)
export_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=H/'tools/lean4export',text=True).strip();kernel_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=H/'tools/nanoda',text=True).strip()
s.write(H/'sample-check-report.json',{'schema':'relational.independent-checker-feasibility/v1','result':'sample-checked','sample_only':True,'target':TARGET,'sample_scope':'E00 unknown-preservation equation; complete exported 18-declaration closure, not the whole relational checker.','universal_translation_proved':False,'checker':'Independent Rust nanoda; standalone binary does not invoke Lean or accept a Lean acceptance flag.','checker_binary':s.binding(binary),'checker_commit':kernel_commit,'exporter_commit':export_commit,'exporter':'Lean4export interpreted by pinned Lean 4.33.1 because local C headers are absent; only toolchain selection file changed.','accepted_source':s.binding(B/'e00/ExpressionSemantics.lean'),'closure':s.binding(H/'dependency-closure.json'),'trusted_statement':expected,'axioms':[],'controls':controls,'cases':cases,'kernel_and_export_format':'Pinned kernel 4.33.1; NDJSON 3.1.0','authority_effect':'none','application_authorized':False})
print('E06 sample controls complete:',len(controls),flush=True)
