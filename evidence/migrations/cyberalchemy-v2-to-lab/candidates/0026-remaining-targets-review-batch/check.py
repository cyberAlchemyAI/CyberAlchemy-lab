"""Inspect candidate graph/profile/view inputs; no publication or external effects."""
import argparse
import json
from pathlib import Path
from engine import read, load_graph, profile_eval, project, check_revision
from support import ROOT, LAB, load, sha, need

def main():
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest='mode',required=True)
    graph=sub.add_parser('graph'); graph.add_argument('manifest',type=Path)
    profile=sub.add_parser('profile'); profile.add_argument('name'); profile.add_argument('input',type=Path)
    view=sub.add_parser('view'); view.add_argument('name'); view.add_argument('manifest',type=Path); view.add_argument('--as-of',default='2026-09-07T00:00:00Z')
    revision=sub.add_parser('revision'); revision.add_argument('before',type=Path); revision.add_argument('after',type=Path)
    args=parser.parse_args()
    try:
        # Once snapshotted, verify executable and declarative code before evaluating inputs.
        if (ROOT/'manifest.json').exists():
            for ref in load(ROOT/'manifest.json')['materials']:
                path=LAB/ref['path']
                if path.suffix=='.py' or path.name in ['contract.json','parameters.json']: need(sha(path)==ref['sha256'],'Candidate implementation drift')
        if args.mode=='graph':
            g=load_graph(args.manifest); result={'graph_valid':True,'nodes':len(g['nodes']),'relations':len(g['relations']),'authority_effect':'none','action_authorized':False}
        elif args.mode=='profile': result=profile_eval(args.name,read(ROOT/'targets'/('profile.'+args.name)/'parameters.json'),read(args.input))
        elif args.mode=='view': result=project(args.name,load_graph(args.manifest),args.as_of)
        else: result=check_revision(read(args.before),read(args.after))
        code=1 if result.get('outcome') in ['block','defer','not-applicable'] else 0
    except Exception as exc:
        result={'input_valid':False,'error':str(exc),'authority_effect':'none','action_authorized':False}; code=2
    print(json.dumps(result,indent=2,sort_keys=True)); return code
if __name__=='__main__': raise SystemExit(main())
