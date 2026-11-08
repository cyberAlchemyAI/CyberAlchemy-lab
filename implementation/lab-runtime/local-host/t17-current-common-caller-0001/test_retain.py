import json
import os
from pathlib import Path
import tempfile
import unittest
from retain import archive


class Retain(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='cal-retain-test-');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.root.chmod(0o700)
        self.vault=self.root/'fixture/workspace';self.vault.mkdir(parents=True,mode=0o700)
        (self.vault/'objects').mkdir(mode=0o700);(self.vault/'objects/a.json').write_bytes(b'{ "original": true }\n')
        (self.vault.parent/'reader.pem').write_bytes(b'PRIVATE KEY-----synthetic test credential')
        self.result=self.root/'retained';self.result.mkdir(mode=0o700)

    def test_originals_and_inventory_preserved_credentials_omitted(self):
        row=archive(self.result/'call',self.vault,{'case':'fixture'})
        target=Path(row['path']);self.assertEqual((target/'vault/objects/a.json').read_bytes(),b'{ "original": true }\n')
        self.assertFalse((target/'reader.pem').exists())
        self.assertEqual((target/'vault/objects/a.json').stat().st_mode&0o777,0o600)
        self.assertEqual(len(json.loads((target/'OBSERVATION.json').read_bytes())['files']),1)

    def test_linked_output_refuses(self):
        (self.vault/'objects/link').symlink_to(self.vault.parent/'reader.pem')
        with self.assertRaises(ValueError):archive(self.result/'call',self.vault,{})
        self.assertFalse((self.result/'call/OBSERVATION.json').exists())

    def test_credential_inside_Vault_refuses(self):
        (self.vault/'objects/a.json').write_bytes(b'-----BEGIN PRIVATE KEY-----')
        with self.assertRaises(ValueError):archive(self.result/'call',self.vault,{})
        self.assertFalse((self.result/'call/OBSERVATION.json').exists())

    def test_existing_retention_refuses_without_overwrite(self):
        archive(self.result/'call',self.vault,{})
        original=(self.result/'call/OBSERVATION.json').read_bytes()
        with self.assertRaises(ValueError):archive(self.result/'call',self.vault,{})
        self.assertEqual((self.result/'call/OBSERVATION.json').read_bytes(),original)


if __name__=='__main__':unittest.main()
