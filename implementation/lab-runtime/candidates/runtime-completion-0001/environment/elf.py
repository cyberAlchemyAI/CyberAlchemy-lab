"""Inert bounded ELF64/x86-64 origin inspection; never invokes a loader.

Dynamic names/version declarations constrain a selected closure. They do not
prove relocation, symbol availability, CPU compatibility or runtime ABI success.
"""
import struct
from lab_contracts.codec import Refusal,need,sha

MAX_BYTES=64*1024*1024
MAX_ENTRIES=16384

def inspect_elf(raw,expected_sha256):
    try:
        need(type(raw)is bytes and 64<=len(raw)<=MAX_BYTES and sha(raw)==expected_sha256,'ELF_INPUT')
        need(raw[:7]==b'\x7fELF\x02\x01\x01' and raw[7] in (0,3) and raw[8]==0
             and raw[9:16]==bytes(7),'ELF_PLATFORM')
        kind,machine,version,entry,phoff,shoff,flags,ehsize,phentsize,phnum,_,_,_=struct.unpack_from('<HHIQQQIHHHHHH',raw,16)
        need(kind in (2,3) and machine==62 and version==1 and flags==0 and ehsize==64
             and phentsize==56 and 0<phnum<=1024 and phoff>=64,'ELF_HEADER')
        def span(offset,size):
            need(type(offset)is int and type(size)is int and 0<=offset<=len(raw) and 0<=size<=len(raw)-offset,'ELF_RANGE')
            return raw[offset:offset+size]
        span(phoff,phnum*56)
        loads=[];dynamic=[];interps=[]
        for i in range(phnum):
            typ,pflags,off,va,pa,filesz,memsz,align=struct.unpack_from('<IIQQQQQQ',raw,phoff+56*i)
            span(off,filesz);need(memsz>=filesz and pflags&~7==0,'ELF_SEGMENT')
            need(align in (0,1) or align&(align-1)==0,'ELF_ALIGNMENT')
            if typ==1:loads.append((va,off,filesz))
            elif typ==2:dynamic.append((off,filesz))
            elif typ==3:interps.append(span(off,filesz))
        need(loads and len(dynamic)<=1 and len(interps)<=1,'ELF_UNIQUE_SEGMENTS')
        def address(va,size):
            hits=[off+va-start for start,off,length in loads if start<=va and size<=length-(va-start)]
            need(len(hits)==1,'ELF_ADDRESS_ORIGIN');span(hits[0],size);return hits[0]
        interpreter=None
        if interps:
            data=interps[0]
            need(2<=len(data)<=4096 and data[-1:]==b'\0' and b'\0' not in data[:-1],'ELF_INTERPRETER')
            interpreter=data[:-1].decode('ascii')
            need(interpreter.startswith('/') and '\\' not in interpreter
                 and all(p not in ('','.','..') for p in interpreter[1:].split('/')),'ELF_INTERPRETER')
            need(interpreter=='/lib64/ld-linux-x86-64.so.2','ELF_INTERPRETER_ORIGIN')
        tags={};terminated=False
        if dynamic:
            off,size=dynamic[0];need(size%16==0 and 0<size//16<=MAX_ENTRIES,'ELF_DYNAMIC_BOUND')
            address(next((va+off-base for va,base,length in loads if base<=off and size<=length-(off-base)),-1),size)
            for pos in range(off,off+size,16):
                tag,value=struct.unpack_from('<qQ',raw,pos)
                if tag==0:terminated=True;break
                need(tag>=0,'ELF_DYNAMIC_TAG');tags.setdefault(tag,[]).append(value)
            need(terminated,'ELF_DYNAMIC_TERMINATOR')
        for tag,values in tags.items():
            need(tag==1 or len(values)==1,'ELF_DUPLICATE_DYNAMIC_TAG')
        def single(tag,default=None):return tags.get(tag,[default])[0]
        supported_tags={1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,
            25,26,27,28,29,30,32,33,34,35,36,37,0x6ffffef5,0x6ffffff0,0x6ffffff9,
            0x6ffffffa,0x6ffffffb,0x6ffffffc,0x6ffffffd,0x6ffffffe,0x6fffffff,
            0x70000000,0x70000001,0x70000003}
        need(set(tags)<=supported_tags,'ELF_UNSUPPORTED_DYNAMIC_REQUIREMENT')
        need(single(30,0)&~(8|16)==0 and single(0x6ffffffb,0)&~(1|8|0x08000000)==0,
             'ELF_UNSUPPORTED_LOADER_FLAGS')
        need(16 not in tags and 22 not in tags,'ELF_UNSUPPORTED_RELOCATION_POLICY')
        features={}
        # glibc x86-64 marked-PLT declarations are bounded byte structures.
        # Loader support/rewriting is retained as a separate runtime obligation.
        plt_tags={0x70000000,0x70000001,0x70000003}
        need(not (plt_tags&set(tags)) or plt_tags<=set(tags),'ELF_PLT_REQUIREMENT_PAIR')
        if plt_tags<=set(tags):
            size=single(0x70000001);width=single(0x70000003)
            need(0<size<=MAX_BYTES and 8<=width<=256 and size%width==0,'ELF_PLT_REQUIREMENT_BOUND')
            address(single(0x70000000),size)
            features['x86_64_marked_plt']={'size_bytes':size,'entry_bytes':width,'runtime_support_verified':False}
        relr_tags={35,36,37}
        need(not (relr_tags&set(tags)) or relr_tags<=set(tags),'ELF_RELR_REQUIREMENT_PAIR')
        if relr_tags<=set(tags):
            need(single(37)==8 and 0<single(35)<=MAX_BYTES and single(35)%8==0,'ELF_RELR_REQUIREMENT_BOUND')
            address(single(36),single(35))
            features['packed_relative_relocations']={'size_bytes':single(35),'entry_bytes':8,'runtime_support_verified':False}
        # Search paths are not made safe by matching a content digest. A future
        # separately reviewed loader policy would be required to support them.
        need(15 not in tags and 29 not in tags,'ELF_SEARCH_PATH_UNSUPPORTED')
        # Audit/filter/auxiliary loading adds dependencies outside DT_NEEDED.
        need(not ({0x6ffffefb,0x6ffffefc,0x7fffffff,0x7ffffffd}&set(tags)),'ELF_DYNAMIC_LOADING_UNSUPPORTED')
        string_tags={1,14,0x6ffffffe,0x6ffffffc}
        strings=b''
        if string_tags&set(tags):
            need(5 in tags and 10 in tags and 0<single(10)<=MAX_BYTES,'ELF_STRING_TABLE')
            strings=span(address(single(5),single(10)),single(10))
        def text(index):
            need(type(index)is int and 0<=index<len(strings),'ELF_STRING_INDEX')
            end=strings.find(b'\0',index,min(len(strings),index+4097))
            need(end>index,'ELF_STRING_BOUND');value=strings[index:end].decode('ascii')
            need('/' not in value and '\\' not in value and '$' not in value and value not in ('.','..'),'ELF_DYNAMIC_NAME')
            return value
        needed=[text(i) for i in tags.get(1,[])]
        need(len(needed)==len(set(needed)) and len(needed)<=4096,'ELF_NEEDED')
        soname=text(single(14)) if 14 in tags else None
        requirements={};provided=[];version_budget=MAX_ENTRIES
        for table_tag,count_tag,width,mode in ((0x6ffffffe,0x6fffffff,16,'need'),(0x6ffffffc,0x6ffffffd,20,'definition')):
            need((table_tag in tags)==(count_tag in tags),'ELF_VERSION_PAIR')
            if table_tag not in tags:continue
            count=single(count_tag);need(0<count<=MAX_ENTRIES,'ELF_VERSION_COUNT')
            current=single(table_tag);visited=set()
            for index in range(count):
                need(current not in visited,'ELF_VERSION_CYCLE');visited.add(current)
                offset=address(current,width)
                if mode=='need':
                    ver,naux,file_index,aux,next_record=struct.unpack_from('<HHIII',raw,offset)
                    library=text(file_index);need(library in needed and library not in requirements,'ELF_VERSION_LIBRARY')
                    requirements[library]=[]
                else:
                    ver,vflags,vindex,naux,vhash,aux,next_record=struct.unpack_from('<HHHHIII',raw,offset)
                    need(vflags&~3==0 and vindex>0,'ELF_VERSION_DEFINITION')
                need(ver==1 and 0<naux<=MAX_ENTRIES and aux>=width,'ELF_VERSION_FORMAT')
                version_budget-=naux+1;need(version_budget>=0,'ELF_VERSION_TOTAL_BOUND')
                cursor=current+aux;aux_seen=set()
                for j in range(naux):
                    need(cursor not in aux_seen,'ELF_VERSION_AUX_CYCLE');aux_seen.add(cursor)
                    if mode=='need':
                        h,aflags,other,name,next_aux=struct.unpack_from('<IHHII',raw,address(cursor,16))
                        need(aflags&~3==0 and other&0x7fff>1,'ELF_VERSION_REQUIREMENT')
                        value=text(name);need(value not in requirements[library],'ELF_VERSION_DUPLICATE')
                        requirements[library].append(value)
                    else:
                        name,next_aux=struct.unpack_from('<II',raw,address(cursor,8))
                        value=text(name)
                        if j==0:
                            need(value not in provided,'ELF_VERSION_DUPLICATE');provided.append(value)
                    need((j==naux-1 and next_aux==0) or (j<naux-1 and next_aux>0),'ELF_VERSION_AUX_COUNT')
                    cursor+=next_aux
                need((index==count-1 and next_record==0) or (index<count-1 and next_record>=width),'ELF_VERSION_TABLE_COUNT')
                current+=next_record
        return {'schema_version':'lab-inert-elf-origin/v1','sha256':expected_sha256,'elf_class':64,
            'machine':'x86_64','endianness':'little','needed':needed,'interpreter':interpreter,
            'soname':soname,'required_versions':requirements,'provided_versions':provided,
            'loader_paths':[],'platform_requirements':features,
            'remaining_runtime_requirements':['actual loader resolution and relocation','actual symbol/version resolution','CPU and process ABI compatibility'],
            'runtime_abi_verified':False,'authority_effect':'none'}
    except Exception:
        raise Refusal('ELF_ORIGIN_REFUSED') from None

def compare_abi_versions(consumer,libraries):
    """Require an exact independently selected SONAME map, not filesystem search."""
    try:
        need(type(libraries)is dict and set(libraries)==set(consumer['needed']),'ABI_EXACT_ORIGINS')
        for name,library in libraries.items():
            need(library['soname']==name and library['machine']==consumer['machine']
                 and library['elf_class']==consumer['elf_class'] and library['endianness']==consumer['endianness'],'ABI_ORIGIN')
            need(set(consumer['required_versions'].get(name,[]))<=set(library['provided_versions']),'ABI_VERSION_GAP')
        return {'declared_version_requirements_satisfied':True,'runtime_abi_verified':False,'authority_effect':'none'}
    except Exception:
        raise Refusal('ABI_ORIGIN_REFUSED') from None
