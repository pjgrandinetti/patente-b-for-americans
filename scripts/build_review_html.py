#!/usr/bin/env python3
"""
build_review_html.py — build a self-contained, offline review page so a human can
sort every old DomandeB image into one of four buckets in a single pass:

  (1) best (top-1) candidate is correct
  (2) best is wrong, but candidate #2 or #3 is correct
  (3) none of the top-3 is correct, but the right figure DOES exist in the library
  (4) no correct figure exists at all (composite / scenario / not in library)

The page shows the old image beside its top-3 look-alike figures. One click marks
the verdict; for bucket (3) a searchable picker lets you choose the correct figure
from the whole library. Choices persist in the browser (localStorage) and can be
exported to review_verdicts.csv, which the apply step consumes.

Open the output directly in a browser (double-click). All images load by relative
path, so keep the file where it's written.

Reads:  scripts/sign_map.csv, sign_library/library_index.csv, public_html/questions.json
Writes: sign_svgs_staging/review.html
"""
import csv, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP  = os.path.join(ROOT, "scripts", "sign_map.csv")
IDX  = os.path.join(ROOT, "sign_library", "library_index.csv")
PUB  = os.path.join(ROOT, "public_html")
OUT  = os.path.join(ROOT, "sign_svgs_staging", "review.html")

# Relative paths FROM sign_svgs_staging/review.html to the image files.
OLD_REL = "../public_html/"          # + questions.json image field
LIB_REL = "../sign_library/"         # + <normfig>.svg

def disp(nf):
    m = re.match(r"ii(\d+)([a-z]?)", nf or "")
    return (f"II {m.group(1)}" + (f"/{m.group(2)}" if m.group(2) else "")) if m else (nf or "")

# figure-number -> family code (same ranges the matcher uses)
FAM_RANGES = [(1,35,"per"),(36,45,"pre"),(46,79,"div"),(80,99,"obb"),
              (100,381,"ind"),(382,414,"tmp"),(415,448,"ori"),(449,462,"lum"),(463,479,"cmp")]
FAM_LABELS = {"per":"Pericolo (danger)","pre":"Precedenza (right of way)",
              "div":"Divieto (prohibition)","obb":"Obbligo (mandatory)",
              "ind":"Indicazione (information)","tmp":"Temporanei / cantiere (roadworks)",
              "ori":"Segnaletica orizzontale (road markings)","lum":"Luminosi / semaforici (signals)",
              "cmp":"Complementari (complementary)","x":"Other / unclassified"}
def fam_of(nf):
    m = re.match(r"ii(\d+)", nf or ""); n = int(m.group(1)) if m else 0
    return next((c for lo,hi,c in FAM_RANGES if lo<=n<=hi), "x")

