"""Read-only independent Mapper Docker effect audit; never opens Source archive body."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
LOCAL = REPO / 'implementation/lab-runtime/local-host'
OUTER = Path('/home/vlad_/.local/state/cyberalchemy-lab-observations/mapper-successor-docker-wrapper-release-0001')
INNER = Path('/home/vlad_/.local/state/cyberalchemy-lab-observations/mapper-successor-docker-release-0001')
ATTEMPT = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/mapper-attempt/docker-attempt')
NAME = 'cal-mapper-only-20261020-0002-successor-0001'
PINS = {
 'mapper-successor-docker-observer-effect-0001/freeze.json':'3d86ac856c6df050e0c7601594cbeeb6f9a3602efc47b5a7fd60faa6bd1f1392',
 'MAPPER-SUCCESSOR-DOCKER-OBSERVER-EFFECT-INDEPENDENT-STATIC-REVIEW-0001.md':'1cd0e3f450a18a86cb1a86c9b83187f02d0f797de68bc132126d4b7de9cf2ad2',
 'mapper-successor-docker-observer-0002/freeze.json':'356a3abd41a28a3400f22f8e1aac35f33e7176893090c3a27783cd51b99b4a07',
 'MAPPER-SUCCESSOR-DOCKER-OBSERVER-INDEPENDENT-STATIC-REVIEW-0002.md':'a76d0fd9245dcce50e362df0f087a2658c1d243c691b085f0176b6b60100ab0b',
 'mapper-successor-docker-release-0001/freeze.json':'ce6356ef776c20d89286cc116c1750eeae6df9fb7a640e6dc545634c5b656452',
 'MAPPER-SUCCESSOR-DOCKER-RELEASE-INDEPENDENT-STATIC-REVIEW-0001.md':'816fa66234f9ac8ccb69ca6d4d1f1657ad3f0c80e4babe644385df3ab4e94ea8',
 'mapper-successor-docker-controller-0002/freeze.json':'4cac02ffa93511633ccdd45f2b0562069225f0e6e7530399ef88f5d2e692da2b',
 'MAPPER-SUCCESSOR-DOCKER-CONTROLLER-INDEPENDENT-STATIC-REVIEW-0002.md':'253503d80afaf0d6af0caa2411f38acc96d50fc8b54e70b85dc7efebd84c7bd9',
 'context-successor-mapper-stage-independent-effect-review-0001/review.json':'bae85fada28780b6bcc88082d2436082402d8acfc25b420328c79df6d2f07406',
 'context-successor-source-independent-effect-review-0001/review.json':'599d7cca4b87b98809e33636ad1326bc60ddba589123ec5a0a0c5e00b58a4440',
 'context-successor-reader-independent-effect-review-0001/review.json':'c2f9d0307610d281784c4d3c86211dbc37bd6a5843130647ff1718561957f295',
}

def blocked(event, args):
    if event == 'open' and args and isinstance(args[0], (str, bytes, os.PathLike)) and str(args[0]).endswith('branch.snapshot'):
        raise RuntimeError('PROTECTED_ARCHIVE_BODY_FORBIDDEN')
sys.addaudithook(blocked)

def raw(path):
    return Path(path).read_bytes()
def sha(value):
    return hashlib.sha256(value).hexdigest()
def obj(path):
    return json.loads(raw(path))
def exact(condition, code):
    if not condition:
        raise RuntimeError(code)
def owner_file(path, mode=0o600):
    info = Path(path).lstat()
    exact(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_uid == os.getuid() and
          info.st_gid == os.getgid() and stat.S_IMODE(info.st_mode) == mode, 'FILE_CUSTODY:'+str(path))
def owner_dir(path):
    info = Path(path).lstat()
    exact(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and
          info.st_gid == os.getgid() and stat.S_IMODE(info.st_mode) == 0o700, 'DIR_CUSTODY:'+str(path))

def main():
    for path in (OUTER, INNER, ATTEMPT, ATTEMPT/'evidence'):
        owner_dir(path)
    pin_matches = {}
    member_counts = {}
    for rel, digest in PINS.items():
        value = raw(LOCAL/rel)
        exact(sha(value) == digest, 'PREDECESSOR_DRIFT:'+rel)
        pin_matches[rel] = digest
        if rel.endswith('/freeze.json'):
            freeze = json.loads(value)
            bindings = freeze.get('file_bindings', freeze.get('bindings'))
            if isinstance(bindings, list):
                for row in bindings:
                    p = REPO/row['path']; v = raw(p)
                    exact(sha(v)==row['sha256'] and len(v)==row['size'], 'FREEZE_MEMBER_DRIFT:'+str(p))
                member_counts[rel] = len(bindings)
            elif isinstance(bindings, dict):
                for name, digest2 in bindings.items():
                    p = (LOCAL/rel).parent/name
                    exact(sha(raw(p)) == digest2, 'FREEZE_MEMBER_DRIFT:'+str(p))
                member_counts[rel] = len(bindings)
    paths = {
      'outer_intent':OUTER/'intent.json','outer_result':OUTER/'result.json',
      'outer_stdout':OUTER/'stdout.bin','outer_stderr':OUTER/'stderr.bin',
      'inner_consumed':INNER/'consumed.json','inner_intent':INNER/'intent.json',
      'inner_capture':INNER/'capture.json','inner_observation':INNER/'observation.json',
      'inner_stdout':INNER/'stdout','inner_stderr':INNER/'stderr',
      'attempt_consumed':ATTEMPT/'consumed.json','prepared':ATTEMPT/'evidence/prepared.json',
      'precreate':ATTEMPT/'evidence/precreate.json','terminal':ATTEMPT/'evidence/terminal.json',
      'final':ATTEMPT/'evidence/final.json',
    }
    for path in paths.values(): owner_file(path)
    values = {name:raw(path) for name,path in paths.items()}
    h = {name:sha(value) for name,value in values.items()}
    docs = {name:json.loads(value) for name,value in values.items() if name not in ('outer_stderr','inner_stderr')}
    oi,orr,osout = docs['outer_intent'],docs['outer_result'],docs['outer_stdout']
    ic,ii,cap,io,isin = (docs[x] for x in ('inner_consumed','inner_intent','inner_capture','inner_observation','inner_stdout'))
    ac,prepared,precreate,terminal,final = (docs[x] for x in ('attempt_consumed','prepared','precreate','terminal','final'))
    exact(oi['wrapper_freeze_sha256']==PINS['mapper-successor-docker-observer-effect-0001/freeze.json'] and
          oi['independent_review_sha256']==PINS['MAPPER-SUCCESSOR-DOCKER-OBSERVER-EFFECT-INDEPENDENT-STATIC-REVIEW-0001.md'] and
          oi['argv']==['/usr/bin/python3','-B',str(LOCAL/'mapper-successor-docker-observer-effect-0001/wrapper.py'),'--execute-reviewed-one-shot'] and
          oi['retry_allowed'] is False, 'OUTER_INTENT')
    exact(type(orr['os_exit_code']) is int and orr['os_exit_code']==0 and orr['process_error'] is None and
          orr['retry_allowed'] is False and orr['stdout_size']==len(values['outer_stdout']) and
          orr['stderr_size']==0 and values['outer_stderr']==b'' and
          orr['stdout_sha256']==h['outer_stdout'] and orr['stderr_sha256']==h['outer_stderr'] and
          oi['created_at_ns']<=orr['finished_at_ns'], 'OUTER_RESULT')
    from datetime import datetime, timezone
    period_start=int(datetime(2026,10,20,15,tzinfo=timezone.utc).timestamp())*10**9
    period_end=int(datetime(2026,10,21,15,tzinfo=timezone.utc).timestamp())*10**9
    exact(period_start<=oi['created_at_ns']<=orr['finished_at_ns']<period_end,
          'SOURCE_EFFECT_INTERVAL')
    exact(osout['status']=='PROVISIONAL_OS_ZERO_FINAL_JOIN' and
          osout['observation_sha256']==h['inner_observation'] and
          osout['stdout_sha256']==h['inner_stdout'] and
          osout['stderr_sha256']==h['inner_stderr'] and
          osout['release_os_exit']==0 and osout['independent_effect_review']=='PENDING' and
          osout['no_retry'] is True and osout['attempt']==str(ATTEMPT),
          'OUTER_INNER_JOIN')
    exact(ic['attempt']==str(ATTEMPT) and ic['container_name']==NAME and
          ic['no_retry'] is True and ii['attempt']==str(ATTEMPT) and
          ii['container_name']==NAME and ii['no_retry'] is True and
          ii['release_freeze_sha256']==PINS['mapper-successor-docker-release-0001/freeze.json'] and
          ii['release_review_sha256']==PINS['MAPPER-SUCCESSOR-DOCKER-RELEASE-INDEPENDENT-STATIC-REVIEW-0001.md'] and
          ii['release_entrypoint_sha256']=='cf85a26da6166e96855050ae0f511d22ff260ce4f807b9c67a077391b01bf927' and
          ii['argv']==['/usr/bin/python3','-B',str(LOCAL/'mapper-successor-docker-release-0001/release.py'),'--execute-reviewed-one-shot'],
          'INNER_CONSUMED_INTENT')
    capture=cap['capture']
    exact(cap['status']=='REAPED_PENDING_POSTCLOSE' and cap['error_class'] is None and
          cap['no_retry'] is True and type(capture['exit_code']) is int and
          capture['exit_code']==0 and capture['counts']==[len(values['inner_stdout']),0] and
          capture['retained']==capture['counts'] and capture['stdout_sha256']==h['inner_stdout'] and
          capture['stderr_sha256']==h['inner_stderr'] and capture['capture_error_class'] is None and
          capture['overflow'] is False and capture['pipe_tail_timeout'] is False and
          capture['signals']==[] and capture['child_preserved_after_signal'] is False and
          values['inner_stderr']==b'' and io['status']=='PROVISIONAL_OS_ZERO_FINAL_JOIN' and
          io['candidate']==cap['candidate'] and io['capture']==capture and
          io['independent_effect_review']=='PENDING' and io['no_retry'] is True,
          'INNER_CAPTURE_OBSERVATION')
    exact(isin==final and h['inner_stdout']!=h['final'] and
          cap['candidate']['final_sha256']==h['final'] and
          cap['candidate']['stdout_sha256']==h['inner_stdout'] and
          cap['candidate']['stderr_sha256']==h['inner_stderr'] and
          cap['candidate']['release_os_exit']==0 and
          cap['candidate']['status']=='PROVISIONAL_OS_ZERO_FINAL_JOIN',
          'RAW_STDOUT_FINAL_JOIN')
    exact(ac['attempt']==str(ATTEMPT) and ac['no_retry'] is True and
          ac['stage_effect_review_sha256']==PINS['context-successor-mapper-stage-independent-effect-review-0001/review.json'] and
          prepared['no_retry'] is True and prepared['container_name']==NAME and
          prepared['entrypoint_sha256']=='e00b863a91b5084e3ec85c662b38d912ee556fd6b1780704cb0f56d5de83cc2a' and
          prepared['label']==precreate['nonce']==terminal['nonce'] and
          prepared['create_argv_sha256']==precreate['create_argv_sha256']==terminal['create_argv_sha256'] and
          prepared['image']==precreate['image']==terminal['image'] and
          precreate['name']==terminal['name']==NAME and precreate['phase']=='BEFORE_CREATE' and
          precreate['effect']=='NOT_STARTED' and
          terminal['schema_version']=='lab-mapper-docker-one-shot-evidence/v2' and
          terminal['phase']=='TERMINAL' and terminal['overall']==terminal['cleanup']=='PASS' and
          type(terminal['client_exit']) is int and terminal['client_exit']==0 and
          type(terminal['daemon_exit']) is int and terminal['daemon_exit']==0 and
          terminal['daemon_exit_consistent'] is True and terminal['container_absent'] is True and
          terminal['forced_cleanup'] is False and terminal['create_attempted'] is True and
          type(terminal['container_id']) is str and len(terminal['container_id'])==64 and
          all(c in '0123456789abcdef' for c in terminal['container_id']),
          'ONE_SHOT_PROTOCOL')
    exact(final['schema']=='lab-mapper-successor-docker-final/v1' and
          final['overall']=='OBSERVED_DOCKER_ONLY' and final['attempt']==str(ATTEMPT) and
          final['terminal_sha256']==h['terminal'] and final['no_retry'] is True and
          final['authority_effect']=='none' and final['actual_owner_outcome'] is None and
          final['original_task_acceptance'] is False and
          final['requires_external_exit_zero_and_independent_effect_review'] is True,
          'PROVISIONAL_FINAL')
    exact(not any('unknown' in p.name.lower() for p in ATTEMPT.rglob('*')),
          'UNKNOWN_RECEIPT_PRESENT')

    sys.path.insert(0,str(LOCAL/'mapper-successor-docker-controller-0002'))
    import controller, output_verifier
    selected=controller.trusted_selection()
    stage=controller.input_inventory(selected['plan'],selected['copy'],
                                     hash_private=False,allow_output=True)
    exact(len(selected['plan']['files'])==991 and len(stage)==992 and
          sum(int(row['target_mode'],8)==0o600 for row in selected['plan']['files'])==37,
          'STAGE_CURRENT_METADATA')
    create=controller.docker_create_argv(selected,label=prepared['label'])
    exact(sha(('\0'.join(create)).encode())==terminal['create_argv_sha256'] and
          create.count('--mount')==4, 'CREATE_ARGV_BINDING')
    mapper_source=controller.ROOT/controller.MAPPER/'source-manifest.json'
    source_bytes=raw(mapper_source); source_obj=json.loads(source_bytes)
    stage_review=obj(LOCAL/'context-successor-mapper-stage-independent-effect-review-0001/review.json')
    source_manifest_sha=sha(raw(controller.ROOT/controller.SOURCE/'source-manifest.json'))
    source_package_sha=sha(raw(controller.ROOT/controller.SOURCE/'packages/0001/manifest.json'))
    reader_manifest_sha=sha(raw(controller.ROOT/controller.READER/'source-manifest.json'))
    exact(source_manifest_sha=='2843a67fd28a295f5c175b8d8c2b31f701040bb8d7dedeade8d76bbdf057d1d1' and
          source_package_sha==stage_review['source_package_manifest_sha256'] and
          reader_manifest_sha==stage_review['reader_manifest_sha256'] and
          stage_review['source_effect_review_sha256']==PINS['context-successor-source-independent-effect-review-0001/review.json'] and
          stage_review['reader_effect_review_sha256']==PINS['context-successor-reader-independent-effect-review-0001/review.json'],
          'SOURCE_READER_LINEAGE')
    rows=source_obj['files']
    exact(len(rows)==953 and len({row['path'] for row in rows})==953 and
          stage_review['mapper_manifest_sha256']==sha(source_bytes),
          'MAPPER_SOURCE_953_STAGE_JOIN')
    package_parent=controller.ROOT/controller.MAPPER/'packages'
    fd=os.open(package_parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        independently_replayed=output_verifier.verify(
            fd,selected['verifier']['expected_package_members'])
    finally:
        os.close(fd)
    package=package_parent/'0001'
    manifest_bytes=raw(package/'manifest.json'); manifest=json.loads(manifest_bytes)
    exact(independently_replayed==final['output'] and
          independently_replayed['files']==55 and
          independently_replayed['semantic_leaves']==25 and
          independently_replayed['governance_leaves']==25 and
          independently_replayed['native_seal_processes']==2 and
          independently_replayed['actual_cold_native_read_processes']==2 and
          independently_replayed['exact_governance_joins']==25 and
          independently_replayed['manifest_sha256']==sha(manifest_bytes) and
          manifest['source_manifest_binding']=={'path':controller.MAPPER+'/source-manifest.json',
                                                'sha256':sha(source_bytes)} and
          len(manifest['files'])==54 and
          manifest['authority_effect']=='none' and manifest['actual_owner_outcome'] is None,
          'FULL_OUTPUT_VERIFIER')
    actual_files={p.relative_to(package).as_posix():p for p in package.rglob('*') if p.is_file()}
    exact(len(actual_files)==55 and
          {r['path'].removeprefix(controller.MAPPER+'/packages/0001/') for r in manifest['files']}==
          set(actual_files)-{'manifest.json'} and
          all(sha(raw(actual_files[r['path'].removeprefix(controller.MAPPER+'/packages/0001/')]))==r['sha256']
              for r in manifest['files']), 'PACKAGE_PHYSICAL_HASHES')
    semantic={}
    for i in range(1,26):
        item=json.loads(raw(package/f'semantic/{i:08d}.json'))
        exact(item['event_family']=='semantic' and type(item['semantic_cursor']) is int and
              item['semantic_cursor']==i, 'SEMANTIC_EVENT')
        semantic[i]=(item['event_id'],item['event_digest'])
    for i in range(1,26):
        item=json.loads(raw(package/f'governance/{i:08d}.json'))
        ref=item['semantic_ref']
        exact(item['event_family']=='governance' and type(item['governance_cursor']) is int and
              item['governance_cursor']==i and ref['semantic_cursor']==i and
              (ref['semantic_event_id'],ref['semantic_event_digest'])==semantic[i],
              'GOVERNANCE_JOIN')
    mapping=json.loads(raw(package/'mapping.json'))
    native=json.loads(raw(package/'native-output.json'))
    build=json.loads(raw(package/'build-result.json'))
    exact(len(mapping['rows'])==25 and mapping['semantic_cursor']==25 and
          mapping['governance_cursor']==25 and mapping['native_seal_processes']==2 and
          mapping['actual_cold_native_read_processes']==2 and
          len(native['governed_nodes'])==15 and native['cut']['semantic_cursor']==25 and
          native['governance_cursor']==25 and build['result']=='PASS' and
          build['exact_governance_joins']==25 and build['task_complete'] is False,
          'DIRECT_SEMANTIC_SUMMARY')
    docker='/usr/bin/docker';cid=terminal['container_id']
    gone=subprocess.run([docker,'inspect','--type','container',cid],
                        stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15,check=False)
    absent=subprocess.run([docker,'ps','-a','--no-trunc','--filter',f'name=^{NAME}$',
                           '--format','{{.ID}}'],stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,timeout=15,check=False)
    exact(gone.returncode==1 and gone.stdout==b'[]\n' and
          gone.stderr==f'Error response from daemon: No such container: {cid}\n'.encode() and
          absent.returncode==0 and absent.stdout==absent.stderr==b'',
          'LIVE_DOCKER_CID_NAME_ABSENCE')
    result={
      'schema':'lab-mapper-successor-docker-independent-audit/v1',
      'verdict_candidate':'PASS_BOUNDED_MAPPER_ONLY_EFFECT',
      'effect_interval_within_source_period':True,
      'all_predecessor_pins_match':True,'member_counts':member_counts,
      'predecessor_pins':pin_matches,
      'observation_sha256':h,'outer_os_exit':orr['os_exit_code'],
      'inner_release_os_exit':capture['exit_code'],'stderr_empty':True,
      'raw_stdout_parsed_final_equal':True,'raw_stdout_distinct_from_final_bytes':True,
      'terminal_client_exit':terminal['client_exit'],'terminal_daemon_exit':terminal['daemon_exit'],
      'container_id':cid,'container_name':NAME,'container_absent_live':True,
      'cid_absence_stdout_sha256':sha(gone.stdout),'cid_absence_stderr_sha256':sha(gone.stderr),
      'name_absence_stdout_sha256':sha(absent.stdout),'name_absence_stderr_sha256':sha(absent.stderr),
      'stage_files_current':991,'stage_directories_current':933,
      'private_input_rows_metadata_only':37,'private_body':'UNOPENED',
      'mapper_source_manifest_sha256':sha(source_bytes),'mapper_source_rows':953,
      'source_manifest_sha256':source_manifest_sha,
      'source_package_manifest_sha256':source_package_sha,
      'reader_manifest_sha256':reader_manifest_sha,
      'package_manifest_sha256':sha(manifest_bytes),'package_files':55,
      'package_total_bytes':independently_replayed['total_bytes'],
      'semantic_governance_joins':25,'native_seal_processes':2,
      'cold_native_read_processes':2,'authority_effect':'none',
      'source_continuity_ceiling':'current snapshot only; creation/pre-effect per-file inode identities were not externally retained',
      'original_task_acceptance':False,'retry_allowed':False,
      'audited_at_ns':time.time_ns(),
    }
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=='__main__':
    main()
