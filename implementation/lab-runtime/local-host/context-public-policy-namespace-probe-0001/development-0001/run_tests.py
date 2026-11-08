import pathlib,sys,json,hashlib,unittest
p=pathlib.Path(__file__).parent
sys.path.insert(0,str(p));sys.path.append('/usr/lib/python3/dist-packages')
pins=json.loads((p/sys.argv[1]).read_bytes())
for name,digest in pins.items():
 if hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest()!=digest:raise RuntimeError('PRE_DRIFT')
def audit(event,args):
 if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.fork','os.exec'):raise RuntimeError('EFFECT_DISABLED_TEST')
 if event=='open' and isinstance(args[0],str) and args[0].endswith('branch.snapshot'):raise RuntimeError('PRIVATE_BODY_DISABLED')
sys.addaudithook(audit)
import test_release
r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test_release))
for name,digest in pins.items():
 if hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest()!=digest:raise RuntimeError('POST_DRIFT')
print(json.dumps({'tests':r.testsRun,'success':r.wasSuccessful(),'docker_effect':'UNRUN','private_inputs':'UNOPENED'}))
sys.exit(not r.wasSuccessful())
