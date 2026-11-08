/* Offline lexical ranking. Evaluation questions never create index aliases. */
(() => {
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[?]/g,'').trim();
  const stop=new Set('a an and are as at be been but by can could did do does enough for from had has have how i in is it its judge know lets me of on or our should the their them there these they this those to was way we were what when where whether which who why will with would you your versus vs'.split(' '));
  const equivalents={approval:'approve',approves:'approve',approved:'approve',approving:'approve',accepted:'accept',admitted:'admit',admission:'admit',permissions:'permission',authorisation:'authorization',ends:'end',ended:'end',ending:'end',stops:'stop',stopped:'stop',stopping:'stop',definitions:'definition',defining:'definition',defined:'definition',define:'definition',calculation:'calculate',calculations:'calculate',calculated:'calculate',calculating:'calculate',governance:'govern',governing:'govern',governed:'govern'};
  const stemCache=new Map();
  const own=(table,key)=>Object.prototype.hasOwnProperty.call(table,key)?table[key]:undefined;
  const stem=word=>{
    if(stemCache.has(word))return stemCache.get(word);
    const original=word;
    word=own({proof:'prove',proves:'prove',proven:'prove',proving:'prove',compiling:'compile',compiled:'compile',compilation:'compile'},word)||own(equivalents,word)||word;
    if(word.length>6&&word.endsWith('ies'))word=word.slice(0,-3)+'y';
    else if(word.length>6&&word.endsWith('ing'))word=word.slice(0,-3);
    else if(word.length>5&&word.endsWith('ed'))word=word.slice(0,-2);
    else if(word.length>5&&word.endsWith('es'))word=word.slice(0,-2);
    else if(word.length>4&&word.endsWith('s')&&!word.endsWith('ss')&&!word.endsWith('us'))word=word.slice(0,-1);
    // Bound memory for repeated queries with arbitrary user text.
    if(stemCache.size>50000)stemCache.clear();
    stemCache.set(original,word);return word;
  };
  const terms=value=>(normalize(value).replace(/\b(?:doesn't|don't|isn't|aren't|can't|won't|shouldn't|wouldn't|couldn't)\b/g,' ').replace(/['’]s\b/g,'').match(/[a-z0-9]+(?:\/[0-9]+)?/g)||[]).filter(word=>!stop.has(word)).map(stem);
  const oneEdit=(a,b)=>{
    if(Math.abs(a.length-b.length)>1)return false;
    let i=0,j=0,edits=0;
    while(i<a.length&&j<b.length){if(a[i]===b[j]){i++;j++;continue;}if(++edits>1)return false;if(a.length>=b.length)i++;if(b.length>=a.length)j++;}
    return edits+a.length-i+b.length-j<=1;
  };
  const statistics=value=>value?.version==='lab-lexical/v1'?{
    version:value.version,df:value.df instanceof Map?value.df:new Map(value.df),
    lexicon:value.lexicon instanceof Map?value.lexicon:new Map(value.lexicon),average:value.average
  }:null;
  const prepare=(entries,compiled)=>{
    const fixed=statistics(compiled);
    const df=new Map(),lexicon=new Map();let total=0;
    const index=entries.map(entry=>{
      if(entry.prepared?.version==='lab-lexical/v1'){
        const f=entry.prepared,titleTerms=new Set(f.title),aliasTerms=new Set(f.aliases),bodyTerms=new Map(f.body);
        total+=f.length;
        if(!fixed){
          const words=f.lexicon||[...new Set(normalize(entry.title+' '+(entry.aliases||[]).join(' ')+' '+entry.text).match(/[a-z0-9]+/g)||[])].filter(word=>!stop.has(word)).map(word=>[word,stem(word)]);
          for(const [word,stem] of words)lexicon.set(word,stem);
          for(const term of new Set([...titleTerms,...aliasTerms,...bodyTerms.keys()]))df.set(term,(df.get(term)||0)+1);
        }
        return {...entry,titleKey:normalize(entry.title),textKey:normalize(entry.text),aliasesKeys:(entry.aliases||[]).map(normalize),aliasesTopics:f.topics,titleTerms,aliasTerms,bodyTerms,length:f.length};
      }
      const titleTerms=new Set(terms(entry.title)),aliasTerms=new Set(terms((entry.aliases||[]).join(' '))),bodyWords=terms(entry.text),bodyTerms=new Map();total+=bodyWords.length;
      for(const word of (normalize(entry.title+' '+(entry.aliases||[]).join(' ')+' '+entry.text).match(/[a-z0-9]+/g)||[]))if(!stop.has(word))lexicon.set(word,stem(word));
      for(const word of bodyWords)bodyTerms.set(word,(bodyTerms.get(word)||0)+1);
      for(const term of new Set([...titleTerms,...aliasTerms,...bodyTerms.keys()]))df.set(term,(df.get(term)||0)+1);
      return {...entry,titleKey:normalize(entry.title),textKey:normalize(entry.text),aliasesKeys:(entry.aliases||[]).map(normalize),aliasesTopics:(entry.aliases||[]).map(alias=>terms(alias).join(' ')),titleTerms,aliasTerms,bodyTerms,length:bodyWords.length};
    });index.stats=fixed||{df,lexicon,average:total/Math.max(1,index.length)};return index;
  };
  function search(index,value){
    const query=normalize(value),words=[...new Set(terms(value))];
    if(/^who\b.*\bfor\b/.test(query))words.push('audience');
    if(!words.length)return [];
    const {df,lexicon,average}=index.stats;
    // Correct an absent word by one character. Literal corpus words stay literal.
    const variants=words.map(word=>df.has(word)?[word]:word.length>=5?[...new Set([...lexicon.keys()].filter(other=>oneEdit(word,other)).map(other=>lexicon.get(other)))]:[]).filter(options=>options.length);
    // A single familiar word must not turn an unrelated multi-word request
    // into a confident result list. Allow a small amount of unmatched context.
    if(!variants.length||variants.length<Math.ceil(words.length*.75))return [];
    const correctedTopic=variants.every(options=>options.length===1)?variants.map(options=>options[0]).join(' '):words.join(' ');
    const isQuestion=/\?|^(what|why|how|who|where|when|does|can|is|are|should)\b/.test(query),results=[];
    for(const item of index){
      let matched=0,score=0,titleMatches=0;
      for(const options of variants){
        let best=0,title=false;
        for(const word of options){
          const count=item.bodyTerms.get(word)||0,inTitle=item.titleTerms.has(word),inAlias=item.aliasTerms.has(word);
          if(!count&&!inTitle&&!inAlias)continue;
          const idf=Math.log(1+(index.length-(df.get(word)||0)+.5)/((df.get(word)||0)+.5));
          const body=count*2.2/(count+1.2*(.35+.65*item.length/Math.max(1,average)));
          const contribution=idf*(body+(inTitle?9:0)+(inAlias?11:0));
          if(contribution>best){best=contribution;title=inTitle;}
        }if(best){matched++;score+=best;if(title)titleMatches++;}
      }
      if(matched<Math.max(1,Math.ceil(variants.length*.75)))continue;
      score+=matched/variants.length*20+titleMatches*5;
      if(item.titleKey===query)score+=2000;else if(item.titleKey.includes(query))score+=100;
      if(item.aliasesKeys.includes(query))score+=300;
      if(item.aliasesTopics.includes(correctedTopic))score+=300;
      if(item.textKey.includes(query))score+=15;
      if(item.titleKey===query&&item.href.includes('#def-'))score+=150;
      if(isQuestion&&item.group!=='Reference records')score+=20;
      results.push({...item,score,matchedTerms:matched});
    }return results.sort((a,b)=>b.score-a.score||a.title.localeCompare(b.title));
  }
  // Keep complete-corpus preparation interruptible on slower phones. Each
  // chunk uses the same rank inputs; only its scheduling changes.
  async function prepareAsync(entries,compiled) {
    const fixed=statistics(compiled);
    const result=[],df=new Map(),lexicon=new Map();let total=0;
    for(let offset=0;offset<entries.length;offset+=32){
      const chunk=prepare(entries.slice(offset,offset+32),fixed);
      for(const item of chunk){result.push(item);total+=item.length;}
      if(!fixed){
        for(const [word,count] of chunk.stats.df)df.set(word,(df.get(word)||0)+count);
        for(const [word,stem] of chunk.stats.lexicon)lexicon.set(word,stem);
      }
      if(offset+32<entries.length){if(globalThis.scheduler?.yield)await scheduler.yield();else await new Promise(resolve=>setTimeout(resolve,0));}
    }
    result.stats=fixed||{df,lexicon,average:total/Math.max(1,result.length)};return result;
  }
  globalThis.LabSearchEngine={normalize,prepare,prepareAsync,search};
})();
