"""Actual private fact-scope identity, lost-resource and dispatch refusals."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v85'


def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    source_binding=bind(API/'source-manifest.json')
    assert source_binding['sha256']=='adb265d1ef7d8762e9fae1a1f984d19b8605d0a40ef43fffe89ba04728d53fae'
    profile_binding=bind(API/'contract-profile.json')
    assert profile_binding['sha256']=='d2932dc480a8097d6bc823dedbc07c2409fdb76e32246f5c848890b84c2e9517'
    name='_cal_API85_actual_Machine_scope_refusals'
    spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    M=__import__(name+'.test_machine_transport',fromlist=['MachineTransport'])
    S=__import__(name+'.test_custody_sessions',fromlist=['Sessions']);S.PROFILE=profile_binding['sha256']
    G=__import__(name+'.guard',fromlist=['verify']);G.verify(source_binding['sha256'])
    selected=__import__(name+'.machine_context_scope',fromlist=['selected']).selected
    phases=[]

    class Refusals(M.MachineTransport):
        def test_actual_scope_closed_identity_and_dispatch_boundaries(self):
            self.authenticated();custodian=self.peer.service.sessions
            K=M.D.FACT_SCOPE
            with selected.read_scope(custodian) as facts:
                scope=K.active_scope()
                self.assertIs(facts,scope.snapshot)
                self.assertIs(K.policy_scope(self.channel),scope)
                self.assertEqual(self.channel.policy_guard()['principal_ref'],self.peer.context['principal_ref'])
                # A Machine Actor is not its parent's policy host.
                with self.assertRaises(ValueError):K.policy_scope(self.peer)
                with self.assertRaises(ValueError):K.policy_scope(object())
                phases.append({'check':'exact-actual-parent-policy-host-only','result':'PASS'})
                # The real dispatcher refuses an invocation while copied facts
                # are registered, before a claim or any writer can run.
                call=M.F.call(self.peer.context,'lab.status',M.cut(self.view))
                before=set((self.root/'workspace/journal').glob('*.allocated.json'))
                reply=self.peer.service.call(M.compact(call))
                self.assertEqual(reply['schema_version'],'lab-api-transport-error/v1-candidate')
                self.assertEqual(reply['code'],'unauthenticated-channel')
                self.assertEqual(set((self.root/'workspace/journal').glob('*.allocated.json')),before)
                self.assertFalse(self.peer.closed);self.assertFalse(self.resource.closed)
                phases.append({'check':'real-dispatch-refused-before-journal-inside-pure-scope','result':'PASS'})
            self.assertIsNone(K.active_scope())
            self.resource.guard();self.peer.guard()
            sid=self.opened_result['session_ref']
            removed=self.service.sessions.live.pop(sid)
            try:
                with self.assertRaises(ValueError):selected.selected(custodian)
            finally:self.service.sessions.live[sid]=removed
            phases.append({'check':'missing-actual-resource-refused-without-reconstruction','result':'PASS'})
            # A changed bridge pointer is refused; original callbacks stay.
            original=custodian.bridge.channel
            custodian.bridge.channel=self.channel
            try:
                with self.assertRaises(ValueError):selected.selected(custodian)
            finally:custodian.bridge.channel=original
            phases.append({'check':'wrong-bridge-channel-identity-refused','result':'PASS'})
            self.resource.guard();self.peer.guard()

    suite=unittest.TestSuite([Refusals('test_actual_scope_closed_identity_and_dispatch_boundaries')])
    log=RUN/'API85-Machine-scope-refusals-case-0001.log'
    with log.open('x') as stream:result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    G.verify(source_binding['sha256'])
    report={'schema_version':'lab-actual-Machine-scope-refusals/v1-candidate','result':'PASS' if result.wasSuccessful() else 'FAIL',
            'actual_cases':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'checks':phases,
            'files':[source_binding,profile_binding,bind(Path(__file__).resolve()),bind(API/'machine_context_scope.py'),
                     bind(ROOT/'product/lab/release-candidates/v1/interface/machine-context-scope-v1/generation.py')],
            'source_permission_and_clock_callbacks_replaced':False,'time_bounds_extended':False,
            'private_memory_or_credentials_exported':False,'canonical_effects':0,'actual_owner_outcome':None,
            'authority_effect':'none','whole_API_qualified':False,'task_complete':False,'goal_complete':False,
            'claim_ceiling':'Actual current private identity and pure-dispatch refusal checks only; complete Machine/fullAPI and final owner admission remain.'}
    output=RUN/'API85-Machine-scope-refusals-0001.json'
    with output.open('x') as stream:json.dump(report,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':report['result'],'binding':bind(output),'actual_cases':result.testsRun}),flush=True)
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':raise SystemExit(main())
