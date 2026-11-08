"""Exact retained issuance procedure; substitute only the trusted worker dispatch."""
from pathlib import Path
import hashlib
import json
HERE=Path(__file__).resolve().parent
text=(HERE.parent/'p06/api.py').read_text()
start=text.index('    def qualify(self,raw,*,cancel=None):');end=text.index('\n    def live_event',start)
original=text[start:end]
old="[sys.executable,str(HERE/'qualification_worker.py')]";new='self.worker_command()'
assert original.count(old)==1
adapted=original.replace(old,new)
assert adapted.replace(new,old)==original
(HERE/'generated_api.py').write_text('"""Exact P06 issuance with fixed owned-worker dispatch."""\nfrom ..p06.api import *\nclass OwnedIssuance:\n'+adapted+'\n')
(HERE/'api-recipe-review.json').write_text(json.dumps({'result':'pass','retained_sha256':hashlib.sha256(original.encode()).hexdigest(),'roundtrip':'exact','only_edit':'fixed P07 worker command supplied by the trusted API class','authority_effect':'none'},indent=2)+'\n')
