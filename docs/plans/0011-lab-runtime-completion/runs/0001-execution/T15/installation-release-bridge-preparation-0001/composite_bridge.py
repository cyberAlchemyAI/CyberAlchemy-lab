"""Selected whole-receipt transition under original public-host guards."""
from contextlib import contextmanager
import fcntl
import hashlib
import os
from pathlib import Path
import stat
import uuid
from .native_launch import closed, module_origin, need
from .protected_bridge import control_root

class CompositeHostBridge:
    def __init__(self, selection, environment, environment_module, environment_module_binding, repository):
        closed(selection, ('descriptor_binding', 'root_anchor', 'lock_anchor', 'active_binding', 'retained_receipt_binding'))
        module_origin(environment_module, environment_module_binding, repository)
        need(type(environment) is environment_module.CompositeEnvironment, 'actual reviewed composite environment required')
        binding = selection['descriptor_binding']; closed(binding, ('path', 'sha256'))
        need(Path(environment.path) == Path(repository)/binding['path'] and environment.pin == binding['sha256'], 'independently selected composite descriptor differs')
        self.value = selection; self.environment = environment; self.encode=environment_module.encoded

    def bind(self, builder):
        self.builder = builder
        root = self.value['root_anchor']
        need(root is not None and root['path'] == builder.plan['install']['root']
             and [root['device'], root['inode']] == builder.plan['install']['root_identity'], 'actual independent installation root anchor unselected/different')

    def check_attachment(self, root_fd, lock_fd=None):
        root = self.value['root_anchor']
        with control_root(root) as reopened:
            left, right = os.fstat(root_fd), os.fstat(reopened)
            need((left.st_dev, left.st_ino, left.st_mode, left.st_uid) == (right.st_dev, right.st_ino, right.st_mode, right.st_uid), 'installation root detached')
            if lock_fd is not None:
                selected = self.value['lock_anchor']; closed(selected, ('name', 'device', 'inode', 'uid', 'mode'))
                need(selected['name'] == '.composite-install.lock' and selected['uid'] == os.geteuid() and selected['mode'] == 0o600, 'independent lock attachment required')
                current = os.stat(selected['name'], dir_fd=reopened, follow_symlinks=False); opened = os.fstat(lock_fd)
                wanted = (selected['device'], selected['inode'], selected['uid'], selected['mode'])
                need(stat.S_ISREG(current.st_mode) and (current.st_dev,current.st_ino,current.st_uid,stat.S_IMODE(current.st_mode)) == wanted
                     and (opened.st_dev,opened.st_ino,opened.st_uid,stat.S_IMODE(opened.st_mode)) == wanted, 'installation lock replaced/detached')

    @contextmanager
    def locked(self):
        selected = self.value['lock_anchor']; need(selected is not None, 'independent preexisting installation lock is unselected')
        with control_root(self.value['root_anchor']) as root_fd:
            lock = os.open('.composite-install.lock', os.O_RDWR | os.O_NOFOLLOW, dir_fd=root_fd)
            try:
                self.check_attachment(root_fd, lock); fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.builder.guard(); self.check_attachment(root_fd, lock)
                try: yield root_fd, lock
                finally: self.check_attachment(root_fd, lock); self.builder.guard()
            finally: os.close(lock)

    def active(self, root):
        need(str(root) == self.value['root_anchor']['path'], 'active descriptor outside selected root')
        binding = self.value['active_binding']; path = Path(root)/'active-composite.json'
        if binding is None:
            need(not os.path.lexists(path), 'unselected active descriptor exists'); return None
        closed(binding, ('path', 'sha256'))
        need(binding['path'] == str(path), 'independent whole active descriptor origin differs')
        raw = self.environment.read(path)
        need(hashlib.sha256(raw).hexdigest() == binding['sha256'], 'independent whole active descriptor bytes differ')
        value = self.environment.parse(raw)
        closed(value, ('schema_version','generation','package_path','package_sha256','composite_binding','R02_environment','receipt_binding','authority_effect'))
        need(value['schema_version'] == 'lab-composite-installed-active/v1-candidate' and value['authority_effect'] == 'none', 'unsupported active environment contract')
        return value

    def verify_environment(self, target_raw, package, package_pin):
        need(hashlib.sha256(target_raw).hexdigest() == self.environment.pin and self.environment.parse(target_raw) == self.environment.value,
             'target must select exact reviewed whole composite, not a shape-coerced R02 object')
        return self.environment.guard(package, package_pin)

    def transition(self, operation, package, package_pin, destination, scope, expected_active):
        need(operation in ('install','upgrade','rollback'), 'unknown composite transition')
        retained_pin = self.value['retained_receipt_binding']
        need((operation == 'rollback') == (retained_pin is not None), 'rollback requires independent whole retained receipt selection only')
        env = self.environment; r02 = env.r02; destination = scope.destination(destination); root = destination.parent
        need(str(root) == self.value['root_anchor']['path'] and not destination.name.startswith('.'), 'canonical selected generation required')
        with self.locked() as (root_fd, lock_fd):
            current = self.active(root); need(current == expected_active and (operation == 'install') == (current is None), 'exact independent active preimage/operation differs')
            verification = env.guard(package, package_pin)
            if current is not None:
                need(current['composite_binding'] == verification['composite_binding'] and current['R02_environment'] == verification['R02_environment'], 'predecessor composite selection differs')
                prior = scope.destination(root/current['generation'])
                installed = r02.verify_install(prior, current['package_path'], current['package_sha256'])
                env.verify_receipt(root, current['generation'], current['receipt_binding'], current['package_sha256'], verification, installed)
            receipt_path = root/(destination.name+'.environment.json')
            if operation == 'rollback':
                installed = r02.verify_install(destination, package, package_pin)
                env.verify_receipt(root, destination.name, retained_pin, package_pin, verification, installed)
            else:
                need(not os.path.lexists(destination) and not os.path.lexists(receipt_path), 'selected generation/receipt collision')
                self.builder.guard(); self.check_attachment(root_fd, lock_fd)
                r02.install(package, package_pin, destination, scope)
            installed = r02.verify_install(destination, package, package_pin)
            env.guard(package, package_pin); self.builder.guard(); self.check_attachment(root_fd, lock_fd)
            receipt = env.receipt(destination.name, package_pin, verification, installed)
            receipt_raw = self.encode(receipt)
            if operation != 'rollback':
                fd = os.open(receipt_path.name, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o600, dir_fd=root_fd)
                with os.fdopen(fd,'wb') as handle: handle.write(receipt_raw); handle.flush(); os.fsync(handle.fileno())
            receipt_binding = {'path':str(receipt_path),'sha256':hashlib.sha256(receipt_raw).hexdigest()}
            env.verify_receipt(root,destination.name,receipt_binding,package_pin,verification,installed)
            active = {'schema_version':'lab-composite-installed-active/v1-candidate','generation':destination.name,
                      'package_path':str(package),'package_sha256':package_pin,'composite_binding':verification['composite_binding'],
                      'R02_environment':verification['R02_environment'],'receipt_binding':receipt_binding,'authority_effect':'none'}
            pending = '.active-composite-'+uuid.uuid4().hex+'.json'
            raw = self.encode(active)
            # A failed operation retains any staged generation/receipt. No retry,
            # cleanup, inferred authority or Session/service activation occurs.
            self.builder.guard(); self.check_attachment(root_fd,lock_fd)
            need(self.active(root) == expected_active, 'whole active preimage changed before activation')
            fd = os.open(pending,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=root_fd)
            with os.fdopen(fd,'wb') as handle: handle.write(raw); handle.flush(); os.fsync(handle.fileno())
            env.guard(package,package_pin); self.builder.guard(); self.check_attachment(root_fd,lock_fd)
            need(self.active(root) == expected_active, 'whole active preimage changed at final boundary')
            os.replace(pending,'active-composite.json',src_dir_fd=root_fd,dst_dir_fd=root_fd);os.fsync(root_fd)
            self.check_attachment(root_fd,lock_fd);self.builder.guard()
            observed = env.read(root/'active-composite.json')
            need(observed == raw, 'actual committed composite descriptor differs')
            return {'active':active,'receipt':receipt,'operation':operation,'verification':installed,'authority_effect':'none',
                    'original_full_proof_status':'REFUSED','historical_unavailable_count':25,'runtime_activations':0}

    def reconcile(self, root, package, package_pin, generation):
        """Cold inspect-only classification; no activation or automatic retry."""
        with self.locked() as (root_fd,lock_fd):
            active_path=Path(root)/'active-composite.json'
            observed=self.environment.parse(self.environment.read(active_path)) if os.path.lexists(active_path) else None
            expected=self.active(root)
            if observed != expected: raise ValueError('active state differs from independent reconciliation selection')
            installed=self.environment.r02.verify_install(Path(root)/generation,package,package_pin)
            self.check_attachment(root_fd,lock_fd)
            return {'posture':'inspect-only','observed_active':observed,'installed':installed,'automatic_retry':False,
                    'activation_performed':False,'authority_effect':'none'}
