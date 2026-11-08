"""Pure bounded envelope validator; no Docker subprocess or authority effect."""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import re

EFFECT_ENABLED=False
MAX_STDOUT=8192
MAX_STDERR=4096
class Refused(RuntimeError):pass
def need(ok,code):
    if not ok:raise Refused(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def parse(raw):
    def pairs(items):
        result={}
        for key,value in items:
            need(key not in result,'DUPLICATE_JSON_KEY')
            result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(Refused('NONFINITE_JSON')))

def validate_fixture_envelope(basis,claim_sha,claim_identity,child_stdout,child_stderr,
                              external_os,terminal,name_absent):
    """Validate a synthetic shape, never turn it into an effect verdict."""
    need(type(child_stdout) is bytes and 0<len(child_stdout)<=MAX_STDOUT and
         type(child_stderr) is bytes and len(child_stderr)<=MAX_STDERR and
         child_stderr==b'' and type(external_os) is int and external_os==0,
         'EXTERNAL_PROCESS_OR_STREAMS')
    need(type(terminal) is dict and set(terminal)=={'cid','exit_code','oom_killed'} and
         type(terminal['cid']) is str and re.fullmatch('[0-9a-f]{64}',terminal['cid']) and
         type(terminal['exit_code']) is int and terminal['exit_code']==0 and
         terminal['oom_killed'] is False and
         name_absent is True,'DOCKER_TERMINAL_OR_ABSENCE')
    need(type(claim_sha) is str and re.fullmatch('[0-9a-f]{64}',claim_sha),
         'CLAIM_MARKER_DIGEST')
    need(type(claim_identity) is dict and set(claim_identity)=={'dev','ino'} and
         all(type(value) is int and value>0 for value in claim_identity.values()),
         'HELD_CLAIM_IDENTITY')
    row=parse(child_stdout)
    expected={'schema','status','scope_ref','source_manifest_sha256',
              'reader_manifest_sha256','reader_code_sha256',
              'loader_freeze_sha256','controller_freeze_sha256',
              'source_period_sha256','opened_at','closed_at',
              'claim_marker_sha256','claim_dev','claim_ino',
              'first_guard','final_guard',
              'reader_guard','close_ok','authority_effect','actual_owner_outcome',
              'retry_allowed'}
    need(set(row)==expected and
         row['schema']=='context-signed-scope-child-attestation/v1' and
         row['status']=='PROVISIONAL_EXTERNAL_OBSERVER_ONLY' and
         row['scope_ref']==basis['scope_expected'] and
         row['source_manifest_sha256']==basis['source_manifest_sha256'] and
         row['reader_manifest_sha256']==basis['reader_manifest_sha256'] and
         row['reader_code_sha256']==basis['reader_code_sha256'] and
         row['loader_freeze_sha256']==basis['loader_freeze_sha256'] and
         row['controller_freeze_sha256']==basis['controller_freeze_sha256'] and
         row['source_period_sha256']==basis['source_period_sha256'] and
         row['claim_marker_sha256']==claim_sha and
         type(row['claim_dev']) is int and row['claim_dev']==claim_identity['dev'] and
         type(row['claim_ino']) is int and row['claim_ino']==claim_identity['ino'] and
         all(row[name] is True for name in
             ('first_guard','final_guard','reader_guard','close_ok')) and
         row['authority_effect']=='none' and
         row['actual_owner_outcome'] is None and
         row['retry_allowed'] is False,
         'SIGNED_SCOPE_ATTESTATION_BINDING')
    need(type(row['opened_at']) is str and type(row['closed_at']) is str,
         'SIGNED_SCOPE_TIME_TEXT')
    try:
        opened=dt.datetime.fromisoformat(row['opened_at'])
        closed=dt.datetime.fromisoformat(row['closed_at'])
    except ValueError as exc:raise Refused('SIGNED_SCOPE_TIME_TEXT') from exc
    start=dt.datetime.fromisoformat(basis['source_period_start'])
    end=dt.datetime.fromisoformat(basis['source_period_end'])
    need(opened.tzinfo is not None and closed.tzinfo is not None and
         opened.utcoffset()==dt.timedelta() and
         closed.utcoffset()==dt.timedelta() and
         start<=opened<=closed<end and
         closed-opened<=dt.timedelta(seconds=900),
         'SIGNED_SCOPE_PERIOD_OR_DURATION')
    return {'schema':'context-signed-scope-observer-fixture/v1-inert',
            'status':'SYNTHETIC_ENVELOPE_VALID_NO_EFFECT_CLAIM',
            'effect':'NOT_RUN','attestation_sha256':sha(child_stdout),
            'claim_marker_sha256':claim_sha,'external_os':0,
            'terminal_exit':0,'name_absent':True}

def dispatch(*_args,**_kwargs):raise Refused('EFFECT_DISABLED_NO_DOCKER_DISPATCH')
def publish_attestation(*_args,**_kwargs):raise Refused('EFFECT_DISABLED_NO_REAL_ATTESTATION')
