// Synthetic, locally authored genuine PDF byte fixtures (not extracted JSON).
import {createHash} from 'node:crypto';
const md5=b=>createHash('md5').update(b).digest();
const pad=Buffer.from('28bf4e5e4e758a4164004e56fffa01082e2e00b6d0683e802f0ca9fe6453697a','hex');
function padded(s){return Buffer.concat([Buffer.from(s,'latin1'),pad]).subarray(0,32);}
function rc4(key,data){const s=Array.from({length:256},(_,i)=>i);let j=0;for(let i=0;i<256;i++){j=(j+s[i]+key[i%key.length])&255;[s[i],s[j]]=[s[j],s[i]];}let i=0;j=0;return Buffer.from(data.map(v=>{i=(i+1)&255;j=(j+s[i])&255;[s[i],s[j]]=[s[j],s[i]];return v^s[(s[i]+s[j])&255];}));}
const escaped=s=>s.replace(/([\\()])/g,'\\$1');
export function makePdf(pageTexts,{imageOnly=false,encrypted=false,script=false}={}){
  const objects=[];
  const add=s=>{objects.push(Buffer.isBuffer(s)?s:Buffer.from(s,'latin1'));return objects.length;};
  add('<< /Type /Catalog /Pages 2 0 R'+(script?' /OpenAction << /S /JavaScript /JS (throw new Error\\(\\"PDF scripts must never run\\"\\)) >>':'')+' >>');
  add('');add('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>');
  const id=md5(Buffer.from(pageTexts.join('|')));
  let key,encryptionObject;
  if(encrypted){
    const owner=rc4(md5(padded('owner')).subarray(0,5),padded('secret'));
    const permissions=Buffer.alloc(4);permissions.writeInt32LE(-4);
    key=md5(Buffer.concat([padded('secret'),owner,permissions,id])).subarray(0,5);
    const user=rc4(key,pad);
    encryptionObject=`<< /Filter /Standard /V 1 /R 2 /Length 40 /O <${owner.toString('hex')}> /U <${user.toString('hex')}> /P -4 >>`;
  }
  const stream=(data,num,dict='')=>{
    let content=Buffer.from(data,'latin1');
    if(key){const suffix=Buffer.from([num&255,(num>>8)&255,(num>>16)&255,0,0]);content=rc4(md5(Buffer.concat([key,suffix])).subarray(0,10),content);}
    return Buffer.concat([Buffer.from(`<< /Length ${content.length} ${dict} >>\nstream\n`),content,Buffer.from('\nendstream')]);
  };
  const pages=[];
  for(const text of pageTexts){
    const page=objects.length+1,content=page+1,image=page+2;
    pages.push(`${page} 0 R`);
    add(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >>${imageOnly?` /XObject << /Im0 ${image} 0 R >>`:''} >> /Contents ${content} 0 R >>`);
    add(stream(imageOnly?'q 10 0 0 10 40 40 cm /Im0 Do Q':`BT /F1 12 Tf 40 740 Td (${escaped(text)}) Tj ET`,content));
    if(imageOnly)add(stream('\xff\x00\x00',image,'/Type /XObject /Subtype /Image /Width 1 /Height 1 /ColorSpace /DeviceRGB /BitsPerComponent 8'));
  }
  objects[1]=Buffer.from(`<< /Type /Pages /Kids [${pages.join(' ')}] /Count ${pages.length} >>`);
  const encryptionRef=encryptionObject?add(encryptionObject):null;
  const chunks=[Buffer.from('%PDF-1.4\n%\xff\xff\xff\xff\n','latin1')],offsets=[0];let length=chunks[0].length;
  objects.forEach((o,i)=>{offsets.push(length);const b=Buffer.concat([Buffer.from(`${i+1} 0 obj\n`),o,Buffer.from('\nendobj\n')]);chunks.push(b);length+=b.length;});
  const xref=length;
  chunks.push(Buffer.from(`xref\n0 ${objects.length+1}\n0000000000 65535 f \n${offsets.slice(1).map(n=>String(n).padStart(10,'0')+' 00000 n \n').join('')}trailer\n<< /Size ${objects.length+1} /Root 1 0 R${encryptionRef?` /Encrypt ${encryptionRef} 0 R /ID [<${id.toString('hex')}><${id.toString('hex')}>]`:''} >>\nstartxref\n${xref}\n%%EOF\n`));
  return Buffer.concat(chunks);
}
