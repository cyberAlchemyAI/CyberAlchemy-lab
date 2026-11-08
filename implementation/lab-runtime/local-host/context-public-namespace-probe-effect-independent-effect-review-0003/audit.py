"""Read-only independent join of the retained public probe0003 effect."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
LOCAL = REPO / 'implementation/lab-runtime/local-host'
STATE = Path('/home/vlad_/.local/state/cyberalchemy-lab')
OBS = Path('/home/vlad_/.local/state/cyberalchemy-lab-observations')
OUTER = OBS / 'context-public-probe-wrapper-20261020-0003'
INNER = OBS / 'context-public-only-probe-20261020-0003'
ATTEMPT = STATE / 'context-public-only-probe-20261020-0003'
NAME = 'cal-context-public-only-probe-20261020-0003'
CID = '70cf0e15a963a1a2584a9a506e4bd3ce4eea5a3c0a8b060ffe61b836c999e264'
EMPTY = hashlib.sha256(b'').hexdigest()
REQUEST = b'{"public_probe":true,"ordinal":1}\n'


def need(ok, code):
    if not ok:
        raise RuntimeError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path, mode=None):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             before.st_uid == os.getuid() and before.st_size <= 2*1024*1024 and
             (mode is None or stat.S_IMODE(before.st_mode) == mode), 'LEAF_CUSTODY')
        raw = b''
        while len(raw) <= before.st_size:
            block = os.read(fd, min(65536, before.st_size + 1 - len(raw)))
            if not block:
                break
            raw += block
        after = os.fstat(fd)
        need(len(raw) == before.st_size and
             (before.st_dev, before.st_ino, before.st_mode, before.st_size) ==
             (after.st_dev, after.st_ino, after.st_mode, after.st_size),
             'LEAF_CHANGED')
        return raw
    finally:
        os.close(fd)


def doc(path, mode=0o600):
    return json.loads(read(path, mode))


def check_dir(path):
    st = path.lstat()
    need(stat.S_ISDIR(st.st_mode) and st.st_uid == os.getuid() and
         stat.S_IMODE(st.st_mode) == 0o700, 'ROOT_CUSTODY')


def docker(argv):
    result = subprocess.run(argv, input=b'', stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=10, check=False,
                            env={'PATH':'/usr/bin:/bin','HOME':'/home/vlad_'})
    return {'os_exit':result.returncode, 'stdout':result.stdout,
            'stderr':result.stderr}


def main():
    for root in (OUTER, INNER, ATTEMPT):
        check_dir(root)
    wrapper_dir = LOCAL/'context-public-namespace-probe-effect-0003'
    release_dir = LOCAL/'context-public-namespace-probe-release-0003'
    static_review = LOCAL/'context-public-namespace-probe-effect-independent-static-review-0003/REVIEW.md'
    wf = read(wrapper_dir/'freeze.json')
    rf = read(release_dir/'freeze.json')
    need(sha(wf) == 'd280d5ea3be0588c79545043530a41e2102698990e4ebb5b1277d3bd596d7e2a' and
         sha(rf) == 'dbb060c109750ac31b3a2b0d25f4a4a3d753787c86077c066a423c90f6c34535' and
         sha(read(static_review)) == '9580350b83ac36c06ba7d8fceabd7ede8e15358c7fcb0b4a459243f28affd710',
         'FROZEN_REVIEW_BINDING')
    for base,freeze in ((wrapper_dir,json.loads(wf)),(release_dir,json.loads(rf))):
        binding = freeze.get('bindings',freeze.get('file_bindings'))
        rows = binding if isinstance(binding,list) else [
            {'path':name,'sha256':digest} for name,digest in binding.items()]
        for row in rows:
            path = REPO/row['path'] if '/' in row['path'] else base/row['path']
            raw = read(path)
            need(sha(raw) == row['sha256'] and
                 ('size' not in row or len(raw) == row['size']), 'FROZEN_MEMBER_DRIFT')
    oi = doc(OUTER/'intent.json')
    oraw = read(OUTER/'stdout.bin',0o600)
    eraw = read(OUTER/'stderr.bin',0o600)
    result = doc(OUTER/'result.json')
    need(oi['wrapper_freeze_sha256'] == sha(wf) and
         oi['independent_review_sha256'] == sha(read(static_review)) and
         oi['argv'] == ['/usr/bin/python3.14','-I','-B','-S',
             str(wrapper_dir/'wrapper.py'),'--observe-reviewed-one-shot'] and
         oi['retry_allowed'] is False and
         type(result['os_exit_code']) is int and result['os_exit_code'] == 0 and
         result['process_error'] is None and
         result['stdout_sha256'] == sha(oraw) and
         result['stdout_size'] == len(oraw) and
         result['stderr_sha256'] == sha(eraw) == EMPTY and
         result['stderr_size'] == len(eraw) == 0 and
         result['retry_allowed'] is False and
         oi['created_at_ns'] < result['finished_at_ns'], 'OUTER_OBSERVATION')
    outer = json.loads(oraw)
    inner = doc(INNER/'observation.json')
    iraw = read(INNER/'stdout',0o600)
    ierr = read(INNER/'stderr',0o600)
    intent = doc(INNER/'intent.json')
    consumed = doc(INNER/'consumed.json')
    need(outer == inner['candidate'] and inner['status'] == 'PROVISIONAL_MATCH' and
         inner['error_class'] is None and inner['error_detail'] is None and
         inner['retry_allowed'] is False and
         outer['overall'] == 'PASS_BOUNDED_PUBLIC_NAMESPACE_PROBE_ONLY' and
         outer['release_os_exit'] == 0 and outer['release_stderr_empty'] is True and
         outer['retry_allowed'] is False and ierr == b'' and
         intent['release_sha256'] == sha(read(wrapper_dir/'wrapper.py')) and
         intent['argv'] == ['/usr/bin/python3.14','-I','-B','-S',
             str(wrapper_dir/'wrapper.py'),'--execute-reviewed-one-shot'] and
         intent['retry_allowed'] is False and
         consumed == {'schema':'context-public-only-probe-consumed/v1',
             'status':'CONSUMED_UNKNOWN_UNTIL_EXTERNAL_REVIEW','name':NAME,
             'attempt':str(INNER),'retry_allowed':False}, 'INNER_OBSERVATION')
    summary = json.loads(iraw)
    terminal_raw = read(ATTEMPT/'terminal.json',0o600)
    terminal = json.loads(terminal_raw)
    admission = doc(ATTEMPT/'admission.json')
    release_consumed = doc(ATTEMPT/'consumed.json')
    output = read(ATTEMPT/'stage/probe/public-only/packages/0001/request.json',0o444)
    child_copy = read(ATTEMPT/'runner-code/public_probe_child.py',0o444)
    need(summary['status'] == 'PROVISIONAL_EXTERNAL_OS_REVIEW_REQUIRED' and
         summary['terminal_sha256'] == sha(terminal_raw) == outer['terminal_sha256'] and
         summary['attempt'] == str(ATTEMPT) and summary['name'] == NAME and
         summary['retry_allowed'] is False and
         terminal['status'] == 'PROVISIONAL_EXTERNAL_OS_REVIEW_REQUIRED' and
         terminal['schema'] == 'context-public-only-probe-terminal/v1' and
         terminal['cid'] == CID and terminal['name'] == NAME and
         terminal['attempt'] == str(ATTEMPT) and terminal['retry_allowed'] is False and
         terminal['child_os_exit'] == 0 and
         terminal['child_stdout_sha256'] == terminal['child_stderr_sha256'] == EMPTY and
         terminal['parent_peer'] == [terminal['child_pid'],os.getuid(),os.getgid()] and
         terminal['erofs_errno'] == outer['child_erofs_errno'] == 30 and
         terminal['mountinfo_sha256'] == outer['child_mountinfo_sha256'] and
         terminal['five_read_only_mounts'] is True and
         terminal['nested_writable_or_private_mount'] is False and
         terminal['post_ack_visibility'] is True and
         terminal['cid_absent'] is True and terminal['name_absent'] is True and
         terminal['request_sha256'] == outer['request_sha256'] == sha(output) and
         output == REQUEST and
         sha(child_copy) == sha(read(release_dir/'probe_child.py')) and
         release_consumed == {'schema':'context-public-only-probe-consumed/v1',
             'status':'CONSUMED_UNKNOWN_UNTIL_EXTERNAL_REVIEW','name':NAME,
             'attempt':str(ATTEMPT),'retry_allowed':False}, 'RELEASE_TERMINAL_JOIN')
    mounts = [admission['argv'][i+1] for i,v in enumerate(admission['argv'])
              if v == '--mount']
    expected_targets = ['/workspace','/control','/runner','/cache-disabled',
                        '/attempt/input/lab-context-native-reader']
    expected_sources = [ATTEMPT/'stage',ATTEMPT/'control',ATTEMPT/'runner-code',
                        ATTEMPT/'cache-guard',ATTEMPT/'native/lab-context-native-reader']
    need(admission['name'] == NAME and admission['retry_allowed'] is False and
         admission['token'] == json.loads(admission['argv'][-1])['token'] and
         admission['argv'].count('--mount') == 5 and
         mounts == [f'type=bind,src={src},dst={dst},readonly'
                    for src,dst in zip(expected_sources,expected_targets)] and
         '--read-only' in admission['argv'] and '--network' in admission['argv'] and
         admission['argv'][admission['argv'].index('--network')+1] == 'none' and
         admission['argv'][-2] == sha(child_copy) and
         not (ATTEMPT/'stage/probe/public-only/.readonly-sentinel').exists(),
         'PUBLIC_TOPOLOGY')
    cid = docker(['/usr/bin/docker','inspect','--type','container',CID])
    name = docker(['/usr/bin/docker','ps','-a','--no-trunc','--filter',
                   f'name=^{NAME}$','--format','{{.ID}}'])
    need(cid['os_exit'] == 1 and cid['stdout'] == b'[]\n' and
         cid['stderr'] == f'Error response from daemon: No such container: {CID}\n'.encode() and
         name['os_exit'] == 0 and name['stdout'] == name['stderr'] == b'',
         'CURRENT_DOCKER_ABSENCE')
    old_release = STATE/'context-public-only-probe-20261020-0002'
    old_inner = OBS/'context-public-only-probe-20261020-0002'
    old_outer = OBS/'context-public-probe-wrapper-20261020-0002'
    old_review = LOCAL/'context-public-namespace-probe-effect-independent-effect-review-0002/review.json'
    for old_root in (old_release, old_inner, old_outer):
        check_dir(old_root)
    prior = json.loads(read(old_review))
    old_terminal = doc(old_release/'terminal.json')
    need(sha(read(old_review)) ==
         '839aeca6fc3d7c61b3affd4b452af185c13e920544bc6bbc4f650223f82d9640' and
         prior['verdict'] == 'UNKNOWN_CONSUMED_NO_RETRY' and
         prior['effect_success'] is False and prior['no_retry'] is True and
         prior['cause']['retained_code'] == 'DIR_MODE_OR_OWNER' and
         old_terminal['status'] == 'UNKNOWN_PRESERVE_NO_RETRY' and
         (old_inner/'observation.json').is_file() and
         (old_outer/'result.json').is_file(), 'PRIOR_UNKNOWN_RETAINED')
    return {
        'schema':'context-public-probe-independent-effect-audit/v1',
        'verdict':'PASS_BOUNDED_PUBLIC_SYNTHETIC_TOPOLOGY',
        'wrapper_freeze_sha256':sha(wf),
        'wrapper_static_review_sha256':sha(read(static_review)),
        'release_freeze_sha256':sha(rf),
        'outer_result_sha256':sha(read(OUTER/'result.json')),
        'outer_stdout_sha256':sha(oraw),
        'inner_observation_sha256':sha(read(INNER/'observation.json')),
        'release_terminal_sha256':sha(terminal_raw),
        'admission_sha256':sha(read(ATTEMPT/'admission.json')),
        'request_sha256':sha(output),
        'mountinfo_sha256':terminal['mountinfo_sha256'],
        'mountinfo_raw_retained':False,
        'mountinfo_assessment':'CHECKED_CHILD_PREDICATE_AND_MATCHED_HANDSHAKE_ONLY',
        'cid':CID,'cid_absent':True,'name_absent':True,
        'prior_0002_retained':True,
        'private_input_read':False,
        'effect_rerun':False,
        'original_protected_context_qualification':False,
    }


if __name__ == '__main__':
    print(json.dumps(main(),sort_keys=True,indent=2))
