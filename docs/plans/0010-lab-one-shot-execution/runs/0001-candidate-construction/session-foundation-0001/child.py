"""Private fixture IPC for the actual read custody kernel; not a Lab API server."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[6]
PACKAGE=ROOT/'implementation/lab-continuity/candidates/v2'
sys.path.insert(0,str(PACKAGE))
os.environ['R03_GENERATOR_SHA']='4dd5907dc1269e2b0f15a217cd1e60a277554b69889ea76f1e2e571e3fd3010e'
from test_foundation import *
from native_reader import NativePins,NativeReadStore


def main():
    value=load(Path(sys.argv[1]));root=Path(value['root'])
    store=VerifiedLegacyReadStore(root/'source',ROOT,ROOT,ReplayPins(**value['store_pins']))
    native=NativeReadStore(root/'native/semantic',root/'native/governance',value['native_request'],NATIVE,NativePins(**value['native_pins']))
    manager=custodian(root/'custody',store,value['snapshot'],native)
    print(json.dumps({'kind':'ready','pid':os.getpid(),'authority_effect':'none'}),flush=True)
    try:
        for line in sys.stdin:
            request=json.loads(line);op=request['operation']
            try:
                if op=='open':result=manager.open(PRINCIPAL,request['key'])
                elif op=='inspect':result=manager.inspect(PRINCIPAL,request['session_ref'])
                elif op=='close':result=manager.close_consumer(PRINCIPAL,request['session_ref'],request['expected_binding'])
                elif op=='note':result=manager.note(PRINCIPAL,request['session_ref'],request['text'])
                elif op=='stop':break
                else:raise ValueError('unsupported fixture IPC')
                reply={'kind':'result','operation':op,'result':result}
            except Exception as error:reply={'kind':'error','operation':op,'reason':str(error)}
            print(json.dumps(reply),flush=True)
    finally:
        manager.close()
    return 0

if __name__=='__main__':sys.exit(main())
