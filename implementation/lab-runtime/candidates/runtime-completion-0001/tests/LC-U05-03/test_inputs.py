import argparse,json,os,stat,sys,time,traceback,unittest
from pathlib import Path
from test_support import P,Fixture

class InputTests(unittest.TestCase):
    def fixture(self):
        f=Fixture(TEMP);self.addCleanup(f.close);return f
    def test_selected_exact_read(self):
        f=self.fixture();self.assertEqual(f.inputs.read('selector'),b'selected-selector')
    def test_unknown_member(self):
        f=self.fixture()
        with self.assertRaises(P.Refusal):f.inputs.read('unknown')
    def test_negative_bound_before_open(self):
        f=self.fixture();(f.root/'selector.json').unlink()
        with self.assertRaises(P.Refusal):f.inputs.read('selector',maximum=-1)
    def test_boolean_bound(self):
        f=self.fixture()
        with self.assertRaises(P.Refusal):f.inputs.read('selector',maximum=True)
    def test_declared_size_bound(self):
        f=self.fixture()
        with self.assertRaises(P.Refusal):f.inputs.read('selector',maximum=1)
    def test_final_symlink_refusal(self):
        f=self.fixture();p=f.root/'selector.json';p.unlink();p.symlink_to(f.root/'grant.json')
        with self.assertRaises(P.Refusal):f.inputs.read('selector')
    def test_final_fifo_does_not_hang(self):
        f=self.fixture();p=f.root/'selector.json';p.unlink();os.mkfifo(p,0o600);start=time.monotonic()
        with self.assertRaises(P.Refusal):f.inputs.read('selector')
        self.assertLess(time.monotonic()-start,1)
    def test_hardlink_refusal(self):
        f=self.fixture();os.link(f.root/'selector.json',f.root/'alias')
        with self.assertRaises(P.Refusal):f.inputs.read('selector')
    def test_equal_bytes_replacement_refused(self):
        f=self.fixture();p=f.root/'selector.json';raw=p.read_bytes();q=f.root/'replacement';q.write_bytes(raw);q.chmod(0o600);q.replace(p)
        with self.assertRaises(P.Refusal):f.inputs.read('selector')
    def test_mode_drift_refused(self):
        f=self.fixture();(f.root/'selector.json').chmod(0o644)
        with self.assertRaises(P.Refusal):f.inputs.read('selector')
    def test_independent_mount_selection_mismatch(self):
        f=self.fixture();roots=P.parse(P.canonical(list(f.inputs._roots.values())))
        members=P.parse(P.canonical(list(f.inputs._members.values())))
        roots[0]['mount_ids'][-1]+=1
        with self.assertRaises(P.Refusal):P.HeldInputs(roots,members)
    def test_member_mount_selection_mismatch(self):
        f=self.fixture();roots=P.parse(P.canonical(list(f.inputs._roots.values())))
        members=P.parse(P.canonical(list(f.inputs._members.values())))
        next(row for row in members if row['file_id']=='selector')['mount_id']+=1
        inputs=P.HeldInputs(roots,members);self.addCleanup(inputs.close)
        with self.assertRaises(P.Refusal):inputs.read('selector')
    def test_root_detachment_refused_preserves_foreign(self):
        f=self.fixture();moved=f.root.with_name(f.root.name+'-old');f.root.rename(moved);f.root.mkdir();marker=f.root/'foreign';marker.write_bytes(b'foreign')
        try:
            with self.assertRaises(P.Refusal):f.inputs.read('selector')
            self.assertEqual(marker.read_bytes(),b'foreign')
        finally:
            marker.unlink();f.root.rmdir();moved.rename(f.root)
    def test_intermediate_symlink_refused(self):
        f=self.fixture();code=f.root/'code';other=f.root/'saved';code.rename(other);code.symlink_to(other,target_is_directory=True)
        try:
            with self.assertRaises(P.Refusal):f.inputs.read('common')
        finally:code.unlink();other.rename(code)
    def test_private_error_traceback_sanitized(self):
        f=self.fixture();(f.root/'selector.json').unlink()
        try:f.inputs.read('selector')
        except P.Refusal:
            rendered=traceback.format_exc()
            self.assertNotIn(str(f.root),rendered);self.assertNotIn('selector.json',rendered)
            self.assertNotIn('FileNotFoundError',rendered);self.assertIn('STARTUP_REFUSED',rendered)
        else:self.fail('missing refusal')
    def test_selected_copy_does_not_repin(self):
        f=self.fixture();row=f.inputs.selected('selector');row['binding']['sha256']='0'*64
        self.assertEqual(f.inputs.read('selector'),b'selected-selector')
    def test_closed_input_refuses_unknown(self):
        value={'kind':'execution','root_id':'r','relative_path':'a','sha256':'0'*64,'size_bytes':0,'extra':True}
        with self.assertRaises(P.Refusal):P.binding(value)
    def test_paths_exact_unicode_not_normalized(self):
        for path in ('a/e\u0301/😀','a/é/😀'):self.assertEqual('/'.join(P.relative(path)),path)
    def test_traversal_empty_nul_backslash_refuse(self):
        for path in ('/a','a//b','a/../b','a/./b','a\\b','a\0b',''):
            with self.subTest(path=repr(path)),self.assertRaises(P.Refusal):P.relative(path)
    def test_control_duplicate_keys_refuse(self):
        with self.assertRaises(P.Refusal):P.parse(b'{"x":1,"x":2}')
    def test_control_float_overflow_and_nonfinite_refuse(self):
        for raw in (b'1e309',b'NaN',b'Infinity',b'1.5'):
            with self.subTest(raw=raw),self.assertRaises(P.Refusal):P.parse(raw)
    def test_control_i64_and_surrogates(self):
        self.assertEqual(P.parse(b'9223372036854775807'),2**63-1)
        for raw in (b'9223372036854775808',b'"\ud800"'):
            with self.assertRaises(P.Refusal):P.parse(raw)
    def test_repeated_fd_refusal_no_leaks(self):
        f=self.fixture();p=f.root/'selector.json';p.unlink();os.mkfifo(p,0o600);before=len(os.listdir('/proc/self/fd'))
        for _ in range(30):
            with self.assertRaises(P.Refusal):f.inputs.read('selector')
        self.assertEqual(len(os.listdir('/proc/self/fd')),before)
    def test_closed_inputs_refuse(self):
        f=self.fixture();f.inputs.close()
        with self.assertRaises(P.Refusal):f.inputs.read('selector')

def main():
    global TEMP
    parser=argparse.ArgumentParser();parser.add_argument('--temp-root',required=True,type=Path);TEMP=parser.parse_args().temp_root
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(InputTests))
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS'if r.wasSuccessful()else'FAIL','checks':r.testsRun,'effect_state':'owned-inert','cleanup':'clean'}));raise SystemExit(0 if r.wasSuccessful()else 1)
if __name__=='__main__':main()
