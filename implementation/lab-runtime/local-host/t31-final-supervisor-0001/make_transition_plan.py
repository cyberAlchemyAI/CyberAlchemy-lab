"""Close the exact 28 native stage configs under current installed pins."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from supervise import INVENTORY,validate,write


def binding(path):
    path=Path(path).absolute()
    if not path.is_file() or path.is_symlink():raise ValueError('regular selected input required')
    return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main(steps_path,control_result,output,prior_result=None):
    selected=sys.modules.get('cal_installed_runtime_selection_v1')
    if selected is None:raise ValueError('installed selected-python launcher required')
    selected.require_runtime_ready();selected.guard()
    entries=json.loads(Path(steps_path).read_bytes())
    if type(entries)is not list or not entries:raise ValueError('ordered step list required')
    steps=[]
    for entry in entries:
        if type(entry)is not dict or set(entry)!={'name','config_path'}:
            raise ValueError('closed stage config selection required')
        chosen=binding(entry['config_path']);config=json.loads(Path(chosen['path']).read_bytes())
        steps.append({'name':entry['name'],'config_binding':chosen,
                      'expected_transitions':[row['transition_ref'] for row in config['stages']]})
    plan={'schema_version':'lab-t31-final-native-supervision/v1','mode':'phase',
          'installed_repository':str(selected.root()),
          'source_sha256':selected.binding('api.source')['sha256'],
          'profile_sha256':selected.binding('api.profile')['sha256'],
          'inventory_binding':binding(INVENTORY),
          'control_result_binding':binding(control_result),
          'prior_result_binding':binding(prior_result) if prior_result is not None else None,
          'steps':steps,'authority_effect':'none'}
    validate(plan)
    output=Path(output).absolute()
    if output.exists() or not output.parent.is_dir() or output.is_relative_to(selected.root()):
        raise ValueError('fresh external private all28 plan path required')
    return write(output,plan)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--steps',required=True)
    parser.add_argument('--control-result',required=True);parser.add_argument('--output',required=True)
    parser.add_argument('--prior-result')
    args=parser.parse_args()
    print(json.dumps(main(args.steps,args.control_result,args.output,args.prior_result),sort_keys=True),flush=True)
