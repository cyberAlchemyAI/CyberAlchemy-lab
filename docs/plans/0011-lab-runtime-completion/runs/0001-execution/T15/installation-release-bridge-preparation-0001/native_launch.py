"""Explicit successor native launcher; technical custody never grants authority."""
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
from tempfile import TemporaryDirectory

VERSION = 'lab-selected-native-launch/v1-candidate'
ENV = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONNOUSERSITE': '1'}

def need(value, reason):
    if not value: raise ValueError(reason)

def closed(value, keys):
    need(type(value) is dict and set(value) == set(keys), 'closed successor bridge fields required')

def parse(raw):
    need(type(raw) is bytes and len(raw)<=1024*1024,'bounded exact bridge control bytes required')
    def pairs(rows):
        value={}
        for key,item in rows:
            need(key not in value,'duplicate bridge control field');value[key]=item
        return value
    def invalid(value):raise ValueError('nonfinite bridge control value')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid)

def module_origin(module, binding, repository):
    closed(binding, ('path', 'sha256'))
    path = Path(repository) / binding['path']
    need(path.is_absolute() and '..' not in path.parts and not any(p.is_symlink() for p in (path, *path.parents)), 'module origin alias')
    need(Path(module.__file__) == path and hashlib.sha256(path.read_bytes()).hexdigest() == binding['sha256'], 'trusted bootstrap module origin differs')

class SelectedNativeLaunch:
    """Trusted bootstrap constructs this from independently selected bytes."""
    def __init__(self, raw, independent_pin, repository, dependencies, dependency_module_binding):
        need(type(raw) is bytes and hashlib.sha256(raw).hexdigest() == independent_pin, 'independent launch selector differs')
        self.raw = raw; self.pin = independent_pin; self.root = Path(repository)
        self.dependencies = dependencies
        self.module_binding = copy.deepcopy(dependency_module_binding)
        module_origin(dependencies, dependency_module_binding, repository)
        self.value = dependencies.BASE.IO.parse(raw)
        from jsonschema import Draft202012Validator
        Draft202012Validator(dependencies.BASE.IO.parse(Path(__file__).with_name('native-launch.schema.json').read_bytes())).validate(self.value)
        closed(self.value, ('schema_version', 'mode', 'dependency_selection_binding', 'installed_root', 'installed_root_anchor', 'environment', 'timeout_seconds', 'authority_effect'))
        need(self.value['schema_version'] == VERSION and self.value['mode'] == 'selected-local-loader/v1'
             and self.value['authority_effect'] == 'none' and self.value['environment'] == ENV
             and type(self.value['timeout_seconds']) is int and self.value['timeout_seconds'] == 30,
             'unsupported native launch environment/mode/timeout')
        binding = self.value['dependency_selection_binding']; closed(binding, ('path', 'sha256'))
        self.selection_path = self.root / binding['path']
        self.selection, self.selection_raw = dependencies.load_selection(self.selection_path, binding['sha256'])
        config = self.selection['execution_configuration']
        need(config['loader_cache'] is False and config['ambient_environment_inherited'] is False and config['locale'] == 'C', 'unsupported selected dependency execution configuration')
        self.installed = Path(self.value['installed_root'])
        need(self.installed.is_absolute() and self.installed.as_posix() == self.value['installed_root']
             and '..' not in self.installed.parts, 'canonical independently selected installation required')
        closed(self.value['installed_root_anchor'],('device','inode','uid','mode'))
        native = [r for r in self.selection['inputs'] if r['kind'] == 'native-executable']
        need(len(native) == 1 and native[0]['destination'] == 'bin/lab-context-native-reader', 'exact original native executable required')
        self.native_row = native[0]; self.native = self.installed / native[0]['destination']
        self.loader = self.installed / 'lib/abi/ld-linux-x86-64.so.2'
        self.abi = self.installed / 'lib/abi'
        self._seal = json.dumps(self.value, sort_keys=True, allow_nan=False)

    def guard(self):
        module_origin(self.dependencies,self.module_binding,self.root)
        need(hashlib.sha256(self.raw).hexdigest() == self.pin and json.dumps(self.value, sort_keys=True, allow_nan=False) == self._seal, 'launch control mutated')
        for path in (self.installed, self.abi, self.loader, self.native):
            need(not any(p.is_symlink() for p in (path, *path.parents)), 'native launch path alias')
        info=self.installed.lstat();anchor=self.value['installed_root_anchor']
        wanted=(anchor['device'],anchor['inode'],anchor['uid'],anchor['mode'])
        identity=lambda s:(s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode))
        need(stat.S_ISDIR(info.st_mode) and identity(info)==wanted and anchor['uid']==os.geteuid() and anchor['mode']==0o700,'independently selected installation root identity differs')
        binding = self.value['dependency_selection_binding']
        self.dependencies.preflight(self.selection_path, binding['sha256'])
        selected, raw = self.dependencies.load_selection(self.selection_path, binding['sha256'])
        need(raw == self.selection_raw and selected == self.selection, 'selected dependency structure changed')
        self.dependencies.verify_installed(self.installed, selected)
        need(identity(self.installed.lstat())==wanted,'selected installation root changed during guard')
        need(self.loader.is_file() and self.native.is_file()
             and stat.S_IMODE(self.loader.stat().st_mode) == stat.S_IMODE(self.native.stat().st_mode) == 0o755,
             'selected native/loader executable missing or mode differs')

    def run(self, executable, arguments, expected_executable_sha256):
        need(Path(executable) == self.native and expected_executable_sha256 == self.native_row['sha256'], 'native locator/digest is not selected launch target')
        need(type(arguments) is list and len(arguments) == 3 and all(type(p) is str and Path(p).is_absolute() for p in arguments), 'exact native replay snapshot arguments required')
        self.guard()
        try:
            return subprocess.run([str(self.loader), '--inhibit-cache', '--library-path', str(self.abi), str(self.native), *arguments],
                                  env=dict(ENV), capture_output=True, timeout=30, shell=False)
        finally:
            self.guard()

