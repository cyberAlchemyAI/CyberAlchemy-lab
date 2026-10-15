"""Static driver/pin review and exact finally AST with owned inert ports only."""
import ast,hashlib,json,os,sys,types
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
HERE=Path(__file__).absolute().parent
DRIVER=RUN/'T07/ontology-installation-root-0002/install.py'
P=RUN/'T07/ontology-native-execution-preparation-0002'
def need(value,message):
    if not value:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def fds():
    rows={}
    for name in os.listdir('/proc/self/fd'):
        try:s=os.fstat(int(name));rows[name]=(s.st_dev,s.st_ino,s.st_mode)
        except OSError:continue
    return rows
baseline=fds();raw=DRIVER.read_bytes();need(sha(raw)=='1122d5928dad7945e6638b821949fd283b3da8de58476f616318d9ee693b4c69','Root driver changed')
tree=ast.parse(raw);functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)};main=functions['main'];text=ast.unparse(main)
constants={n.targets[0].id:n.value.value for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and isinstance(n.value,ast.Constant)}
checks=[]
def check(name,value):need(value,name);checks.append(name)
check('exact-frozen-role-proposal',sha((P/'ROOT-PREPARE-PROVISION-PROPOSAL.json').read_bytes())==constants['PROPOSAL_PIN']=='b506322170257a5b44388ac0fa77bbed9302bc05f7e08f14a1f003ec8fe237b5')
check('exact-frozen176-role-manifest',sha((P/'source-manifest.json').read_bytes())==constants['MF_PIN']=='cec90b3efee6a949706bef250447db110da5d07a0bcfe88eae082be061eb7548'and len(json.loads((P/'source-manifest.json').read_bytes())['files'])==176)
check('current-source-and-profile-fixed',constants['SOURCE']=='ee969cc8c6b539aa3247d81c82322cb9e7aefd42188d63db0195e381cdad4cb1'and constants['PROFILE']=='9c8c3018226abb9077c6a99ee3cbc9dd0174c148b332b9488fd4a3a9cd30418b')
check('original-selected-deps-before-API-guard-load',text.index("sys.path.insert(0, str(BASE / 'deps'))")<text.index('loaded ='))
check('all-entry-proofs-before-fresh-installation-effect',text.index('guard.verify(SOURCE)')<text.index('tempfile.mkdtemp')and text.index('deps.preflight(')<text.index('tempfile.mkdtemp')and text.index('deps.verify_installed(')<text.index('tempfile.mkdtemp'))
check('fresh-sibling-ontology0002-only',"tempfile.mkdtemp(prefix='ontology-0002-', dir=BASE.parent)"in text and "os.listdir(newroot) == []"in text)
check('actual-returned-selector-persisted-before-provision',text.index('executor_module.prepare_selection(')<text.index("emit('execution-selection.json', raw)")<text.index('executor_module.provision(executor)'))
check('whole1011-and-one-added-role-required','len(executor.expected) == 1011' in text and "len(executor.value['added_inputs']) == 1"in text)
check('no-ontology-native-run-port-called',not any(isinstance(n,ast.Call)and(isinstance(n.func,ast.Attribute)and n.func.attr in('run_native','run','Popen','unlink','rmtree','remove'))for n in ast.walk(tree)))
check('exclusive0600-fsync-outputs',all(token in ast.unparse(functions['emit'])for token in('os.O_EXCL','os.O_NOFOLLOW','os.fchmod(fd, 384)','os.fsync(fd)')))
outer=next(n for n in main.body if isinstance(n,ast.Try));loop=next(n for n in outer.finalbody if isinstance(n,ast.For));extra=next(n for n in outer.finalbody if isinstance(n,ast.If)and ast.unparse(n.test)=='executor is not None')
seen=[];errors=[]
def port(label,refuse=False):
    def call(*args):
        seen.append(label)
        if refuse:raise ValueError('owned inert refusal')
    return call
scope={'guard':types.SimpleNamespace(verify=port('Source',True)),'SOURCE':'owned-inert','PROFILE':'owned-inert','API':Path('/owned-inert'),
       'control':types.SimpleNamespace(capture=port('profile')),'inputs':port('176'),'original_base':port('base1010',True),
       'executor':types.SimpleNamespace(guard=port('new1011')),'errors':errors,'diagnostic':lambda:{'exception_class':'ValueError'}}
block=ast.Module(body=[loop,extra],type_ignores=[]);ast.fix_missing_locations(block);exec(compile(block,str(DRIVER),'exec'),scope)
check('all-five-exit-guards-independent-despite-Source-and-base-failure',seen==['Source','profile','176','base1010','new1011']and len(errors)==2)
check('author-controls-did-not-import-API-native-or-ctypes','ctypes'not in sys.modules and not any(n.startswith('_Root827')for n in sys.modules))
check('inert-controls-FD0',baseline==fds())
value={'result':'PASS-static-driver-and-owned-inert-only','checks':checks,'check_count':len(checks),'FD_delta':0,'actual_Source_API_native_executor_installation_or_lease_executed':False,'all176-body-row-recapture_by_this_driver_review':False,'full_role_input_closure_review_owned_separately':True}
with(HERE/'checks-result.json').open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps(value,sort_keys=True))
