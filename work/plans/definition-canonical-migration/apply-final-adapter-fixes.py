from pathlib import Path
R=Path('/home/vlad_/projects/CyberAlchemy-lab')
p=R/'implementation/lab-runtime/alchlang/shared-records/ports.mjs'
s=p.read_text().replace("entry.body.path!==prior.path","(entry.body.path??entry.body.ref)!==prior.path")
p.write_text(s)
p=R/'implementation/lab-runtime/alchlang/shared-records/recovery.mjs'
s=p.read_text().replace("const data=JSON.parse(gunzipSync(archive,{maxOutputLength:64*1024*1024}));","""const declared=binding.uncompressed_bytes,limit=declared??64*1024*1024;
 if(!Number.isSafeInteger(limit)||limit<1||limit>512*1024*1024)throw Error('recovery-uncompressed-limit-invalid');
 const inflated=gunzipSync(archive,{maxOutputLength:limit});
 if(declared!==undefined&&inflated.length!==declared)throw Error('recovery-uncompressed-size-mismatch');
 const data=JSON.parse(inflated);""")
p.write_text(s)
p=R/'implementation/lab-runtime/alchlang/shared-records/verify-hardening.mjs'
s=p.read_text().replace("binding={sha256:digest(archive),bytes:archive.length}","binding={sha256:digest(archive),bytes:archive.length,uncompressed_bytes:archive.readUInt32LE(archive.length-4)}")
s=s.replace("const bad=Buffer.from(archive);bad[0]^=1;","""await assert.rejects(()=>restoreRecovery(archive,{...binding,uncompressed_bytes:512*1024*1024+1},path.join(home,'bad-limit'),active,rootTrust),/limit-invalid/);
 await assert.rejects(()=>restoreRecovery(archive,{...binding,uncompressed_bytes:binding.uncompressed_bytes+1},path.join(home,'bad-inflated-size'),active,rootTrust),/size-mismatch/);
 const bad=Buffer.from(archive);bad[0]^=1;""")
p.write_text(s)
