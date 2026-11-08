"""Raw-byte CLI; mathematical request decoding stays inside the owned worker."""
from pathlib import Path
import argparse
import json
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from v3.p03.context import C,BASE,require
from v3.p06.api import SupervisedQualifier

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy',required=True,type=Path)
    parser.add_argument('--request',required=True,type=Path)
    parser.add_argument('--runs',type=Path,default=BASE/'p06/cli-runs')
    parser.add_argument('--cgroup-parent',type=Path)
    parser.add_argument('--pids-max',type=int)
    args=parser.parse_args()
    with args.policy.open('rb') as f:operator_raw=f.read(8193)
    require(len(operator_raw)<=8192,'operator policy file byte ceiling')
    policy=C.decode(operator_raw);C.validate('resource-policy',policy)
    with args.request.open('rb') as f:raw=f.read(policy['work_limits']['input_bytes']+1)
    answer=SupervisedQualifier(args.runs,policy,cgroup_parent=args.cgroup_parent,pids_max=args.pids_max).qualify(raw)
    print(json.dumps(answer,allow_nan=False,ensure_ascii=False))
    return 0 if answer['status']=='qualified-candidate' else 2
if __name__=='__main__':raise SystemExit(main())
