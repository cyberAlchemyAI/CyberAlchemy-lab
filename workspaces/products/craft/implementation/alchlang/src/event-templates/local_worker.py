"""Generated invocation boundary and local outbox dispatch. Linux-only prototype."""
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time


def clock():
    now = time.time_ns() // 1000000
    return {'now': now, 'at': time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(now // 1000)) + f'.{now % 1000:03d}Z'}


def sandbox_command(executable, data):
    return ['/usr/bin/bwrap', '--unshare-all', '--die-with-parent', '--new-session',
            '--ro-bind', '/usr', '/usr', '--ro-bind', '/lib', '/lib', '--ro-bind', '/lib64', '/lib64',
            '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp', '--dir', '/app',
            '--ro-bind', str(executable), '/app/alch-event', '--bind', str(data), '/data',
            '--chdir', '/app', '--clearenv', '--setenv', 'PATH', '/usr/bin:/bin',
            '--setenv', 'ALCH_EVENT_DATABASE', '/data/function.sqlite', '--', '/app/alch-event']


def invoke(bundle, cfg, database, request, context):
    executable = Path(bundle) / 'alch-event'
    argv = sandbox_command(executable, database.parent) if cfg['isolation'] == 'bubblewrap' else [str(executable)]
    # A separate launcher applies limits; preexec_fn is unsafe in the threaded host.
    command = [sys.executable, str(Path(bundle) / 'local_worker.py'), '--launch', str(cfg['timeout_ms']), *argv]
    with subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          cwd=bundle, env={'PATH':'/usr/bin:/bin', 'ALCH_EVENT_DATABASE':str(database)},
                          start_new_session=True) as proc:
        try:
            out, _ = proc.communicate(json.dumps({'request':{**request, **clock()}, 'context':context}).encode(), timeout=cfg['timeout_ms']/1000)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.communicate()
            raise TimeoutError('OUTCOME_UNKNOWN')
        try:
            value = json.loads(out)
        except (ValueError, UnicodeError):
            raise RuntimeError('RUNTIME_PROTOCOL_FAILURE')
        return proc.returncode, value


def dispatch_once(call, cfg, context, worker, crash_after_consume=False):
    transport_context = {'transport_grants':[cfg['transport']]}
    code, claim = call({'command':'claim','worker':worker}, transport_context)
    if code:
        raise RuntimeError('CLAIM_FAILED')
    if claim['status'] in ('empty','dead'):
        return claim['status']
    if claim['status'] != 'leased':
        raise RuntimeError('CLAIM_PROTOCOL')
    accepted = False
    try:
        code, consumed = call({'command':'invoke','operation':cfg['consumer']['operation'],'message':claim['message']}, context)
        accepted = code == 0 and consumed.get('status') in ('processed','duplicate') and consumed.get('message_id') == claim['message']['messageId']
    except (TimeoutError, RuntimeError):
        pass  # uncertain completion is reconciled by the same message id
    if crash_after_consume and accepted:
        os._exit(75)
    code, settled = call({'command':'settle','worker':worker,'message_id':claim['message']['messageId'],
                          'attempt':claim['attempt'],'outcome':'provider-accepted' if accepted else 'unknown'}, transport_context)
    if code:
        # An expired lease cannot be acknowledged by a stale worker. Let the
        # existing claim protocol recover it; never force a status update.
        return 'settlement-unconfirmed'
    return settled['status']


if __name__ == '__main__':
    if len(sys.argv) < 4 or sys.argv[1] != '--launch':
        raise SystemExit(2)
    cpu = max(1, math.ceil(int(sys.argv[2])/1000))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu,cpu))
    resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024,256*1024*1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64,64))
    resource.setrlimit(resource.RLIMIT_FSIZE, (64*1024*1024,64*1024*1024))
    os.execv(sys.argv[3], sys.argv[3:])
