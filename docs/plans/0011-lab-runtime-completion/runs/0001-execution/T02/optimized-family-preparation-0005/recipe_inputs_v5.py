"""Exact independently pinned preparation baseline; selections grant no authority."""
import hashlib,json,os,stat
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[6]
RECIPE4=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/optimized-family-preparation-0004'
BASELINE_PIN='95a73902cc5b584f0185a0b16df5ad4213816d57a0356e8fc3bc62c86fba0067'
FORBIDDEN_LIVE_API_INPUTS=frozenset(['product/lab/release-candidates/v1/interface/api-integration-v17/authentication.schema.json', 'product/lab/release-candidates/v1/interface/api-integration-v17/current_context_sessions.py', 'product/lab/release-candidates/v1/interface/api-integration-v17/current_machine_context_scope.py', 'product/lab/release-candidates/v1/interface/api-integration-v17/machine_auth_scope.py', 'product/lab/release-candidates/v1/interface/api-integration-v17/source-manifest.json', 'product/lab/release-candidates/v1/interface/api-integration-v17/source_bridge.py'])
def need(value, reason):
    if not value:
        raise ValueError(reason)
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def parse(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate selected JSON key'); result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: need(False, 'nonfinite selected JSON'))
def exact(binding, limit=16 * 1024 * 1024):
    need(type(binding) is dict and set(binding) == {'path', 'sha256'}, 'closed exact binding required')
    relative = Path(binding['path'])
    need(not relative.is_absolute() and relative.as_posix() == binding['path'] and '..' not in relative.parts,
         'canonical repository locator required')
    path = ROOT / relative; descriptors = [os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)]
    links = []
    try:
        parent = descriptors[-1]
        for part in path.parts[1:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            descriptors.append(child); info = os.fstat(child)
            links.append((parent, part, child, (info.st_dev, info.st_ino, info.st_mode, info.st_uid)))
            parent = child
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            before = os.fstat(fd)
            need(stat.S_ISREG(before.st_mode) and before.st_size <= limit, 'bounded selected regular input required')
            def stamp(value):
                return (value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
            parts = []; size = 0
            while block := os.read(fd, min(1024 * 1024, limit + 1 - size)):
                parts.append(block); size += len(block); need(size <= limit, 'selected input grew beyond limit')
            raw = b''.join(parts)
            need(stamp(before) == stamp(os.fstat(fd)) == stamp(os.stat(path.name, dir_fd=parent, follow_symlinks=False))
                 and sha(raw) == binding['sha256'], 'selected bytes or attachment changed')
            for anchor, name, held, identity in reversed(links):
                a = os.stat(name, dir_fd=anchor, follow_symlinks=False); h = os.fstat(held)
                need((a.st_dev, a.st_ino, a.st_mode, a.st_uid) == (h.st_dev, h.st_ino, h.st_mode, h.st_uid) == identity,
                     'selected ancestor detached')
            return raw
        finally:
            os.close(fd)
    finally:
        for fd in reversed(descriptors):
            os.close(fd)


def verify_baseline():
    binding={'path':(HERE/'preparation-baseline.json').relative_to(ROOT).as_posix(),'sha256':BASELINE_PIN}
    baseline=parse(exact(binding))
    need(set(baseline)=={'schema_version','authority_effect','native_assembly_or_shared_changes_authorized','parent_recipe4_binding','parent_manifest4_binding','parent_recipe4_review_binding','Root_causal_review_binding','parent_recipe_declaration_count','unchanged_declaration_count','snapshot_declaration_count','original_recipe_declarations','declaration_mapping','technical_bindings','mutable_snapshot_pairs','fixed_runtime_descriptor_binding','historical_current_API_source_binding','historical_runtime_API_bindings','runtime_template_snapshot_pairs','historical_families_unchanged'},'closed original recipe5 baseline required')
    need(baseline['schema_version']=='lab-T02-v5-preparation-baseline/v1-candidate' and baseline['authority_effect']=='none' and baseline['native_assembly_or_shared_changes_authorized'] is False,'technical preparation only')
    need(baseline['parent_recipe4_binding']['path']==(RECIPE4/'recipe-selection.json').relative_to(ROOT).as_posix(),'true recipe4 dependency required')
    parent=parse(exact(baseline['parent_recipe4_binding']))
    need(parent['files']==baseline['original_recipe_declarations'] and len(parent['files'])==baseline['parent_recipe_declaration_count']==349,'all349 original declarations required')
    for key in ['parent_manifest4_binding','parent_recipe4_review_binding','Root_causal_review_binding','fixed_runtime_descriptor_binding']:exact(baseline[key])
    pairs=baseline['mutable_snapshot_pairs'];need(type(pairs) is list and len(pairs)==6,'exact six snapshot pairs required')
    snapshots={}
    for item in pairs:
        need(set(item)=={'original_binding','snapshot_binding','size_bytes'},'closed snapshot pair required')
        old,new=item['original_binding'],item['snapshot_binding']
        need(old['path'] in FORBIDDEN_LIVE_API_INPUTS and old['path'] not in snapshots and old['sha256']==new['sha256'] and new['path']==(RECIPE4/'preimages'/old['path']).relative_to(ROOT).as_posix(),'true immutable preparation snapshot origin required')
        need(len(exact(new))==item['size_bytes'],'full retained snapshot bytes changed');snapshots[old['path']]=new
    need(set(snapshots)==FORBIDDEN_LIVE_API_INPUTS,'six original declarations missing')
    mapping=baseline['declaration_mapping'];need(type(mapping) is list and len(mapping)==349 and [item['original_binding'] for item in mapping]==parent['files'],'one-to-one declaration mapping required')
    technical={};changed=0
    for item in mapping:
        need(set(item)=={'original_binding','technical_binding','disposition','size_bytes'},'closed declaration mapping')
        original,current=item['original_binding'],item['technical_binding'];historical=original['path'] in snapshots
        need(current==snapshots.get(original['path'],original) and current['path'] not in FORBIDDEN_LIVE_API_INPUTS,'live mutable preparation origin selected')
        need(item['disposition']==('historical-preparation-at-exact-retained-snapshot' if historical else 'unchanged-technical-origin'),'declaration disposition differs')
        need(len(exact(current))==item['size_bytes'],'full technical input changed')
        need(technical.get(current['path'],current)==current,'conflicting technical identity');technical[current['path']]=current;changed+=historical
    need(changed==baseline['snapshot_declaration_count']==6 and len(mapping)-changed==baseline['unchanged_declaration_count']==343,'declaration conservation counts differ')
    need(baseline['technical_bindings']==[technical[k] for k in sorted(technical)] and len(technical)==343,'closed complete technical input set required')
    need([item['original_binding'] for item in baseline['runtime_template_snapshot_pairs']]==baseline['historical_runtime_API_bindings'] and all(item in pairs for item in baseline['runtime_template_snapshot_pairs']),'all five original runtime template pairs preserved')
    return baseline

def check_activation(binding,instance):
    # Root supplies separate execution authorization and its exclusive slot.
    need(instance=='optimized-0005','exclusive new instance required')
    need(binding['path'].startswith('docs/plans/0011-lab-runtime-completion/runs/0001-execution/T00/'),'Root composition selector required')
    value=parse(exact(binding))
    need(set(value)=={'schema_version','status','authority_effect','instance','margin_merge_binding','observer_merge_binding'},'closed composition prerequisite required')
    need(value['schema_version']=='lab-T02-family-composition-prerequisite/v1-candidate' and value['status']=='merged-reviewed-ready-for-Root-coordination' and value['authority_effect']=='none' and value['instance']==instance,'new Root activation and merged prerequisites pending')
    exact(value['margin_merge_binding']);exact(value['observer_merge_binding']);return value

def check_pre_source_review(binding,family,value=None):
    need(binding['path'].startswith('docs/plans/0011-lab-runtime-completion/runs/0001-execution/T00/'),'Root pre-source review acceptance required')
    accepted=parse(exact(binding))
    need(set(accepted)=={'schema_version','status','authority_effect','instance','construction_binding','preview_binding','independent_review_binding'},'closed pre-source acceptance required')
    need(accepted['schema_version']=='lab-T00-family5-pre-source-closure-acceptance/v1-candidate' and accepted['status']=='Root-reviewed-staged-family5-closure' and accepted['authority_effect']=='none' and accepted['instance']=='optimized-0005','independently reviewed actual staged closure pending')
    need(accepted['construction_binding']['path']==(family/'construction-selection.json').relative_to(ROOT).as_posix() and accepted['preview_binding']['path']==(family/'source-closure-preview.json').relative_to(ROOT).as_posix(),'actual new construction/preview origin required')
    exact(accepted['construction_binding']);preview=parse(exact(accepted['preview_binding']))
    need(preview['construction_binding']==accepted['construction_binding'] and preview['instance']=='optimized-0005' and preview['authority_effect']=='none' and preview['actual_native_or_runtime_executed'] is False,'actual reviewed preview differs')
    review=parse(exact(accepted['independent_review_binding']))
    need(review['result']=='PASS' and review['construction_binding']==accepted['construction_binding'] and review['preview_binding']==accepted['preview_binding'],'independent exact construction/preview review missing')
    if value is not None:need(value==preview['source_manifest_value'],'actual Source metadata closure differs from independently reviewed preview')
    need(not {row['path'] for row in preview['source_manifest_value']['files']}&FORBIDDEN_LIVE_API_INPUTS,'reviewed Source closure contains live mutable API preparation input')
    need(all(row in preview['source_manifest_value']['files'] for row in preview['snapshot_bindings']),'reviewed Source closure omitted a fresh guarded snapshot')
    return accepted
