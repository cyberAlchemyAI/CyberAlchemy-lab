"""Prospective pure review scheduler correction; no generation or score changes.

The frozen V2 planner treats review dependencies as inputs requiring successful
generation. Reviews instead require terminal dispositions, including failures.
This adapter verifies the full original graph and packet before delegating the
unchanged literal prompt and admission/raw-lock guards. Independent approval of
this addendum is required externally before any actual review preparation.
"""
import copy
import composition_i12_runtime_v2 as base


def prepare_review(job, jobs, states, artifacts, context):
    base.require('review_phase' in job and jobs[job['job_id']] == job,
                 'original scheduled review role only')
    dependencies = job['depends_on']
    base.require(len(dependencies) == len(set(dependencies)) and
                 all(k in jobs and 'review_phase' not in jobs[k] for k in dependencies),
                 'exact distinct generation dependencies')
    base.require(all(states[k] in base.TERMINAL for k in dependencies),
                 'every original source disposition terminal before review')
    packet, admin = context['review_packet'], context['review_admin_map']
    base.validate_packet(packet)
    base.require(packet['opaque_map_sha256'] == base.canonical_hash(admin),
                 'exact privately bound administrative map')
    unit_map = {m['job_id']: m['unit_id'] for m in admin['mapping'] if 'unit_id' in m}
    units = {u['unit_id']: u for u in packet['core_packet']['units']}
    base.require(set(unit_map) == set(dependencies) and set(unit_map.values()) == set(units),
                 'complete original review dependency and unit coverage')
    base.require(all(units[unit_map[k]]['execution'] == states[k] for k in dependencies),
                 'failed source dispositions remain exact in assessed packet')
    review_map = {m['job_id']: m['opaque_job_id'] for m in admin['review_job_bindings']}
    base.require(review_map.get(job['job_id']) == context['assigned_reviewer_id'],
                 'original review maps to exact assigned opaque reviewer')
    # Successful construction is not a prerequisite for assessing its failure.
    # Graph completeness above replaces only that inappropriate success test.
    # All original admission, first-save, phase, raw-lock and prompt guards run.
    delegated_job = copy.deepcopy(job)
    delegated_job['depends_on'] = []
    return base.prepare_job(delegated_job, jobs, states, artifacts, context)
