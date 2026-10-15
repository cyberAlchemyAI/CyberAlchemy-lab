"""Unchanged original C07 publisher rehearsal, never final owner qualification."""
import argparse
import ast
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import unittest
from datetime import datetime, timezone
import build_runtime as B

NAMES=('test_selected_export_and_private_exclusion',
    'test_one_response_complete_carriers_and_cold_replay',
    'test_crash_before_and_after_commit_and_cold_repair')
PACKAGE=B.ROOT/'implementation/lab-runtime/candidates/repeatable-operation'
CASE=PACKAGE/'tests/test_promotion.py'
LOCK=B.ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/final-api-regression-0173-0190.execution.lock'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--api-directory',required=True)
    parser.add_argument('--source-sha256',required=True);parser.add_argument('--profile-sha256',required=True)
    parser.add_argument('--output-prefix',required=True)
    args=parser.parse_args();prefix=Path(args.output_prefix).resolve()
    B.need(prefix.parent==B.HERE and all(not Path(str(prefix)+s).exists() for s in ('.json','.log','.events.jsonl')), 'exclusive owned proof outputs required')
    api=Path(args.api_directory).resolve();B.need(api.parent==B.BASE,'actual selected API family required')
    def event(row):
        with Path(str(prefix)+'.events.jsonl').open('a') as stream:
            json.dump({'at':datetime.now(timezone.utc).isoformat(),**row},stream,sort_keys=True);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    event({'phase':'waiting-shared-0190','pid':os.getpid(),'source_sha256':args.source_sha256})
    fd=os.open(LOCK,os.O_RDWR|os.O_NOFOLLOW)
    started=datetime.now(timezone.utc).isoformat();entry=False;exit_guard=False;failure=None;result=None;observed=None;cases=[]
    with Path(str(prefix)+'.log').open('x') as log:
        try:
            fcntl.flock(fd,fcntl.LOCK_SH)
            guard=B.module('_bounded_original_publisher_guard',api/'guard.py')
            manifest=guard.verify(args.source_sha256);B.exact(api/'contract-profile.json',args.profile_sha256);entry=True
            rows={r['path']:r['sha256'] for r in manifest['files']}
            origin=B.bind(CASE);B.need(rows.get(origin['path'])==origin['sha256'],'original case file outside exact source selection')
            raw=B.read(CASE);tree=ast.parse(raw);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='PromotionTests')
            definitions={n.name:n for n in cls.body if isinstance(n,ast.FunctionDef)}
            witnesses={n:hashlib.sha256(ast.get_source_segment(raw.decode(),definitions[n]).encode()).hexdigest()
                for n in (*NAMES,'setUpClass','tearDownClass','setUp','tearDown')}
            sys.path.insert(0,str(PACKAGE/'tests'));sys.path.insert(0,str(PACKAGE))
            import test_promotion as original
            B.need(Path(original.__file__).resolve()==CASE,'wrong original case origin')
            from lab_runtime import publisher,promotion
            B.need(Path(publisher.__file__).resolve()==PACKAGE/'lab_runtime/publisher.py'
                and Path(promotion.__file__).resolve()==PACKAGE/'lab_runtime/promotion.py','wrong original publisher/kernel origin')
            event({'phase':'full-source-entry-passed','source_rows':len(manifest['files']),'case_origin':origin,'AST_method_sha256s':witnesses})
            class Result(unittest.TextTestResult):
                def startTest(self,test):
                    self.at=time.monotonic();event({'phase':'case-start','id':test.id()});super().startTest(test)
                def stopTest(self,test):
                    failures={str(t) for t,_ in self.failures};errors={str(t) for t,_ in self.errors}
                    status='FAIL' if str(test) in failures else 'ERROR' if str(test) in errors else 'PASS'
                    row={'id':test.id(),'result':status,'elapsed_seconds':time.monotonic()-self.at};cases.append(row);event({'phase':'case-end',**row});super().stopTest(test)
            suite=unittest.TestSuite(original.PromotionTests(methodName=n) for n in NAMES)
            result=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=Result).run(suite)
            observed=original.PromotionTests.observed
            B.need(B.bind(CASE)==origin,'original case source changed')
            guard.verify(args.source_sha256);B.exact(api/'contract-profile.json',args.profile_sha256);exit_guard=True
            event({'phase':'full-source-exit-passed'})
        except Exception as exc:
            failure={'type':type(exc).__name__,'message':str(exc)};event({'phase':'harness-error',**failure})
        finally:
            fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
    good=failure is None and result is not None and result.wasSuccessful() and result.testsRun==len(NAMES) and entry and exit_guard
    report={'schema_version':'lab-bounded-original-mixed-publisher-rehearsal/v1-candidate','result':'PASS-REHEARSAL' if good else 'FAIL',
        'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'caller_binding':B.bind(Path(__file__)),
        'API_source_binding':B.bind(api/'source-manifest.json'),'API_profile_binding':B.bind(api/'contract-profile.json'),
        'source_rows':len(manifest['files']) if entry else None,'case_binding':B.bind(CASE),
        'case_AST_bindings':witnesses if entry else None,'cases':cases,'expected_tests':len(NAMES),
        'tests_run':result.testsRun if result else 0,'failure':failure,
        'unittest_failures':[{'case':str(t),'traceback':trace} for t,trace in result.failures] if result else [],
        'unittest_errors':[{'case':str(t),'traceback':trace} for t,trace in result.errors] if result else [],
        'actual_original_case_observation':observed,'full_source_entry_guard':entry,'full_source_exit_guard':exit_guard,
        'fixture_only':True,'fixture_native_local_commits_and_scratch_repository_publications_occurred':bool(result and result.testsRun),
        'rehearsal_owner_key_origin':'New original-test-owned ephemeral fixture adapter outside its temporary repository; not a restored source owner key.',
        'original_assertions_unchanged':True,'new_scope_or_namespace_work_qualified':False,
        'selected_363_final_members_qualified':False,'final_owner_authority_resolved':False,'actual_owner_outcome':None,
        'human_outcome':None,'canonical_repository_admissions':0,'runtime_activations':0,'authority_effect':'none',
        'ready_for_R08':False,'task_complete':False,'goal_complete':False,
        'log_binding':B.bind(Path(str(prefix)+'.log')),'events_binding':B.bind(Path(str(prefix)+'.events.jsonl'))}
    B.emit(Path(str(prefix)+'.json'),report)
    print(json.dumps({'result':report['result'],'tests_run':report['tests_run'],'report_binding':B.bind(Path(str(prefix)+'.json')),'failure':failure}),flush=True)
    return 0 if good else 1

if __name__=='__main__':raise SystemExit(main())
