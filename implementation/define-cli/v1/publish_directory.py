#!/usr/bin/env python3
"""Linux atomic directory publication: an existing destination is never replaced."""
import ctypes
import os
import sys
libc=ctypes.CDLL(None,use_errno=True)
rename=getattr(libc,'renameat2',None)
if rename is None:
    raise SystemExit('Define directory publication requires Linux renameat2 support')
rename.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint]
rename.restype=ctypes.c_int
if rename(-100,os.fsencode(sys.argv[1]),-100,os.fsencode(sys.argv[2]),1)!=0:
    code=ctypes.get_errno()
    raise SystemExit(f'Define output publication refused: {os.strerror(code)}')
