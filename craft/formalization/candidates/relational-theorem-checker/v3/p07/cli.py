"""Owned-run CLI; raw mathematical request decoding remains supervised."""
from pathlib import Path
import argparse
import json
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from v3.p03.context import C,BASE,require
from v3.p07.api import OwnedQualifier

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--policy',type=Path,required=True);p.add_argument('--request',type=Path,required=True)
    p.add_argument('--runs',type=Path,default=BASE/'p07/cli-runs')
    p.add_argument('--cgroup-parent',type=Path);p.add_argument('--pids-max',type=int)
    a=p.parse_args()
    with a.policy.open('rb') as f:raw_policy=f.read(8193)
    require(len(raw_policy)<=8192,'operator policy file byte ceiling')
    policy=C.decode(raw_policy);C.validate('resource-policy',policy)
    with a.request.open('rb') as f:raw=f.read(policy['work_limits']['input_bytes']+1)
    answer=OwnedQualifier(a.runs,policy,cgroup_parent=a.cgroup_parent,pids_max=a.pids_max).qualify(raw)
    print(json.dumps(answer,allow_nan=False,ensure_ascii=False))
    return 0 if answer['status']=='qualified-candidate' else 2
if __name__=='__main__':raise SystemExit(main())
