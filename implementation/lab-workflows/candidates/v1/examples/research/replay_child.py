#!/usr/bin/env python3
"""One fresh, independently pinned replay observation; owns and removes its store."""
from pathlib import Path
import base64,json,sys,tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'workflows'))
from research import *


def observe(approach,archive_sha,owned_parent=None):
    require(approach in ['direct','facade'],'unselected replay approach')
    raw=ARCHIVE.read_bytes();require(byte_sha(raw)==archive_sha,'independent archive pin differs')
    archive=parse(raw);require(archive['private_key_included'] is False and archive['Session_memory_included'] is False,'private archive material forbidden')
    sys.path.insert(0,str(BRIDGE))
    from lab_runtime.replay import ReplayPins,full_replay
    from lab_runtime.store import VerifiedLegacyReadStore
    from lab_runtime.common import digest
    if owned_parent is not None:
        parent=Path(owned_parent);require(parent.is_dir() and not parent.is_symlink() and parent.name.startswith('lab-W04-owned-child-'),'selected child root not owned')
    with tempfile.TemporaryDirectory(prefix='lab-W04-public-replay-',dir=owned_parent) as temporary:
        store=Path(temporary)/'store';store.mkdir(mode=0o700)
        for name,row in archive['files'].items():
            require(not Path(name).is_absolute() and '..' not in Path(name).parts,'archived file outside owned store')
            body=base64.b64decode(row['base64_original_bytes'],validate=True);require(byte_sha(body)==row['sha256'],'archive original file differs')
            p=store/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(body)
        pins=ReplayPins(**archive['project_pins'])
        # Offline committed-byte reconstruction, not current live-repository verification.
        result=(full_replay(store,ROOT,ROOT,pins,require_current=False) if approach=='direct' else
            VerifiedLegacyReadStore(store,ROOT,ROOT,pins).replay(require_current=False))
        require(result['head']['transaction_digest']==pins.expected_head,'replayed actual HEAD differs')
        return {'authority_effect':'none','approach':approach,'archive_sha256':archive_sha,
            'projection_sha256':digest(result['projection']),'head':result['head']['transaction_digest'],
            'actual_owner_outcome':None,'cache_enabled':False,'owned_store_removed_on_return':True}


if __name__=='__main__':
    require(len(sys.argv)==4,'exact approach, archive pin and owned parent required')
    print(json.dumps(observe(sys.argv[1],sys.argv[2],sys.argv[3]),sort_keys=True),flush=True)
