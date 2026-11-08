"""Fresh selected bytes and live scopes at every derived effect boundary."""
import copy
import hashlib
import importlib
from pathlib import Path
from .session_source_freshness import declared_externals, closure_inputs
from .protocol import source,ROOT,HERE

def require(value,reason):
    if not value:raise ValueError(reason)

def fresh_selected_source(selected, expected_family=None, *, context_package_pin):
    """Recheck every selected physical source byte without native replay.

    The original producer capture checks no-follow path custody and exact
    digests. Its archive-handle read also rehashes the owner-only archive.
    The full signed source proof is still required at call entry.
    """
    reader = selected.view.integrated_reader
    require(reader is not None and selected.view.custody_signed_sources is selected,
            'selected source/view identity changed')
    producer = reader.adapter.source
    context = selected.view.legacy_context_producer
    from . import source_bridge
    require(context.reader is reader and context.MAPPED.reader is reader,
            'selected Context/Mapper/Reader family changed')
    basis = selected.selected['candidate_selection_basis']
    context_source = context.HERE / 'source-manifest.json'
    context_pin = source_bridge.CURRENT_LEGACY_DELIVERY_PIN
    context_body = producer.parse(producer.original({
        'path': context_source.relative_to(ROOT).as_posix(), 'sha256': context_pin}))
    mapper_source = context.MAPPED.HERE / 'source-manifest.json'
    mapper_package = context.MAPPED.HERE / 'packages/0001/manifest.json'
    mapper_source_pin = context_body['qualified_mapper_source_binding']['sha256']
    mapper_package_pin = context_body['qualified_mapper_package_binding']['sha256']
    require(context_body['qualified_mapper_source_binding']['path'] == mapper_source.relative_to(ROOT).as_posix()
            and context_body['qualified_mapper_package_binding']['path'] == mapper_package.relative_to(ROOT).as_posix(),
            'Context selected Mapper source/package paths differ')
    manifests = (
        (reader.HERE / 'source-manifest.json', basis['source_manifest_sha256']),
        (reader.adapter.HERE / 'source-manifest.json', basis['adapter_source_sha256']),
        (mapper_source, mapper_source_pin),
        (context_source, context_pin),
    )
    closure = {}
    external = {}
    family = {}
    for path, digest in manifests:
        ref = path.relative_to(ROOT).as_posix()
        raw = producer.original({'path': ref, 'sha256': digest})
        family[ref] = digest
        body = producer.parse(raw)
        require(type(body.get('files')) is list and len(body['files']) <= 4096,
                'selected family source manifest inventory differs')
        declared_externals(body, external)
        for row in body['files']:
            previous = closure.setdefault(row['path'], row['sha256'])
            require(previous == row['sha256'], 'signed family member pins conflict')
    packages = (
        (reader.HERE / 'packages/0001/manifest.json', basis['manifest_sha256']),
        (mapper_package, mapper_package_pin),
        (context.HERE / 'packages/0001/manifest.json', context_package_pin),
    )
    for path, pin in packages:
        ref = path.relative_to(ROOT).as_posix()
        if pin is None:
            raw = path.read_bytes()
            pin = hashlib.sha256(raw).hexdigest()
        raw = producer.original({'path': ref, 'sha256': pin})
        body = producer.parse(raw)
        require(type(body.get('files')) is list and len(body['files']) <= 4096,
                'selected family package inventory differs')
        family[ref] = pin
        if path.parent.parent.parent == context.HERE:
            require(body['source_manifest_binding'] == {'path': (context.HERE / 'source-manifest.json').relative_to(ROOT).as_posix(),
                                                       'sha256': source_bridge.CURRENT_LEGACY_DELIVERY_PIN},
                    'Context package is not bound to selected source manifest')
        for row in body['files']:
            previous = closure.setdefault(row['path'], row['sha256'])
            require(previous == row['sha256'], 'signed family package member pins conflict')
    producer.original(selected.selected['archive_binding'])
    producer.original(selected.selected['expected_replay_binding'])
    materials = selected.view.data['baseline']['materials']
    require(type(materials) is dict and 0 < len(materials) <= 2048,
            'selected baseline material closure differs')
    for path, digest in materials.items():
        previous = closure.setdefault(path, digest)
        require(previous == digest, 'baseline and signed family pins conflict')
    rows, selected_external = closure_inputs(closure, external)
    producer.B.verify_inputs(rows, selected_external=selected_external)
    if expected_family is not None:
        require(family == expected_family, 'selected signed family package bindings changed')
    return family



