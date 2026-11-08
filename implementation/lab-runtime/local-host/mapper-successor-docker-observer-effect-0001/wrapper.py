"""Exact one-shot selection of PASS-reviewed Mapper external observer bytes."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
REPO = HERE.parents[3]
PREVIOUS = LOCAL/'mapper-successor-docker-observer-0002'
PREVIOUS_FREEZE = PREVIOUS/'freeze.json'
PREVIOUS_REVIEW = LOCAL/'MAPPER-SUCCESSOR-DOCKER-OBSERVER-INDEPENDENT-STATIC-REVIEW-0002.md'
SELF_FREEZE = HERE/'freeze.json'
PREVIOUS_FREEZE_SHA = '356a3abd41a28a3400f22f8e1aac35f33e7176893090c3a27783cd51b99b4a07'
PREVIOUS_REVIEW_SHA = 'a76d0fd9245dcce50e362df0f087a2658c1d243c691b085f0176b6b60100ab0b'
OBSERVER_SHA = '119ee270ddf26bd00ecfad18752d0380601aca362966bd5f70ed2623930ebbe4'
RELEASE_FREEZE_SHA = 'ce6356ef776c20d89286cc116c1750eeae6df9fb7a640e6dc545634c5b656452'
RELEASE_REVIEW_SHA = '816fa66234f9ac8ccb69ca6d4d1f1657ad3f0c80e4babe644385df3ab4e94ea8'
OBSERVATION = Path('/home/vlad_/.local/state/cyberalchemy-lab-observations/mapper-successor-docker-release-0001')
ATTEMPT = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/mapper-attempt/docker-attempt')
NAME = 'cal-mapper-only-20261020-0002-successor-0001'
EFFECT_ENABLED = True
DIR_FLAGS = os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
LEAF_FLAGS = os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC


class Refused(RuntimeError): pass


def need(ok,code):
    if not ok: raise Refused(code)


def sha(raw): return hashlib.sha256(raw).hexdigest()


def close_all(fds,primary=None):
    errors = []
    for fd in reversed(fds):
        try: os.close(fd)
        except BaseException as exc: errors.append(exc)
    if primary is not None:
        for exc in errors: primary.add_note('pin cleanup: '+type(exc).__name__)
        return
    if errors:
        first = errors[0]
        for exc in errors[1:]: first.add_note('additional pin cleanup: '+type(exc).__name__)
        raise first


def checked_bytes(path,expected=None,*,limit=2*1024*1024):
    path = Path(path)
    need(path.is_absolute() and '..' not in path.parts,'ABSOLUTE_PIN_PATH')
    fds = [os.open('/',DIR_FLAGS)]
    try:
        for part in path.parent.parts[1:]:
            fds.append(os.open(part,DIR_FLAGS,dir_fd=fds[-1]))
        for fd in fds:
            st = os.fstat(fd)
            need(stat.S_ISDIR(st.st_mode) and st.st_uid in (0,os.getuid()) and
                 not(st.st_mode & 0o022),'PIN_ANCESTOR_CUSTODY')
        parent = fds[-1]
        before = os.stat(path.name,dir_fd=parent,follow_symlinks=False)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             before.st_uid == os.getuid() and not(before.st_mode & 0o022) and
             0 < before.st_size <= limit,'PIN_LEAF_SHAPE')
        leaf = os.open(path.name,LEAF_FLAGS,dir_fd=parent)
        fds.append(leaf)
        key = lambda st:(st.st_dev,st.st_ino,st.st_mode,st.st_uid,st.st_gid,
                         st.st_nlink,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
        need(key(os.fstat(leaf)) == key(before),'PIN_OPEN_DRIFT')
        raw = bytearray()
        while len(raw) <= before.st_size:
            block = os.read(leaf,min(65536,before.st_size+1-len(raw)))
            if not block: break
            raw.extend(block)
        named = os.stat(path.name,dir_fd=parent,follow_symlinks=False)
        need(len(raw) == before.st_size and
             key(os.fstat(leaf)) == key(named) == key(before) and
             (expected is None or sha(raw) == expected),'PIN_CONTENT_DRIFT')
        return bytes(raw)
    finally:
        close_all(fds,sys.exception())


def parse(raw):
    def pairs(rows):
        value = {}
        for key,item in rows:
            need(key not in value,'DUPLICATE_JSON_KEY')
            value[key] = item
        return value
    value = json.loads(raw,object_pairs_hook=pairs)
    need(type(value) is dict,'PIN_JSON_OBJECT')
    return value


def check_rows(rows,directory,names):
    need(type(rows) is list and len(rows) == len(names),'PIN_BINDINGS')
    captured = {}
    for row,name in zip(rows,names):
        need(type(row) is dict and row.get('path') == str((directory/name).relative_to(REPO))
             and type(row.get('size')) is int and 0 < row['size'] <= 2*1024*1024 and
             type(row.get('sha256')) is str and len(row['sha256']) == 64,
             'PIN_BINDING_ROW')
        raw = checked_bytes(directory/name,row['sha256'],limit=row['size'])
        need(len(raw) == row['size'],'PIN_BINDING_SIZE')
        captured[name] = raw
    return captured


def load_reviewed_observer():
    own = parse(checked_bytes(SELF_FREEZE,limit=65536))
    need(own == {'schema':'lab-mapper-successor-docker-observer-effect-freeze/v1',
                 'status':'READY_FOR_INDEPENDENT_STATIC_REVIEW_NO_EFFECT_YET',
                 'effect':'NOT_RUN','effect_enabled':True,'no_retry':True,
                 'predecessor_freeze_sha256':PREVIOUS_FREEZE_SHA,
                 'predecessor_review_sha256':PREVIOUS_REVIEW_SHA,
                 'observer_sha256':OBSERVER_SHA,
                 'observation':str(OBSERVATION),'attempt':str(ATTEMPT),
                 'file_bindings':own.get('file_bindings')},
         'WRAPPER_FREEZE_CONTRACT')
    check_rows(own['file_bindings'],HERE,('wrapper.py','tests.py','HANDOFF.md'))
    review = checked_bytes(PREVIOUS_REVIEW,PREVIOUS_REVIEW_SHA,limit=262144)
    need(b'**Verdict: PASS for the bounded effect-disabled correction.**' in review
         and PREVIOUS_FREEZE_SHA.encode() in review,'OBSERVER_PASS_REVIEW')
    previous = parse(checked_bytes(PREVIOUS_FREEZE,PREVIOUS_FREEZE_SHA,limit=65536))
    need(previous['schema'] == 'lab-mapper-successor-docker-external-observer-freeze/v2'
         and previous['status'] == 'READY_FOR_INDEPENDENT_STATIC_REVIEW_NO_EFFECT_YET'
         and previous['effect'] == 'NOT_RUN' and previous['effect_enabled'] is False
         and previous['release_freeze_sha256'] == RELEASE_FREEZE_SHA
         and previous['release_review_sha256'] == RELEASE_REVIEW_SHA
         and previous['observation'] == str(OBSERVATION)
         and previous['attempt'] == str(ATTEMPT) and previous['no_retry'] is True,
         'OBSERVER_FROZEN_SCOPE')
    selected = check_rows(previous['file_bindings'],PREVIOUS,
                          ('observer.py','tests.py','HANDOFF.md'))
    need(sha(selected['observer.py']) == OBSERVER_SHA,'EXACT_OBSERVER_SOURCE')
    module = types.ModuleType('cal_reviewed_mapper_external_observer_0002')
    module.__file__ = str(PREVIOUS/'observer.py')
    exec(compile(selected['observer.py'],module.__file__,'exec'),module.__dict__)
    need(module.EFFECT_ENABLED is False and module.OBSERVATION == OBSERVATION and
         module.ATTEMPT == ATTEMPT and module.NAME == NAME and
         module.FREEZE_SHA == RELEASE_FREEZE_SHA and
         module.REVIEW_SHA == RELEASE_REVIEW_SHA and
         module.COMMAND == ['/usr/bin/python3','-B',str(module.RELEASE),
                            '--execute-reviewed-one-shot'],
         'SELECTED_OBSERVER_IDENTITY')
    return module


def preflight(loader=load_reviewed_observer):
    selected = loader()
    result = selected.preflight()
    need(result['effect'] == 'NOT_RUN' and
         result['observation'] == str(OBSERVATION) and
         result['release']['freeze_sha256'] == RELEASE_FREEZE_SHA and
         result['release']['review_sha256'] == RELEASE_REVIEW_SHA and
         result['release']['release_sha256'] == selected.RELEASE_SHA,
         'SELECTED_PREFLIGHT_DRIFT')
    return {key:value for key,value in result.items()
            if key != 'preflight_stdout'}


def dispatch(loader=load_reviewed_observer):
    need(EFFECT_ENABLED is True,'WRAPPER_EFFECT_DISABLED')
    selected = loader()
    # One captured, compiled source buffer supplies both the final preflight
    # and the one-shot external process observer. No pathname re-import occurs.
    result = selected._run_once(preflight_fn=selected.preflight)
    need(result['status'] == 'PROVISIONAL_OS_ZERO_FINAL_JOIN' and
         result['no_retry'] is True and
         result['independent_effect_review'] == 'PENDING',
         'OBSERVER_NOT_PROVISIONAL')
    return result


if __name__ == '__main__':
    if sys.argv[1:] == ['--preflight']:
        print(json.dumps(preflight(),sort_keys=True))
    elif sys.argv[1:] == ['--execute-reviewed-one-shot']:
        print(json.dumps(dispatch(),sort_keys=True))
    else:
        raise SystemExit('expected --preflight or --execute-reviewed-one-shot')
