"""Build an explicitly selected public margin software inventory before freeze.

No Lab imports, runtime/configuration creation, credentials or policy defaults.
The independently supplied Root selection must already name reviewed code.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat

HERE = Path(__file__).absolute().parent
ROOT = HERE.parents[6]
API = 'product/lab/release-candidates/v1/interface/api-integration-v17'
MODULES = ('service','workspace','auth','protocol','guard','session_attachment',
           'current_context_sessions','handlers','lesson_assessment','application_journal',
           'observed_margin','margin_capture','margin_kernel','margin_seal')
METHOD = 'product/lab/release-candidates/v1/interface/lesson-assessment-v2-action-0148/preparation.py'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def parse(raw):
    def pairs(rows):
        result = {}
        for name, value in rows:
            if name in result:
                raise ValueError('duplicate inventory input key')
            result[name] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)

def exact(binding):
    if type(binding) is not dict or set(binding) != {'path','sha256'}:
        raise ValueError('closed independent binding required')
    name, pin = binding['path'], binding['sha256']
    if type(name) is not str or type(pin) is not str or re.fullmatch('[a-f0-9]{64}', pin) is None:
        raise ValueError('invalid independent input binding')
    relative = Path(name)
    if not name or relative.is_absolute() or relative.as_posix() != name or '..' in relative.parts or '\\' in name or '\0' in name or name == '.':
        raise ValueError('canonical input locator required')
    path = ROOT / relative
    handles = []; links = []; fd = None
    stamp = lambda s: (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    try:
        parent = os.open('/', os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC); handles.append(parent)
        for part in path.parts[1:-1]:
            child = os.open(part, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC, dir_fd=parent)
            handles.append(child); info = os.fstat(child)
            links.append((parent,part,child,(info.st_dev,info.st_ino,info.st_mode,info.st_uid,info.st_gid))); parent = child
        fd = os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent)
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > 16*1024*1024:
            raise ValueError('bounded regular inventory input required')
        chunks = []; size = 0
        while block := os.read(fd, min(1024*1024,16*1024*1024+1-size)):
            chunks.append(block); size += len(block)
            if size > 16*1024*1024:
                raise ValueError('inventory input grew')
        raw = b''.join(chunks)
        if size != before.st_size or sha(raw) != pin or stamp(before) != stamp(os.fstat(fd)) or stamp(before) != stamp(os.stat(path.name,dir_fd=parent,follow_symlinks=False)):
            raise ValueError('inventory input bytes or attachment changed')
        for anchor,part,held,identity in links:
            a = os.stat(part,dir_fd=anchor,follow_symlinks=False); h = os.fstat(held)
            if (a.st_dev,a.st_ino,a.st_mode,a.st_uid,a.st_gid) != identity or (h.st_dev,h.st_ino,h.st_mode,h.st_uid,h.st_gid) != identity:
                raise ValueError('inventory input ancestor changed')
        return raw
    finally:
        if fd is not None:
            os.close(fd)
        for handle in reversed(handles):
            os.close(handle)

def validate(selection):
    fields = {'schema_version','authority_effect','status','api_directory','module_bindings','policy_schema_binding','assessment_method_binding','merge_review_binding'}
    if type(selection) is not dict or set(selection) != fields:
        raise ValueError('closed Root inventory selection required')
    if selection['schema_version'] != 'lab-T03-margin-software-inputs/v1-candidate' or selection['authority_effect'] != 'none' or selection['status'] != 'Root-selected-reviewed-software':
        raise ValueError('reviewed software selection required')
    if selection['api_directory'] != API or type(selection['module_bindings']) is not dict or set(selection['module_bindings']) != set(MODULES):
        raise ValueError('exact selected API module set required')
    rows = []
    for name in MODULES:
        row = selection['module_bindings'][name]
        if type(row) is not dict or row.get('path') != API+'/'+name+'.py':
            raise ValueError('true selected module origin required')
        exact(row); rows.append(row)
    for key, expected in [('policy_schema_binding',API+'/observed-margin-policy.schema.json'),('assessment_method_binding',METHOD)]:
        row = selection[key]
        if type(row) is not dict or row.get('path') != expected:
            raise ValueError('true selected schema/method origin required')
        exact(row); rows.append(row)
    exact(selection['merge_review_binding'])
    return sorted(rows,key=lambda row:row['path'])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--selection',required=True); parser.add_argument('--selection-sha256',required=True)
    parser.add_argument('--output',required=True)
    args = parser.parse_args()
    if re.fullmatch(r'software-[0-9]{4}\.json',args.output) is None:
        raise ValueError('exclusive owned inventory filename required')
    binding = {'path':args.selection,'sha256':args.selection_sha256}
    selection = parse(exact(binding)); rows = validate(selection)
    value = {'schema_version':'lab-T03-observed-margin-software/v1-candidate','authority_effect':'none','files':rows}
    raw = (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
    for row in rows:
        exact(row)
    exact(binding); exact(selection['merge_review_binding'])
    path = HERE/args.output
    fd = os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    with os.fdopen(fd,'wb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps({'result':'PREPARED-selected-software-inventory','software_binding':{'path':path.relative_to(ROOT).as_posix(),'sha256':sha(raw)},'file_count':len(rows),'runtime_executed':False,'task_complete':False}))

if __name__ == '__main__':
    main()
