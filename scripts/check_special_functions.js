// The statistics behind the readiness estimate rest on three special functions written for this
// project from the published formulas (Lanczos g = 7 for log-gamma, DLMF 8.17.22 and 8.9.2 for the
// incomplete beta and gamma, evaluated by forward recurrence). This compares them with reference
// values computed by mpmath at 30 digits (scripts/special_functions_ref.json) and with scipy's
// t and chi-square figures quoted in the other checks. Run: node scripts/check_special_functions.js
const fs=require('fs'), vm=require('vm'); const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const src=fs.readFileSync(root+'/app.js','utf8');
const grab=name=>{const i=src.indexOf('function '+name+'('); let d=0,j=src.indexOf('{',i); for(let k=j;k<src.length;k++){ if(src[k]==='{')d++; else if(src[k]==='}'){d--; if(!d) return src.slice(i,k+1);} } };
const ctx={Math}; vm.createContext(ctx);
for (const n of ['logGamma','betaContinuedFraction','betaInc','gammaP','chiSquareQuantile','studentT','tQuantile']) vm.runInContext(grab(n),ctx);
const ref=JSON.parse(fs.readFileSync(__dirname+'/special_functions_ref.json','utf8'));
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
let worst=0;
for (const r of ref){ let v; if(r[0]==='beta') v=ctx.betaInc(r[1],r[2],r[3]); else if(r[0]==='gamma') v=ctx.gammaP(r[1],r[2]); else v=ctx.logGamma(r[1]); worst=Math.max(worst,Math.abs(v-r[4])); }
ok(worst<1e-12,'every reference value within 1e-12 (worst '+worst.toExponential(2)+') over '+ref.length+' points');
ok(Math.abs(ctx.studentT(2.0,14)-0.967356023555444)<1e-12 && Math.abs(ctx.studentT(-1.5,3)-0.11529193262241151)<1e-12,'Student t cdf matches mpmath at two points to 1e-12');
ok(Math.abs(ctx.tQuantile(0.95,14)-1.7613101)<1e-6,'t quantile 0.95 on 14 df is 1.7613');
ok(Math.abs(ctx.chiSquareQuantile(0.95,10)-18.307038053275143)<1e-6,'chi-square quantile 0.95 on 10 df is 18.307');
console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
