"""Read-only exact preimage/postimage verification; does not apply this proposal."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ledger=json.loads((HERE/'patch-ledger.json').read_bytes())
for row in ledger['rows']:
 target=ROOT/row['target'];post=ROOT/row['postimage']
 assert sha(post)==row['postimage_sha256'],'postimage changed'
 if row['preimage_sha256'] is None:assert not target.exists(),'new target already exists'
 else:assert target.is_file() and not target.is_symlink() and sha(target)==row['preimage_sha256'],'target preimage changed'
for row in json.loads((HERE/'PREIMAGE-AND-RETAINED-INPUTS.json').read_bytes())['files']:
 p=ROOT/row['path'];assert p.is_file() and not p.is_symlink() and sha(p)==row['sha256'],'consumed preimage changed'
print(json.dumps({'result':'PASS-exact-static-preimages-postimages','targets':len(ledger['rows']),'shared_files_written':False,'runtime_or_full_source_guard_PASS_claimed':False}))
