"""Exact byte-origin closure over the selected T08 reader; no loader execution."""
from dataclasses import dataclass
import io,stat,zipfile
from lab_contracts.codec import Refusal,need,closed,sha,canonical
from lab_selectors.anchors import relative
from dependency_graph.reader import RoleReader,binding,source_cut
from .elf import inspect_elf,compare_abi_versions

@dataclass(frozen=True)
class OriginSelection:
    source_binding:dict
    profile_binding:dict
    source_cut:dict
    members:list

def wheel_inventory(raw):
    """Original bounded archive semantics, hashing only; never extracts a path."""
    try:
        need(type(raw)is bytes and len(raw)<=64*1024*1024,'WHEEL_BYTES')
        rows={};total=0;names=set()
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            entries=archive.infolist();need(len(entries)<=10000,'WHEEL_COUNT')
            for entry in entries:
                name=entry.filename;clean=name[:-1] if entry.is_dir() else name
                parts=relative(clean)
                need(name==entry.orig_filename and name not in names and not entry.flag_bits&1 and '\0' not in name,'WHEEL_IDENTITY')
                names.add(name)
                kind=stat.S_IFMT(entry.external_attr>>16)
                need(kind in (0,stat.S_IFREG,stat.S_IFDIR) and kind!=stat.S_IFLNK,'WHEEL_SPECIAL')
                if entry.is_dir():continue
                need(kind!=stat.S_IFDIR and '.data' not in parts and not name.endswith('.pth')
                     and not any(p.endswith('.data') for p in parts),'WHEEL_HOOK')
                need(entry.file_size<=32*1024*1024,'WHEEL_MEMBER_BOUND')
                total+=entry.file_size;need(total<=128*1024*1024,'WHEEL_TOTAL_BOUND')
                with archive.open(entry) as stream:data=stream.read(entry.file_size+1)
                need(len(data)==entry.file_size,'WHEEL_EXPANDED_SIZE')
                rows['deps/'+name]={'sha256':sha(data),'size_bytes':len(data),'mode':0o644}
        return rows
    except Exception:
        raise Refusal('WHEEL_ORIGIN_REFUSED') from None

def verify_selected_origins(reader,requirements,selection):
    """Inert byte verification; mode/custody/runtime obligations remain explicit.

Requirements are the exact original document already validated by the composite
consumer. No original locator is followed: every member has a full independently
selected C01 binding and reader file ID. Alternate locations never qualify the
historical proof's original locators.
"""
    try:
        need(type(reader)is RoleReader and type(selection)is OriginSelection,'ORIGIN_SELECTION')
        sealed_selection=canonical(selection.__dict__)
        for name in ('source_binding','profile_binding'):binding(getattr(selection,name))
        source_cut(selection.source_cut)
        for name in ('source_binding','profile_binding','source_cut'):
            need(getattr(selection,name)==reader.selection[name],'ORIGIN_SOURCE_CUT')
        need(type(selection.members)is list and len(selection.members)<=100000,'ORIGIN_BOUND')
        expected={}
        for row in requirements['inputs']:
            need(row['destination'] not in expected,'ORIGIN_DUPLICATE')
            expected[row['destination']]={k:row[k] for k in ('sha256','size_bytes','mode')}
        for name,row in requirements['wheel_members'].items():
            need(name not in expected,'ORIGIN_WHEEL_COLLISION');expected[name]=row
        need(sum(row['size_bytes'] for row in expected.values())<=512*1024*1024,'ORIGIN_TOTAL_BOUND')
        selected={};file_ids=set();tokens=set();files=reader.files
        for row in selection.members:
            closed(row,('destination','file_id','binding'));relative(row['destination']);binding(row['binding'])
            name=row['destination'];file_id=row['file_id']
            need(name not in selected and name in expected and type(file_id)is str and file_id not in file_ids,'ORIGIN_DUPLICATE')
            need(file_id in files and files[file_id]['kind']=='host-dependency' and files[file_id]['binding']==row['binding'],'ORIGIN_ROLE')
            b=row['binding'];token=(b['root_id'],b['relative_path'])
            need(token not in tokens,'ORIGIN_AMBIGUOUS_ALIAS');tokens.add(token);file_ids.add(file_id)
            need((b['sha256'],b['size_bytes'])==(expected[name]['sha256'],expected[name]['size_bytes']),'ORIGIN_CONTENT')
            selected[name]=row
        need(set(selected)==set(expected),'ORIGIN_COMPLETE')
        observed={};archives={};total=0
        wheel_destinations={row['destination'] for row in requirements['inputs'] if row['kind']=='wheel'}
        with reader.boundary():
            for name,row in selected.items():
                raw=reader.read(row['file_id'],'host-dependency');total+=len(raw)
                need(sha(raw)==expected[name]['sha256'] and len(raw)==expected[name]['size_bytes'],'ORIGIN_BYTES')
                if raw.startswith(b'\x7fELF'):observed[name]=inspect_elf(raw,expected[name]['sha256'])
                if name in wheel_destinations:
                    members=wheel_inventory(raw)
                    need(not set(members)&set(archives),'ORIGIN_WHEEL_COLLISION');archives.update(members)
            need(archives==requirements['wheel_members'],'ORIGIN_ARCHIVE_MEMBERSHIP')
            need(set(observed)==set(requirements['elf_graph']),'ORIGIN_ALL_ELF_MEMBERS')
            for name,value in observed.items():
                original=requirements['elf_graph'][name]
                need(sorted(value['needed'])==original['needed'] and
                     (value['interpreter'].rsplit('/',1)[-1] if value['interpreter'] else None)==original['interpreter'],'ORIGIN_ELF_DECLARATIONS')
                libraries={needed:observed['lib/abi/'+needed] for needed in value['needed']}
                compare_abi_versions(value,libraries)
            for row in selected.values():
                raw=reader.read(row['file_id'],'host-dependency');total+=len(raw)
            need(reader.files==files,'ORIGIN_READER_SELECTION_CHANGED')
            need(canonical(selection.__dict__)==sealed_selection,'ORIGIN_SELECTION_CHANGED')
        return {'schema_version':'lab-selected-execution-origins/v1','members':len(expected),'bytes_read':total,
            'elf_members':len(observed),'wheel_members':len(archives),
            'marked_plt_members':sum('x86_64_marked_plt' in value['platform_requirements'] for value in observed.values()),
            'packed_relocation_members':sum('packed_relative_relocations' in value['platform_requirements'] for value in observed.values()),
            'selected_content_verified':True,'runtime_abi_verified':False,'actual_modes_verified':False,
            'historical_original_locators_qualified':False,'authority_effect':'none',
            'remaining':['current independent host custody/mode observations','actual loader/symbol/version/CPU behavior',
                'installed source-loading bytecode-cache policy','original proof member qualification']}
    except Exception:
        raise Refusal('EXECUTION_ORIGIN_REFUSED') from None
