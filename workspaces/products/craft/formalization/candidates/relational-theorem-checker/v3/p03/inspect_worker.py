"""Dedicated interpreter for the accepted shared saved-evidence checker."""
from pathlib import Path
import json
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'p02'))
import evidence

if __name__=='__main__':
    try:
        envelope=evidence.c.decode(sys.stdin.buffer.read())
        result=evidence.validate(envelope['request'],envelope['result'])
        print(json.dumps({'ok':True,'value':result}))
    except Exception as e:
        print(json.dumps({'ok':False,'error':str(e).splitlines()[0]}));sys.exit(2)