def _private_tree(root):
    """Bounded exact private application input/journal bytes; no values escape."""
    from .workspace import read_private,safe
    root=Path(root);safe(root,0o700)
    result={}
    for folder in ('inputs','objects','journal'):
        safe(root/folder,0o700)
        for path in sorted((root/folder).iterdir()):
            require(path.is_file() and not path.is_symlink(),'unexpected private journal object')
            raw=read_private(path)
            result[path.relative_to(root).as_posix()]=source.sha(raw)
    result['workspace.json']=source.sha(read_private(root/'workspace.json'))
    require(len(result)<=1024,'private journal snapshot exceeds bound')
    return result


class DerivedEffectGuard:
    """One invocation's selected facts; permission, files and clocks stay live."""
    def __init__(self,host,config,deadline):
        package=type(host).__module__.rsplit('.',1)[0]
        self.S=importlib.import_module(package+'.service')
        self.A=importlib.import_module(package+'.auth')
        self.G=importlib.import_module(package+'.guard')
        self.M=importlib.import_module(package+'.observed_margin')
        require(type(host) is self.S.Service and type(host.channel) is self.A.ReaderChannel,
                'selected operator Service required for derived writes')
        require(deadline is not None and deadline.tzinfo is not None and deadline.utcoffset() is not None,
                'effective caller deadline required for derived effects')
        self.effective_deadline=deadline
        self.host=host;self.config=copy.deepcopy(config)
        self.source=host.handlers.view.legacy_signed_sources
        require(host.handlers.view.custody_signed_sources is self.source,
                'derived effect Source differs')
        self.cut=copy.deepcopy(self.source.source_cut)
        self.policy_sha=host.channel.expected_sha
        self.kind=host.channel.policy['schema_version']
        manifest=self.G.verify(config['api_source_binding']['sha256'])
        require(manifest['profile_binding']==config['profile_binding']==self.M.protocol_file_binding(host.schemas.profile_binding,config['profile_binding']),
                'derived effect profile selection differs')
        self.context_package_pin=manifest['family_context_package_binding']['sha256']
        self.family=fresh_selected_source(self.source,context_package_pin=self.context_package_pin)
        self.operator_inputs=_private_tree(host.vault.root)
        if self.kind=='lab-local-lesson-application-policy/v2-candidate':
            attachment=host.session_attachment
            SA=importlib.import_module(package+'.session_attachment')
            require(type(attachment) is SA.SessionAttachment and attachment.host is host,
                    'actual application attachment required at derived write')
            self.parent=attachment.parent;self.sessions=attachment.sessions
            self.resource=attachment.resource;self.expected=copy.deepcopy(attachment.expected)
            self.expiry=self.resource.expires
            self.parent_policy_sha=self.parent.channel.expected_sha
            self.session_row=self.sessions.selected(self.expected['session_ref'])
            require(self.session_row['posture']=='active' and self.session_row['source_cut']==self.cut,
                    'actual parent Session is not active on selected cut')
        else:
            require(self.kind=='lab-local-lesson-assessment-policy/v1-candidate'
                    and host.sessions is None and host.session_attachment is None,
                    'independent metadata assessment cannot borrow live Session capability')
            self.parent=None;self.sessions=None;self.resource=None
            policy=host.channel.policy_guard();self.journal_scope=copy.deepcopy(policy['application_journal_scope'])
            from .current_legacy_context_sessions import D
            require(policy['principal_ref']!=D.records.PRINCIPAL
                    and policy['scope_refs']==[self.source.sources.scope_ref],
                    'independent assessment Principal/scope required')
            # The original helper validates completed result/claim, exact source,
            # Principal, Lesson, scope and candidate original bytes. Snapshot its
            # immutable input store only after that real validation succeeds.
            assessment=importlib.import_module(package+'.current_lesson_assessment')
            control=policy['assessment_control']
            builder=assessment.LessonAssessment(host,control['routing_binding'],config['api_source_binding'])
            routing=source.parse(host.vault.object_read(control['routing_binding']))
            observation=source.parse(host.vault.material(routing['observation_binding']))
            self.application=copy.deepcopy(observation['application'])
            body=builder.completed_candidate_application(self.application)
            require(body['scope_ref']==self.source.sources.scope_ref,
                    'completed application belongs to another scope')
            self.journal=_private_tree(Path(self.journal_scope['root']))

    def _fresh(self):
        self.G.verify(self.config['api_source_binding']['sha256'])
        require(self.M.protocol_file_binding(self.host.schemas.profile_binding,self.config['profile_binding'])==self.config['profile_binding'],
                'derived effect schema selection changed')
        self.M.dependency(self.config)
        fresh_selected_source(self.source,self.family,context_package_pin=self.context_package_pin)
        context=self.host.channel.termination_guard()
        require(self.host.channel.expected_sha==self.policy_sha
                and self.source.source_cut==self.cut,'derived operator/cut changed')
        # Only immutable input members are compared for the operator workspace;
        # derived objects/journal naturally grow during this invocation.
        from .workspace import read_private
        current=_private_tree(self.host.vault.root)
        inputs={key:value for key,value in self.operator_inputs.items() if key=='workspace.json' or key.startswith('inputs/')}
        require({key:value for key,value in current.items() if key=='workspace.json' or key.startswith('inputs/')}==inputs,
                'derived operator selected inputs changed')
        return context

    def __call__(self):
        from . import current_legacy_context_sessions as runtime
        runtime.D.FACT_SCOPE.require_outside_scope()
        require(self.A.now()<self.effective_deadline,
                'effective caller deadline expired before derived write')
        if self.resource is not None:
            with self.resource._lifetime_lock:
                require(type(self.resource) is runtime.LiveReader and not self.resource.closed
                        and self.resource.expires==self.expiry and self.resource.source is self.source
                        and self.parent.sessions is self.sessions
                        and self.sessions.live.get(self.expected['session_ref']) is self.resource
                        and self.resource.bridge is self.sessions.bridge,
                        'parent Session custody ended before derived write')
                self._fresh()
                self.parent.channel.termination_guard()
                require(self.parent.channel.expected_sha==self.parent_policy_sha,
                        'parent grant changed before derived write')
                row=self.sessions.selected(self.expected['session_ref'])
                require(row==self.session_row and row['posture']=='active',
                        'parent Session journal changed before derived write')
                require(self.A.now()<self.expiry,
                        'parent Session expired before derived write')
        else:
            self._fresh()
            policy=self.host.channel.policy
            require(policy['application_journal_scope']==self.journal_scope
                    and _private_tree(Path(self.journal_scope['root']))==self.journal,
                    'completed application journal changed before assessment write')
            require(self.A.now()<self.A.instant(policy['expires_at']),
                    'independent assessor grant expired before derived write')
        require(self.A.now()<self.effective_deadline,
                'effective caller deadline expired during derived guard')
        return True


