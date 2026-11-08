"""Bounded in-memory Context fixture query/generate facade.

No original Source/control/generation imports, permission issuance, I/O, native
read, bridge action or authentication. Handles contain selected fixture bytes.
Evaluation time is an explicit fixture observation, never actual host authority.
"""
import copy
import datetime as dt
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import PurePosixPath

from . import context_fixture_provider_0001 as bodies

MAX_RECORD = 65536
MAX_REQUEST = 1048576
MAX_OUTPUT = 2097152
ROLES = ('source','channel','profile','mapper_manifest','mapping','native_output')
PROFILE = {'schema_version':'lab-context-fixture-profile/v1-inert','fixture_only':True,
           'body_schema':bodies.SCHEMA,'query_schema':'lab-context-orchestration-query/v1-inert',
           'delivery_schema':'lab-context-orchestration-delivery/v1-inert',
           'provenance_schema':'lab-context-orchestration-provenance/v1-inert',
           'lesson_schema':'lab-context-orchestration-lessons/v1-inert',
           'authority_effect':'none'}


class Refusal(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise Refusal(code)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def encoded(value):return bodies.encoded(value)


def compact(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()


def _closed(value, keys):
    need(type(value) is dict and set(value)==set(keys),'CLOSED_FIELDS')


def _pairs(rows):
    result={}
    for key,value in rows:
        need(key not in result,'DUPLICATE_KEY');result[key]=value
    return result


def _json(raw):
    need(type(raw) is bytes and 0<len(raw)<=MAX_RECORD,'RECORD_BOUND')
    try:
        value=json.loads(raw,object_pairs_hook=_pairs,parse_constant=lambda _: (_ for _ in ()).throw(Refusal('NONFINITE_JSON')))
    except (ValueError,UnicodeError,RecursionError):
        raise Refusal('RECORD_JSON') from None
    need(encoded(value)==raw,'CANONICAL_BYTES')
    return value


def _hash(value):
    need(type(value) is str and re.fullmatch('[0-9a-f]{64}',value) is not None,'HASH')


def _path(value):
    need(type(value) is str and 0<len(value)<=4096 and '\\' not in value and
         PurePosixPath(value).as_posix()==value and
         all(part not in ('.','..') for part in PurePosixPath(value).parts),'LOCATOR')


def _binding(row,raw):
    _closed(row,('path','sha256','size_bytes'));_path(row['path']);_hash(row['sha256'])
    need(type(row['size_bytes']) is int and 0<row['size_bytes']<=MAX_RECORD and
         type(raw) is bytes and row['size_bytes']==len(raw) and row['sha256']==sha(raw),'SELECTED_BYTES')


def _instant(value):
    need(type(value) is str and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ',value) is not None,'UTC_TIME')
    try:return dt.datetime.strptime(value,'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc)
    except ValueError:raise Refusal('UTC_TIME') from None


def _identity(value):
    need(type(value) is str and re.fullmatch(r'fixture:[a-z0-9:@._-]{1,160}',value) is not None,'FIXTURE_IDENTITY')


@dataclass(frozen=True)
class FixtureSource:
    raw: bytes


@dataclass(frozen=True)
class FixtureChannel:
    raw: bytes


@dataclass(frozen=True)
class FixtureSchemas:
    raw: bytes


class FixtureFacade:
    """Closed value facade; construction does not authenticate these fixtures."""
    def __init__(self,selection_raw,*,expected_selection_sha256,selection_path,inputs,body_bytes,evaluation_time):
        _hash(expected_selection_sha256);_path(selection_path)
        need(type(selection_raw) is bytes and sha(selection_raw)==expected_selection_sha256,'SELECTION_DIGEST')
        need(type(inputs) is dict and set(inputs)==set(ROLES) and all(type(v) is bytes for v in inputs.values()),'INPUT_ROLES')
        need(type(body_bytes) is tuple,'BODY_INPUTS')
        self._selection_raw=selection_raw
        self._expected=expected_selection_sha256
        self._selection_path=selection_path
        self._inputs=tuple((role,inputs[role]) for role in ROLES)
        self._body_bytes=body_bytes
        self._time=evaluation_time
        self._validate(evaluation_time)

    def _validate(self,time):
        need(type(self._selection_raw) is bytes and sha(self._selection_raw)==self._expected,'SELECTION_CHANGED')
        _path(self._selection_path)
        s=_json(self._selection_raw)
        _closed(s,('schema_version','fixture_only','attempt_id','bindings','body_rows','deadline','authority_effect','actual_owner_outcome'))
        need(s['schema_version']=='lab-context-fixture-facade-selection/v1-inert' and s['fixture_only'] is True and
             s['authority_effect']=='none' and s['actual_owner_outcome'] is None and
             type(s['attempt_id']) is str and re.fullmatch('[a-z0-9-]{1,64}',s['attempt_id']) is not None,'SELECTION_POSTURE')
        _closed(s['bindings'],ROLES)
        need(type(self._inputs) is tuple and len(self._inputs)==len(ROLES) and tuple(r[0] for r in self._inputs)==ROLES,'INPUT_ROLES')
        inputs=dict(self._inputs);parsed={}
        for role in ROLES:
            _binding(s['bindings'][role],inputs[role]);parsed[role]=_json(inputs[role])
        need(len({r['path'] for r in s['bindings'].values()})==len(ROLES),'DUPLICATE_LOCATOR')
        source,channel,profile=parsed['source'],parsed['channel'],parsed['profile']
        _closed(source,('schema_version','fixture_only','principal_ref','scope_ref','assignment_ref','work_ref','coordination_ref','source_cut','not_before','expires_at','authority_effect','actual_owner_outcome'))
        need(source['schema_version']=='lab-context-fixture-source/v1-inert' and source['fixture_only'] is True and source['authority_effect']=='none' and source['actual_owner_outcome'] is None,'SOURCE_POSTURE')
        for key in ('principal_ref','scope_ref','assignment_ref','work_ref','coordination_ref'):_identity(source[key])
        _closed(channel,('schema_version','fixture_only','principal_ref','scope_ref','source_sha256','profile_sha256','allowed_operations','not_before','expires_at','revoked','max_input_bytes','max_output_bytes','max_session_seconds','authority_effect','actual_owner_outcome'))
        need(channel['schema_version']=='lab-context-fixture-channel/v1-inert' and channel['fixture_only'] is True and channel['authority_effect']=='none' and channel['actual_owner_outcome'] is None and channel['revoked'] is False,'FIXTURE_PERMISSION')
        need(channel['principal_ref']==source['principal_ref'] and channel['scope_ref']==source['scope_ref'] and
             channel['source_sha256']==s['bindings']['source']['sha256'] and channel['profile_sha256']==s['bindings']['profile']['sha256'] and
             channel['allowed_operations']==['context.get','session.open'],'PERMISSION_JOIN')
        for field,maximum in [('max_input_bytes',MAX_REQUEST),('max_output_bytes',MAX_OUTPUT),('max_session_seconds',900)]:
            need(type(channel[field]) is int and 1<=channel[field]<=maximum,'PERMISSION_BOUND')
        need(type(profile) is dict and encoded(profile)==encoded(PROFILE),'FIXTURE_SCHEMA')
        mapping,native,manifest=parsed['mapping'],parsed['native_output'],parsed['mapper_manifest']
        need(type(mapping) is dict and mapping.get('authority_effect')=='none' and mapping.get('actual_owner_outcome') is None and
             type(mapping.get('rows')) is list and len(mapping['rows'])==25,'MAPPING_FIXTURE')
        need(encoded(source['source_cut'])==encoded(mapping.get('source_cut')),'SOURCE_CUT_JOIN')
        _closed(source['source_cut'],('fixture_only','sha256'))
        need(source['source_cut']['fixture_only'] is True,'SOURCE_CUT_FIXTURE');_hash(source['source_cut']['sha256'])
        need(all(type(r) is dict and type(r.get('artifact')) is dict and 'scope_ref' not in r['artifact'] for r in mapping['rows']),'MAPPING_SCOPE_ENRICHMENT')
        need(encoded(native)==encoded({'authority_effect':'none','cut':{'semantic_cursor':25},'governance_cursor':25,'governed_nodes':[{'fixture_only':True} for _ in range(15)]}),'NATIVE_FIXTURE_ENRICHMENT')
        _closed(manifest,('schema_version','files','source_manifest_binding','authority_effect','actual_owner_outcome'))
        need(manifest['schema_version']=='lab-mapped-context-package/v1-candidate' and manifest['authority_effect']=='none' and manifest['actual_owner_outcome'] is None and
             type(manifest['files']) is list and len(manifest['files'])==54,'MAPPER_MANIFEST')
        seen={}
        for row in manifest['files']:
            _closed(row,('path','sha256'));_path(row['path']);_hash(row['sha256']);need(row['path'] not in seen,'MAPPER_DUPLICATE');seen[row['path']]=row['sha256']
        for role in ('mapping','native_output'):
            b=s['bindings'][role];need(seen.get(b['path'])==b['sha256'],'MAPPER_MEMBER_JOIN')
        now=_instant(time);deadline=_instant(s['deadline'])
        for period in (source,channel):
            need(_instant(period['not_before'])<=now<deadline<=_instant(period['expires_at']),'FIXTURE_INTERVAL')
        need(0<(deadline-now).total_seconds()<=channel['max_session_seconds'],'FIXTURE_SESSION_BOUND')
        try:
            selected=bodies.select_bodies(self._body_bytes,expected_rows=s['body_rows'],
                mapper_manifest_sha256=s['bindings']['mapper_manifest']['sha256'],mapping_sha256=s['bindings']['mapping']['sha256'])
        except bodies.Refusal:raise Refusal('BODY_SELECTION') from None
        need(sum(map(len,self._body_bytes))<=channel['max_output_bytes'],'OUTPUT_BUDGET')
        return s,source,channel,selected

    def handles(self):
        self._validate(self._time);inputs=dict(self._inputs)
        return FixtureSource(inputs['source']),FixtureChannel(inputs['channel']),FixtureSchemas(inputs['profile'])

    def _guard(self,source,channel,schemas,time):
        s,src,ch,selected=self._validate(time)
        originals=dict(self._inputs)
        need(type(source) is FixtureSource and type(source.raw) is bytes and source.raw==originals['source'],'SOURCE_HANDLE')
        need(type(channel) is FixtureChannel and type(channel.raw) is bytes and channel.raw==originals['channel'],'CHANNEL_HANDLE')
        if schemas is not None:
            need(type(schemas) is FixtureSchemas and type(schemas.raw) is bytes and schemas.raw==originals['profile'],'SCHEMA_HANDLE')
        return s,src,ch,selected

    def fixture_query(self,source,channel,*,evaluation_time=None):
        s,src,ch,_=self._guard(source,channel,None,self._time if evaluation_time is None else evaluation_time)
        query={'schema_version':PROFILE['query_schema'],'fixture_only':True,'request_ref':'fixture:context-request:'+s['attempt_id'],
               'actor':{'principal_ref':src['principal_ref'],'role_assignment_refs':[],'agent_instance_ref':None,'session_ref':None,'assignment_ref':None},
               'assignment':src['assignment_ref'],'work':src['work_ref'],'coordination_context':src['coordination_ref'],
               'source_cut':copy.deepcopy(src['source_cut']),'intended_use':'Exercise owned Context builder orchestration only',
               'selectors':[],'exclusions':['historical-session-memory','private-source-archives','external-effects','unrelated-work'],
               'freshness_requirement':'fixture-only','budget':{'max_actions':0,'max_input_bytes':ch['max_input_bytes'],'max_output_bytes':ch['max_output_bytes'],'deadline':s['deadline']},'authority_effect':'none'}
        need(len(compact(query))<=ch['max_input_bytes'],'REQUEST_BUDGET')
        return query

    def generate(self,source,channel,message,raw,mapped_pin,schemas,*,evaluation_time=None):
        need(type(schemas) is FixtureSchemas,'SCHEMA_HANDLE')
        time=self._time if evaluation_time is None else evaluation_time
        s,src,ch,selected=self._guard(source,channel,schemas,time)
        expected=self.fixture_query(source,channel,evaluation_time=time)
        need(type(message) is dict and message==expected and type(raw) is bytes and len(raw)<=MAX_REQUEST and raw==compact(expected) and compact(message)==raw,'REQUEST_JOIN')
        need(type(mapped_pin) is str and mapped_pin==s['bindings']['mapper_manifest']['sha256'],'MAPPED_PIN')
        values,refs=selected.values()
        simple=lambda role:{k:s['bindings'][role][k] for k in ('path','sha256')}
        request={'ref':'request:'+message['request_ref'],'sha256':sha(raw)}
        delivery={'schema_version':PROFILE['delivery_schema'],'posture':'fixture-only','expires_at':s['deadline'],
                  'request_binding':request,'artifact_refs':list(refs.values()),'mapper_manifest_binding':simple('mapper_manifest'),
                  'authority_effect':'none','actual_owner_outcome':None}
        provenance={'schema_version':PROFILE['provenance_schema'],'fixture_only':True,'request_binding':copy.deepcopy(request),
                    'fixture_input_binding':{'path':self._selection_path,'sha256':self._expected},'mapper_manifest_binding':simple('mapper_manifest'),
                    'native_output_binding':simple('native_output'),'original_generation_executed':False,'authority_effect':'none'}
        lesson={'schema_version':PROFILE['lesson_schema'],'fixture_only':True,'selected_lessons':[],'catalog_evaluated':False,'authority_effect':'none'}
        need(sum(map(len,self._body_bytes))+sum(len(encoded(v)) for v in (refs,delivery,provenance,lesson))<=ch['max_output_bytes'],'OUTPUT_BUDGET')
        return values,refs,delivery,provenance,lesson
