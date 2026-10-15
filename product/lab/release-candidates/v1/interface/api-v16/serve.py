"""Local stdio reader adapter, one bounded UTF-8 JSON value per line."""

# Keep this successor in its own module namespace. Frozen producers retain
# their exact original top-level dependency modules.
if __package__ in (None,''):
    import importlib.util as _boot_util,sys as _boot_sys
    from pathlib import Path as _BootPath
    _boot_root=_BootPath(__file__).resolve().parent
    _boot_name='_cal_'+_boot_root.name.replace('-','_')
    if _boot_name not in _boot_sys.modules:
        _boot_spec=_boot_util.spec_from_file_location(_boot_name,_boot_root/'__init__.py',submodule_search_locations=[str(_boot_root)])
        _boot_module=_boot_util.module_from_spec(_boot_spec);_boot_sys.modules[_boot_name]=_boot_module;_boot_spec.loader.exec_module(_boot_module)
    __package__=_boot_name
import argparse
import sys
from .auth import ReaderChannel
from .service import *


def write(value):
    sys.stdout.buffer.write(compact(value)+b'\n');sys.stdout.buffer.flush()


def receive(stream,limit):
    raw=stream.readline(limit+2)
    if not raw:return None
    if not raw.endswith(b'\n'):
        if len(raw)>limit:
            while raw and not raw.endswith(b'\n'):raw=stream.readline(4096)
            return transport('input-too-large')
        return transport('invalid-envelope',raw)
    raw=raw[:-1]
    if len(raw)>limit:return transport('input-too-large',raw)
    return raw


def main():
    parser=argparse.ArgumentParser(description='Authenticated isolated candidate Lab reader API over local stdio.')
    parser.add_argument('--policy',required=True);parser.add_argument('--policy-sha256',required=True)
    parser.add_argument('--protocol-profile-sha256',required=True)
    args=parser.parse_args();channel=None;service=None
    try:
        schemas=Schemas(args.protocol_profile_sha256);channel=ReaderChannel(args.policy,args.policy_sha256,schemas)
        write(channel.challenge);proof=receive(sys.stdin.buffer,16384)
        if proof is None:return 2
        if not isinstance(proof,bytes):write(proof);return 2
        try:authenticated=channel.authenticate(proof)
        except Exception:write(transport('unauthenticated-channel',proof));return 2
        with source.replay_source(channel.policy['source_name']) as view:
            service=Service(view,channel,schemas)
            write(authenticated)
            while True:
                raw=receive(sys.stdin.buffer,channel.policy['max_request_bytes'])
                if raw is None:break
                if not isinstance(raw,bytes):write(raw);continue
                response=service.call(raw)
                write(response)
        return 0
    except Exception:
        write(transport('unauthenticated-channel'))
        return 2
    finally:
        if service is not None:service.close()
        elif channel is not None:channel.close()


if __name__=='__main__':raise SystemExit(main())
