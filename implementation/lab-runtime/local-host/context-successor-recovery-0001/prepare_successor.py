"""Public-only new Source identity from the reviewed public recipe.

No historical branch.snapshot bytes are opened. Running this script without
--materialize-public is read-only; materialization writes only eight public
generated files and a public-cut manifest under this candidate directory.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'source-only-docker-0002/prepare_public.py'
NEW_ID = 'R03-docker-source-20261020-0002'
NEW_FAMILY = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0002'
NEW_AUTH = ('docs/plans/0011-lab-runtime-completion/runs/0001-execution/'
            'source-only-dev-20261020-successor/authorization.json')
START = '2026-10-20T15:00:00+00:00'
END = '2026-10-21T15:00:00+00:00'
OLD_ENGINE_ALIAS = '_cal_docker_source_engine_20261020_0001'
NEW_ENGINE_ALIAS = '_cal_docker_source_engine_20261020_0002'
OLD_BRIDGE_ALIAS = '_cal_docker_source_bridge_20261020_0001'
NEW_BRIDGE_ALIAS = '_cal_docker_source_bridge_20261020_0002'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def need(ok, why):
    if not ok:
        raise ValueError(why)


def construct():
    spec = importlib.util.spec_from_file_location('_cal_source_public_preimage', BASE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.NEW_ID = NEW_ID
    module.NEW_FAMILY = NEW_FAMILY
    module.NEW_AUTH = NEW_AUTH
    module.START = START
    module.END = END
    predecessor_projection = module.project_role

    def successor_projection(name, raw):
        projected = predecessor_projection(name, raw)
        if name == 'base.py':
            text = projected.decode('utf-8')
            for old, new in ((OLD_ENGINE_ALIAS, NEW_ENGINE_ALIAS),
                             (OLD_BRIDGE_ALIAS, NEW_BRIDGE_ALIAS)):
                need(text.count(old) == 1 and new not in text,
                     'Source module alias projection differs')
                text = text.replace(old, new, 1)
            projected = text.encode('utf-8')
            compile(projected, NEW_FAMILY + '/' + name, 'exec', optimize=0)
            compile(projected, NEW_FAMILY + '/' + name, 'exec', optimize=2)
        return projected

    module.project_role = successor_projection
    plan, generated = module.construct()
    need(plan['new_family'] == NEW_FAMILY and plan['identity_prefix'] == NEW_ID and
         plan['not_before'] == START and plan['expires_at'] == END and
         plan['private_archive_bodies_read'] is False and plan['effect'] == 'NOT_RUN',
         'successor identity or effect differs')
    need(len(plan['public_inputs']) == 933 and len(generated) == 8 and
         len(plan['generated_bindings']) == 8 and
         all(not row['path'].endswith('/branch.snapshot') for row in
             plan['public_inputs'] + plan['generated_bindings']),
         'successor public cut contains private archive or wrong count')
    need({row['path']: row['sha256'] for row in plan['generated_bindings']} ==
         {name: sha(raw) for name, raw in generated.items()},
         'generated public bytes differ from bindings')
    return plan, generated, module.encoded(plan)


def materialize():
    plan, generated, raw = construct()
    target = HERE / 'generated'
    output = HERE / 'public-cut.json'
    need(not target.exists() and not output.exists(), 'public successor cut already exists')
    target.mkdir(mode=0o700)
    for name, value in sorted(generated.items()):
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)
    output.write_bytes(raw)
    return {'status': 'PUBLIC_ONLY_MATERIALIZED', 'generated_files': len(generated),
            'source_manifest_sha256': plan['source_manifest']['sha256'],
            'public_cut_sha256': sha(raw), 'private_body_read': False,
            'source_effect': 'NOT_RUN'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--materialize-public', action='store_true')
    args = parser.parse_args()
    if args.materialize_public:
        result = materialize()
    else:
        plan, generated, raw = construct()
        result = {'status': 'PUBLIC_ONLY_READ_ONLY_PROJECTION',
                  'generated_files': len(generated),
                  'source_manifest_sha256': plan['source_manifest']['sha256'],
                  'public_cut_sha256': sha(raw), 'source_effect': 'NOT_RUN'}
    print(json.dumps(result, sort_keys=True))
