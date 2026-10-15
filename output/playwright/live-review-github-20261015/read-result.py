import pathlib,json,sys
for arg in sys.argv[1:]:
 p=pathlib.Path(arg);s=p.read_text()
 if '### Result\n' not in s: print(s[:2000]);raise SystemExit(1)
 data=json.JSONDecoder().raw_decode(s.split('### Result\n',1)[1])[0]
 while isinstance(data,str):data=json.loads(data)
 dest=p.with_name(p.name.replace('.raw.txt','.json'))
 dest.write_text(json.dumps(data,indent=2)+'\n')
 print(dest.name,json.dumps(data.get('summary',{})))
