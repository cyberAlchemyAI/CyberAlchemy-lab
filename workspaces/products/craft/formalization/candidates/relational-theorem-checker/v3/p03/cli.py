"""Public local v3 qualification and saved-inspection transport."""
from pathlib import Path
import argparse
import json
import sys
sys.dont_write_bytecode=True
if __package__ in (None,''):
    sys.path.insert(0,str(Path(__file__).resolve().parents[2]));__package__='v3.p03'
from .context import QualificationContext,C,BASE
from .qualification import qualify_fresh,inspect_saved,failure


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=['qualify','inspect'])
    parser.add_argument('request',type=Path);parser.add_argument('--result',type=Path)
    parser.add_argument('--output',type=Path);parser.add_argument('--run-root',type=Path,default=BASE/'p03/runs')
    args=parser.parse_args();request={}
    try:
        request=C.decode(args.request.read_bytes());C.validate('request',request)
        ctx=QualificationContext(args.run_root,request['resource_policy'])
        if args.operation=='inspect':
            if args.result is None:raise ValueError('inspect requires --result')
            result=inspect_saved(request,C.decode(args.result.read_bytes()),ctx);code=0
        else:
            result=qualify_fresh(request,ctx)
            code={'qualified-candidate':0,'invalid':2,'unknown-resource':3,'unsupported':4,'unsupported-policy':4,'cancelled':130}[result['status']]
    except Exception as e:
        result=failure(request,'refused-before-run','invalid',e,'transport-or-inspection');code=5 if args.operation=='inspect' else 2
    if args.output:
        p=args.output.resolve()
        if not p.is_relative_to(BASE):raise ValueError('output must stay in v3')
        p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result));return code


if __name__=='__main__':sys.exit(main())
