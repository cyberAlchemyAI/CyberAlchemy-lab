"""Seal the full helper proof only from an actually observed successful terminal.

Tool terminal fields are supplied from the real completed tool response. This
script never starts or stops a suite and never infers an exit from a log.
"""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
HELPER=ROOT/'product/lab/release-candidates/v1/interface/fact-read-scope-v2'


def bind(path):
    return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path,value):
    with path.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True)
    parser.add_argument('--observed-tool-session',type=int,required=True)
    parser.add_argument('--observed-exit-code',type=int,required=True)
    parser.add_argument('--observed-terminal-chunk',required=True)
    args=parser.parse_args();assert args.observed_exit_code==0
    source=HELPER/'source-manifest.json';assert bind(source)['sha256']==args.source_sha256
    manifest=json.loads(source.read_bytes());rows={row['path']:row for row in manifest['files']}
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    report_path=HELPER/'receipts/checks-0001.json';report=json.loads(report_path.read_bytes())
    assert report['result']=='PASS' and report['tests_run']==report['expected_tests']==22
    assert report['failures']==report['errors']==0 and report['source_sha256']==args.source_sha256
    assert len(report['cases'])==22 and all(row['result']=='PASS' for row in report['cases'])
    assert report['actual_signed_original_source'] and report['actual_private_host_nonce_authentication']
    assert report['integration_qualified'] is False and report['current_Agent_qualified'] is False
    log=RUN/'fact-policy-boundary-checks-0002.log';text=log.read_text()
    methods={node.name for file in ['checks.py', 'current_checks.py'] for node in ast.walk(ast.parse((HELPER/file).read_bytes()))
             if isinstance(node,ast.FunctionDef) and node.name.startswith('test_')}
    actual=re.findall(r'^(test_\S+) \([^\n]+\) \.\.\. ok$',text,re.M)
    assert len(methods)==len(actual)==len(set(actual))==22 and set(actual)==methods
    assert re.search(r'Ran 22 tests in [0-9.]+s\n\nOK\n',text)
    terminal=RUN/'fact-policy-boundary-terminal-0002.json'
    value={'schema_version':'lab-actual-terminal-observation/v1-candidate',
           'checked_at':datetime.now(timezone.utc).isoformat(),
           'tool_session_id':args.observed_tool_session,'exit_code':args.observed_exit_code,
           'chunk_id':args.observed_terminal_chunk,'terminal_observed':True,
           'source_binding':bind(source),'report_binding':bind(report_path),'log_binding':bind(log),
           'authority_effect':'none','actual_owner_outcome':None}
    assert not terminal.exists() and not (HELPER/'receipts/proof-0001.json').exists()
    put(terminal,value)
    for path in [source,report_path,log,terminal,Path(__file__)]:rows[bind(path)['path']]=bind(path)
    proof={'schema_version':'lab-actual-fact-scope-qualified-proof/v1-candidate',
           'result':'PASS','tests_run':22,'expected_tests':22,'failures':0,'errors':0,
           'actual_terminal_exit_code':0,'actual_terminal_binding':bind(terminal),
           'source_binding':bind(source),'report_binding':bind(report_path),'log_binding':bind(log),
           'all_actual_case_names':sorted(actual),'files':[rows[k] for k in sorted(rows)],
           'actual_signed_original_source':True,'actual_private_host_nonce_authentication':True,
           'integration_qualified':False,'current_Agent_qualified':False,
           'task_complete':False,'goal_complete':False,'authority_effect':'none','actual_owner_outcome':None,
           'claim_ceiling':'All22actual helper cases and unchanged full selected inputs only. Context/API integration and the original complete plan remain required.'}
    out=HELPER/'receipts/proof-0001.json';put(out,proof)
    print(json.dumps({'result':'PASS','tests_run':22,'files':len(rows),'proof_binding':bind(out)}),flush=True)


if __name__=='__main__':main()
