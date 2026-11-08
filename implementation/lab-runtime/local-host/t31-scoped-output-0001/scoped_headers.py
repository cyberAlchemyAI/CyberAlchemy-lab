"""Private host-selected currentness providers; wire facts cannot select a profile.

Source and coordination providers are trusted host adapters. They must retrieve
and verify their original records, scope, cut and semantics under the supplied
live guard. This class checks the closed proof form; it does not invent those
adapters, authority, schema validation, or successful producer invocations.
"""
import copy
from scoped_currentness import OwnedCurrentness, need


class HostHeaders:
    def __init__(self, *, source_resolver, owned_resolver, coordination_resolver, guard):
        need(callable(source_resolver) and callable(coordination_resolver) and callable(guard)
             and (owned_resolver is None or type(owned_resolver) is OwnedCurrentness),
             'independently selected host currentness providers required')
        self.source_resolver = source_resolver
        self.owned_resolver = owned_resolver
        self.coordination_resolver = coordination_resolver
        self.guard = guard
        self._owned = {}

    def select_owned(self, header, *, sequence, transaction_sha256):
        need(type(self.owned_resolver) is OwnedCurrentness, 'selected committed-output resolver required')
        key = header['version_ref']
        need(key not in self._owned, 'ambiguous owned output selection')
        self._owned[key] = (copy.deepcopy(header), sequence, transaction_sha256)

    def resolve(self, header):
        self.guard()
        selected = self._owned.get(header['version_ref'])
        if selected is not None:
            need(header == selected[0], 'owned output header substitution')
            row = self.owned_resolver.resolve(header, sequence=selected[1], transaction_sha256=selected[2])
            need(set(row) == {'artifact', 'posture', 'semantic_kind', 'lineage_binding'}
                 and row['posture'] == 'owned-produced-current', 'verified owned output proof required')
        else:
            row = self.source_resolver(copy.deepcopy(header))
            if row is not None:
                need(set(row) == {'artifact', 'posture', 'semantic_kind'}
                     and row['posture'] in ('admitted-current', 'local-admitted-current'),
                     'verified original signed-source posture required')
            else:
                row = self.coordination_resolver(copy.deepcopy(header))
                need(type(row) is dict and set(row) == {'artifact', 'posture', 'semantic_kind', 'lineage_binding'}
                     and row['posture'] == 'owned-coordination-current', 'verified private coordination proof required')
        need(row['artifact'] == header and type(row['semantic_kind']) is str and bool(row['semantic_kind']),
             'exact verified original header and semantic kind required')
        if 'lineage_binding' in row:
            binding = row['lineage_binding']
            need(type(binding) is dict and set(binding) == {'ref', 'sha256'}
                 and type(binding['ref']) is str and bool(binding['ref'])
                 and type(binding['sha256']) is str and len(binding['sha256']) == 64
                 and all(c in '0123456789abcdef' for c in binding['sha256']), 'exact owned lineage binding required')
        self.guard()
        return copy.deepcopy(row)

    def scope_permitted(self,header,authority_scope):
        selected=self._owned.get(header['version_ref'])
        if selected is None:
            return header['scope_ref']==authority_scope
        need(header==selected[0], 'scoped native input header substituted')
        return self.owned_resolver.scope_permitted(header,authority_scope,sequence=selected[1],
                                                   transaction_sha256=selected[2])
