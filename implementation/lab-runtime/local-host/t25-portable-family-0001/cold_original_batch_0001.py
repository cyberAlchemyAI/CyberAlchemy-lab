"""Original byte parity from one actual verified canonical replay cut.

The caller still performs two independent C.open_source replays, with their
original signed/current checks and physical archive entry/exit guards.
"""
from pathlib import Path
def need(value,reason):
 if not value:raise ValueError(reason)
def archive_unchanged(view):
 need(all((view.store/name).read_bytes()==raw for name,raw in view.originals.items()),'cold archive changed during original batch')
 need({p.relative_to(view.store).as_posix() for p in view.store.rglob('*') if p.is_file()}==set(view.originals),'cold archive member set changed during original batch')
def verify(view,base,family):
 archive_unchanged(view)
 index=base.load(family/'source/packages/0001/record-index.json')
 need(type(index)is list and len(index)==26 and len({row['version_ref'] for row in index})==26,'exact26 original Source index required')
 rows=view.handle.custody.content_rows(view.data)
 for selected in index:
  found=[row for row in rows if row['role']=='authored-target' and row['version_ref']==selected['version_ref']]
  need(len(found)==1,'one committed original per exact Source revision required')
  row=found[0];raw=base.original(selected['original_binding']);subject=view.data['projection']['subjects'][selected['version_ref']]
  need(raw==row['raw'] and base.sha(raw)==row['byte_sha256']==selected['original_binding']['sha256']==subject['source']['sha256'],'actual canonical-cut original bytes differ')
  need(base.parse(raw)==subject['record'] and row['structural_value_sha256']==view.handle.common.digest(subject['record']),'actual original semantic record differs')
  need(row['encoding']==selected['encoding']==subject['source']['encoding'] and row['sequence']==int(Path(subject['source']['path']).stem),'actual original transaction or encoding differs')
 need(view.data['head']['transaction_digest']==view.expected['expected_head'] and view.handle.common.digest(view.data['projection'])==view.expected['projection_sha256'] and [view.handle.common.digest(tx) for tx in view.data['transactions']]==view.expected['transaction_sha256s'],'verified canonical replay cut changed during original batch')
 archive_unchanged(view)
 return {'original_records':26,'method':'original custody.content_rows over this independent verified canonical cut','physical_archive_entry_exit_unchanged':True}
