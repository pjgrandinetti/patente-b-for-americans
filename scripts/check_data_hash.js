// The data URLs carry each file's content hash, and the worker's install
// skips a file already cached under that hash. Run: node scripts/check_data_hash.js
// (SRC= another public_html). It runs sw.js in a fake worker with a fake Cache
// API, then simulates a page load followed by an install.
const fs=require('fs'), vm=require('vm');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const src=fs.readFileSync(root+'/sw.js','utf8'), app=fs.readFileSync(root+'/app.js','utf8');
const hApp=app.match(/^const DATA_HASH = (\{.*\});$/m)[1], hSw=src.match(/^const DATA_HASH = (\{.*\});$/m)[1];
ok(hApp===hSw,'app.js and sw.js carry the same DATA_HASH');
ok(!/cache: 'reload'/.test(src.split('NETWORK_FIRST.test(url.pathname)')[1].split('.then')[0]),'network-first fetches with no-cache, not reload');
// --- fake worker environment
const stores={}; const fetches=[];
class FakeCache{constructor(n){this.n=n;stores[n]=stores[n]||new Map();}
  key(r){return new URL(typeof r==='string'?r:r.url,'https://patente.physyapps.com/').href;}
  async match(r){return stores[this.n].get(this.key(r))||undefined;}
  async put(r,resp){stores[this.n].set(this.key(r),resp);}
  async delete(r){return stores[this.n].delete(this.key(r));}
  async keys(){return [...stores[this.n].keys()].map(u=>({url:u}));}}
const caches={open:async n=>new FakeCache(n),keys:async()=>Object.keys(stores),delete:async n=>delete stores[n],match:async r=>{for(const n in stores){const v=stores[n].get(typeof r==='string'?r:r.url);if(v)return v;}}};
const listeners={};
const mkResp=(url,body)=>({ok:true,status:200,url,headers:{get:h=>h==='content-length'?String(body.length):null},clone(){return mkResp(url,body);},json:async()=>JSON.parse(body),text:async()=>body});
const files={};
for(const f of ['questions.json','vocabulary.json','topic_reviews.json']) files[f]=fs.readFileSync(root+'/'+f,'utf8');
const fetch=async(req,opts)=>{const url=typeof req==='string'?req:req.url; fetches.push({url,opts:opts||req.cacheOpt});
  const path=new URL(url,'https://patente.physyapps.com/').pathname.replace(/^.*\//,''); return mkResp(url, files[path]!==undefined?files[path]:'{}');};
class Request{constructor(u,o){this.url=u;this.cacheOpt=o&&o.cache;}}
const self={addEventListener:(k,f)=>{(listeners[k]=listeners[k]||[]).push(f);},clients:{claim(){}},skipWaiting(){},location:{origin:'https://patente.physyapps.com',pathname:'/sw.js'},registration:{scope:'https://patente.physyapps.com/'}};
vm.runInNewContext(src,{self,caches,fetch,Request,Response:class{},URL,console,setTimeout,location:self.location});
const run=async ev=>{let p=[];for(const f of listeners[ev])await f({waitUntil:x=>p.push(x)});await Promise.all(p);};
(async()=>{
  const H=JSON.parse(hApp.replace(/'/g,'"'));
  // 1. page load, old worker: the fetch handler stores questions.json under its hash
  const dataReq={url:'https://patente.physyapps.com/questions.json?v='+H['questions.json'],method:'GET',mode:'cors'};
  let out; for(const f of listeners.fetch) await f({request:dataReq,respondWith:p=>{out=p;}}); await out;
  ok(stores['patente-data-v1']&&stores['patente-data-v1'].has(dataReq.url),'the fetch handler caches a data file under its hash');
  const n0=fetches.length;
  // 2. install: questions.json is already there and must not be fetched again
  await run('install');
  const dataFetches=fetches.slice(n0).filter(f=>/\.json\?v=/.test(f.url));
  ok(!dataFetches.some(f=>/questions\.json/.test(f.url)),'install does not refetch a data file already cached under its hash');
  ok(dataFetches.filter(f=>/vocabulary|topic_reviews/.test(f.url)).length===2,'install fetches the two files not yet cached, once each: '+dataFetches.map(f=>f.url.replace(/.*\//,'')).join(', '));
  ok(dataFetches.every(f=>f.opts==='no-cache'),'data files are fetched with no-cache');
  const shellFetches=fetches.slice(n0).filter(f=>/app\.js|style\.css/.test(f.url));
  ok(shellFetches.length>0&&shellFetches.every(f=>f.opts==='no-cache'),'shell assets are fetched with no-cache, so an unchanged file returns 304');
  // 3. activate: a stale entry of a file whose current copy is present is pruned; one without is kept
  const dc=stores['patente-data-v1'];
  dc.set('https://patente.physyapps.com/questions.json?v=oldhash',mkResp('x','{}'));
  dc.delete('https://patente.physyapps.com/vocabulary.json?v='+H['vocabulary.json']);
  dc.set('https://patente.physyapps.com/vocabulary.json?v=oldhash',mkResp('x','{}'));
  await run('activate');
  ok(!dc.has('https://patente.physyapps.com/questions.json?v=oldhash'),'activate prunes the stale copy once the current one is cached');
  ok(dc.has('https://patente.physyapps.com/vocabulary.json?v=oldhash'),'activate keeps a stale copy when it is the only one');
  // 4. a second install with everything cached fetches no data at all
  dc.set('https://patente.physyapps.com/vocabulary.json?v='+H['vocabulary.json'],mkResp('x','{}'));
  const n1=fetches.length; await run('install');
  const late=fetches.slice(n1).filter(f=>/\.json\?v=/.test(f.url));
  ok(late.length===0,'a release with unchanged data downloads no data file'+(late.length?': '+late.map(f=>f.url).join(', '):''));
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
})().catch(e=>{console.error(e);process.exit(1);});
