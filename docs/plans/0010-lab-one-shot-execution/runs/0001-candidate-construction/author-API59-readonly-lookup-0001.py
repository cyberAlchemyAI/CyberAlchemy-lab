"""Preserve API58 and author a successor for genuinely read-only lookup."""
from pathlib import Path
import shutil

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
def replace(path,before,after):
    text=path.read_text();assert text.count(before)==1,(path,before)
    path.write_text(text.replace(before,after,1))
def main():
    api=BASE/'api-v59';composition=BASE/'lesson-host-composition-v9'
    assert not api.exists() and not composition.exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(BASE/'api-v58',api,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v8',composition,ignore=ignore)
    replace(composition/'host.py','api-v58/service.py','api-v59/service.py')
    replace(api/'lesson_selection.py','lesson-host-composition-v8','lesson-host-composition-v9')
    path=api/'workspace.py'
    replace(path,"    def lock(self):\n        self.guard();fd=os.open(self.root/'.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)",
        "    def lock(self,*,create=True):\n        self.guard()\n        flags=(os.O_RDWR|os.O_CREAT) if create else os.O_RDONLY\n        fd=os.open(self.root/'.lock',flags|os.O_NOFOLLOW,0o600)")
    replace(path,"    def lookup(self,lookup,context):\n        with self.lock():",
        "    def lookup(self,lookup,context):\n        # An empty journal is a valid read observation. Its first durable lock\n        # is created only by claim(), after public preflight succeeds. A later\n        # claim rechecks the fingerprint under the exclusive writer lock.\n        self.guard()\n        if not (self.root/'.lock').exists():\n            durable=('.allocated.json','.claim.json','.result.json','.pending-evidence.json')\n            source.require(not any(p.name.endswith(durable) for p in (self.root/'journal').iterdir()),\n                'durable journal without its lock requires reconciliation')\n            self.guard()\n            return None,None\n        # Never recreate a removed lock while inspecting an existing journal.\n        with self.lock(create=False):")
    with (api/'READONLY-LOOKUP.md').open('x') as f:f.write('''# Read-only operation lookup

API58's full export suite found that refusal before claim still created an empty
workspace `.lock`. API59 preserves the original API58 source and evidence and
changes operation lookup to make an empty-journal observation without writing.

An authorized claim still creates the exclusive lock and rechecks the exact key,
fingerprint and prior result before any dispatch. Inspection of an existing lock
opens it without creation. A durable journal whose lock is missing is refused;
inspection and retry do not recreate it. A concurrent first claim can follow an
empty observation, and the claim's original locked recheck remains authoritative.

The host authority, original source guards, clocks, native validation, export
publisher and all public contracts remain unchanged. Actual export and recovery
checks are required on the new source; predecessor qualification does not transfer.
''')
    print('Authored API59 read-only lookup successor; freeze and actual checks remain required.',flush=True)
if __name__=='__main__':main()
