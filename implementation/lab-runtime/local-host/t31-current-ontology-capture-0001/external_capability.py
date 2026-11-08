"""Explicit private host capability selection, separate from signed API Source.

This variant permits one already selected external component. It grants no wire
selection, Source membership, channel permission or historical capability.
"""
import copy
import hashlib
import inspect
import os
from pathlib import Path
import stat
import sys
import types


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical_path(value, *, absolute):
    need(type(value) is str and value and '\\' not in value and '\0' not in value,
         'closed canonical component locator required')
    path = Path(value)
    need(path.is_absolute() is absolute and path.as_posix() == value
         and '..' not in path.parts and not value.startswith('//')
         and value not in ('.', '/'), 'closed canonical component locator required')
    return path


def read_component(path):
    path = canonical_path(str(path), absolute=True)
    directories=[]
    def open_ancestors():
        opened=[]
        try:
            parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            opened.append(parent)
            for part in path.parts[1:-1]:
                parent=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
                opened.append(parent)
            return opened
        except BaseException:
            for handle in reversed(opened):os.close(handle)
            raise
    try:
        directories=open_ancestors();parent=directories[-1]
        directory_stamp=lambda fd:(os.fstat(fd).st_dev,os.fstat(fd).st_ino,os.fstat(fd).st_mode,os.fstat(fd).st_uid)
        identities=[directory_stamp(fd) for fd in directories]
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)
        try:
            before=os.fstat(fd)
            need(stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid()
                 and before.st_nlink==1 and before.st_size<=1024*1024
                 and not stat.S_IMODE(before.st_mode)&0o022,'bounded owned external component required')
            chunks=[];size=0
            while chunk:=os.read(fd,65536):
                chunks.append(chunk);size+=len(chunk);need(size<=before.st_size,'external component grew')
            raw=b''.join(chunks)
            stamp=lambda value:(value.st_dev,value.st_ino,value.st_mode,value.st_uid,value.st_nlink,
                                value.st_size,value.st_mtime_ns,value.st_ctime_ns)
            need(stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=parent,follow_symlinks=False))
                 and size==before.st_size,'external component changed during capture')
            checked=open_ancestors()
            try:need([directory_stamp(fd) for fd in checked]==identities,'external component ancestor changed')
            finally:
                for handle in reversed(checked):os.close(handle)
            return raw
        finally:os.close(fd)
    finally:
        for handle in reversed(directories):os.close(handle)


class ExternalCapabilitySelection:
    """One private selection over one actual bound function and current host."""
    FIELDS = {'schema_version', 'logical_binding', 'component_binding', 'entrypoint',
              'source_cut', 'principal_ref', 'work_ref', 'authority_effect'}

    def __init__(self, host, *, binding, capability, source_cut, work_ref, live_guard):
        self.host = host
        self.binding = copy.deepcopy(binding)
        self.raw = host.vault.material(self.binding)
        pkg = type(host).__module__.rsplit('.', 1)[0]
        from importlib import import_module
        self.P = import_module(pkg + '.protocol')
        self.H = import_module(pkg + '.handlers')
        service = import_module(pkg + '.service')
        auth = import_module(pkg + '.auth')
        need(type(host) is service.Service and type(host.channel) is auth.ReaderChannel,
             'actual current external-capability Service/Reader required')
        self.selection = self.P.frame_parse(self.raw)
        selected = self.selection
        need(type(selected) is dict and set(selected) == self.FIELDS
             and selected['schema_version'] == 'lab-private-external-native-capability/v1'
             and selected['authority_effect'] == 'none',
             'closed explicit external host capability selection required')
        need(selected['source_cut'] == source_cut and selected['work_ref'] == work_ref
             and selected['principal_ref'] == host.channel.guard()['principal_ref'],
             'external host capability cut/Work/principal differs')
        for key in ('logical_binding', 'component_binding'):
            value = selected[key]
            need(type(value) is dict and set(value) == {'path', 'sha256'}
                 and type(value['path']) is str and type(value['sha256']) is str
                 and len(value['sha256']) == 64
                 and all(char in '0123456789abcdef' for char in value['sha256']),
                 'closed independent external component binding required')
        canonical_path(selected['logical_binding']['path'], absolute=False)
        canonical_path(selected['component_binding']['path'], absolute=True)
        need(selected['logical_binding']['sha256'] == selected['component_binding']['sha256'],
             'logical capability must identify the exact external code bytes')
        self.capability = capability
        self.function = getattr(capability, '__func__', capability)
        self.owner = getattr(capability, '__self__', None)
        self.live_guard = live_guard
        self.guard(capability, {'resolver_binding': selected['logical_binding'],
                                'resolver_entrypoint': selected['entrypoint']})

    def guard(self, capability, row):
        self.live_guard()
        self.host.channel.termination_guard()
        self.host.schemas.guard()
        selected = self.selection
        need(self.host.vault.material(self.binding) == self.raw
             and self.P.compact(selected) == self.P.compact(self.P.frame_parse(self.raw)),
             'private external capability selection changed')
        need(self.H.cut(self.host.handlers.view) == selected['source_cut']
             and self.host.channel.guard()['principal_ref'] == selected['principal_ref'],
             'external capability current cut/principal changed')
        need(type(row) is dict and set(row) == {'resolver_binding', 'resolver_entrypoint'}
             and row['resolver_binding'] == selected['logical_binding']
             and row['resolver_entrypoint'] == selected['entrypoint'],
             'external capability differs from its private logical selection')
        function = getattr(capability, '__func__', capability)
        owner = getattr(capability, '__self__', None)
        need(function is self.function and owner is self.owner,
             'external capability function or bound owner changed')
        path = Path(selected['component_binding']['path'])
        raw = read_component(path)
        need(sha(raw) == selected['component_binding']['sha256']
             and not path.is_relative_to(self.P.ROOT),
             'external capability code differs or is falsely declared API code')
        need(inspect.isfunction(function) and Path(function.__code__.co_filename) == path
             and function.__qualname__ == selected['entrypoint'],
             'actual external capability code origin differs')
        module = sys.modules.get(function.__module__)
        need(module is not None and function.__globals__ is module.__dict__
             and Path(module.__file__) == path, 'actual external capability module differs')
        parts = function.__qualname__.split('.')
        need('<locals>' not in parts, 'external capability requires a registered entrypoint')
        registered = module
        for name in parts:
            registered = getattr(registered, name)
        need(getattr(registered, '__func__', registered) is function,
             'external capability registered function changed')
        if owner is not None:
            selected_type = module
            for name in parts[:-1]:
                selected_type = getattr(selected_type, name)
            need(type(owner) is selected_type or owner is selected_type,
                 'actual external capability bound type differs')

        def codes(code):
            yield code
            for item in code.co_consts:
                if isinstance(item, types.CodeType):
                    yield from codes(item)
        matches = [code for code in codes(compile(raw, str(path), 'exec', dont_inherit=True))
                   if code.co_qualname == function.__qualname__]
        need(len(matches) == 1 and matches[0] == function.__code__,
             'external capability executable code differs')
        self.live_guard()
        return True
