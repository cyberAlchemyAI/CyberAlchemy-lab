"""Closed exact-byte contracts; no digest domain or authority inference."""
import base64,hashlib,json,re
from pathlib import PurePosixPath
class Refusal(ValueError):pass
class Uncertain(Refusal):pass
def need(value,reason):
    if not value:raise Refusal(reason)
def sha(raw):
    need(type(raw)is bytes,'exact original bytes required');return hashlib.sha256(raw).hexdigest()
def compact(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def parse(raw):
    need(type(raw)is bytes and len(raw)<=16*1024*1024,'bounded exact JSON bytes required')
    def pairs(rows):
        out={}
        for k,v in rows:need(k not in out,'duplicate JSON key');out[k]=v
        return out
    def invalid(value):raise Refusal('nonfinite JSON forbidden')
    try:return json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid)
    except (ValueError,UnicodeError):raise Refusal('invalid original JSON') from None
def closed(value,fields):need(type(value)is dict and set(value)==set(fields),'closed contract fields required')
def pin(value):need(type(value)is str and re.fullmatch('[0-9a-f]{64}',value),'exact independent SHA256 required');return value
def relative(value):
    need(type(value)is str and value and '\\' not in value and '\0' not in value,'exact relative origin required');p=PurePosixPath(value)
    need(not p.is_absolute() and '..' not in p.parts and p.as_posix()==value and value!='.','canonical relative origin required');return value
def flat(value):need(type(value)is str and re.fullmatch('[a-z0-9][a-z0-9-]{0,95}',value),'bounded flat operation required');return value
def pointer(value,selector):
    need(type(selector)is str and (selector=='' or selector.startswith('/')),'explicit original pointer required')
    for token in selector.split('/')[1:]:
        need(re.search('~(?![01])',token)is None,'invalid pointer escape');part=token.replace('~1','/').replace('~0','~')
        try:
            if type(value)is list:need(re.fullmatch('0|[1-9][0-9]*',part),'canonical list index required');value=value[int(part)]
            else:need(type(value)is dict,'original pointer unresolved');value=value[part]
        except (KeyError,IndexError):raise Refusal('original pointer unresolved') from None
    return value
def verify_files(files,expected):
    need(type(files)is dict and type(expected)is dict and bool(files) and set(files)==set(expected),'exact full original member closure required')
    total=0
    for path,raw in files.items():
        relative(path);pin(expected[path]);need(type(raw)is bytes and len(raw)<=16*1024*1024 and sha(raw)==expected[path],'original member changed')
        total+=len(raw);need(total<=128*1024*1024,'full original byte budget exceeded')
    return True

def typed_records(files,original_manifest,review,original):
    """Headers follow original authoritative promotion's actual subjects.

    This new explicit materializer adds the five-field interchange header to
    exact original C07 entry/version/carrier derivations. No native event is
    guessed into a typed Artifact. T31 revalidates each original carrier.
    """
    context=original.loads(files['validation/context.json']);out=[]
    for path,raw in sorted(files.items()):
        if not path.startswith(('targets/','instances/')):continue
        body=original.loads(raw)
        selected=[r for r in review['targets'] if r['record_path']==path]
        if selected:
            need(len(selected)==1,'unique original selected target required');row=selected[0]
            identity=row['identity'];version=row['version_ref'];carrier=row['carrier_ref']
        else:
            identity=body['node_id'];version=identity+'@repository.'+review['bundle_id'];carrier=original._carrier(context,body['kind'])
        scope=body.get('scope_ref',review['authority']['scope_ref'])
        need(scope==review['authority']['scope_ref'],'original material scope differs')
        header={'scope_ref':scope,'identity_ref':identity,'version_ref':version,'carrier_ref':carrier,'byte_sha256':sha(raw)}
        out.append({'role':body.get('kind',row['kind'] if selected else None),'artifact':header,
                    'original_path':path,'base64_original':base64.b64encode(raw).decode()})
    need(out and {r['role'] for r in out}>={'decision','decision-bundle','decision-checkpoint','admission-transaction','project-state','project-semantic-event-history','project-governance-event-history'},'original coupled governance/State/history closure missing')
    return out

DESCRIPTOR_FIELDS=('schema_version','bundle_id','repository_bundle_binding','review_sha256','owner_response_sha256','owner_verification','owner_verified_at','native_store_root','native_store_identity','source_binding','profile_binding','source_cut','principal_ref','work_ref','native_store_ref','native_branch_ref','native_head_binding','native_generation','native_event_files','native_projection_sha256','files','commit_point','inner_native_commit_is_outer_visibility','automatic_retry','runtime_activations','external_effect_refs','authority_effect')
def validate_descriptor(value):
    closed(value,DESCRIPTOR_FIELDS)
    need(value['schema_version']=='lab-coupled-native-original-publication/v1-candidate'and value['authority_effect']=='none'and value['commit_point']=='descriptor-bound-coupled-original-byte-record'and value['inner_native_commit_is_outer_visibility']is False and value['automatic_retry']is False and type(value['runtime_activations'])is int and value['runtime_activations']==0 and value['external_effect_refs']==[],'coupled commit cannot infer activation/authority/two-HEAD atomicity')
    flat(value['bundle_id'])
    for field in ('review_sha256','owner_response_sha256','native_projection_sha256'):pin(value[field])
    need(type(value['files'])is dict and bool(value['files'])and type(value['native_event_files'])is dict and bool(value['native_event_files']),'complete selected original member maps required')
    for field in ('files','native_event_files'):
        for path,digest in value[field].items():relative(path);pin(digest)
    for field in ('repository_bundle_binding','source_binding','profile_binding'):
        closed(value[field],('ref','sha256'));pin(value[field]['sha256']);need(type(value[field]['ref'])is str and value[field]['ref'],'original binding origin absent')
    closed(value['native_head_binding'],('path','sha256'));pin(value['native_head_binding']['sha256'])
    need(type(value['native_store_identity'])is list and len(value['native_store_identity'])==2 and all(type(i)is int for i in value['native_store_identity']),'independent native root identity required')
    return True

NATIVE_SELECTION_FIELDS=('head_binding','generation','event_files','projection_sha256','source_cut','review_sha256','witness_correspondence')
def validate_native_selection(selected,native,review,control):
    closed(selected,NATIVE_SELECTION_FIELDS)
    need(selected['head_binding']==native['head_binding']and selected['generation']==native['generation']and selected['event_files']=={p:r['sha256']for p,r in native['event_files'].items()}and selected['projection_sha256']==native['projection_sha256'],'independent actual native selection differs')
    need(selected['source_cut']==control['source_cut']and selected['review_sha256']==sha(compact(review)),'native/source/review coupling differs')
    rows=selected['witness_correspondence'];need(type(rows)is list and rows,'exact original native witness-to-target correspondence required')
    versions=[]
    for row in rows:
        closed(row,('target_version_ref','witness_pointer','witness_sha256'))
        need(row['target_version_ref']not in versions,'duplicate native target correspondence');versions.append(row['target_version_ref'])
        witness=pointer(native['causal_witnesses'],row['witness_pointer'])
        need(sha(compact(witness))==row['witness_sha256'],'actual native source witness differs')
        # Original source_view/source_typed_relation retains exact represented
        # revision; Root explicitly selects its actual tuple, never a string
        # discovered elsewhere in native event prose.
        need(type(witness)is dict and witness.get('version_ref')==row['target_version_ref'],'selected native witness must be exact original represented-subject tuple')
    need(set(versions)=={r['version_ref']for r in review['targets']},'every selected target needs actual native correspondence; no package-member inference')
    return True
