"""Observed child-process stdio authentication, read handlers and refusal paths."""
from contextlib import contextmanager
import copy
import os
from pathlib import Path
import select
import subprocess
import sys
import tempfile
import time
from fixtures import *


class Child:
    def __init__(self,policy,pin,out):
        self.out=out;self.frames=[]
        self.stderr=(out/'child.stderr').open('xb')
        self.process=subprocess.Popen([sys.executable,str(HERE/'serve.py'),'--policy',str(policy),'--policy-sha256',pin],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr)
    def receive(self):
        start=time.monotonic()
        while True:
            ready,_,_=select.select([self.process.stdout],[],[],1)
            if ready:
                raw=self.process.stdout.readline()
                source.require(raw.endswith(b'\n'),'child terminated before a complete observed frame')
                self.frames.append(('server',raw[:-1]));return frame_parse(raw[:-1])
            source.require(self.process.poll() is None,'child terminal before expected response')
            source.require(time.monotonic()-start<60,'owned reader observation deadline exceeded')
    def send(self,raw,newline=True):
        self.frames.append(('client',raw));self.process.stdin.write(raw+(b'\n' if newline else b''));self.process.stdin.flush()
    def invoke(self,value):self.send(compact(value));return self.receive()
    def finish(self):
        if not self.process.stdin.closed:self.process.stdin.close()
        code=self.process.wait(timeout=30);self.stderr.close()
        self.process.stdout.close()
        return code
    def retain(self):
        rows=[]
        for index,(direction,raw) in enumerate(self.frames):
            name=f'{index:04d}-{direction}.json'
            # Retain arbitrary malformed byte frames separately without claiming JSON.
            try:frame_parse(raw)
            except Exception:name=f'{index:04d}-{direction}.wire'
            (self.out/name).write_bytes(raw)
            rows.append({'direction':direction,'file':name,'sha256':source.sha(raw),'size_bytes':len(raw)})
        (self.out/'frames.json').write_bytes(source.encoded({'framing':'LF excluded from exact wire hashes','frames':rows}))
    def cancel(self):
        if self.process.poll() is None:
            self.process.terminate();self.process.wait(timeout=30)
        if not self.stderr.closed:self.stderr.close()


@contextmanager
def child_case(root,name,configure=None):
    out=root/name;out.mkdir()
    with tempfile.TemporaryDirectory(prefix='cal-R03-api-owned-') as temp:
        owned=Path(temp);key,policy,pin=provision(owned)
        if configure:
            value=frame_parse(policy.read_bytes());configure(value);policy.write_bytes(compact(value));pin=source.sha(policy.read_bytes())
        (out/'original-public-reader-policy.json').write_bytes(policy.read_bytes())
        child=Child(policy,pin,out)
        try:yield child,key,policy,out
        finally:child.retain();child.cancel()
    source.require(not owned.exists(),'owned API credential/policy cleanup incomplete')


