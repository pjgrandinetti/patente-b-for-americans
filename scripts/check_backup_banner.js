// The backup banner's buttons open Settings AT the block they name (20261013a,
// maintainer, 2026-10-14: they opened it at the top, and since the groups by
// stage the sync and backup blocks sit near the bottom). jsdom lays nothing
// out, so the scroll itself cannot be measured here; what is asserted is the
// target openSettingsAt chose, which is the element it flashes.
// Run: node scripts/check_backup_banner.js (UILANG=it-IT; SRC= another public_html).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US';
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  for(let i=0;i<60&&!w.eval('questions.length');i++) await wait(100);
  const $=id=>w.document.getElementById(id);
  const flashed=()=>[...w.document.querySelectorAll('.settings-flash')].map(e=>e.id);
  // The file-backup variant.
  $('btn-export-banner').click(); await wait(100);
  ok(!$('settings-overlay').classList.contains('hidden'),'Back up now opens Settings');
  ok(flashed().includes('settings-backup'),'and lands on the Backup block: '+flashed().join(','));
  w.closeSettings();
  // The synced variant.
  $('btn-code-banner').click(); await wait(100);
  ok(!$('settings-overlay').classList.contains('hidden'),'View my sync code opens Settings');
  ok(flashed().includes('settings-sync'),'and lands on the Sync block: '+flashed().join(','));
  ok($('backup-banner').classList.contains('hidden') && !!w.localStorage.getItem('patente_code_ack'),'the synced banner is acknowledged and hidden');
  // A checkbox row still works as before.
  w.closeSettings(); w.openSettingsAt('set-sound'); await wait(100);
  ok(flashed().some(id=>$(id)?.querySelector?.('#set-sound')||$(id)?.classList.contains('settings-row'))||!!w.document.querySelector('.settings-row.settings-flash #set-sound'),'a checkbox row is still found');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
})();
