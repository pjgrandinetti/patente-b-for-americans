// The host's bot-check splash ("Please wait while your request is being
// verified", Imunify360, 200 OK text/html in place of the file asked for)
// must never be served as the app or cached as it (20261102u). Run:
// node scripts/check_sw_splash.js (SRC= another public_html to see it fail).
const fs=require('fs'), vm=require('vm');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const src=fs.readFileSync(root+'/sw.js','utf8');
const index=fs.readFileSync(root+'/index.html','utf8');
ok(index.includes('name="apple-mobile-web-app-title"'),'index.html carries the home-screen title meta tag the worker looks for');
const SPLASH='<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Please wait</title></head><body><p>Please wait while your request is being verified...</p><script>setTimeout(function(){location.reload()},3000)</script></body></html>';
const ORIGIN='https://patente.physyapps.com';
const stores={};
class FakeCache{constructor(n){this.n=n;stores[n]=stores[n]||new Map();}
  key(r){return new URL(typeof r==='string'?r:r.url,ORIGIN+'/').href;}
  async match(r){return stores[this.n].get(this.key(r))||undefined;}
  async put(r,resp){stores[this.n].set(this.key(r),resp);}
  async delete(r){return stores[this.n].delete(this.key(r));}
  async keys(){return [...stores[this.n].keys()].map(u=>({url:u}));}}
const caches={open:async n=>new FakeCache(n),keys:async()=>Object.keys(stores),delete:async n=>delete stores[n],
  match:async r=>{const k=new URL(typeof r==='string'?r:r.url,ORIGIN+'/').href;for(const n in stores){const v=stores[n].get(k);if(v)return v;}}};
const listeners={};
const mkResp=(url,body,ct)=>({ok:true,status:200,url,tag:body.slice(0,40),headers:{get:h=>h==='content-length'?String(body.length):h==='content-type'?ct:null},clone(){return mkResp(url,body,ct);},json:async()=>JSON.parse(body),text:async()=>body});
let serve={}; // path -> [body, content-type]
const fetch=async(req)=>{const url=typeof req==='string'?req:req.url; const path=new URL(url,ORIGIN+'/').pathname; const s=serve[path]||serve['*']; return mkResp(url,s[0],s[1]);};
class Request{constructor(u,o){this.url=u;}}
const self={addEventListener:(k,f)=>{(listeners[k]=listeners[k]||[]).push(f);},clients:{claim(){}},skipWaiting(){},location:{origin:ORIGIN,pathname:'/sw.js'},registration:{scope:ORIGIN+'/'}};
vm.runInNewContext(src,{self,caches,fetch,Request,Response:class{},URL,console,setTimeout,location:self.location});
const CV=src.match(/^const CACHE_VERSION = '([^']+)'/m)[1];
const nav=async(path,mode)=>{let out;for(const f of listeners.fetch)await f({request:{url:ORIGIN+path,method:'GET',mode:mode||'no-cors'},respondWith:p=>{out=p;}});return out;};
const run=async ev=>{let p=[];for(const f of listeners[ev])await f({waitUntil:x=>p.push(x)});await Promise.all(p);};
(async()=>{
  const good={'/':[index,'text/html'],'/index.html':[index,'text/html'],'/app.js':['// app','application/javascript'],'/style.css':['body{}','text/css'],'*':['{}','application/json']};
  // 1. a clean navigation is served and cached
  serve=good; let r=await nav('/','navigate');
  ok(r&&r.tag===index.slice(0,40),'a good shell is served to the page');
  await new Promise(res=>setTimeout(res,10));
  const shell=()=>stores[CV]&&stores[CV].get(ORIGIN+'/');
  ok(shell()&&shell().tag===index.slice(0,40),'and cached as the shell');
  r=await nav('/app.js'); await new Promise(res=>setTimeout(res,10));
  ok(stores[CV].get(ORIGIN+'/app.js').tag.startsWith('// app'),'app.js is cached');
  // 2. the splash arrives for the shell
  serve={...good,'/':[SPLASH,'text/html'],'/app.js':[SPLASH,'text/html']};
  r=await nav('/','navigate'); await new Promise(res=>setTimeout(res,10));
  ok(r&&r.tag===index.slice(0,40),'a splash for the shell is answered with the cached shell');
  ok(shell().tag===index.slice(0,40),'and the cached shell is untouched');
  r=await nav('/app.js'); await new Promise(res=>setTimeout(res,10));
  ok(r&&r.tag.startsWith('// app'),'app.js answered as text/html is served from the cache');
  ok(stores[CV].get(ORIGIN+'/app.js').tag.startsWith('// app'),'and the cached app.js is untouched');
  // 3. nothing cached: the splash is handed on (the host must clear it), still not cached
  delete stores[CV]; r=await nav('/','navigate'); await new Promise(res=>setTimeout(res,10));
  ok(r&&r.tag===SPLASH.slice(0,40),'with nothing cached the splash is handed to the page');
  ok(!shell(),'but not cached');
  // 4. an install that meets the splash caches no shell; a clean install does
  await run('install');
  ok(!shell(),'install does not cache a splash as the shell');
  serve=good; await run('install');
  ok(shell()&&shell().tag===index.slice(0,40),'a clean install caches the shell');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
})().catch(e=>{console.error(e);process.exit(1);});
