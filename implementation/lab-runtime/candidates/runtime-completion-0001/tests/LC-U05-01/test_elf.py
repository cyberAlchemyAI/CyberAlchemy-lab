"""Bounded ELF origin failures; fixture bytes never execute."""
import bootstrap
from bootstrap import E
import argparse,copy,json,struct,unittest
from pathlib import Path
from lab_contracts.codec import sha,Refusal
from environment.elf import inspect_elf,compare_abi_versions

def fixture(*,needed=('libfixture.so',),soname=None,version='FIXTURE_1',definition=False,extra=()):
    raw=bytearray(2048);raw[:16]=b'\x7fELF\x02\x01\x01'+bytes(9)
    struct.pack_into('<HHIQQQIHHHHHH',raw,16,3,62,1,0,64,0,0,64,56,2,0,0,0)
    struct.pack_into('<IIQQQQQQ',raw,64,1,6,0,0x400000,0,len(raw),len(raw),4096)
    names=bytearray(b'\0');indices={}
    def text(v):
        if v not in indices:indices[v]=len(names);names.extend(v.encode()+b'\0')
        return indices[v]
    entries=[(1,text(v)) for v in needed]
    if soname:entries.append((14,text(soname)))
    if version:
        name=text(version)
        if definition:
            struct.pack_into('<HHHHIII',raw,1200,1,0,2,1,0,20,0)
            struct.pack_into('<II',raw,1220,name,0)
            entries += [(0x6ffffffc,0x400000+1200),(0x6ffffffd,1)]
        else:
            library=text(needed[0]);struct.pack_into('<HHIII',raw,1200,1,1,library,16,0)
            struct.pack_into('<IHHII',raw,1216,0,0,2,name,0)
            entries += [(0x6ffffffe,0x400000+1200),(0x6fffffff,1)]
    raw[768:768+len(names)]=names
    entries += [(5,0x400000+768),(10,len(names)),*extra,(0,0)]
    struct.pack_into('<IIQQQQQQ',raw,120,2,6,256,0x400000+256,0,len(entries)*16,len(entries)*16,8)
    for i,row in enumerate(entries):struct.pack_into('<qQ',raw,256+i*16,*row)
    return bytes(raw)

