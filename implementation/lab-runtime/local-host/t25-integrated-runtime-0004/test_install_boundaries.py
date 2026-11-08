"""Installation refuses unselected artifacts and preserves existing targets."""
import hashlib,importlib.util,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_cal_install_boundaries_subject',HERE/'install_from_archive.py');I=importlib.util.module_from_spec(spec);spec.loader.exec_module(I)
class Boundaries(unittest.TestCase):
 def test_wrong_archive_pin_creates_no_installation(self):
  with tempfile.TemporaryDirectory(prefix='cal-install-boundary-') as tmp:
   root=Path(tmp);archive=root/'artifact.tgz';archive.write_bytes(b'not the selected artifact');target=root/'destination'
   with self.assertRaisesRegex(ValueError,'archive bytes differ'):I.install(archive,'0'*64,'1'*64,target)
   self.assertFalse(target.exists());self.assertEqual(list(root.iterdir()),[archive])
 def test_existing_target_preserved_before_archive_extraction(self):
  with tempfile.TemporaryDirectory(prefix='cal-install-boundary-') as tmp:
   root=Path(tmp);archive=root/'artifact.tgz';archive.write_bytes(b'selected but not extracted');target=root/'destination';target.mkdir();sentinel=target/'keep';sentinel.write_bytes(b'existing user content')
   with self.assertRaisesRegex(ValueError,'existing installation target'):I.install(archive,hashlib.sha256(archive.read_bytes()).hexdigest(),'1'*64,target)
   self.assertEqual(sentinel.read_bytes(),b'existing user content');self.assertEqual(sorted(p.name for p in root.iterdir()),['artifact.tgz','destination'])
if __name__=='__main__':unittest.main()
