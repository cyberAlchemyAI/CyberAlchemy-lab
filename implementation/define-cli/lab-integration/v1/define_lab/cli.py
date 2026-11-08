"""Explicit configuration and bounded local operations; JSON output hides secrets."""
import argparse
import json
from pathlib import Path
import sys

from .bootstrap import integrity


def main(argv=None):
    args = None
    try:
        manifest = integrity()
        from .host import Host, setup
        from define_core.exact import encode, write_package
        p = argparse.ArgumentParser(description='Define v3 to Lab v2: explicitly provisioned local integration.')
        sub = p.add_subparsers(dest='command', required=True)
        sub.add_parser('doctor')
        s = sub.add_parser('setup');s.add_argument('--home', required=True);s.add_argument('--principal', required=True)
        s.add_argument('--store-id', default='define-lab-local');s.add_argument('--hours', type=int, default=24)
        s = sub.add_parser('renew');s.add_argument('--home', required=True);s.add_argument('--hours', type=int, default=24)
        for name in ['status', 'context', 'example', 'prepare', 'retain', 'review', 'authorize', 'apply', 'reconstruct']:
            s = sub.add_parser(name);s.add_argument('--home', required=True)
            if name in ['context', 'example', 'prepare', 'review', 'authorize', 'reconstruct']:s.add_argument('--output', required=True)
            if name == 'context':s.add_argument('--definition', action='append')
            if name == 'prepare':
                s.add_argument('--input', required=True);s.add_argument('--permit-retention', action='store_true')
            if name in ['retain', 'review']:s.add_argument('--package', required=True)
            if name == 'review':s.add_argument('--id', required=True)
            if name in ['authorize', 'apply']:s.add_argument('--proposal', required=True)
            if name == 'apply':s.add_argument('--approval', required=True)
            if name == 'reconstruct':s.add_argument('--work', required=True)
        args = p.parse_args(argv)
        if args.command == 'doctor':
            from define_core.integrity import verify
            verify()
            result = {'integrity': 'verified', 'selected_files': len(manifest['files']),
                      'native_contract': 'lab-runtime-proposal/v1', 'define_contract': 'cal.define.pack/v3',
                      'configuration': 'explicit-setup-required', 'repository_admission_effect': 'none'}
        elif args.command == 'setup':result = setup(args.home, args.principal, store_id=args.store_id, hours=args.hours)
        elif args.command == 'renew':result = Host(args.home, allow_expired=True).renew(args.hours)
        else:
            host = Host(args.home)
            if args.command == 'status':result = host.status()
            elif args.command == 'context':
                context, definitions = host.context(args.definition or ['cal.definition.product'])
                write_package(args.output, {'context.json': encode(context), **{
                    'definitions/' + str(i) + '.json': row['raw'] for i, row in enumerate(definitions)}})
                result = {'project_ref': context['project_ref'], 'head': context['head'], 'session_closed': True}
            elif args.command == 'example':
                from .example import author
                result = author(host, args.output)
            elif args.command == 'prepare':result = host.prepare(args.input, args.output, permit_retention=args.permit_retention)
            elif args.command == 'retain':result = host.retain(args.package)
            elif args.command == 'review':result = host.review(args.package, args.output, args.id)
            elif args.command == 'authorize':result = host.authorize(args.proposal, args.output)
            elif args.command == 'apply':result = host.apply(args.proposal, args.approval)
            elif args.command == 'reconstruct':result = host.reconstruct(args.work, args.output)
        sys.stdout.buffer.write(encode({'schema_version': 'cal.define.lab-result/v1', 'command': args.command,
                                        'outcome': 'completed', 'result': result, 'repository_admission_effect': 'none', 'authority_effect': 'none'}))
        return 0
    except KeyboardInterrupt:
        sys.stdout.write(json.dumps({'outcome': 'outcome-unknown', 'continuation': 'Inspect the original destination and native head before retrying.'}) + '\n')
        return 130
    except Exception as exc:
        code = getattr(exc, 'code', 'local-integration-refused')
        sys.stdout.write(json.dumps({'schema_version': 'cal.define.lab-result/v1', 'command': getattr(args, 'command', None),
                                    'outcome': 'outcome-unknown' if code == 'publication-outcome-unknown' else 'blocked',
                                    'diagnostics': [{'code': code, 'message': 'Operation refused; no private input echoed.'}],
                                    'repository_admission_effect': 'none', 'authority_effect': 'none'}) + '\n')
        return 3
