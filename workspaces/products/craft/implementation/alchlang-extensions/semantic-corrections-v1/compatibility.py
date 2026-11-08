"""Strict candidate compatibility; no general migration/equivalence claim."""
import hashlib
import json
from pathlib import Path


def fingerprint(bundle):
    bundle=Path(bundle)
    cfg=json.loads((bundle/'host.json').read_bytes())
    event=json.loads((bundle/'config.json').read_bytes())
    event.pop('binding_digest',None)
    contract={'profile':'alch.compatible-state/v1','event':event,
              'host':{k:cfg[k] for k in ('id','runtime','events','isolation','operation','actors','boundary','consumer','transport')},
              'runtime':{p:hashlib.sha256((bundle/p).read_bytes()).hexdigest() for p in
                         ('rust/src/lib.rs','rust/src/main.rs','rust/src/mappings.rs','rust/Cargo.toml','rust/Cargo.lock','local_worker.py')}}
    return hashlib.sha256(json.dumps(contract,sort_keys=True,separators=(',',':')).encode()).hexdigest()
