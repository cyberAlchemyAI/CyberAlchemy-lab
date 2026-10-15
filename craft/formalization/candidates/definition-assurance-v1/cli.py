"""Read-only candidate assurance commands; all output goes to stdout."""
import sys
sys.dont_write_bytecode=True
import argparse
import json
import contracts as c
import diff as revision
import ir
import reports
import resolver as r
import verifier

def selected(path, sha):return {'path':path,'sha256':sha}

def parser():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',required=True);p.add_argument('--format',choices=['json','human'],default='json')
    commands=p.add_subparsers(dest='command',required=True)
    commands.add_parser('capture',help='Capture current sources to stdout; no publication.')
    check=commands.add_parser('check',help='Check declared contract and, for interpretations, static typing.')
    check.add_argument('--input',required=True);check.add_argument('--input-sha',required=True);check.add_argument('--kind',choices=sorted(c.KINDS),required=True)
    check.add_argument('--snapshot');check.add_argument('--snapshot-sha')
    verify=commands.add_parser('verify',help='Independently verify an exactly selected candidate bundle.')
    verify.add_argument('--bundle',required=True);verify.add_argument('--selection',required=True);verify.add_argument('--selection-sha',required=True)
    diff=commands.add_parser('diff',help='Generate requirements for an exactly selected revision.')
    diff.add_argument('--selection',required=True);diff.add_argument('--selection-sha',required=True)
    report=commands.add_parser('report',help='Inspect exact whole-definition and separate projection coverage.')
    report.add_argument('--snapshot',required=True);report.add_argument('--snapshot-sha',required=True)
    report.add_argument('--delivery',required=True);report.add_argument('--delivery-sha',required=True)
    return p

def run(args):
    root=r.resolve_root(args.repo)
    if args.command=='capture':
        snapshot=r.capture(root);return {'status':'candidate-source-captured','authority_effect':'none','semantic_ready':False,'snapshot':snapshot}
    if args.command=='report':return reports.coverage(root,selected(args.snapshot,args.snapshot_sha),selected(args.delivery,args.delivery_sha))
    if args.command=='verify':return verifier.verify(root,args.bundle,selected(args.selection,args.selection_sha),live_source_root=root)
    if args.command=='diff':return revision.analyze_selected(root,selected(args.selection,args.selection_sha))
    ref=selected(args.input,args.input_sha);data=reports.load(root,ref);out=c.validate(data,args.kind)
    out['semantic_ready']=False;out['mechanized_proof']=False
    if out['status']!='structurally-valid':return out
    if bool(args.snapshot)!=bool(args.snapshot_sha):raise reports.ReportFault('snapshot-reference-incomplete')
    snapshot=reports.load(root,selected(args.snapshot,args.snapshot_sha)) if args.snapshot else None
    if snapshot is not None:r.verify(snapshot,root)
    if args.kind=='interpretation':
        typed=ir.compile_interpretation(data['payload'],snapshot);ir.verify_ir(typed)
        out.update({'status':'typed-candidate-interpretation','source':data['payload']['source'],'source_currentness':'verified-live' if snapshot is not None else 'not-selected',
                    'ir_sha256':ir.digest(typed),'source_fidelity':data['payload']['source_fidelity'],'whole_definition_translation':'not-assessed',
                    'claim_ceiling':'Declared input contract and selected static typing only. No source fidelity, inhabitation, model truth, proof or semantic readiness.'})
    reports.load(root,ref)
    if snapshot is not None:reports.load(root,selected(args.snapshot,args.snapshot_sha));r.verify(snapshot,root)
    return out

def main(argv=None):
    args=parser().parse_args(argv)
    try:result=run(args)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,RecursionError) as error:
        result={'status':'candidate-command-unresolved','authority_effect':'none','semantic_ready':False,'mechanized_proof':False,
                'diagnostics':[{'code':getattr(error,'code',type(error).__name__),'path':getattr(error,'path','')}]}
    print(reports.human(result) if args.format=='human' else json.dumps(result,indent=2,sort_keys=True,allow_nan=False))
    return 0 if result.get('status') in {'candidate-source-captured','candidate-coverage-inspected','typed-candidate-interpretation','structurally-valid','candidate-revision-generated','verified-candidate-accounting'} else 2

if __name__=='__main__':sys.exit(main())
