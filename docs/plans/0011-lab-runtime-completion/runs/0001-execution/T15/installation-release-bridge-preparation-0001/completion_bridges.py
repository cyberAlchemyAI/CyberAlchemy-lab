"""Opt-in private plan/v2 integration; original plan/v1 remains unchanged."""
import copy
import hashlib
from pathlib import Path
from .native_launch import closed, module_origin, need, parse, SelectedNativeLaunch
from .protected_bridge import ProtectedHostBridge, REVIEW_FIELDS, REVIEW_VERSION
from .composite_bridge import CompositeHostBridge

class CompletionBridge:
    """Trusted bootstrap capability, never constructed from a public API call.

    Root supplies actual original module objects at their true pinned origins and
    the actual reviewed CompositeEnvironment. This object creates fresh bound
    readers for each host builder; it caches neither permission nor file bytes.
    """
    def __init__(self, raw, independent_binding, repository, modules, environment):
        closed(independent_binding,('ref','sha256'))
        need(type(raw) is bytes and hashlib.sha256(raw).hexdigest() == independent_binding['sha256'], 'independent private bridge selector differs')
        need(set(modules) == {'protected_inputs','semantic_graph','environment','dependencies'}, 'complete actual trusted bridge modules required')
        value = parse(raw)
        fields={'schema_version','module_bindings','protected_inputs','composite_environment','native_launch_binding','authority_effect'}
        need(set(value) in (fields,fields|{'workflow_output_binding'}),'closed trusted host bridge fields required')
        need(value['schema_version'] == 'lab-installation-release-host-bridge/v1-candidate' and value['authority_effect'] == 'none', 'unsupported bridge control version/authority')
        need(set(value['module_bindings']) == set(modules), 'closed complete trusted module selection required')
        for key, module in modules.items(): module_origin(module,value['module_bindings'][key],repository)
        modules['semantic_graph'].Draft202012Validator(parse(Path(__file__).with_name('host-bridge.schema.json').read_bytes())).validate(value)
        self.raw=raw;self.pin=independent_binding['sha256'];self.binding=copy.deepcopy(independent_binding);self.root=repository;self.modules=modules;self.environment=environment
        self._seal=modules['protected_inputs'].canonical(value)
        self._binding_seal=modules['protected_inputs'].canonical(self.binding)

    @property
    def descriptor_binding(self):
        need(self.modules['protected_inputs'].canonical(self.binding)==self._binding_seal,'independent descriptor binding changed')
        return copy.deepcopy(self.binding)

    def verify_descriptor(self, raw, binding):
        need(binding==self.descriptor_binding and type(raw) is bytes and raw==self.raw
             and hashlib.sha256(raw).hexdigest()==self.pin,'fresh trusted descriptor selection differs')
        need(self.modules['protected_inputs'].canonical(self.modules['protected_inputs'].parse(raw))==self._seal,'trusted descriptor object changed')

    @property
    def workflow_output_binding(self):
        value=self.modules['protected_inputs'].parse(self.raw)
        need(hashlib.sha256(self.raw).hexdigest()==self.pin and self.modules['protected_inputs'].canonical(value)==self._seal,'trusted bridge descriptor changed')
        return copy.deepcopy(value.get('workflow_output_binding'))

    def bind(self, builder):
        value=self.modules['protected_inputs'].parse(self.raw)
        need(hashlib.sha256(self.raw).hexdigest()==self.pin and self.modules['protected_inputs'].canonical(value)==self._seal, 'trusted bridge selector changed')
        need(builder.plan['schema_version']=='lab-installation-release-plan/v2-candidate'
             and builder.plan['bridge_binding']==self.binding
             and builder.read(builder.plan['bridge_binding'])==self.raw, 'private plan does not independently select this bridge')
        return BoundCompletionBridge(self,builder,value)

class BoundCompletionBridge:
    def __init__(self, selected, builder, value):
        self.selected=selected;self.builder=builder
        modules=selected.modules
        self.value=value;self._value_seal=modules['protected_inputs'].canonical(value)
        need(value['protected_inputs'] is not None, 'actual protected host controls remain unselected')
        self.protected=ProtectedHostBridge(value['protected_inputs'],modules['protected_inputs'],modules['semantic_graph'],value['module_bindings'],selected.root)
        self.protected.bind(builder)
        self.composite=None
        if builder.operation=='installation.execute':
            need(value['composite_environment'] is not None, 'actual composite transition/root/receipt controls remain unselected')
            self.composite=CompositeHostBridge(value['composite_environment'],selected.environment,modules['environment'],value['module_bindings']['environment'],selected.root)
            self.composite.bind(builder)
        self.native_launch=None
        if value['native_launch_binding'] is not None:
            row=value['native_launch_binding'];closed(row,('ref','sha256'))
            self.native_launch=SelectedNativeLaunch(builder.read(row),row['sha256'],selected.root,modules['dependencies'],value['module_bindings']['dependencies'])

    def guard_selection(self):
        parser=self.selected.modules['protected_inputs']
        need(parser.canonical(self.value)==self._value_seal and hashlib.sha256(self.selected.raw).hexdigest()==self.selected.pin
             and self.builder.read(self.selected.descriptor_binding)==self.selected.raw,'private bridge bytes or selected indices changed')
    def read_selected(self, selected):
        self.guard_selection();return self.protected.read_selected(selected)
    def active(self, root):
        self.guard_selection()
        need(self.composite is not None,'composite installation bridge unselected')
        return self.composite.active(root)
    def verify_environment(self, raw, package, pin):
        self.guard_selection()
        need(self.composite is not None,'composite installation bridge unselected')
        with self.protected.boundary():return self.composite.verify_environment(raw,package,pin)
    def transition(self, operation, package, pin, destination, scope, expected_active):
        self.guard_selection()
        need(self.composite is not None,'composite installation bridge unselected')
        need(type(scope) is self.composite.environment.r02.OwnedScope,'actual original trusted R02 scope required')
        with self.protected.boundary():return self.composite.transition(operation,package,pin,destination,scope,expected_active)
    def scope(self, root):
        need(self.composite is not None,'composite installation bridge unselected')
        return self.composite.environment.r02.OwnedScope(str(root))
    def review_graph(self, observed, roots):
        self.guard_selection();return self.protected.review_graph(observed,roots)

def bind_host(builder):
    selected=getattr(builder.host,'completion_bridge',None)
    need(type(selected) is CompletionBridge,'trusted bootstrap CompletionBridge is unavailable; public calls cannot select one')
    return selected.bind(builder)
