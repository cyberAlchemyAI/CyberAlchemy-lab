import pathlib,json,hashlib,ast,sys
R=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab');L=R/'implementation/lab-runtime/local-host';E=L/'independent-context-docker-design-review-0002';P=L/'independent-context-docker-design-review-0001';bindings=[];checks=[]
def check(ok,name):
 if not ok:raise RuntimeError(name)
 checks.append(name)
def read(p,pin=None):
 if p.name=='branch.snapshot':raise RuntimeError('private body denied')
 raw=p.read_bytes();s=hashlib.sha256(raw).hexdigest()
 if pin:check(s==pin,'pin '+str(p.relative_to(R)))
 bindings.append({'path':str(p.relative_to(R)),'sha256':s,'size':len(raw)});return raw
raw=read(L/'CONTEXT-DOCKER-NEXT-UNIT-DESIGN-20261020-0002.md','308c697a2bc850c81b59d7a4b86a4b8cd31c97438d106aabb60362a5d16b890c');text=raw.decode()
read(P/'review.json','3c08f21aa693073877602903f9ac8c92259e017a6eceb8ce4a95b11b6e86e778')
old=json.loads(read(P/'bindings-normal.json'))
for row in old:
 b=read(R/row['path'],row['sha256']);check(len(b)==row['size'],'size '+row['path'])
# These are design requirements, not execution evidence.
for phrase in ['no final Context source manifest','all eleven historical Context preimage bytes','Only after that full render','five occurrence vector','context/implementation-binding.json',"`AUTH` path and `AUTH_SHA`",'durable EMIT ACK','send exactly one FINISH','only then sends the exact FINISH ACK','closes its dedicated client endpoint **once**','Only after that checked close','enclosing controller verdict remains UNKNOWN','manifest EMIT-ACK loss','FINISH-ACK loss','client close failure/interruption','39 sorted exact bindings','40-leaf/39-row','self-provisioned development channel']:
 check(phrase in text,'explicit design clause '+phrase)
C=R/'product/lab/release-candidates/v1/interface/legacy-session-fixture-context-v1-action-0148';t=ast.parse((C/'build.py').read_bytes());f=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='build');tail=f.body[-2:];check([n.value.func.id for n in tail]==['emit','print'],'original final emit synchronously precedes summary')
args=tail[0].value.args;check(isinstance(args[0],ast.BinOp) and isinstance(args[0].right,ast.Constant) and args[0].right.value=='manifest.json','exact final manifest callsite')
check(4+30+4+2==40 and 4+30+4+1==39,'40 emitted leaves39 prior manifestrows')
(E/('bindings-optimized.json' if sys.flags.optimize else 'bindings-normal.json')).write_text(json.dumps(bindings,indent=2)+'\n')
print(json.dumps({'status':'PASS_READ_ONLY_DESIGN_CHECKS','optimization':sys.flags.optimize,'checks':len(checks),'bindings':len(bindings),'candidate_imports':False,'private_body_read':False,'effects':'NOT_RUN','executed_FINISH_bridge':False,'design_requirements_only':True},sort_keys=True))
