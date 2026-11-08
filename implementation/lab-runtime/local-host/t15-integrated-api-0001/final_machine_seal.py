"""Apply the reviewed shared captured-source seal to an unselected final cut."""
import ast


def apply(text):
    def once(before, after):
        nonlocal text
        if text.count(before) != 1:
            raise ValueError('Machine seal merge seam differs: ' + before[:100])
        text = text.replace(before, after, 1)
    once("        self.expires = min(resource.expires, self.A.instant(owner.channel.context['expires_at']))",
         """        self.expires = min(resource.expires, self.A.instant(owner.channel.context['expires_at']))
        from .session_source_freshness import captured_source_basis
        self._source_memory_basis = copy.deepcopy(captured_source_basis(resource.source))
        self._peer_owner = owner
        self._peer_resource = resource
        self._peer_binding_basis = self.P.source.sha(self.P.compact({
            'row': self.row, 'connection': self.connection,
            'public_key': base64.b64encode(self.public_key_bytes).decode()}))
        self._authenticated_context_basis = None""")
    once('    def live(self):\n', """    def _peer_basis_guard(self):
        from .session_source_freshness import captured_source_basis
        require(self.owner is self._peer_owner and self.resource is self._peer_resource
                and self.owner.sessions.source is self.resource.source
                and self.owner.sessions.bridge is self.resource.bridge
                and self.owner.sessions.live.get(self.row['session_ref']) is self.resource,
                'Machine peer selected owner or actual Session changed')
        current = self.P.source.sha(self.P.compact({
            'row': self.row, 'connection': self.connection,
            'public_key': base64.b64encode(self.public_key_bytes).decode()}))
        require(current == self._peer_binding_basis,
                'Machine peer Actor, cut, connection or signer changed')
        if self._authenticated_context_basis is None:
            require(self.context is None, 'Machine context predates actual authentication')
        else:
            require(self.context is not None
                    and self.P.source.sha(self.P.compact(self.context)) == self._authenticated_context_basis,
                    'Machine authenticated opaque context changed')
        require(captured_source_basis(self.resource.source) == self._source_memory_basis,
                'Machine captured source facts changed')

    def live(self):
""")
    once('            self.schemas.guard()\n            self.resource.guard()',
         """            self._peer_basis_guard()
            self.schemas.guard()
            # The selected API69 resource guard performs complete physical and
            # captured freshness. Retain an explicit original semantic proof at
            # the outer Machine boundary before the private dispatch scope.
            self.resource.source.guard()
            self.resource.guard()""")
    once('        self.context = context\n        self.live()',
         '        self.context = context\n        self._authenticated_context_basis = self.P.source.sha(self.P.compact(context))\n        self.live()')
    once('        fresh_selected_source(self.resource.source, self._family_bindings)',
         '        self._peer_basis_guard()\n        fresh_selected_source(self.resource.source, self._family_bindings)')
    once('            self.context = None\n            self.challenge = None',
         """            self.context = None
            self._authenticated_context_basis = None
            self._source_memory_basis = None
            self._peer_binding_basis = None
            self._peer_owner = None
            self._peer_resource = None
            self.challenge = None""")
    ast.parse(text)
    return text