class SelectedNativeReadStore:
    """New explicit type reusing the original pinned native-read boundaries."""
    def __init__(self, original_module, original_module_binding, repository, launch,
                 semantic_directory, governance_directory, request, executable, pins):
        module_origin(original_module, original_module_binding, repository)
        need(type(launch) is SelectedNativeLaunch and type(pins) is original_module.NativePins, 'actual selected launcher/original NativePins required')
        self.original = original_module; self.launch = launch; self.module_binding=copy.deepcopy(original_module_binding);self.root=repository
        self.semantic_directory = Path(semantic_directory); self.governance_directory = Path(governance_directory)
        self.request = copy.deepcopy(request); self.executable = Path(executable); self.pins = pins

    def read(self):
        original = self.original; pins = self.pins
        module_origin(original,self.module_binding,self.root)
        semantic = original.closure(self.semantic_directory); governance = original.closure(self.governance_directory)
        need(sum(map(len, semantic.values())) + sum(map(len, governance.values())) <= 32*1024*1024, 'native history byte budget exceeded')
        shas = lambda values: {k: original.byte_digest(v) for k, v in values.items()}
        need(original.digest(shas(semantic)) == pins.semantic_files_digest and original.digest(shas(governance)) == pins.governance_files_digest, 'original semantic/governance history changed')
        need(original.byte_digest(original.regular(self.executable)) == pins.executable_sha256, 'original native executable changed')
        raw_request = original.encoded(self.request)
        need(original.byte_digest(raw_request) == pins.request_sha256, 'original native request pin differs')
        need(type(pins.semantic_cursor) is int and type(pins.governance_cursor) is int
             and self.request['selector']['semantic_cursor'] == pins.semantic_cursor
             and self.request['governance_cursor'] == pins.governance_cursor, 'original native cursor differs')
        with TemporaryDirectory(prefix='lab-selected-native-read-') as temp:
            stage = Path(temp)
            for name, values in [('semantic', semantic), ('governance', governance)]:
                (stage/name).mkdir()
                for filename, raw in values.items(): (stage/name/filename).write_bytes(raw)
            (stage/'request.json').write_bytes(raw_request)
            process = self.launch.run(self.executable, [str(stage/'semantic'), str(stage/'governance'), str(stage/'request.json')], pins.executable_sha256)
        need(process.returncode == 0, 'selected original native replay rejected')
        result = original.loads(process.stdout)
        need(original.digest(result) == pins.projection_digest and result['schema_version'] == 'lab-native-context-read/v1-candidate'
             and result['authority_effect'] == 'none', 'original projection digest/envelope differs')
        need(result['cut']['semantic_cursor'] == pins.semantic_cursor and result['governance_cursor'] == pins.governance_cursor, 'original projection cut differs')
        need(original.closure(self.semantic_directory) == semantic and original.closure(self.governance_directory) == governance
             and original.byte_digest(original.regular(self.executable)) == pins.executable_sha256, 'original history/native bytes changed during replay')
        module_origin(original,self.module_binding,self.root)
        return copy.deepcopy(result)
