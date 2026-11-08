"""Three explicitly selected historical acceptance adapters, never current proof."""
from lab_contracts.codec import closed, need, sha
from lab_selectors.anchors import legacy_json
from .common import load, binding, LIMIT
from .eligibility import Capture, Evaluation, disclosure


def historical(reader, expected_selection):
    capture=Capture(reader)
    selection=load(capture,expected_selection,'lab-historical-selection/v1',
                   ['documents','public_retention_bindings','privacy_class'])
    need(selection['privacy_class']=='reviewed-public-selector','PUBLIC_HISTORY_REQUIRED')
    docs={}
    bindings={}
    for item in selection['documents']:
        closed(item,['id','binding']);binding(item['binding'])
        need(item['id'] not in docs,'DUPLICATE_HISTORY')
        bindings[item['id']]=item['binding']
        raw=capture.read(item['binding'],max_bytes=LIMIT)
        docs[item['id']]=legacy_json(raw)
    need(set(docs)=={'T00-receipt','T00-environment','T00-selection','T01-report',
        'T01-acceptance','T04-receipt','T04-qualification','T04-terminal','T04-acceptance'},
        'HISTORY_COVERAGE')
    def joined(value,source):
        b=bindings[source]
        need(value['path']==b['relative_path'] and value['sha256']==b['sha256'],'HISTORY_JOIN')
    zero=docs['T00-receipt']
    need(zero['result']=='PASS' and zero['runtime_tests_executed'] is False and
         zero['whole_API_qualified'] is False,'T00_SCOPE')
    need(docs['T00-environment']['result']=='PASS','T00_ENVIRONMENT')
    one=docs['T01-acceptance'];report=docs['T01-report']
    joined(one['accepted_report'],'T01-report')
    need(one['result']=='PASS-causal-diagnosis' and
         one['OS_exit_code_currently_recoverable'] is False and
         one['missing_terminal_handle']==73068 and
         report['result']=='CAUSAL-INTEGRITY-REFUSAL-OBSERVED' and
         report['whole_API_qualified'] is False,'T01_SCOPE')
    four=docs['T04-acceptance'];receipt=docs['T04-receipt'];q=docs['T04-qualification'];term=docs['T04-terminal']
    joined(four['receipt_binding'],'T04-receipt')
    joined(receipt['qualification_binding'],'T04-qualification')
    joined(receipt['terminal_binding'],'T04-terminal')
    joined(term['qualification_binding'],'T04-qualification')
    need(four['result']=='PASS' and four['API17_integrated'] is False and
         receipt['runtime_qualification_pending'] is True and
         q['test_cases']==q['expected_cases']==term['test_cases']==31 and
         term['actual_os_exit']==0 and term['actual_live_API_calls']==0 and
         q['whole_API_qualified'] is False,'T04_SCOPE')
    records=[{'task':'T00','historical_status':'complete','scope':'baseline-selection-only',
        'runtime_tests_executed':False,'terminal_accounting':'not-a-runtime-test',
        'acceptance_binding':bindings['T00-receipt']},
        {'task':'T01','historical_status':'complete','scope':one['completion_scope'],
         'runtime_tests_executed':True,'terminal_accounting':'unavailable-explicit',
         'acceptance_binding':bindings['T01-acceptance']},
        {'task':'T04','historical_status':'complete','scope':four['completion_scope'],
         'runtime_tests_executed':True,'live_API_calls_executed':0,
         'terminal_accounting':'focused31-exit0',
         'acceptance_binding':bindings['T04-acceptance']}]
    disclosure(capture,selection['public_retention_bindings'],expected_selection)
    return Evaluation({'schema_version':'lab-historical-acceptance/v1',
        'selection_binding':expected_selection,'records':records,
        'current_eligibility_conferred':False,'authority_effect':'none'},
        tuple(capture.originals.values()))
