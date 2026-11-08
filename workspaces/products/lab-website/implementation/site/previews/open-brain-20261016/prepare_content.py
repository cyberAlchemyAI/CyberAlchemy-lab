from pathlib import Path
import re,json,hashlib
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
source=ROOT/'docs/proposals/0010-lab-craft-content/COPY-DECK.md'
s=source.read_text()
# Public content is delimited by explicit editorial markers, not by visual heading levels.
blocks={};current=None;public=False
for line in s.splitlines():
 m=re.match(r'^### ([A-Z]+-\d{2}|ST-[ABC])\b',line)
 major=re.match(r'^## (\d+)\. ',line)
 if m:current=m.group(1);blocks.setdefault(current,[]);public=False;continue
 if major:
  n=int(major.group(1));current={4:'REP',5:'HAND'}.get(n);public=False
  if current:blocks.setdefault(current,[])
  continue
 if line.startswith('**Public copy'):
  public=True;continue
 if line.startswith('**Editorial / placement') or line.startswith('**Maintained source basis:'):
  public=False;continue
 if current and public:blocks[current].append(line)
blocks={k:'\n'.join(v).strip() for k,v in blocks.items()}
(HERE/'copy.json').write_text(json.dumps(blocks,indent=2,ensure_ascii=False))
# All production sources and the complete current output are inspected, never written.
paths=list((ROOT/'website/source').rglob('*'))+list((ROOT/'website/dist').rglob('*'))
paths+=list((ROOT/'website').glob('*.py'))+list((ROOT/'website').glob('*.json'))
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
(HERE/'baseline.json').write_text(json.dumps(manifest,indent=2))
print('Public copy blocks:',len(blocks),'Preservation hashes:',len(manifest))
