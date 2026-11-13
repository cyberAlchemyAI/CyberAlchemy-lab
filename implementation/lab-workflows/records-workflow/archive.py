"""Bounded regular-file archive I/O. No Define or Lab business decisions."""
import io,json,sys,tarfile,base64
from pathlib import Path,PurePosixPath
q=json.load(sys.stdin);target=Path(q["output"]).resolve();target.mkdir(parents=True,exist_ok=False)
raw=base64.b64decode(q["archive"],validate=True)
if len(raw)>8*1024*1024:raise ValueError("archive-byte-bound")
with tarfile.open(fileobj=io.BytesIO(raw),mode="r:gz") as archive:
 members=archive.getmembers()
 if len(members)>4096 or sum(m.size for m in members)>64*1024*1024:raise ValueError("archive-expansion-bound")
 seen=set()
 for member in members:
  name=PurePosixPath(member.name)
  if name.is_absolute() or ".." in name.parts or not member.isfile() or member.name in seen:raise ValueError("archive-unsafe-member")
  seen.add(member.name);out=target.joinpath(*name.parts)
  out.parent.mkdir(parents=True,exist_ok=True)
  with out.open("xb") as stream:stream.write(archive.extractfile(member).read())
print(json.dumps({"files":len(members)}))
