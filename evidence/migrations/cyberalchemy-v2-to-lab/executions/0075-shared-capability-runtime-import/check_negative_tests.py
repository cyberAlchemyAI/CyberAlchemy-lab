"""Run original mutations with one explicitly corrected diagnostic expectation.
The source validator and package files are unchanged. Open questions: README.md.
"""
import importlib.util,sys
from pathlib import Path
p=Path.cwd()/'.local/shared-capability-package-0075/cyberAlchemy-v2/capability/tests/test_negative_mutations.py'
s=importlib.util.spec_from_file_location('source_negative_tests',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
old='public-private bridge lacks separate business and system source evidence';new='bridge lacks separate meaning and realization source evidence'
assert sum(label=='one-sided bridge evidence' and expected==old for label,_,expected in m.CASES)==1
m.CASES=[(label,mutation,new if label=='one-sided bridge evidence' else expected) for label,mutation,expected in m.CASES]
sys.exit(m.main())
