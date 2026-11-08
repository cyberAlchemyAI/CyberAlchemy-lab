"""CI gates fresh extension review; it never accepts a supplied outcome file."""
from pathlib import Path
import json
import subprocess
import sys
import runtime as c
s=c.s; o=c.o


def review_ready(outcome, required_ids, process_code):
    o.validate(outcome, required_ids)
    return process_code == 0 and o.exit_code(outcome) == 0 and outcome['command'] in ['check-extension', 'replay-evidence'] and \
        outcome['execution'] == 'completed' and outcome['currentness'] == 'current' and \
        outcome['readiness'] == 'ready-for-review' and bool(required_ids) and \
        not outcome['missing_hard_obligation_ids'] and not outcome['unresolved_hard_obligation_ids']


def main():
    try:
        # Accept only the public checker command grammar, then execute our pinned local launcher.
        args = c.parser().parse_args(sys.argv[1:])
        if args.command in ['check-extension', 'replay-evidence']:
            proposal, binding = c.read_input(args.input if args.command == 'check-extension' else args.proposal)
            c.b.source_boundary(proposal)
            required = [x['id'] for x in c.g.generate(proposal)['obligations']]
        else:
            required = None
        before = c.current_adapter()
        run = subprocess.run([str(c.HERE / 'cli'), *sys.argv[1:]], capture_output=True, text=True)
        if run.stderr: print(run.stderr, end='', file=sys.stderr)
        outcome = c.d.decode(run.stdout)
        s.require(c.current_adapter() == before, 'CI checker dependencies changed')
        if required is not None:
            c.v.safe_binding(binding, limit=4 * 1024 * 1024)
            ready = review_ready(outcome, required, run.returncode)
        else:
            ready = False  # A successful isolated instance/proof check cannot stand in for extension readiness.
        print(json.dumps(outcome, indent=2, ensure_ascii=False))
        return 0 if ready else (run.returncode or 4)
    except (ValueError, KeyError, TypeError, OSError, c.g.c.jsonschema.ValidationError) as error:
        outcome = c.a.invalid_outcome('check-extension', error)
        print(json.dumps(outcome, indent=2, ensure_ascii=False)); return 2


if __name__ == '__main__': raise SystemExit(main())
