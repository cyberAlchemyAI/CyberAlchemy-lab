"""Join actual successful Context8 tool terminals before independent auditing."""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
SELECTED=ROOT/'product/lab/release-candidates/v1/interface/current-context-delivery-v8'


def bind(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path,value):
    with path.open('x') as stream:
        json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--observed-checks-session',type=int,required=True)
    parser.add_argument('--observed-checks-exit',type=int,required=True)
    parser.add_argument('--observed-checks-chunk',required=True)
    args=parser.parse_args();assert args.observed_checks_exit==0
    source=SELECTED/'source-manifest.json'
    assert bind(source)==json.loads((RUN/'current-context-build-terminal-0008.json').read_bytes())['source_binding']
    report_path=SELECTED/'receipts/checks.json';report=json.loads(report_path.read_bytes())
    assert report['result']=='PASS' and report['tests_run']==report['expected_tests']==50
    assert len(report['cases'])==50 and all(row['result']=='PASS' for row in report['cases'])
    code_path=RUN/'current-context-code-execution-checks-0008.json'
    code=json.loads(code_path.read_bytes())
    assert code['phase']=='checks' and code['execution_checked_before_each_repository_module_exec'] is True
    assert code['entrypoint_outcome']=={'entrypoint_exit':0,'exception_type':'SystemExit'}
    assert code['source_sha256']==bind(source)['sha256']
    log=RUN/'current-context-delivery-checks-0008.log';text=log.read_text()
    actual=re.findall(r'^(test_\S+) \([^\n]+\) \.\.\. ok$',text,re.M)
    methods={node.name for path in SELECTED.glob('test*.py') for node in ast.walk(ast.parse(path.read_bytes()))
             if isinstance(node,ast.FunctionDef) and node.name.startswith('test_')}
    assert len(actual)==len(set(actual))==50 and set(actual)==methods
    assert re.search(r'Ran 50 tests in [0-9.]+s\n\nOK\n',text)
    build_path=RUN/'current-context-build-terminal-0008.json';build=json.loads(build_path.read_bytes())
    assert build['terminal_observed'] and build['exit_code']==0 and build['source_binding']==bind(source)
    checks={'terminal_observed':True,'exit_code':args.observed_checks_exit,
            'tool_session_id':args.observed_checks_session,'chunk_id':args.observed_checks_chunk,
            'actual_cases':50,'source_binding':bind(source),'report_binding':bind(report_path),
            'log_binding':bind(log),'code_execution_observation_binding':bind(code_path)}
    value={'schema_version':'lab-observed-context-build-check-terminals/v1-candidate',
           'checked_at':datetime.now(timezone.utc).isoformat(),'selected_exit_codes':{'build':0,'checks':0},
           'build':build,'checks':checks,'build_terminal_binding':bind(build_path),
           'sealer_binding':bind(Path(__file__)),'Context_qualified':False,
           'actual_owner_outcome':None,'authority_effect':'none',
           'claim_ceiling':'Actual build and all50 original checks; independent audit remains required.'}
    terminal=RUN/'current-context-delivery-terminal-0008.json'
    context=RUN/'context-R03-current-context-audit-0008.json'
    assert not terminal.exists() and not context.exists()
    put(terminal,value)
    inputs=[source,SELECTED/'packages/0001/manifest.json',SELECTED/'EXECUTION-DEPENDENCIES.json',
            report_path,terminal,build_path,code_path,RUN/'current-context-code-execution-build-0008.json',
            RUN/'current-context-code-audit-source-0008.json',RUN/'run-context-with-code-audit-0008.py',
            RUN/'audit-R03-current-context-0008.py',RUN/'freeze-R03-current-context-audit-0008.py',
            RUN/'authorization.json',SELECTED.parent/'current-context-delivery-v6/receipts/qualification-0001.json']
    put(context,{'schema_version':'lab-bounded-context/v1-candidate','task':'R03 independent full Context8 audit',
                 'strict_coverage':'PASS','blockers':[],'source_bindings':[bind(path) for path in inputs],
                 'constraints':['Full original50 actual cases and successful terminals are required.',
                                'Complete parent qualification and original source/package/profile/native guards retained.',
                                'Execution dependency selection must be independently checked against full qualification and actual module execution.',
                                'No callback replacement, permission caching, fake clock, interval renewal or owner outcome.',
                                'Full API/Agent and sole R08 owner checkpoint remain required.'],
                 'actual_owner_outcome':None,'authority_effect':'none'})
    print(json.dumps({'result':'PASS','actual_cases':50,'terminal_binding':bind(terminal),'context_binding':bind(context)}),flush=True)


if __name__=='__main__':main()
