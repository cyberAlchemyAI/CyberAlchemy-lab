"""Currently permitted disposable generation refresh over exact signed sources."""
import copy
from .handlers import ApplicationError, cut, gap
from .projection import Generation, DDL, DDL_SHA, row_digest, DATA_TABLES
from .protocol import HERE, ROOT, source, compact, binding


def catalog_binding(view):
    raw = view.handle.common.encoded(view.data['projection']['contracts'])
    return binding('captured-contract-catalog:' + source.sha(compact(cut(view))), raw)


def control(view, maximum=4):
    """Fixture provisioner selects this independently; caller fields grant nothing."""
    return {'projector_binding': binding(str((HERE / 'projection.py').relative_to(ROOT)), (HERE / 'projection.py').read_bytes()),
            'schema_binding': {'ref': str(DDL.relative_to(ROOT)), 'sha256': DDL_SHA},
            'contract_catalog_binding': catalog_binding(view),
            'source_cut_sha256': source.sha(compact(cut(view))), 'max_generations': maximum}


class ProjectionRefresh:
    def __init__(self, readers, vault, schemas):
        self.readers = readers
        self.vault = vault
        self.schemas = schemas
        self.created = 0

    def preflight(self, message, outer, *, count_budget=True):
        channel = self.readers.channel
        channel.guard()
        grant = channel.policy['projection_control']
        if grant is None:
            raise ApplicationError('unauthorized', 'This independently provisioned host grants no projection builder permission.')
        observed = self.readers.selected_cut(message, outer)
        view = self.readers.selected_view
        expected = control(view, grant['max_generations'])
        if grant != expected:
            raise ApplicationError('unauthorized', 'Current projection permission does not select this exact schema, projector, catalog and source cut.')
        if message['projector_binding'] != grant['projector_binding'] or message['contract_catalog_binding'] != grant['contract_catalog_binding']:
            raise ApplicationError('invalid-contract', 'Requested projector or compiled exact catalog differs from the independently selected host permission.')
        key = source.sha(compact(observed))
        prior = self.readers.generations.get(key)
        if message['expected_generation_binding'] != (None if prior is None else prior.binding):
            raise ApplicationError('conflict', 'Expected generation differs from the current verified connection slot.')
        if prior is not None:
            try:
                prior.verify()
            except Exception:
                raise ApplicationError('integrity-failed', 'Selected prior generation failed independent verification; refresh cannot silently replace uncertain state.')
        if count_budget and self.created >= grant['max_generations']:
            raise ApplicationError('budget-exceeded', 'Independently granted generation budget is exhausted.')
        return view, observed, key, prior

    def refresh(self, message, request, outer, original_message):
        view, observed, key, prior = self.preflight(message, outer)
        staged = None
        published = False
        try:
            self.created += 1
            staged = Generation(view, observed, self.schemas)
            staged.verify()
            verification = {'schema_version': 'lab-private-projection-verification/v1-candidate',
                'request_binding': request, 'original_message_byte_sha256': source.sha(original_message),
                'source_cut': observed, 'canonical_current_cut': cut(self.readers.view),
                'source_archive_binding': view.selected['archive_binding'],
                'source_profile_sha256': source.PINS.profile_sha256,
                'projector_binding': message['projector_binding'], 'schema_binding': {'ref': str(DDL.relative_to(ROOT)), 'sha256': DDL_SHA},
                'contract_catalog_binding': message['contract_catalog_binding'],
                'generation_binding': staged.binding, 'generation_file_sha256': staged.expected_file_sha,
                'derived_rows_sha256': row_digest(staged.db),
                'table_counts': {table: staged.db.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0] for table in DATA_TABLES},
                'stream_watermarks': copy.deepcopy(observed['streams']),
                'source_semantic_gaps': copy.deepcopy(staged.gaps),
                'integrity_check': ['ok'], 'foreign_key_violations': [],
                'canonical_replay_source': False, 'authority_effect': 'none', 'actual_owner_outcome': None,
                'private_memory_cached': False}
            evidence = self.vault.object(compact(verification))
            # Recheck current independent permission/source and expected pointer
            # after the entire DB and evidence are built, before publication.
            checked = self.preflight(message, outer, count_budget=False)
            source.require(checked[0] is view and checked[2] == key and checked[3] is prior, 'projection source or slot changed before publication')
            staged.verify()
            self.readers.generations[key] = staged
            published = True
            if prior is not None:
                prior.close()
            result = {'schema_version': 'lab-projection-query-status/v1-candidate',
                'generation_binding': staged.binding, 'source_cut': observed,
                'canonical_current_cut': cut(self.readers.view), 'posture': 'ready',
                'source_verification_binding': evidence, 'canonical_replay_source': False, 'gaps': [],
                'claim_ceiling': ('Complete verified connection-local SQLite materialization of the selected signed source cut. '
                    + str(len(staged.gaps)) + ' unresolved source semantic joins remain explicitly indexed in projection_gap and reported by artifact.query. '
                    'Generation availability expires with this process; recorded operation results are historical evidence. '
                    'No canonical admission, source conformance, owner authority or Session memory continuity is established.'),
                'authority_effect': 'none'}
            source.require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:projection-query-status:v1-candidate', result), 'projection result violates original schema')
            return result, [evidence]
        finally:
            if staged is not None and not published:
                staged.close()
