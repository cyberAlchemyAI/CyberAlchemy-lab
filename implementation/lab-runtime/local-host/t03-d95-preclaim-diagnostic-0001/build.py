"""Disjoint API recut with bounded T03 preclaim stage telemetry."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v33-t03-one-lesson-native-v4-margin-0006'
NEW = BASE / 'api-integration-v33-t03-one-lesson-native-v4-preclaim-diagnostic-0001'
OLD_MANIFEST_SHA = '2e152c9ec926f9f1e161b1002cf1ba1b128e86e2cef1f6712c1ef2714022abe9'
OLD_PROFILE_SHA = '1f2cf91eaa72c4687a791faaaac264ef5132afa2ba369f970f10787a17fe1750'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def row(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError('selected file missing or linked: ' + str(path))
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': digest(path.read_bytes())}


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def replace_once(raw, old, new):
    if raw.count(old) != 1:
        raise ValueError('selected instrumentation anchor cardinality differs: ' + repr(old[:90]))
    return raw.replace(old, new)


def instrument(raw):
    raw = replace_once(raw, 'import re\n', 'import re\nimport json\nimport sys\nimport time\nimport traceback\n')
    anchor = '\n\ndef __getattr__(name):'
    helper = '''\n\ndef _t03_trace(stage, error=None, context_deadline=None):
    """Public diagnostic only; never returns private exception text or affects dispatch."""
    try:
        event = {'kind':'T03-preclaim-stage','stage':stage,
                 'utc':now().isoformat(),'monotonic_ns':time.monotonic_ns()}
        if error is not None:
            frames=traceback.extract_tb(error.__traceback__)
            frame=frames[-1] if frames else None
            path=Path(frame.filename).resolve() if frame is not None else None
            event.update(exception_class=type(error).__name__,
                         origin_file=(str(path.relative_to(ROOT)) if path is not None and path.is_relative_to(ROOT) else '<external>'),
                         origin_line=None if frame is None else frame.lineno,
                         exception_text_sha256=source.sha(str(error).encode()),
                         context_deadline=context_deadline)
        sys.stderr.write(json.dumps(event,sort_keys=True)+'\\n')
        sys.stderr.flush()
    except Exception:
        pass
'''
    raw = replace_once(raw, anchor, helper + anchor)
    raw = replace_once(raw,
        "        message=call['message'];inner=message_bytes(raw);effect_started=False;namespace=None\n",
        "        message=call['message'];inner=message_bytes(raw);effect_started=False;namespace=None\n"
        "        diagnostic_stage='before-schemas-guard'\n"
        "        if name=='lesson.apply':_t03_trace(diagnostic_stage)\n")
    raw = replace_once(raw,
        "                try:jcs.fingerprint(call,context)\n",
        "                if name=='lesson.apply':\n"
        "                    diagnostic_stage='before-jcs';_t03_trace(diagnostic_stage)\n"
        "                try:jcs.fingerprint(call,context)\n")
    raw = replace_once(raw,
        "                old,recorded=self.vault.lookup({'operation':name,'idempotency_key':call['idempotency_key']},context)\n",
        "                if name=='lesson.apply':\n"
        "                    diagnostic_stage='before-lookup';_t03_trace(diagnostic_stage)\n"
        "                old,recorded=self.vault.lookup({'operation':name,'idempotency_key':call['idempotency_key']},context)\n"
        "                if name=='lesson.apply':\n"
        "                    diagnostic_stage='after-lookup';_t03_trace(diagnostic_stage)\n")
    raw = replace_once(raw,
        "                elif name=='lesson.apply':application_builder=self.select_application(message,call['expected_source_cut'],call['idempotency_key'])\n",
        "                elif name=='lesson.apply':\n"
        "                    diagnostic_stage='before-builder';_t03_trace(diagnostic_stage)\n"
        "                    application_builder=self.select_application(message,call['expected_source_cut'],call['idempotency_key'])\n"
        "                    diagnostic_stage='after-builder';_t03_trace(diagnostic_stage)\n")
    raw = replace_once(raw,
        "                try:namespace,fp,prior,record,fresh=self.vault.claim(call,raw,context,deadline=effective)\n",
        "                if name=='lesson.apply':\n"
        "                    diagnostic_stage='before-claim';_t03_trace(diagnostic_stage)\n"
        "                try:namespace,fp,prior,record,fresh=self.vault.claim(call,raw,context,deadline=effective)\n")
    raw = replace_once(raw,
        "        except Exception:\n            return self.error(call,raw,inner,ApplicationError('indeterminate' if effect_started else 'integrity-failed',\n",
        "        except Exception as error:\n"
        "            if name=='lesson.apply':_t03_trace(diagnostic_stage,error,context['limits']['deadline'])\n"
        "            return self.error(call,raw,inner,ApplicationError('indeterminate' if effect_started else 'integrity-failed',\n")
    return raw


def build():
    if row(OLD / 'source-manifest.json')['sha256'] != OLD_MANIFEST_SHA or row(OLD / 'contract-profile.json')['sha256'] != OLD_PROFILE_SHA:
        raise ValueError('predecessor source/profile changed')
    if NEW.exists():
        raise ValueError('successor already exists')
    source = json.loads((OLD / 'source-manifest.json').read_bytes())
    profile = json.loads((OLD / 'contract-profile.json').read_bytes())
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    own = [r for r in source['files'] if r['path'].startswith(old_prefix)]
    if len(own) != 203 or len(source['files']) != 211:
        raise ValueError('predecessor closure cardinality differs')
    NEW.mkdir()
    for selected in own:
        path = ROOT / selected['path']
        if row(path) != selected:
            raise ValueError('predecessor own source changed: ' + selected['path'])
        target = NEW / selected['path'][len(old_prefix):]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    service = NEW / 'service.py'
    service.write_text(instrument(service.read_text()))
    new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
    profile['files'] = sorted((row(NEW / r['path'][len(old_prefix):]) if r['path'].startswith(old_prefix) else r
                               for r in profile['files']), key=lambda r: r['path'])
    profile['integration_members_binding'] = row(NEW / 'integration-members.json')
    profile['claim_ceiling'] = 'T03 bounded preclaim stage diagnosis only; no Lesson effect established.'
    write(NEW / 'contract-profile.json', profile)
    source['files'] = sorted((row(NEW / r['path'][len(old_prefix):]) if r['path'].startswith(old_prefix) else r
                              for r in source['files']), key=lambda r: r['path'])
    source['profile_binding'] = row(NEW / 'contract-profile.json')
    source['predecessor_source_manifest_binding'] = row(OLD / 'source-manifest.json')
    source['claim_ceiling'] = profile['claim_ceiling']
    write(NEW / 'source-manifest.json', source)
    receipt = {'schema_version':'lab-T03-d95-preclaim-diagnostic-recut/v1-candidate',
               'predecessor_binding':row(OLD / 'source-manifest.json'),
               'successor_package':NEW.relative_to(ROOT).as_posix(),
               'successor_manifest_sha256':row(NEW / 'source-manifest.json')['sha256'],
               'successor_binding':row(NEW / 'source-manifest.json'),
               'successor_profile_binding':row(NEW / 'contract-profile.json'),
               'service_binding':row(service),'own_file_count':203,'external_file_count':8,
               'authority_effect':'none','lesson_applied':False,'lesson_assessed':False}
    write(NEW / 'rebind-receipt.json', receipt)
    return receipt


if __name__ == '__main__':
    print(json.dumps(build(),sort_keys=True,indent=2))
