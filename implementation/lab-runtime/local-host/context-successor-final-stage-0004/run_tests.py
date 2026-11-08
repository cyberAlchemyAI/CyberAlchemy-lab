import hashlib,json,pathlib,sys,types,unittest
HERE=pathlib.Path(__file__).parent
sys.path.insert(0, '/usr/lib/python3/dist-packages')
pins=json.loads((HERE/sys.argv[1]).read_bytes())
raws={p:pathlib.Path(p).read_bytes() for p in pins}
if any(hashlib.sha256(raws[p]).hexdigest()!=pins[p] for p in pins):raise RuntimeError('DRIFT')
def audit(event,args):
    if event=='open' and isinstance(args[0],(str,bytes)) and str(args[0]).endswith('branch.snapshot'):
        raise RuntimeError('ARCHIVE_BODY_FORBIDDEN')
    if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.fork','os.exec'):
        raise RuntimeError('EFFECT_FORBIDDEN')
sys.addaudithook(audit)
p=str(HERE/'test_final_stage.py');module=types.ModuleType('tests');module.__file__=p
exec(compile(raws[p],p,'exec'),module.__dict__)
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
if any(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()!=pins[p] for p in pins):raise RuntimeError('POSTDRIFT')
print(json.dumps({'tests':result.testsRun,'success':result.wasSuccessful(),'effects':'NOT_RUN','archive_body':'UNOPENED','pins':pins},sort_keys=True))
sys.exit(0 if result.wasSuccessful() else 1)
