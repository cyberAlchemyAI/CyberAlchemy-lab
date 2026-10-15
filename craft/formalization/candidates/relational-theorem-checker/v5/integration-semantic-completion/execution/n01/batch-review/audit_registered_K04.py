"""Audit immutable K04 proof evidence with explicit historical context snapshots."""
from pathlib import Path
from collections import Counter
import json, re

def audit(root, preparations, seq, progress, check):
    assert len(preparations)==2
    assert seq['current_unit']==progress['current_review']
    current=next(unit for unit in seq['units'] if unit['unit']=='K04')
    if current['actual_assessment'] is None:
        assert current['status'] in {'awaiting-actual-meaning-assessment','ready-for-consolidated-review'}
    else:
        assert current['status']=='meaning-accepted-proof-work-pending'
    assert len(current['pending_preparations'])==2
    names=[]
    for package in preparations:
        check(package)
        history=json.loads((root/package['historical_context']['path']).read_text())
        check(history)
        mapping={row['original_path']:row for row in history['snapshots']}
        assert len(mapping)==4
        assert {Path(key).name for key in mapping}=={
            'plan.json','sequential-review.json','decision-gate.json','K04-assessment-request.json'}
        for row in mapping.values():
            assert row['original_sha256']==row['snapshot']['sha256']
        def historical_check(value):
            if isinstance(value,dict):
                if {'path','sha256'}<=value.keys():
                    captured=mapping.get(value['path'])
                    if captured and value['sha256']==captured['original_sha256']:
                        check(captured['snapshot'])
                    else:
                        check({'path':value['path'],'sha256':value['sha256']})
                for child in value.values():historical_check(child)
            elif isinstance(value,list):
                for child in value:historical_check(child)
        def read(ref):
            check(ref)
            data=json.loads((root/ref['path']).read_text())
            historical_check(data)
            return data
        proof=read(package['verification'])
        completion=read(package['component_completion'])
        assert completion['result']=='candidate-component-verified'
        assert proof['inherited_discharges']==completion['inherited_discharges']==0
        assert proof['N01_accepted'] is completion['N01_accepted'] is False
        assert proof['independent_verification'] is False and proof['raw_source_refinement'] is False
        actual=[]
        for source_ref in package['local_sources']:
            check(source_ref)
            source=root/source_ref['path']
            namespaces=[]
            for line in source.read_text().splitlines():
                entered=re.match(r'^namespace ([\w.]+)$',line)
                ended=re.match(r'^end(?: [\w.]+)?$',line)
                theorem=re.match(r'^theorem (\w+)',line)
                if entered:namespaces.append(entered.group(1))
                elif ended:namespaces.pop()
                elif theorem:actual.append('.'.join(namespaces+[theorem.group(1)]))
        assert len(actual)==len(set(actual))==package['theorems']
        assert set(actual)==set(proof['theorems'])
        names.extend(actual)
        if package['unit']=='K04-draft':
            assert proof['result']=='pass' and proof['candidate_declarations']==43
            assert proof['general_theorems']==15 and proof['worked_controls']==28
            assert len(proof['phases'])==2
            for phase in proof['phases']:
                assert phase['fresh_module_compilations']==2 and phase['axiom_inspections']==43
                log=(root/phase['axiom_log']['path']).read_text()
                inspected=re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",log,re.S)
                assert len(inspected)==43 and {name for name,_ in inspected}==set(actual)
                for _,listed in inspected:
                    assert set(re.findall(r'[A-Za-z][A-Za-z0-9_.]*',listed))<={'propext','Quot.sound','Classical.choice'}
        else:
            assert package['unit']=='K04-source-adapter'
            assert proof['result']=='candidate-fragment-pass' and proof['new_candidate_theorems']==9
            assert proof['fresh_compilations']==len(proof['records'])==10
            assert proof['candidate_runtime_controls']==279
            assert proof['complete_shape_controls']==250 and proof['semantic_join_controls']==29
            assert proof['complete_record_field_count']==55 and proof['record_type_count']==6
            assert proof['source_qualifier_adapter_exact']
            controls=read(package['control_index'])
            assert len(controls['runtime_cases'])==279
            expected=[row['expected'] for row in controls['runtime_cases']]
            generation=read(package['generation_audit'])
            assert generation['complete_record_field_count']==55 and generation['active_assertion_nodes']==70
            assert not generation['unsupported_assertions_ignored']
            pool={}
            for prior_ref in proof['prior_verifications']:
                prior=read(prior_ref)
                for row in prior.get('records',[])+prior.get('reused_dependencies',[]):
                    output=row.get('olean',row.get('reused_output'))
                    key=(row['phase'],Path(output['path']).name)
                    assert key not in pool
                    pool[key]=(row['source']['sha256'],output['sha256'])
            reused={}
            for row in proof['reused_dependencies']:
                key=(row['phase'],Path(row['reused_output']['path']).name)
                assert key not in reused
                assert row['reused_output']['sha256']==row['output']['sha256']
                reused[key]=(row['source']['sha256'],row['output']['sha256'])
            assert reused==pool
            local_counts=[]
            for row in proof['records']:
                log=(root/row['log']['path']).read_text()
                assert 'warning:' not in log and 'error:' not in log
                if Path(row['source']['path']).stem=='LessonSourceControls':
                    assert [line=='true' for line in log.splitlines() if line in ['true','false']]==expected
                    assert row['runtime_controls']==279
                if not row['prior_model_module']:
                    local_counts += re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",log,re.S)
            assert Counter(name for name,_ in local_counts)==Counter({name:2 for name in actual})
            for _,listed in local_counts:
                assert set(re.findall(r'[A-Za-z][A-Za-z0-9_.]*',listed))<={'propext','Quot.sound','Classical.choice'}
            assert {row['phase'] for row in proof['records']}=={'compile','replay'}
            for dependency in proof['import_resolution']:
                dep=root/dependency['dependency']['path']
                assert dep.parent.name==dependency['phase'] or '/.toolcache/' in str(dep)
    assert len(names)==len(set(names))==52
    assert seq['pending_review_candidate_theorems']==progress['pending_review_candidate_theorems']==52
    return names
