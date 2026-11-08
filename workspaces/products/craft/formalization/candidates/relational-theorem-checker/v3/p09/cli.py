"""Public commands with an explicit operator policy and original raw requests."""
from pathlib import Path
import argparse
import json
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from v3.p03.context import C,BASE,binding,require
from v3.p09.api import Client
from v3.p08.metadata import Store

def bounded(path,limit):
    with Path(path).open('rb') as f:return f.read(limit+1)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=['qualify','inspect','describe','bootstrap','apply','recover'])
    parser.add_argument('input',type=Path);parser.add_argument('--policy',type=Path,required=True)
    parser.add_argument('--run-root',type=Path,default=BASE/'p07/consumer-runs/P09-cli')
    parser.add_argument('--store',type=Path);parser.add_argument('--result',type=Path);parser.add_argument('--review',type=Path)
    parser.add_argument('--query',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        policy=C.decode(bounded(args.policy,4194304));C.validate('resource-policy',policy)
        client=Client(policy,args.run_root);marker=binding(Path(__file__))
        client.shadow._sources.append(marker);client.owned.sources.append(marker);client.shadow.mapped.sources.append(marker)
        raw=bounded(args.input,policy['work_limits']['input_bytes'])
        if args.operation=='qualify':out=client.qualify(raw)
        elif args.operation=='bootstrap':
            require(args.store is not None,'bootstrap requires --store');out=client.bootstrap(args.store,raw)
        elif args.operation=='apply':
            require(args.store is not None and args.review is not None,'apply requires --store and --review')
            out=client.apply(binding(args.review),raw,Store(args.store))
        elif args.operation=='recover':
            require(args.store is not None,'recover requires --store');out=Store(args.store).recover()
        else:
            require(args.result is not None,'inspection/explanation requires --result')
            request=C.decode(raw);public=C.decode(bounded(args.result,8388608))
            if args.operation=='inspect':out=client.inspect(request,public)
            else:out=client.describe(request,public,C.decode(bounded(args.query,4194304)) if args.query else None)
        encoded=(json.dumps(out,allow_nan=False,ensure_ascii=False)+'\n').encode()
        if args.output:
            p=args.output.resolve();require(p.is_relative_to(BASE/'p09'),'CLI output must stay in P09');p.parent.mkdir(parents=True,exist_ok=True)
            with p.open('xb') as f:f.write(encoded)
        sys.stdout.buffer.write(encoded)
        return 0 if out.get('status',out.get('outcome')) in ['qualified-candidate','recorded-current','initialized-candidate-shadow','applied-candidate-shadow','head-current','present','summary','absent-in-complete-profile'] else 3
    except Exception as e:
        print(json.dumps({'schema':'relational.public-cli-refusal/v3','status':'invalid','reason':str(e).splitlines()[0][:400],'authority_effect':'none','application_authorized':False}));return 2

if __name__=='__main__':sys.exit(main())
