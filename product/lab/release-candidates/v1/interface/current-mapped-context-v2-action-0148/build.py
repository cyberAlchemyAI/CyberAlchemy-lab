"""Original native executable/signature functions, separately selected fresh mapper guard."""
from .base import *
EXE=ORIGINAL.EXE;EXE_SHA=ORIGINAL.EXE_SHA;ONTOLOGY=ORIGINAL.ONTOLOGY
PROFILE=ORIGINAL.PROFILE;EDGE_PROFILE=ORIGINAL.EDGE_PROFILE
call=ORIGINAL.call;native_bytes=ORIGINAL.native_bytes;seal=ORIGINAL.seal
# Package lives in the frozen original directory. SELECTOR_ROOT selects code.
def guard(pin,*,additional_rows=()):
    verify_source(pin,additional_rows=additional_rows)
    require(EXE.is_file() and not EXE.is_symlink() and sha(EXE.read_bytes())==EXE_SHA,'original native executable differs')
