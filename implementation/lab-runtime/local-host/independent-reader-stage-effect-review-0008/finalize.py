import pathlib,json,hashlib
R=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab');E=R/'implementation/lab-runtime/local-host/independent-reader-stage-effect-review-0008'
def b(p):
 raw=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw)}
obs=json.loads((E/'observations.json').read_bytes());archive=obs['archive_hash_only'];report={
 'schema_version':'independent-reader-stage-posteffect-review/v1','reviewer':'evidence_review','candidate':'fresh-reader-docker-0008','verdict':'PASS_RETAINED_STAGE_INTEGRITY_WITH_REPORTED_EXTERNAL_EXIT','findings':[],
 'freeze_sha256':'7baa002724d031a1225e73518dee282caf3f9d26a914bdc306788c3873917606','stage_plan_sha256':'82ddcf898953881d49cfb1b99ba0b91f4f9c7393cfde5ae3bb9549b5a769e524',
 'attempt':'/tmp/cal-reader-stage-20261020-0001-0008','consumed':True,'retry_performed':False,
 'verified':{'files':986,'directories':931,'bytes':33411923,'archive_stream_hash':archive['stage']['sha256'],'archive_bytes':archive['stage']['size'],'archive_body_parsed_printed_or_copied':False,'source_original_files_unchanged':978,'reader_originals_unchanged':8,'freeze_members_unchanged':24,'source_root_exact_inventory':True,'nonregular_or_extra_entries':False,'all_selected_owner_mode_nlink_checks_passed':True,'attempt_mode':'0700','private_package_dirs':'0700','private_package_members':'0600','neutral_receipt':'OBSERVED_STAGE_ONLY','unknown_receipt_present':False,'reader_input_released':False,'reader_output_empty':True,'predecessor_0005_and_release_0007_freezes_verified':True},
 'external_process_observation':{'provenance':'Coordinator message in this conversation, not independently retained command-output file','tool_chunk_id':'865246','reported_exit_code':0,'reported_wall_time_seconds':1.294298305,'reported_stdout':'One JSON OBSERVED_STAGE_ONLY receipt','reported_stderr':'No stderr shown','independent_file_bound_exit':False,'interpretation':'Neutral receipt and current exact stage are independently verified. Historical successful command completion additionally relies on this explicit coordinator report; it is not inferred from receipt presence.'},
 'claim_ceiling':[
 'Observed disposable private stage copy only. No Reader cold-open, Docker execution, protected Source8, G01/G02, full chain or original-plan acceptance follows.',
 'No stage, Reader or Docker command was executed by this reviewer. Existing consumed attempt was not modified or retried.',
 'Archive was read only as streaming bytes into SHA-256 for both source and destination; no archive parsing, body export or second copy.',
 'Current named files matched exact selection at the recorded read time; same-UID mutable paths are not certified immutable. Future Reader must revalidate bytes, attachment and period at use.',
 'No durable standalone external exit transcript exists. The coordinator-reported external zero exit remains a provenance limitation, separate from the independently file-bound stage integrity result.',
 'Period spans 2026-10-20T08:20:00Z to 2026-10-21T08:20:00Z; selected period grants no automatic current host permission.'
 ],
 'review_execution':{'final_checks_exit_code':0,'final_checks_tool_chunk_id':'496cec','source_inventory_check_exit_code':0,'source_inventory_tool_chunk_id':'ab0b31','initial_reviewer_error':'Initial independent directory inventory omitted the selected empty Source receipts directory and stopped before archive reads. Preserved initial-check-failure.json and checks.py; corrected checks-0002.py matches audit_stage.expected_dirs. No candidate defect inferred.'},
 'evidence':[b(E/n) for n in ['checks.py','initial-check-failure.json','checks-0002.py','checks-0002.log','bindings.json','inventory.json','observations.json','source-inventory-confirmation.json','finalize.py']]
}
(E/'review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(b(E/'review.json'),sort_keys=True))
