"""Read-only exact-diff check for the API46 to API47 T31 source successor."""
import hashlib
import json
from pathlib import Path

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v46-t31-workflow-current-0002'
NEW = BASE / 'api-integration-v47-t31-output-current-0001'
ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t31-api47-output-bootstrap-0002/bootstrap.py'
OLD_SOURCE = 'caf4aa1f4dbfcc8a5eab336e15704487f3e1913b8d76bfbcfbd88b56204a0969'
OLD_PROFILE = 'a4a2afdf2853f135a473c19b8dd83dc4cd3b587bc00821a227a4790a365c7402'
NEW_SOURCE = 'de4487eef78b5737cd2f4919c1e7280b5eef2e78dc5beb342cde87cb19651fd1'
NEW_PROFILE = '2c62d15d212b1151ce91928a0f78346d0679725bd9953f972dd86c64af2660f9'
ADAPTER_SHA = '06b8346aba1feef12e07a0d14c7a6b5cb95f1aaaebd76827e042f3ed83cdcc85'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    require((sha(OLD/'source-manifest.json'),sha(OLD/'contract-profile.json'),sha(NEW/'source-manifest.json'),sha(NEW/'contract-profile.json'),sha(ADAPTER)) ==
            (OLD_SOURCE,OLD_PROFILE,NEW_SOURCE,NEW_PROFILE,ADAPTER_SHA),'selected predecessor/successor byte differs')
    old_manifest = json.loads((OLD/'source-manifest.json').read_text())
    new_manifest = json.loads((NEW/'source-manifest.json').read_text())
    old_profile = json.loads((OLD/'contract-profile.json').read_text())
    new_profile = json.loads((NEW/'contract-profile.json').read_text())
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
    adapter_path = ADAPTER.relative_to(ROOT).as_posix()
    def partition(rows,prefix):
        local = {r['path'][len(prefix):]:r['sha256'] for r in rows if r['path'].startswith(prefix)}
        external = {(r['path'],r['sha256']) for r in rows if not r['path'].startswith(prefix)}
        require(len(local)+len(external)==len(rows),'duplicate or missing selected row')
        return local,external
    old_local,old_other = partition(old_manifest['files'],old_prefix)
    new_local,new_other = partition(new_manifest['files'],new_prefix)
    require(len(old_local)==len(new_local)==201 and set(old_local)==set(new_local),'local source inventory differs')
    changed = {name for name in old_local if old_local[name]!=new_local[name]}
    require(changed=={'contract-profile.json','guard.py','workflow_output_registry.py'},'unexpected selected local byte change')
    require(new_other-old_other=={(adapter_path,ADAPTER_SHA)} and not old_other-new_other,'external source closure differs')
    for name,digest in new_local.items():
        require(sha(NEW/name)==digest,'successor selected file differs: '+name)
    old_p_local,old_p_other = partition(old_profile['files'],old_prefix)
    new_p_local,new_p_other = partition(new_profile['files'],new_prefix)
    require(len(old_p_local)==len(new_p_local)==146 and set(old_p_local)==set(new_p_local),'profile local inventory differs')
    require(new_p_other-old_p_other=={(adapter_path,ADAPTER_SHA)} and not old_p_other-new_p_other,'profile external closure differs')
    require({name for name in old_p_local if old_p_local[name]!=new_p_local[name]}==changed & set(old_p_local),'profile changed byte set differs')
    before=(OLD/'workflow_output_registry.py').read_text()
    after=(NEW/'workflow_output_registry.py').read_text()
    label='STAGED_PRODUCER_ORIGINS = ('
    prefix, tail=before.split(label,1)
    line,suffix=tail.split('\n',1)
    require(line.count('api-integration-v23/')==7,'historical staged origin count differs')
    expected=prefix+label+line.replace('api-integration-v23/',NEW.name+'/')+'\n'+suffix
    require(after==expected,'registry changed beyond seven exact staged origins')
    guard=(OLD/'guard.py').read_text()
    needle="helper_paths = {str((HERE.parent / helper / name).relative_to(ROOT))\n                    for helper in helpers for name in ('__init__.py','generation.py')}"
    require(guard.count(needle)==1,'historical guard helper selection differs')
    require((NEW/'guard.py').read_text()==guard.replace(needle,needle+"\n    helper_paths.add('"+adapter_path+"')"),'guard changed beyond exact adapter closure')
    require(new_manifest['profile_binding']=={'path':new_prefix+'contract-profile.json','sha256':NEW_PROFILE},'successor profile binding differs')
    require(new_manifest['predecessor_source_manifest_binding']=={'path':old_prefix+'source-manifest.json','sha256':OLD_SOURCE},'predecessor source binding differs')
    require(new_profile['integration_members_binding']['path']==new_prefix+'integration-members.json','current integration member origin differs')
    print(json.dumps({'result':'PASS','old_source_sha256':OLD_SOURCE,'new_source_sha256':NEW_SOURCE,
                      'new_profile_sha256':NEW_PROFILE,'source_rows':len(new_manifest['files']),
                      'profile_rows':len(new_profile['files']),'changed_local_files':sorted(changed),
                      'staged_origin_replacements':7,'selected_external_adapter_sha256':ADAPTER_SHA,
                      'actual_producer_calls':0,'authority_effect':'none'},sort_keys=True))


if __name__=='__main__':
    main()
