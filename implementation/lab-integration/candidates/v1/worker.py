#!/usr/bin/env python3
"""Isolated regression worker with an exact per-case inventory and terminal evidence."""
import argparse,importlib,io,json,os,sys,tempfile,time,unittest
from pathlib import Path
from inventory_manifest import ROOT,groups

parser=argparse.ArgumentParser();parser.add_argument('group');parser.add_argument('output');parser.add_argument('--inventory',action='store_true');parser.add_argument('--case');args=parser.parse_args()
output=Path(args.output)
if 'C09_FIXTURE_ROOT' in os.environ:tempfile.tempdir=os.environ['C09_FIXTURE_ROOT']
group=next(g for g in groups() if g['id']==args.group)
sys.path.insert(0,str(ROOT/group['test_directory']))
suite=unittest.TestSuite()
specs=[group]+group.get('additional',[])
for spec in specs:
    module=importlib.import_module(spec['module'])
    for name in spec['classes']:suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(getattr(module,name)))
tests=list(suite);ids=[t.id() for t in tests]
if len(ids)!=len(set(ids)):raise ValueError('duplicate regression test identity')
if args.inventory:
    output.write_text(json.dumps({'group':args.group,'test_ids':ids,'count':len(ids)},indent=2)+'\n');sys.exit(0)
if args.case:
    tests=[t for t in tests if t.id()==args.case]
    if len(tests)!=1:raise ValueError('exact frozen regression case missing')
    suite=unittest.TestSuite(tests)
stream=io.StringIO();started=time.perf_counter()


class Result(unittest.TextTestResult):
    def __init__(self,*a,**k):super().__init__(*a,**k);self.checks=[]
    def addSuccess(self,test):super().addSuccess(test);self.checks.append({'test':test.id(),'result':'PASS'})
    def addFailure(self,test,error):super().addFailure(test,error);self.checks.append({'test':test.id(),'result':'FAIL','detail':self._exc_info_to_string(error,test)})
    def addError(self,test,error):super().addError(test,error);self.checks.append({'test':test.id(),'result':'ERROR','detail':self._exc_info_to_string(error,test)})
    def stopTest(self,test):
        super().stopTest(test)
        Path(str(output)+'.progress').write_text(json.dumps({'group':args.group,'tests':self.testsRun,'checks':self.checks,'last_test':test.id(),'elapsed_seconds':time.perf_counter()-started})+'\n')


result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Result).run(suite)
observations={}
for module_name,class_name,key in [('test_transition','TransitionTests','transition'),('test_promotion','PromotionTests','publication'),('test_bootstrap','BootstrapTests','bootstrap'),('test_context','ContextTests','context'),('test_join','JoinTests','joined'),('test_publication_join','PublicationJoinTests','publication_invalidation')]:
    module=sys.modules.get(module_name)
    if module is not None and hasattr(module,class_name):
        cls=getattr(module,class_name);value=getattr(cls,'observed',None)
        if value is not None:observations[key]=value
module=sys.modules.get('test_context')
if args.group=='context' and module is not None:observations['context_packs']=module.ContextTests.observed
module=sys.modules.get('test_replay')
if args.group=='replay' and module is not None:observations['replay_timings']=module.ReplayTests.performance
data={'schema_version':'lab-C09-regression-group/v1-candidate','authority_effect':'none','group':args.group,'expected_test_ids':[t.id() for t in tests],'checks':result.checks,'tests':result.testsRun,'successful':result.wasSuccessful(),'failures':len(result.failures),'errors':len(result.errors),'duration_seconds':time.perf_counter()-started,'observations':observations,'claim_ceiling':group.get('scope','Isolated candidate component mechanics only; no owner outcome or live repository effects.')}
output.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
print(stream.getvalue(),flush=True)
sys.exit(0 if result.wasSuccessful() and result.testsRun==len(tests) and len(result.checks)==len(tests) else 1)
