#!/usr/bin/env python3
"""Conditional grammar v11 with the same prospective six-key review clarity."""
import argparse, json
from ac_runtime import read
from ac_grammar_runtime_v11 import GrammarRuntime as PreviousGrammar
from ac_review_schema_runtime_v12 import CoverageRuntime


class GrammarRuntime(PreviousGrammar, CoverageRuntime):
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('command', choices=['status','verify','start','spawned','finish',
        'failed','gate','reserve-overhead','record-overhead'])
    for name in ['job','handle','witness-file','invocation-id','purpose','evidence']:
        ap.add_argument('--' + name)
    ap.add_argument('--outcome',choices=['spawn','error'],default='spawn')
    a=ap.parse_args(); r=GrammarRuntime()
    if a.command == 'status': v=r.grammar_status()
    elif a.command == 'verify': v=r.verify()
    elif a.command == 'start': v=r.start(a.job)
    elif a.command == 'spawned': v=r.spawned(a.job,a.handle)
    elif a.command == 'finish': v=r.finish(a.job,read(a.witness_file))
    elif a.command == 'failed': v=r.failed(a.job,read(a.witness_file))
    elif a.command == 'gate': v=r.gate(a.job)
    elif a.command == 'reserve-overhead': v=r.reserve_overhead(a.invocation_id,a.purpose)
    else: v=r.record_overhead(a.invocation_id,a.handle,a.purpose,a.evidence,a.outcome)
    print(json.dumps(v,ensure_ascii=False,indent=2))


if __name__ == '__main__': main()
