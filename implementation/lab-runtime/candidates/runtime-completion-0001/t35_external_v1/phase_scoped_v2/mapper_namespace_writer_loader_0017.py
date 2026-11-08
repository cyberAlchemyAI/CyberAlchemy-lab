"""Exact-byte module loader for reviewed static tests and unrun local fixture."""
import hashlib
from pathlib import Path
import sys
import types


def load(inputs):
    def raw(row):
        b=Path(row['path']).read_bytes()
        if len(b)!=row['size_bytes'] or hashlib.sha256(b).hexdigest()!=row['sha256']:raise RuntimeError('SOURCE_DRIFT')
        return b
    def package(name):
        if name in sys.modules:raise RuntimeError('MODULE_COLLISION')
        m=types.ModuleType(name);m.__path__=[];sys.modules[name]=m
    root='_selected_local_writer';phase=root+'.phase_scoped_v2';package(root);package(phase)
    def module(name,key):
        if name in sys.modules:raise RuntimeError('MODULE_COLLISION')
        row=inputs[key];m=types.ModuleType(name);m.__package__=name.rpartition('.')[0];m.__file__=row['path'];sys.modules[name]=m
        exec(compile(raw(row),row['path'],'exec'),m.__dict__);return m
    for name,key in [('path_contract','path_contract'),('held_paths','held_paths'),('role_stage','role_stage')]:module(root+'.'+name,key)
    for name,key in [('mapper_namespace_probe_common_0004','common'),('mapper_package_ipc_model_0004','wire'),('mapper_namespace_package_model_0007','model'),('mapper_namespace_package_runner_0010','runner'),('mapper_package_transport_0001','transport'),('mapper_namespace_package_mediator_0017','mediator'),('mapper_package_plan_0002','writer_plan'),('mapper_package_writer_0001','writer')]:module(phase+'.'+name,key)
    module(phase+'.mapper_namespace_probe_controller_0004','controller')
    module(phase+'.mapper_namespace_writer_resources_0017','resources')
    module(phase+'.mapper_namespace_writer_pump_0014','pump')
    return module(phase+'.mapper_namespace_writer_candidate_0017','candidate')
