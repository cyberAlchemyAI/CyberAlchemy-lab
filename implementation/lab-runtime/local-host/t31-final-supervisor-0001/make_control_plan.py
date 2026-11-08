"""Bind a fresh control probe to the actually installed API selection."""
import argparse
import json
from pathlib import Path
import sys
from supervise import write


def main(output):
    selected=sys.modules.get('cal_installed_runtime_selection_v1')
    if selected is None:raise ValueError('installed selected-python launcher required')
    selected.require_runtime_ready();selected.guard()
    plan={'schema_version':'lab-t31-final-native-supervision/v1','mode':'control',
          'installed_repository':str(selected.root()),
          'source_sha256':selected.binding('api.source')['sha256'],
          'profile_sha256':selected.binding('api.profile')['sha256'],
          'authority_effect':'none'}
    output=Path(output).absolute()
    if output.exists() or not output.parent.is_dir() or output.is_relative_to(selected.root()):
        raise ValueError('fresh external private control plan path required')
    return write(output,plan)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    args=parser.parse_args();print(json.dumps(main(args.output),sort_keys=True),flush=True)