def run(destination):
    destination=Path(destination).resolve()
    source.require(destination.is_relative_to(ROOT/'product/lab/release-candidates/v1/examples/operator-journeys/api')
        and not destination.exists(),'fresh selected API example root required')
    destination.mkdir(parents=True);observations=[];foreign_cursor=None
    def record(name,code,checks):
        observations.append({'name':name,'terminal_exit_code':code,'checks':checks,'result':'PASS',
            'authority_effect':'none','canonical_effects':0,'local_authoring_effects':0,'private_keys_exported':False,'owned_credentials_removed':True})
        print(name,code,flush=True)
    with child_case(destination,'authenticated-discovery') as (client,key,policy,out):
        challenge=client.receive();client.send(proof(key,challenge));authenticated=client.receive()
        source.require(authenticated['schema_version']=='lab-local-reader-authenticated/v1-candidate','actual handshake did not authenticate')
        context=authenticated['context'];status=client.invoke(call(context,'lab.status'))
        source.require(status['kind']=='result' and status['message']['supported_operations']==list(SUPPORTED),'actual status handler differs')
        selected=status['message']['source_cut'];catalog=client.invoke(call(context,'catalog.get',selected,limit=10))
        source.require(catalog['kind']=='result' and len(catalog['message']['relation_signatures'])==41,'actual catalog failed')
        foreign_cursor=catalog['message']['next_page_cursor']
        page=client.invoke(call(context,'catalog.get',selected,limit=10,page_cursor=foreign_cursor))
        source.require(page['kind']=='result' and not ({e['carrier_ref'] for e in page['message']['contract_entries']}
            & {e['carrier_ref'] for e in catalog['message']['contract_entries']}),'actual cursor page duplicates results')
        denied=call(context,'lab.status');denied['message']['actor']['principal_ref']='role:repository-owner'
        source.require(client.invoke(denied)['message']['code']=='unauthorized','actor spoof accepted')
        unsupported=call(context,'lab.status');unsupported['operation']='artifact.inspect'
        source.require(client.invoke(unsupported)['code']=='unsupported-operation','unimplemented API claimed success')
        budget=call(context,'catalog.get',selected,limit=143);budget['max_response_bytes']=4096
        source.require(client.invoke(budget)['message']['code']=='budget-exceeded','partial oversized catalog accepted')
        client.send(b'{"operation":"lab.status","operation":"catalog.get"}')
        source.require(client.receive()['code']=='malformed-json','duplicate JSON accepted over stdio')
        code=client.finish();source.require(code==0,'authenticated child did not close cleanly')
    record('authenticated-discovery',code,['actual one-use signature','exact status/source cut','catalog 41 signatures','bound next page','actor spoof refusal','unsupported operation refusal','bounded response refusal','duplicate key refusal','EOF cleanup'])
    with child_case(destination,'wrong-key') as (client,key,policy,out):
        challenge=client.receive();client.send(proof(Ed25519PrivateKey.generate(),challenge));reply=client.receive()
        source.require(reply['code']=='unauthenticated-channel' and 'context' not in reply,'wrong credential disclosed context')
        code=client.finish();source.require(code==2,'wrong credential process not terminal refusal')
    record('wrong-key',code,['invalid cryptographic signature','no trusted context/source disclosure'])
    with child_case(destination,'foreign-challenge') as (client,key,policy,out):
        challenge=client.receive();challenge['connection_ref']='connection:foreign';client.send(proof(key,challenge));reply=client.receive()
        source.require(reply['code']=='unauthenticated-channel','foreign connection proof accepted')
        code=client.finish();source.require(code==2,'foreign challenge process not terminal refusal')
    record('foreign-challenge',code,['challenge connection binding'])
    with child_case(destination,'foreign-cursor') as (client,key,policy,out):
        challenge=client.receive();client.send(proof(key,challenge));context=client.receive()['context']
        selected=client.invoke(call(context,'lab.status'))['message']['source_cut']
        reply=client.invoke(call(context,'catalog.get',selected,limit=10,page_cursor=foreign_cursor))
        source.require(reply['message']['code']=='invalid-cursor','cursor from prior authenticated child accepted')
        code=client.finish();source.require(code==0,'foreign cursor child did not close')
    record('foreign-cursor',code,['cross-process/context cursor refusal'])
    with child_case(destination,'oversized-frame') as (client,key,policy,out):
        challenge=client.receive();client.send(proof(key,challenge));context=client.receive()['context']
        client.send(b'x'*70000);reply=client.receive();source.require(reply['code']=='input-too-large','oversized wire accepted')
        source.require(client.invoke(call(context,'lab.status'))['kind']=='result','oversized frame corrupted next frame boundary')
        code=client.finish();source.require(code==0,'oversized frame child did not close')
    record('oversized-frame',code,['bounded frame refusal','safe next-frame recovery'])
    with child_case(destination,'revoked-policy') as (client,key,policy,out):
        challenge=client.receive();client.send(proof(key,challenge));context=client.receive()['context']
        value=frame_parse(policy.read_bytes());value['revoked']=True;policy.write_bytes(compact(value))
        reply=client.invoke(call(context,'lab.status'));source.require(reply['code']=='unauthenticated-channel','revoked policy accepted read')
        code=client.finish();source.require(code==0,'revocation child did not close')
    record('revoked-policy',code,['live policy invalidation before read'])
    with child_case(destination,'expired-policy',lambda p:p.update(expires_at='2000-01-01T00:00:00Z')) as (client,key,policy,out):
        reply=client.receive();source.require(reply['code']=='unauthenticated-channel','expired policy started authenticated channel')
        code=client.finish();source.require(code==2,'expired policy process not terminal refusal')
    record('expired-policy',code,['expiry before challenge/source access'])
    with child_case(destination,'truncated-frame') as (client,key,policy,out):
        challenge=client.receive();client.send(proof(key,challenge));context=client.receive()['context']
        client.send(b'{"partial":',newline=False);client.process.stdin.close()
        reply=client.receive();source.require(reply['code']=='invalid-envelope','unterminated frame accepted')
        code=client.finish();source.require(code==0,'truncated frame child did not close')
    record('truncated-frame',code,['incomplete frame refusal','EOF cleanup'])
    result={'result':'PASS','authority_effect':'none','actual_owner_outcome':None,'human_pilot':False,
        'episodes':observations,'child_processes':8,'private_keys_exported':False,'Session_memory_exported':False,
        'original_domain_cases_reexecuted':0,'canonical_effects_applied':0,'local_authoring_transactions':0}
    (destination/'result.json').write_bytes(source.encoded(result))
    return result


if __name__=='__main__':
    source.require(len(sys.argv)==2,'usage: exercise_stdio.py fresh-selected-example-directory')
    run(sys.argv[1])
