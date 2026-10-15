"""Deterministic local-script delivery with built-in gzip and a plain fallback.

Both forms contain the same complete payload. Browsers need no fetch request or
external library, including at a file origin. Inspect the fallback for a readable
payload; compare payload_sha256 when validating either delivery form.
"""
import base64
import gzip
import hashlib
import json


def write_payload(path, global_name, value, set_base=False):
    plain = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    data = plain.encode('utf-8')
    fallback = path.with_name(path.stem + '-fallback.js')
    footer = f'\nwindow.{global_name}.base=new URL("../",document.currentScript.src).href;' if set_base else ''
    fallback.write_text(f'/* Complete plaintext fallback; generated. */\nwindow.{global_name}={plain};{footer}\n', encoding='utf-8')
    compressed=bytearray(gzip.compress(data, compresslevel=9, mtime=0))
    compressed[9]=255  # Portable gzip OS marker, including older Python versions.
    encoded = base64.b64encode(compressed).decode('ascii')
    if gzip.decompress(base64.b64decode(encoded)) != data:
        raise ValueError('Compressed search delivery changed payload bytes.')
    base_assignment = 'value.base=new URL("../",address).href;' if set_base else ''
    code = f'''/* Compressed complete payload; generated. No fetch or external dependency. */
(() => {{
  const address=document.currentScript.src;
  const publish=value=>{{{base_assignment}window.{global_name}=value;return value;}};
  const fallback=()=>new Promise((resolve,reject)=>{{
    const script=document.createElement('script');script.src=new URL({json.dumps(fallback.name)},address);
    script.onload=()=>resolve(window.{global_name});
    script.onerror=()=>{{script.remove();reject(new Error('The local search data could not be loaded.'));}};
    document.head.append(script);
  }});
  window.{global_name}Ready=(async()=>{{
    if(typeof DecompressionStream==='undefined')return fallback();
    try {{
      const bytes=Uint8Array.from(atob({json.dumps(encoded)}),character=>character.charCodeAt(0));
      const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
      return publish(JSON.parse(await new Response(stream).text()));
    }} catch {{return fallback();}}
  }})();
  // A loader attaches onload after evaluation; retain rejection for that
  // caller while avoiding an unhandled rejection during the intervening task.
  window.{global_name}Ready.catch(()=>{{}});
}})();
'''
    path.write_text(code, encoding='utf-8')
    return {'encoding': 'gzip-base64 local script with complete plaintext fallback',
            'payload_bytes': len(data), 'payload_sha256': hashlib.sha256(data).hexdigest(),
            'script_bytes': len(code.encode()), 'fallback': fallback.name,
            'fallback_sha256': hashlib.sha256(fallback.read_bytes()).hexdigest()}
