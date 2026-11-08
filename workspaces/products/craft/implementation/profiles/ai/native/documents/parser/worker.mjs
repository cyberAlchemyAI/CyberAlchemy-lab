import {readFileSync,writeFileSync} from 'node:fs';
import {createConnection} from 'node:net';
import {spawnSync} from 'node:child_process';

// Dependency warnings must never contaminate the finite machine result.
let repaired=false;
console.log=console.warn=console.error=(...messages)=>{if(messages.some(v=>typeof v==='string'&&/Indexing all PDF objects|Invalid XRef|bad XRef|XRef\.parse/.test(v)))repaired=true;};
const request=JSON.parse(readFileSync(0,'utf8'));
const reply=x=>process.stdout.write(JSON.stringify(x));
if(process.argv[2]==='probe') {
  const denied=fn=>{try{fn();return false;}catch{return true;}};
  const networkDenied=await new Promise(resolve=>{const s=createConnection({host:'127.0.0.1',port:9});s.on('error',e=>resolve(e.code==='EPERM'||e.code==='EACCES'));s.on('connect',()=>{s.destroy();resolve(false);});});
  const child=spawnSync('/node',['-e','process.exit(0)']);
  reply({hostFilesystemDenied:denied(()=>readFileSync('/etc/passwd')),packageWriteDenied:denied(()=>writeFileSync('/app/isolation-probe','x')),rootWriteDenied:denied(()=>writeFileSync('/escape','x')),networkDenied,processCreationDenied:!!child.error,evalDenied:denied(()=>eval('1+1')),nodeVersion:process.version,limits:readFileSync('/proc/self/limits','utf8'),processStatus:readFileSync('/proc/self/status','utf8')});
} else if(process.argv[2]==='burn') {while(true){}}
else if(process.argv[2]==='allocate') {const pages=[];while(true){const b=Buffer.alloc(16*1024*1024,1);pages.push(b);}}
else if(process.argv[2]==='flood') {while(true)process.stdout.write('x'.repeat(8192));}
else {
  const {mediaType,limits}=request;
  const bytes=Uint8Array.from(Buffer.from(request.base64,'base64'));
  const failure=(status,reason)=>({status,reason});
  let task;
  try{
    if(bytes.byteLength>limits.bytes)throw Error('BYTE_LIMIT');
    if(mediaType!=='application/pdf'){
      let text;
      try{text=new TextDecoder('utf-8',{fatal:true}).decode(bytes);}catch{throw Error('INVALID_UTF8');}
      if(text.includes('\0'))throw Error('INVALID_TEXT');
      if(text.length>limits.textChars)throw Error('TEXT_LIMIT');
      reply(text.trim()?{status:'parsed',pages:[{page:1,text,spans:[{start:0,end:text.length,text}]}]}:failure('review','NO_TEXT'));
    }else{
      if(Buffer.from(bytes.subarray(0,8)).toString('ascii').match(/^%PDF-\d\.\d/)==null)throw Error('MALFORMED_PDF');
      const trailer=Buffer.from(bytes.buffer,bytes.byteOffset,bytes.byteLength).toString('latin1').match(/\bstartxref\s+([0-9]{1,12})\s+%%EOF[\x00\t\n\r\f ]*$/);
      if(!trailer||Number(trailer[1])<8||Number(trailer[1])>=bytes.length)throw Error('MALFORMED_PDF');
      const pdf=await import('./node_modules/pdfjs-dist/legacy/build/pdf.mjs');
      if(pdf.version!=='6.4.299')throw Error('PACKAGE_IDENTITY_MISMATCH');
      task=pdf.getDocument({data:bytes,verbosity:1,stopAtErrors:true,enableScripting:false,isEvalSupported:false,enableXfa:false,useWasm:false,useWorkerFetch:false,disableFontFace:true,useSystemFonts:false,disableAutoFetch:true,disableStream:true,disableRange:true,isOffscreenCanvasSupported:false,isImageDecoderSupported:false,maxImageSize:1,canvasMaxAreaInBytes:1});
      const doc=await task.promise;
      if(repaired)throw Error('MALFORMED_PDF');
      if(await doc.getPermissions()!==null){reply(failure('review','ENCRYPTED_PDF'));}
      else if(doc.numPages>limits.pages)throw Error('PAGE_LIMIT');
      else {
        const pages=[];let total=0,spanCount=0;
        for(let page=1;page<=doc.numPages;page++){
          const p=await doc.getPage(page),stream=p.streamTextContent({includeMarkedContent:false,disableNormalization:true}),reader=stream.getReader();
          let text='',spans=[];
          while(true){const {value,done}=await reader.read();if(done)break;
            for(const item of value.items){if(typeof item.str!=='string')continue;
              const str=item.str+(item.hasEOL?'\n':'');
              if(!str)continue;
              const start=text.length;total+=str.length;
              if(total>limits.textChars)throw Error('TEXT_LIMIT');
              if(++spanCount>limits.spans)throw Error('SPAN_LIMIT');
              text+=str;
              const transform=Array.isArray(item.transform)&&item.transform.every(Number.isFinite)?item.transform:undefined;
              spans.push({start,end:text.length,text:str,...(transform?{bounds:{transform,width:item.width,height:item.height}}:{})});
            }
          }
          pages.push({page,text,spans});p.cleanup();
        }
        if(repaired)throw Error('MALFORMED_PDF');
        reply(pages.some(p=>p.text.trim())?{status:'parsed',pages}:failure('review','IMAGE_ONLY_OR_NO_TEXT'));
      }
    }
  }catch(e){
    const encrypted=e?.name==='PasswordException';
    const reason=encrypted?'ENCRYPTED_PDF':['BYTE_LIMIT','PAGE_LIMIT','TEXT_LIMIT','SPAN_LIMIT','INVALID_UTF8','INVALID_TEXT','PACKAGE_IDENTITY_MISMATCH'].includes(e.message)?e.message:'MALFORMED_PDF';
    reply(failure(encrypted?'review':'quarantine',reason));
  }finally{if(task)try{await task.destroy();}catch{}}
}
