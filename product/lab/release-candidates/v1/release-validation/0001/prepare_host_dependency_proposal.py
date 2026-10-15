"""Read-only, fully guarded host/proof selection; no production change or install."""
import ast
import json
import os
from pathlib import Path
import stat
from datetime import datetime, timezone
import build_runtime as B

def proposal():
    here=B.HERE;api=B.BASE/'api-integration-v14'
    source_pin='aea84d1d97c2780e8fb172b6dd4d8807f2e89892a02f0fe0e5daab97b3f0c240'
    profile_pin='327d3c480168b0008597969e31e11e73f429370a226bd16370245e82ef78fb16'
    started=datetime.now(timezone.utc).isoformat()
    source=B.exact(api/'source-manifest.json',source_pin);profile=B.exact(api/'contract-profile.json',profile_pin)
    guard=B.module('_host_proposal_exact_guard',api/'guard.py');guard.verify(source_pin)
    environment=B.load(here/'environment-contract.json');execution=B.load(api/'SCHEMA-EXECUTION-DEPENDENCIES.json')
    B.need(environment['API_source_binding']==B.bind(api/'source-manifest.json')
        and environment['API_profile_binding']==B.bind(api/'contract-profile.json'), 'draft selects different family')
    absolute=[r for r in source['files'] if Path(r['path']).is_absolute()]
    native=environment['host_native_binding'];extra=environment['host_ABI_library_bindings']
    inputs={r['path']:r for r in absolute}
    for row in extra:
        B.need(row['path'] not in inputs or inputs[row['path']]==row,'conflicting host binding')
        inputs[row['path']]=row
    host=[]
    for path,row in sorted(inputs.items()):
        raw=B.read(Path(path));info=Path(path).lstat()
        B.need(B.sha(raw)==row['sha256'] and stat.S_ISREG(info.st_mode),'host byte/type differs')
        kind=('host-native-reader' if row==native else 'host-ABI-library' if row in extra else 'protected-external-source-history')
        mode=stat.S_IMODE(info.st_mode)
        if row==native:B.need(mode==0o755,'native execution mode differs from actual recovery')
        host.append({'binding':row,'input_class':kind,'mode_octal':format(mode,'04o'),
            'size_bytes':len(raw),'public_export_allowed':False,'installed_into_candidate_Vault':False,
            'reason':'Exact selected original native reader; retained locator/ABI required.' if row==native else
                'Exact host ABI bytes used by retained ELF reader.' if row in extra else
                'Protected original external repository/history proof; fresh verification only, no source relocation.'})
    selected=set((r['path'],r['sha256']) for r in source['files'])
    B.need(all((r['path'],r['sha256']) in selected for r in profile['files']),'profile input outside full source')
    active=execution['files']
    B.need(all((r['path'],r['sha256']) in selected for r in active),'active input outside full source')
    for row in environment['offline_environment_wheel_bindings']:B.need(B.bind(B.ROOT/row['path'])==row,'wheel byte differs')
    guard.verify(source_pin)
    result={'schema_version':'lab-protected-host-proof-selection-proposal/v1-candidate',
        'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),
        'proposer_binding':B.bind(Path(__file__)),'original_source_binding':B.bind(api/'source-manifest.json'),
        'original_profile_binding':B.bind(api/'contract-profile.json'),
        'original_execution_selection_binding':B.bind(api/'SCHEMA-EXECUTION-DEPENDENCIES.json'),
        'large_environment_contract_binding':B.bind(here/'environment-contract.json'),
        'large_environment_contract_size_bytes':(here/'environment-contract.json').stat().st_size,
        'original_runtime_draft_binding':B.bind(here/'runtime-implementation.json'),
        'public_selection_binding':B.bind(B.ROOT/'product/lab/release-candidates/v1/boundary-review/0008/public-inputs.json'),
        'full_source_row_count':len(source['files']),'profile_row_count':len(profile['files']),
        'active_row_count':len(active),'source_rows_removed':0,'source_rows_reclassified_as_Artifact_nodes':0,
        'public_payload_row_count':environment['public_payload_members'],
        'absolute_full_source_rows':len(absolute),'profile_external_execution_rows':profile['external_execution_dependency_bindings'],
        'host_inputs':host,'host_input_count':len(host),'host_ABI_library_count':len(extra),
        'R02_environment':environment['R02_environment'],
        'offline_environment_wheel_bindings':environment['offline_environment_wheel_bindings'],
        'current_host_recovery_binding':environment['current_host_recovery_binding'],
        'selected_local_environment':'local Linux repository with exact protected host inputs',
        'all_34_operation_declarations_retained':True,'portable_or_self_contained_claim':False,
        'future_private_selection_contract':{
            'independently_selected_plan_version':'lab-installation-release-plan/v2-candidate-proposed',
            'exact_control_fields':['source_binding','profile_binding','execution_selection_binding',
                'environment_contract_binding','host_dependency_selection_binding','proof_input_bindings'],
            'proof_input_kinds':['source-manifest','contract-profile','schema-execution-selection',
                'large-environment-contract','retained-original-history-proof','runtime-recovery-proof'],
            'selection_authority':'Independent authenticated private custody grant selects exact kind, binding, original Source cut, operation, expiry and host paths; public requests confer no host access.',
            'fresh_guard':'At every boundary, fresh no-follow anchored regular-file reads, full SHA/size/mode checks, captured inode/read identity consistency and directory attachments; native0755/ABI/interpreter/wheels exact. Revalidate all original Source/profile/active rows; never cache byte verification.',
            'protected_read_policy':'Only independently selected exact Repo proof files and explicit absolute host paths. Permit bounded parsing of the 27MB environment manifest by a protected proof reader; do not put it in Vault, do not grant arbitrary absolute paths, do not restore private keys/Session RAM.',
            'artifact_graph_policy':'Ordinary governed member graph edges come from exact selected record schemas/explicit reference selectors. Infrastructure source/profile/env row tables are proof inputs with complete independently verified closure, not implicit Artifact nodes. Retained historical digest cycles are preserved and reported; no claim that their raw tables form an acyclic Artifact graph.',
            'installation_policy':'Keep original R02 package install/upgrade/rollback/retry behavior and OwnedScope. For the new version compare environment.R02_environment with exact package.environment, then separately verify full protected host/source/proof selection before claim, before publish, and after install. Native stays host-provided at its original locator; candidate archive0600 cannot execute.',
            'no_effects':['source admission','runtime activation','service start','host install','protected proof publication','new owner recognition']},
        'schema_and_compatibility_impacts':[
            'New versioned private plan/protected-input selector schema; original v1 custody plan path and existing assertions preserved.',
            'New versioned release-readiness contract/evidence schema separates artifact_graph members/edges from exact protected proof inputs. No generic schema-approved path bypass.',
            'If supported_environment_bindings selects the full environment contract, its protocol schema and installation v2 branch must explicitly declare the nested R02_environment comparison; original v1 still compares the original R02 environment.',
            'No change to the public 34-operation catalog or ordinary API ref/sha binding. Bind new helper/schema/selector in final successor Source/profile/active selection and qualification inputs.',
            'Root must select the exact future API15 Source/profile and re-materialize a separate release-validation output; this API14 proposal cannot qualify API15.'
        ],
        'required_actual_successor_cases':[
            'Authorized exact large Repo manifest + full protected closure read and isolated install/upgrade/rollback/retry/inspect.',
            'Unselected absolute path, changed host byte, mode, symlink, inode attachment, ABI/interpreter/wheel, missing proof row, changed source/profile/active row all refuse before effect.',
            'Same exact blocked-release retry and operation.inspect preserve state; no readiness true without actual all34/current-family/regression/pilot/owner evidence.',
            'Privacy checker scans only explicitly selected publicpayload bytes; protected proof inclusion cannot confer export permission.'
        ],
        'full_entry_exit_guards_observed':True,'proposal_only':True,'production_files_changed':False,
        'installation_executed':False,'whole_API_qualified':False,'complete_original_regression_qualified':False,
        'owner_authority_resolved':False,'human_pilot_observed':False,'release_ready':False,
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False}
    B.emit(here/'host-dependency-readiness-proposal.json',result)
    print(json.dumps({'result':'GUARDED-PROPOSAL-ONLY','report_binding':B.bind(here/'host-dependency-readiness-proposal.json'),
        'source_rows':len(source['files']),'protected_absolute_source_rows':len(absolute),'ABI_rows':len(extra),
        'full_entry_exit_guards':True,'release_ready':False}),flush=True)

if __name__=='__main__':proposal()