class ElfTests(unittest.TestCase):
    def inspect(self,raw):return inspect_elf(raw,sha(raw))
    def reject(self,raw):
        with self.assertRaisesRegex(Refusal,'^ELF_ORIGIN_REFUSED$'):self.inspect(raw)
    def mutate(self,offset,fmt,*values):
        raw=bytearray(fixture());struct.pack_into(fmt,raw,offset,*values);self.reject(bytes(raw))
    def test_real_structural_version_requirement_and_provider_match(self):
        consumer=self.inspect(fixture());library=self.inspect(fixture(needed=(),soname='libfixture.so',definition=True))
        self.assertEqual(consumer['required_versions'],{'libfixture.so':['FIXTURE_1']})
        self.assertFalse(compare_abi_versions(consumer,{'libfixture.so':library})['runtime_abi_verified'])
    def test_independent_byte_pin_refuses_coherent_change(self):
        a=fixture();b=fixture(version='FIXTURE_2')
        with self.assertRaises(Refusal):inspect_elf(b,sha(a))
    def test_unselected_version_provider_refuses(self):
        consumer=self.inspect(fixture());library=self.inspect(fixture(needed=(),soname='libfixture.so',version='FIXTURE_2',definition=True))
        with self.assertRaisesRegex(Refusal,'^ABI_ORIGIN_REFUSED$'):compare_abi_versions(consumer,{'libfixture.so':library})
    def test_missing_transitive_provider_refuses(self):
        with self.assertRaises(Refusal):compare_abi_versions(self.inspect(fixture()),{})
    def test_wrong_soname_cannot_alias_by_caller_mapping(self):
        library=self.inspect(fixture(needed=(),soname='libwrong.so',definition=True))
        with self.assertRaises(Refusal):compare_abi_versions(self.inspect(fixture()),{'libfixture.so':library})
    def test_wrong_class_endianness_machine_and_version(self):
        for offset,value in ((4,1),(5,2),(6,0),(7,9),(8,1)):
            with self.subTest(offset=offset):
                raw=bytearray(fixture());raw[offset]=value;self.reject(bytes(raw))
        self.mutate(18,'H',183)
    def test_rpath_runpath_and_origin_refuse(self):
        for tag in (15,29):
            with self.subTest(tag=tag):self.reject(fixture(extra=((tag,1),)))
        self.reject(fixture(extra=((30,1),)))
    def test_unknown_dynamic_requirement_refuses(self):self.reject(fixture(extra=((0x60000001,1),)))
    def test_filter_audit_loader_side_effects_refuse(self):
        for tag in (0x6ffffefb,0x6ffffefc,0x7fffffff,0x7ffffffd):self.reject(fixture(extra=((tag,1),)))
    def test_missing_dynamic_terminator_refuses(self):
        raw=bytearray(fixture());size=struct.unpack_from('<Q',raw,120+32)[0]
        struct.pack_into('<qQ',raw,256+size-16,21,0);self.reject(bytes(raw))
    def test_duplicate_singleton_and_needed_refuse(self):
        self.reject(fixture(extra=((5,0x400000+768),)))
        self.reject(fixture(needed=('libfixture.so','libfixture.so')))
    def test_unterminated_private_name_cannot_escape_error(self):
        import traceback
        raw=bytearray(fixture());raw[768:2048]=b'PRIVATE_ELF_VALUE'+b'x'*(1280-17)
        try:self.inspect(bytes(raw))
        except Refusal as e:self.assertNotIn('PRIVATE_ELF_VALUE',''.join(traceback.format_exception(e)))
        else:self.fail('invalid bytes must refuse')
    def test_program_header_and_mapping_bounds(self):
        self.mutate(32,'Q',2**64-1);self.mutate(56,'H',65535)
        self.mutate(120+8,'Q',2**64-1)
    def test_version_chain_count_and_forward_pointer_refuse(self):
        self.mutate(1200+12,'I',16);self.mutate(1200+8,'I',2**32-1)
        self.mutate(1200,'H',2)
    def test_unknown_version_library_and_empty_name_refuse(self):
        self.mutate(1200+4,'I',0);self.mutate(1216+8,'I',0)
    def test_loader_flags_with_ambient_search_semantics_refuse(self):
        self.reject(fixture(extra=((0x6ffffffb,0x800),)))
    def test_marked_plt_complete_bounded_declaration_preserves_runtime_obligation(self):
        value=self.inspect(fixture(extra=((0x70000000,0x400000+1600),(0x70000001,32),(0x70000003,16))))
        self.assertFalse(value['platform_requirements']['x86_64_marked_plt']['runtime_support_verified'])
        self.reject(fixture(extra=((0x70000000,0x400000+1600),)))
        self.reject(fixture(extra=((0x70000000,0x400000+1600),(0x70000001,31),(0x70000003,16))))
    def test_packed_relocation_unknown_entry_size_or_origin_refuses(self):
        self.reject(fixture(extra=((35,16),(36,0x400000+1600),(37,4))))
        self.reject(fixture(extra=((35,16),(36,2**63),(37,8))))
        self.assertIn('packed_relative_relocations',self.inspect(fixture(extra=((35,16),(36,0x400000+1600),(37,8))))['platform_requirements'])
    def test_same_basename_does_not_substitute_interpreter_origin(self):
        for path,valid in (('/lib64/ld-linux-x86-64.so.2',True),('/unselected/ld-linux-x86-64.so.2',False)):
            raw=bytearray(fixture());data=path.encode()+b'\0';raw[1500:1500+len(data)]=data
            struct.pack_into('<H',raw,56,3)
            struct.pack_into('<IIQQQQQQ',raw,176,3,4,1500,0x400000+1500,0,len(data),len(data),1)
            if valid:self.assertEqual(self.inspect(bytes(raw))['interpreter'],path)
            else:self.reject(bytes(raw))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--temp-root',type=Path,required=True);a=p.parse_args()
    if a.temp_root!=E or not E.is_dir():raise ValueError('owned root')
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ElfTests))
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS' if result.wasSuccessful() else 'FAIL',
        'checks':result.testsRun,'effect_state':'owned-inert','cleanup':'clean'}))
    raise SystemExit(0 if result.wasSuccessful() else 1)