def main():
    lib = {r["normfig"]: r for r in csv.DictReader(open(IDX, encoding="utf-8"))}
    # Source the picker from the SVG files actually on disk (union with the index for
    # names), so every downloadable figure is selectable — including any present on
    # disk but absent from the index.
    LIBDIR = os.path.join(ROOT, "sign_library")
    IMG_EXT = (".svg", ".png", ".gif", ".jpg", ".jpeg")
    files = {}   # stem -> filename (svg or raster), so raster figures render too
    for fn in sorted(os.listdir(LIBDIR)):
        stem, ext = os.path.splitext(fn)
        if ext.lower() in IMG_EXT:
            files.setdefault(stem, fn)
    disk = sorted(files)
    libinfo = {nf: {"fig": lib.get(nf, {}).get("figure") or disp(nf),
                    "name": lib.get(nf, {}).get("name", "")} for nf in disk}
    famq = lambda nf: (lib.get(nf, {}).get("fam") or fam_of(nf))   # index fam wins
    picker = sorted(({"nf": nf, "fig": v["fig"], "name": v["name"], "fam": famq(nf)}
                     for nf, v in libinfo.items()),
                    key=lambda d: [int(x) if x.isdigit() else x
                                   for x in re.findall(r"\d+|\D+", d["nf"])])

    img_by_id = {str(c["id"]): c.get("image", "")
                 for c in json.load(open(os.path.join(PUB, "questions.json"), encoding="utf-8"))
                 if c.get("image")}

    # Optional: `--exclude <verdicts.csv>` drops cards already decided in a previous
    # pass, so a round-2 reviewer contains only the leftovers. A card counts as decided
    # if its 'bucket' column is non-empty.
    exclude = set()
    if "--exclude" in sys.argv:
        p = sys.argv[sys.argv.index("--exclude") + 1]
        for r in csv.DictReader(open(p, encoding="utf-8")):
            if (r.get("bucket") or "").strip():
                exclude.add(str(r["id"]))
        print(f"  excluding {len(exclude)} already-decided cards from {os.path.basename(p)}")

    cards = []
    for r in csv.DictReader(open(MAP, encoding="utf-8")):
        cid = r["id"]
        if cid in exclude:
            continue
        cands = [c for c in (r.get("candidates", "") or "").split("|") if c]
        cards.append({
            "id": cid,
            "old": OLD_REL + img_by_id.get(cid, f"domandeb_images/{cid}.jpeg"),
            "note": r.get("note", ""),
            "score": r.get("score", ""),
            "margin": r.get("margin", ""),
            "fam": famq(cands[0]) if cands else "",
            "cands": [{"nf": nf, "fig": libinfo.get(nf, {}).get("fig", disp(nf)),
                       "name": libinfo.get(nf, {}).get("name", "")} for nf in cands[:3]],
        })

    # Storage key: rounds after the first get a distinct key (via --key) so a
    # round-2 leftover file doesn't share browser state with the first pass.
    store_key = "patente_review_v1"
    if "--key" in sys.argv:
        store_key = "patente_review_" + sys.argv[sys.argv.index("--key") + 1]
    data = {"cards": cards, "picker": picker, "libRel": LIB_REL,
            "famLabels": FAM_LABELS, "files": files}
    html = HTML.replace("/*DATA*/", json.dumps(data)).replace("__STORE_KEY__", store_key)
    out = OUT
    if "--out" in sys.argv:
        out = os.path.join(os.path.dirname(OUT), sys.argv[sys.argv.index("--out") + 1])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    globals()["OUT"] = out  # so the summary print below reports the real path
    n_nocand = sum(1 for c in cards if not c["cands"])
    print(f"Wrote {OUT}\n  {len(cards)} cards ({n_nocand} with no candidates), "
          f"{len(picker)} figures in the picker.")

HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sign match review</title>
<style>
  :root{--good:#1a7f37;--bad:#cf222e;--warn:#9a6700;--line:#d0d7de;--muted:#57606a;}
  *{box-sizing:border-box}
  body{margin:0;font:15px/1.4 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#1f2328;background:#f6f8fa}
  header{position:sticky;top:0;z-index:20;background:#fff;border-bottom:1px solid var(--line);
    padding:10px 16px;display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center}
  header h1{font-size:16px;margin:0 12px 0 0}
  .counts{display:flex;gap:14px;flex-wrap:wrap;color:var(--muted);font-size:13px}
  .counts b{color:#1f2328}
  .filters,.actions{display:flex;gap:6px;align-items:center}
  button{font:inherit;cursor:pointer;border:1px solid var(--line);background:#fff;border-radius:6px;padding:5px 10px}
  button.on{background:#0969da;color:#fff;border-color:#0969da}
  .primary{background:#1f883d;color:#fff;border-color:#1f883d}
  .loadbtn{border:1px solid var(--line);background:#fff;border-radius:6px;padding:5px 10px;cursor:pointer}
  .warn{background:#fff3cd;border-bottom:1px solid #e6c200;padding:8px 16px;font-size:13px}
  .warn.hidden{display:none}
  main{padding:14px;max-width:1080px;margin:0 auto}
  .card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px;margin:0 0 12px;
    display:grid;grid-template-columns:200px 1fr;gap:14px;align-items:start}
  .card.decided{border-color:#b6e3c0}
  .card.b1{background:#f2fbf4}.card.b23{background:#fff8e8}.card.b3{background:#fff1f0}.card.b4{background:#f6f8fa}
  .old{text-align:center}
  .old img{max-width:180px;max-height:150px;background:#fff;border:1px solid var(--line);border-radius:6px}
  .old .id{font-weight:700;margin-top:6px}
  .old .meta{font-size:12px;color:var(--muted)}
  .right{display:flex;flex-direction:column;gap:10px}
  .cands{display:flex;gap:10px;flex-wrap:wrap}
  .cand{border:2px solid var(--line);border-radius:8px;padding:8px;width:150px;text-align:center;cursor:pointer;background:#fff}
  .cand:hover{border-color:#0969da}
  .cand.sel{border-color:var(--good);box-shadow:0 0 0 2px #1a7f3733}
  .cand img{width:120px;height:110px;object-fit:contain;background:#fff}
  .cand .lab{font-size:12px;margin-top:4px}
  .cand .lab b{display:block}
  .cand .k{position:absolute;font-size:11px;color:var(--muted)}
  .verdict{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
  .verdict .tag{font-size:12px;color:var(--muted);margin-right:2px}
  .pick{border:1px dashed var(--line);border-radius:8px;padding:8px;background:#fbfcfd}
  .pick.hidden{display:none}
  .pickbar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:6px}
  .pick input{width:260px;padding:6px 8px;border:1px solid var(--line);border-radius:6px;font:inherit}
  .famsel{padding:6px 8px;border:1px solid var(--line);border-radius:6px;font:inherit;background:#fff;max-width:300px}
  .pickcount{white-space:nowrap}
  .picked{display:inline-flex;align-items:center;gap:8px;margin-left:8px}
  .picked img{width:44px;height:44px;object-fit:contain;border:1px solid var(--line);border-radius:4px;background:#fff}
  .results{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;max-height:230px;overflow:auto}
  .res{width:96px;text-align:center;cursor:pointer;border:1px solid var(--line);border-radius:6px;padding:4px;background:#fff}
  .res:hover{border-color:#0969da}
  .res img{width:80px;height:72px;object-fit:contain}
  .res .l{font-size:11px}
  .chosen-badge{font-size:12px;color:var(--good);font-weight:600}
  .none-badge{font-size:12px;color:var(--bad);font-weight:600}
  .hint{color:var(--muted);font-size:12px}
  @media(max-width:640px){.card{grid-template-columns:1fr}}
</style></head><body>
<header>
  <h1>Sign match review</h1>
  <div class="counts" id="counts"></div>
  <div class="filters">
    <span class="hint">Show:</span>
    <button data-f="all" class="on">All</button>
    <button data-f="undecided">Undecided</button>
    <button data-f="flagged">Flagged</button>
    <button data-f="b3">Bucket&nbsp;3</button>
    <button data-f="b4">Bucket&nbsp;4</button>
  </div>
  <div class="actions">
    <button id="export" class="primary">Export CSV</button>
    <button id="save">Save progress</button>
    <label class="loadbtn">Load progress<input type="file" id="load" accept=".json" hidden></label>
    <button id="reset">Reset all</button>
  </div>
</header>
<div id="warn" class="warn hidden">⚠ This browser is blocking storage for local files, so progress won't
  auto-save. Use <b>Save progress</b> often (and <b>Load progress</b> to resume), or open this file in Chrome.</div>
<main id="list"></main>
<script>
const DATA = /*DATA*/;
const LIB = DATA.libRel;
const FILES = DATA.files || {};
const imgSrc = nf => LIB + (FILES[nf] || (nf + ".svg"));   // raster figures too
const KEY = "__STORE_KEY__";
// Detect whether localStorage actually works (Safari blocks it for file:// pages).
let LS_OK = true;
try { localStorage.setItem("_t","1"); localStorage.removeItem("_t"); } catch(e){ LS_OK = false; }
let verdicts = {};
if (LS_OK) { try { verdicts = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch(e){ verdicts = {}; } }
let filter = "all";

const flagged = c => {
  const s = parseFloat(c.score), m = parseFloat(c.margin);
  return c.cands.length && ((isFinite(s) && s < 0.55) || (isFinite(m) && m < 0.05));
};
// bucket codes: "1" best ok | "2"/"3" other top3 | "other" picked from library | "none"
const bucketOf = id => (verdicts[id] || {}).v || "";
function save(){ if (LS_OK){ try{ localStorage.setItem(KEY, JSON.stringify(verdicts)); }catch(e){} } render(); }

function setVerdict(id, v, figNf, fig){
  if (v === null){ delete verdicts[id]; }
  else verdicts[id] = {v, nf: figNf||"", fig: fig||""};
  save();
}

function counts(){
  let b1=0,b23=0,b3=0,b4=0,dec=0;
  for (const c of DATA.cards){
    const v = bucketOf(c.id);
    if (!v) continue; dec++;
    if (v==="1") b1++; else if (v==="2"||v==="3") b23++;
    else if (v==="other") b3++; else if (v==="none") b4++;
  }
  return {b1,b23,b3,b4,dec,tot:DATA.cards.length};
}

function passesFilter(c){
  const v = bucketOf(c.id);
  if (filter==="all") return true;
  if (filter==="undecided") return !v;
  if (filter==="flagged") return flagged(c) && !v;
  if (filter==="b3") return v==="other";
  if (filter==="b4") return v==="none";
  return true;
}

function candCard(c, cand, i){
  const v = verdicts[c.id];
  const sel = v && (v.v===String(i+1)) ? " sel" : "";
  return `<div class="cand${sel}" data-id="${c.id}" data-i="${i}" data-nf="${cand.nf}" data-fig="${cand.fig}">
    <img loading="lazy" src="${imgSrc(cand.nf)}" alt="${cand.fig}">
    <div class="lab"><b>${cand.fig}${i===0?" ·best":""}</b>${cand.name||""}</div></div>`;
}

function cardHTML(c){
  const v = bucketOf(c.id);
  const cls = v==="1"?"b1":(v==="2"||v==="3")?"b23":v==="other"?"b3":v==="none"?"b4":"";
  const vv = verdicts[c.id];
  const cands = c.cands.length
    ? c.cands.map((cd,i)=>candCard(c,cd,i)).join("")
    : `<div class="hint">No candidates were generated for this card (likely a composite A-vs-B image or a scenario diagram).</div>`;
  let chosen = "";
  if (vv && vv.v==="other" && vv.nf)
    chosen = `<span class="picked chosen-badge">Chosen: ${vv.fig}
      <img src="${imgSrc(vv.nf)}"></span>`;
  if (vv && vv.v==="none") chosen = `<span class="none-badge">Marked: no correct figure</span>`;
  return `<div class="card ${cls} ${v?"decided":""}" id="card-${c.id}">
    <div class="old">
      <img loading="lazy" src="${c.old}" alt="#${c.id}">
      <div class="id">#${c.id}</div>
      <div class="meta">score ${c.score} · gap ${c.margin}</div>
    </div>
    <div class="right">
      <div class="cands">${cands}</div>
      <div class="verdict">
        <span class="tag">Verdict:</span>
        <button data-act="none" data-id="${c.id}">No match (bucket 4)</button>
        <button data-act="other" data-id="${c.id}">Right one isn't shown → pick… (bucket 3)</button>
        <button data-act="clear" data-id="${c.id}">Clear</button>
        ${chosen}
      </div>
      <div class="pick hidden" id="pick-${c.id}">
        <div class="pickbar">
          <select class="famsel" data-id="${c.id}"></select>
          <input type="text" placeholder="…or filter by figure/name (e.g. II 62, sosta)" data-id="${c.id}">
          <span class="hint pickcount"></span>
        </div>
        <div class="results"></div>
      </div>
    </div></div>`;
}

function render(){
  const cs = counts();
  document.getElementById("counts").innerHTML =
    `<span><b>${cs.dec}</b>/${cs.tot} decided</span>
     <span>① best ok: <b>${cs.b1}</b></span>
     <span>②③ top-3 fix: <b>${cs.b23}</b></span>
     <span>③ picked other: <b>${cs.b3}</b></span>
     <span>④ no match: <b>${cs.b4}</b></span>`;
  const list = DATA.cards.filter(passesFilter);
  document.getElementById("list").innerHTML =
    list.map(cardHTML).join("") || `<p class="hint">Nothing matches this filter.</p>`;
}

// Populate the family <select> (defaulting to the card's own family) and render the
// grid, so EVERY downloaded figure in that family is visible — including ones that
// never appear in any card's top-3. "All families" browses the whole library.
function openPick(id){
  const card = DATA.cards.find(c=>c.id===id);
  const sel = document.querySelector(`#pick-${id} .famsel`);
  if (sel && !sel.dataset.built){
    const fams = Object.keys(DATA.famLabels).filter(f=>DATA.picker.some(p=>p.fam===f));
    sel.innerHTML = `<option value="">All families (${DATA.picker.length})</option>` +
      fams.map(f=>{const n=DATA.picker.filter(p=>p.fam===f).length;
        return `<option value="${f}">${DATA.famLabels[f]} — ${n}</option>`;}).join("");
    sel.value = (card && card.fam) ? card.fam : "";
    sel.dataset.built = "1";
  }
  runPick(id);
}
function runPick(id){
  const wrap = document.getElementById("pick-"+id);
  const fam = wrap.querySelector(".famsel").value;
  const q = wrap.querySelector("input").value.trim().toLowerCase();
  let hits = DATA.picker;
  if (fam) hits = hits.filter(p=>p.fam===fam);
  if (q)   hits = hits.filter(p=>(p.fig+" "+p.name+" "+p.nf).toLowerCase().includes(q));
  wrap.querySelector(".pickcount").textContent = `${hits.length} figure${hits.length===1?"":"s"}`;
  wrap.querySelector(".results").innerHTML = hits.slice(0,400).map(p =>
    `<div class="res" data-id="${id}" data-nf="${p.nf}" data-fig="${p.fig}">
       <img loading="lazy" src="${imgSrc(p.nf)}"><div class="l"><b>${p.fig}</b><br>${p.name||""}</div></div>`).join("")
    || `<span class="hint">No figures match. Try "All families" or a different term.</span>`;
}

document.addEventListener("click", e=>{
  const cand = e.target.closest(".cand");
  if (cand){ setVerdict(cand.dataset.id, String(+cand.dataset.i+1), cand.dataset.nf, cand.dataset.fig); return; }
  const res = e.target.closest(".res");
  if (res){ setVerdict(res.dataset.id, "other", res.dataset.nf, res.dataset.fig); return; }
  const b = e.target.closest("button[data-act]");
  if (b){
    const id = b.dataset.id, act = b.dataset.act;
    if (act==="none")  setVerdict(id, "none");
    if (act==="clear") setVerdict(id, null);
    if (act==="other"){
      const p=document.getElementById("pick-"+id);
      if(p){ p.classList.toggle("hidden");
             if(!p.classList.contains("hidden")) openPick(id); }
    }
    return;
  }
  const f = e.target.closest("header button[data-f]");
  if (f){ filter=f.dataset.f; document.querySelectorAll("header [data-f]").forEach(x=>x.classList.toggle("on",x===f)); render(); }
});
document.addEventListener("input", e=>{
  if (e.target.matches(".pick input")) runPick(e.target.dataset.id);
});
document.addEventListener("change", e=>{
  if (e.target.matches(".famsel")) runPick(e.target.dataset.id);
});
document.getElementById("reset").onclick = ()=>{ if(confirm("Clear ALL verdicts?")){ verdicts={}; save(); } };
// Save/Load progress as a JSON file — works even when localStorage is blocked.
document.getElementById("save").onclick = ()=>{
  const a=document.createElement("a");
  a.href=URL.createObjectURL(new Blob([JSON.stringify(verdicts)],{type:"application/json"}));
  a.download="review_progress.json"; a.click();
};
document.getElementById("load").onchange = (e)=>{
  const f=e.target.files[0]; if(!f) return;
  const r=new FileReader();
  r.onload=()=>{ try{ const o=JSON.parse(r.result);
      Object.assign(verdicts, o); save();
      alert("Loaded "+Object.keys(o).length+" saved verdicts."); }
    catch(err){ alert("Could not read that progress file."); } };
  r.readAsText(f);
};
if (!LS_OK) document.getElementById("warn").classList.remove("hidden");
document.getElementById("export").onclick = ()=>{
  const rows = [["id","bucket","verdict","chosen_figure","chosen_normfig","best_figure","best_normfig"]];
  for (const c of DATA.cards){
    const v = verdicts[c.id]; const best = c.cands[0]||{};
    let bucket="", cf="", cnf="";
    if (v){
      if (v.v==="1"){ bucket="1_best_ok"; cf=best.fig||""; cnf=best.nf||""; }
      else if (v.v==="2"||v.v==="3"){ const cd=c.cands[+v.v-1]||{}; bucket="2_top3_fix"; cf=cd.fig; cnf=cd.nf; }
      else if (v.v==="other"){ bucket="3_picked_other"; cf=v.fig; cnf=v.nf; }
      else if (v.v==="none"){ bucket="4_no_match"; }
    }
    rows.push([c.id, bucket, v?v.v:"", cf, cnf, best.fig||"", best.nf||""]);
  }
  const csv = rows.map(r=>r.map(x=>`"${String(x).replace(/"/g,'""')}"`).join(",")).join("\n");
  const a=document.createElement("a");
  a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv"}));
  a.download="review_verdicts.csv"; a.click();
};
render();
</script></body></html>
"""

if __name__ == "__main__":
    main()