def selected_effect_guard(host,config=None,*,deadline=None):
    if host.channel.policy['source_name']!=source.CURRENT_LEGACY_NAME or host.channel.policy['schema_version'] not in (
        'lab-local-lesson-application-policy/v2-candidate','lab-local-lesson-assessment-policy/v1-candidate'):
        return None
    margin=importlib.import_module(type(host).__module__.rsplit('.',1)[0]+'.observed_margin')
    binding=host.vault.observed_margin_runtime
    require(type(binding) is margin.RuntimeBinding and binding.host is host,
            'selected current derived margin runtime required')
    binding.check_entry(margin.before_claim)
    config=binding.selection() if config is None else config
    require(config==binding.selection(),'derived guard configuration changed')
    require(config['mode']=='diagnostic-measurement',
            'local derived branch does not claim empirical margin qualification')
    return DerivedEffectGuard(host,config,deadline)


def guard_for(host,operation,key):
    from . import jcs
    namespace=jcs.namespace(operation,key,host.channel.context)
    guard=host.vault.derived_effect_guards.get(namespace)
    require(type(guard) is DerivedEffectGuard and guard.host is host,
            'current invocation derived write guard absent')
    require((operation=='lesson.apply' and guard.resource is not None)
            or (operation=='lesson.assess' and guard.resource is None),
            'derived guard belongs to another operation')
    return guard
