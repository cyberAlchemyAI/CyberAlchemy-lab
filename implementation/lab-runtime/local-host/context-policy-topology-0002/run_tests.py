import hashlib,json,pathlib,sys,types,unittest
p=pathlib.Path(__file__).parent
pins=json.loads((p/'test-selection.json').read_bytes())
raws={name:(p/name).read_bytes() for name in pins}
if any(hashlib.sha256(raws[k]).hexdigest()!=pins[k] for k in pins):raise RuntimeError('DRIFT')
def audit(event,args):
    if event=='open' and isinstance(args[0],(str,bytes)) and str(args[0]).endswith('branch.snapshot'):raise RuntimeError('NO_ARCHIVE')
    if event.startswith(('socket.','subprocess.')) or event in ('os.system','os.fork','os.exec'):raise RuntimeError('NO_EFFECT')
sys.addaudithook(audit)
m=types.ModuleType('tests');m.__file__=str(p/'test_adapter.py')
exec(compile(raws['test_adapter.py'],m.__file__,'exec'),m.__dict__)
r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(m))
if any(hashlib.sha256((p/k).read_bytes()).hexdigest()!=pins[k] for k in pins):raise RuntimeError('POSTDRIFT')
print(json.dumps({'tests':r.testsRun,'success':r.wasSuccessful(),'effects':'NOT_RUN','pins':pins},sort_keys=True))
sys.exit(0 if r.wasSuccessful() else 1)
