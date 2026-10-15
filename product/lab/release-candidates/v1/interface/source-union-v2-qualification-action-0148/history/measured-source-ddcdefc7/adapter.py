"""New selected guard; byte-identical original constructor/replay/schema/eligibility callbacks."""
from .base import parent
source=parent.adapter.source;ROOT=source.ROOT;cut=parent.adapter.cut
model=parent.adapter.model;eligibility=parent.adapter.eligibility
CARRIERS=parent.adapter.CARRIERS;CURRENT=parent.adapter.CURRENT
EXCLUDED_CATEGORIES=parent.adapter.EXCLUDED_CATEGORIES
class SignedSources(parent.adapter.SignedSources):
    def guard(self):
        source.require(not self.closed, 'closed source adapter cannot serve context')
        if self._trusted_records is not None:
            source.require(self.record_stamp(self.records)==self._trusted_records
                and self.record_stamp(self.sources.records.values())==self._trusted_sources
                and self.schema_stamp(self.schemas)==self._trusted_schemas
                and self.schema_stamp(self.sources.schemas.values())==self._trusted_source_schemas
                and self.sources.scope_ref==self.view.data['config']['scope_ref']
                and self.sources.source_cut==self.source_cut
                and self.sources.current_guard==self.guard
                and set(self.sources.validators)==set(self.sources.schemas)
                and all(source.encoded(v.schema)==source.encoded(source.parse(self.sources.schemas[k].original_schema)) for k,v in self.sources.validators.items()),'captured source records or schemas changed')
        self.view.handle.guard()
        source.require(self.selection_reader(self.selected['name']) == self.selected == self.view.selected, 'independently selected branch changed')
        for key in ['archive_binding', 'expected_replay_binding']:
            source.original(self.selected[key])
        source.require(self.source_cut == cut(self.view), 'captured signed source cut changed')
        source.require(self.configuration_digest == self.view.handle.common.digest(self.view.data['config']), 'captured configuration changed')
        source.require(self.baseline_digest == self.view.handle.common.digest(self.view.data['baseline']), 'captured baseline changed')
        source.require(self.projection_digest == self.view.handle.common.digest(self.view.data['projection'])
            and self.view.subjects == self.view.data['projection']['subjects'], 'captured signed projection changed')
        source.require(self.original_bindings == {k: source.sha(v) for k, v in self.view.originals.items()}, 'original signed transaction byte closure changed')
        source.require(self.view.handle.sources.freshness(ROOT, self.view.data['baseline'])['status'] == 'current', 'selected baseline material bytes are stale')
        return True

