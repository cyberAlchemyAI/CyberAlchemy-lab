"""Exact independently pinned preparation baseline; selections grant no authority."""
import hashlib,json,os,stat
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[6]
BASELINE_PIN='9632f298d7faccf903aaa2adbea41c09fe00ca28fd92f06a6f58fc8ba249a742'
def need(value, reason):
    if not value:
        raise ValueError(reason)
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def parse(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate selected JSON key'); result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: need(False, 'nonfinite selected JSON'))
def exact(binding, limit=16 * 1024 * 1024):
    need(type(binding) is dict and set(binding) == {'path', 'sha256'}, 'closed exact binding required')
    relative = Path(binding['path'])
    need(not relative.is_absolute() and relative.as_posix() == binding['path'] and '..' not in relative.parts,
         'canonical repository locator required')
    path = ROOT / relative; descriptors = [os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)]
    links = []
    try:
        parent = descriptors[-1]
        for part in path.parts[1:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            descriptors.append(child); info = os.fstat(child)
            links.append((parent, part, child, (info.st_dev, info.st_ino, info.st_mode, info.st_uid)))
            parent = child
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            before = os.fstat(fd)
            need(stat.S_ISREG(before.st_mode) and before.st_size <= limit, 'bounded selected regular input required')
            def stamp(value):
                return (value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
            parts = []; size = 0
            while block := os.read(fd, min(1024 * 1024, limit + 1 - size)):
                parts.append(block); size += len(block); need(size <= limit, 'selected input grew beyond limit')
            raw = b''.join(parts)
            need(stamp(before) == stamp(os.fstat(fd)) == stamp(os.stat(path.name, dir_fd=parent, follow_symlinks=False))
                 and sha(raw) == binding['sha256'], 'selected bytes or attachment changed')
            for anchor, name, held, identity in reversed(links):
                a = os.stat(name, dir_fd=anchor, follow_symlinks=False); h = os.fstat(held)
                need((a.st_dev, a.st_ino, a.st_mode, a.st_uid) == (h.st_dev, h.st_ino, h.st_mode, h.st_uid) == identity,
                     'selected ancestor detached')
            return raw
        finally:
            os.close(fd)
    finally:
        for fd in reversed(descriptors):
            os.close(fd)

def verify_baseline():
    binding={'path':(HERE/'preparation-baseline.json').relative_to(ROOT).as_posix(),'sha256':BASELINE_PIN}
    baseline=parse(exact(binding))
    need(baseline['authority_effect']=='none' and baseline['parent_recipe_row_count']==28,'closed original recipe baseline required')
    for row in baseline['rows']:
        original=exact(row['original']);retained=exact(row['preimage'])
        need(original==retained and len(original)==row['size_bytes'],'independent immutable baseline changed')
    return baseline

def check_activation(binding,instance):
    # This evidence is only a composition prerequisite. Root still supplies
    # direct execution authorization and the sole sequential runtime slot.
    need(instance=='optimized-0003','exclusive new instance required')
    need(binding['path'].startswith('docs/plans/0011-lab-runtime-completion/runs/0001-execution/T00/'),'Root composition selector required')
    value=parse(exact(binding))
    need(set(value)=={'schema_version','status','authority_effect','instance','margin_merge_binding','observer_merge_binding'},'closed future composition prerequisite required')
    need(value['schema_version']=='lab-T02-family-composition-prerequisite/v1-candidate'
         and value['status']=='merged-reviewed-ready-for-Root-coordination'
         and value['authority_effect']=='none' and value['instance']==instance,'margin/observer merge pending')
    exact(value['margin_merge_binding']);exact(value['observer_merge_binding'])
    return value
