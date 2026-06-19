"""
build_html.py
-------------
Lê data/df_batters.csv e data/df_pitchers.csv e gera docs/index.html

Uso:
    python scripts/build_html.py
"""

import json
import pandas as pd
from pathlib import Path

# ── Caminhos ───────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "data"
DOCS_DIR = Path(__file__).parent.parent / "docs"


def load_data():
    db = pd.read_csv(DATA_DIR / "df_batters.csv",  low_memory=False)
    dp = pd.read_csv(DATA_DIR / "df_pitchers.csv", low_memory=False)
    db["RBI"]        = db["RBI"].fillna(0).astype(int)
    dp["total_outs"] = dp["total_outs"].fillna(0).astype(int)
    return db, dp


def build_html(db: pd.DataFrame, dp: pd.DataFrame) -> str:
    teams = sorted(set(
        db["batting_team"].dropna().unique().tolist() +
        dp["fielding_team"].dropna().unique().tolist()
    ))
    teams_opts = "".join(f"<option>{t}</option>" for t in teams)

    b_cols = ["batting_team", "fielding_team", "batter", "bat_side", "batter_split",
              "men_on_base", "pitcher", "day_night", "home_away_batting",
              "PA", "AB", "H", "singles", "doubles", "triples", "HR",
              "RBI", "BB", "IBB", "SO", "HBP", "SF"]
    p_cols = ["fielding_team", "batting_team", "pitcher", "pitch_hand", "pitcher_split",
              "men_on_base", "batter", "day_night", "home_away_pitching",
              "BF", "AB", "H", "singles", "doubles", "triples", "HR",
              "BB", "IBB", "SO", "HBP", "SF", "total_outs"]

    b_json = db[[c for c in b_cols if c in db.columns]].to_json(orient="records", force_ascii=False)
    p_json = dp[[c for c in p_cols if c in dp.columns]].to_json(orient="records", force_ascii=False)

    season = str(db["season"].iloc[0]) if "season" in db.columns else "2026"

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MLB Stats {season}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0a1628;color:#e8eaf0;min-height:100vh}}
header{{padding:1.2rem 2rem;border-bottom:1px solid rgba(245,197,24,.2);display:flex;align-items:center;gap:1rem;flex-wrap:wrap}}
h1{{font-size:1.25rem;font-weight:600;color:#f5c518;margin-right:auto}}
.tabs{{display:flex;gap:6px}}
.tab{{padding:6px 18px;border-radius:20px;border:1px solid rgba(255,255,255,.15);background:transparent;color:#8892a4;font-size:13px;cursor:pointer;transition:all .15s}}
.tab.active{{background:#f5c518;border-color:#f5c518;color:#0a1628;font-weight:600}}
.filters{{display:flex;gap:10px;padding:.8rem 2rem;flex-wrap:wrap;align-items:flex-end;background:rgba(255,255,255,.02);border-bottom:1px solid rgba(255,255,255,.06)}}
.fg{{display:flex;flex-direction:column;gap:3px}}
label{{font-size:11px;color:#8892a4;text-transform:uppercase;letter-spacing:.04em}}
input,select{{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);color:#e8eaf0;padding:6px 10px;border-radius:5px;font-size:13px;outline:none}}
input:focus,select:focus{{border-color:rgba(245,197,24,.5)}}
select option{{background:#0d1f38}}
.info-bar{{display:flex;gap:16px;padding:.5rem 2rem;font-size:12px;color:#8892a4;border-bottom:1px solid rgba(255,255,255,.06)}}
.info-bar b{{color:#f5c518}}
.wrap{{overflow-x:auto;padding-bottom:2rem}}
table{{width:100%;border-collapse:collapse;font-size:13px;min-width:900px}}
thead tr{{background:rgba(255,255,255,.04)}}
th{{padding:9px 12px;text-align:right;font-weight:500;color:#8892a4;font-size:11px;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap;cursor:pointer;user-select:none;background:#0d1f38;position:sticky;top:0;z-index:1}}
th:first-child,th:nth-child(2),th:nth-child(3){{text-align:left}}
th:hover{{color:#f5c518}}
th.asc::after{{content:' ↑';color:#f5c518}}
th.desc::after{{content:' ↓';color:#f5c518}}
tbody tr{{border-bottom:1px solid rgba(255,255,255,.04)}}
tbody tr:hover{{background:rgba(245,197,24,.04)}}
td{{padding:8px 12px;text-align:right;color:#c8cdd8}}
td:first-child{{text-align:left;color:#5a6478;font-size:11px}}
td:nth-child(2){{text-align:left;font-weight:500;color:#e8eaf0;white-space:nowrap}}
td:nth-child(3){{text-align:left;color:#8892a4;font-size:12px;white-space:nowrap}}
.hi{{color:#4ade80;font-weight:600}}
.md{{color:#fbbf24;font-weight:500}}
.lo{{color:#f87171}}
.empty{{text-align:center;color:#5a6478;padding:3rem;font-size:14px}}
</style>
</head>
<body>
<header>
  <h1>⚾ MLB Stats {season}</h1>
  <div class="tabs">
    <button class="tab active" onclick="switchTab('bat')">Batters</button>
    <button class="tab" onclick="switchTab('pit')">Pitchers</button>
  </div>
</header>

<div class="filters" id="bat-filters">
  <div class="fg"><label>Jogador</label><input id="b-q" placeholder="Buscar..."/></div>
  <div class="fg"><label>Time (bat)</label><select id="b-tm"><option value="">Todos</option>{teams_opts}</select></div>
  <div class="fg"><label>Adversário</label><select id="b-ft"><option value="">Todos</option>{teams_opts}</select></div>
  <div class="fg"><label>Lado</label><select id="b-bs"><option value="">Ambos</option><option value="R">Direita (R)</option><option value="L">Esquerda (L)</option></select></div>
  <div class="fg"><label>Split</label><select id="b-sp"><option value="">Todos</option><option value="vs_RHP">vs RHP</option><option value="vs_LHP">vs LHP</option></select></div>
  <div class="fg"><label>Situação</label><select id="b-mo"><option value="">Todas</option><option value="Empty">Empty</option><option value="Men_On">Men On</option><option value="RISP">RISP</option><option value="Loaded">Loaded</option></select></div>
  <div class="fg"><label>Home/Away</label><select id="b-ha"><option value="">Todos</option><option value="home">Home</option><option value="away">Away</option></select></div>
  <div class="fg"><label>Mín. PA</label><input id="b-mpa" type="number" value="10" min="1" style="width:65px"/></div>
</div>

<div class="filters" id="pit-filters" style="display:none">
  <div class="fg"><label>Pitcher</label><input id="p-q" placeholder="Buscar..."/></div>
  <div class="fg"><label>Time (pit)</label><select id="p-tm"><option value="">Todos</option>{teams_opts}</select></div>
  <div class="fg"><label>Adversário</label><select id="p-ft"><option value="">Todos</option>{teams_opts}</select></div>
  <div class="fg"><label>Mão</label><select id="p-ph"><option value="">Ambas</option><option value="R">Direita (R)</option><option value="L">Esquerda (L)</option></select></div>
  <div class="fg"><label>Split</label><select id="p-sp"><option value="">Todos</option><option value="vs_RHB">vs RHB</option><option value="vs_LHB">vs LHB</option></select></div>
  <div class="fg"><label>Situação</label><select id="p-mo"><option value="">Todas</option><option value="Empty">Empty</option><option value="Men_On">Men On</option><option value="RISP">RISP</option><option value="Loaded">Loaded</option></select></div>
  <div class="fg"><label>Home/Away</label><select id="p-ha"><option value="">Todos</option><option value="home">Home</option><option value="away">Away</option></select></div>
  <div class="fg"><label>Mín. BF</label><input id="p-mbf" type="number" value="10" min="1" style="width:65px"/></div>
</div>

<div class="info-bar" id="info">Carregando...</div>
<div class="wrap">
  <table><thead id="thead"></thead><tbody id="tb"></tbody></table>
  <div class="empty" id="emp" style="display:none">Nenhum resultado encontrado.</div>
</div>

<script>
const BRAW={b_json};
const PRAW={p_json};
let mode='bat', sortK='PA', sortAsc=false;

function fmt3(v){{return v===0?'.000':v.toFixed(3).replace('0.','.'); }}
function fmtPct(v){{return (v*100).toFixed(1)+'%'; }}
function fmtIP(o){{return Math.floor(o/3)+'.'+(o%3); }}
function cls(v,hi,md,inv=false){{
  if(inv) return v<=hi?'hi':v<=md?'md':'lo';
  return v>=hi?'hi':v>=md?'md':'lo';
}}

function aggBat(rows){{
  const m={{}};
  for(const r of rows){{
    const k=r.batter+'|||'+r.batting_team;
    if(!m[k]) m[k]={{batter:r.batter,batting_team:r.batting_team,PA:0,AB:0,H:0,singles:0,doubles:0,triples:0,HR:0,RBI:0,BB:0,IBB:0,SO:0,HBP:0,SF:0}};
    const a=m[k];
    a.PA+=r.PA;a.AB+=r.AB;a.H+=r.H;a.singles+=r.singles;
    a.doubles+=r.doubles;a.triples+=r.triples;a.HR+=r.HR;
    a.RBI+=r.RBI;a.BB+=r.BB;a.IBB+=r.IBB;a.SO+=r.SO;a.HBP+=r.HBP;a.SF+=r.SF;
  }}
  return Object.values(m).map(a=>{{
    const avg=a.AB>0?a.H/a.AB:0;
    const obp=(a.AB+a.BB+a.IBB+a.HBP+a.SF)>0?(a.H+a.BB+a.IBB+a.HBP)/(a.AB+a.BB+a.IBB+a.HBP+a.SF):0;
    const slg=a.AB>0?(a.singles+2*a.doubles+3*a.triples+4*a.HR)/a.AB:0;
    return {{...a,AVG:+avg.toFixed(3),OBP:+obp.toFixed(3),SLG:+slg.toFixed(3),OPS:+(obp+slg).toFixed(3)}};
  }});
}}

function aggPit(rows){{
  const m={{}};
  for(const r of rows){{
    const k=r.pitcher+'|||'+r.fielding_team;
    if(!m[k]) m[k]={{pitcher:r.pitcher,fielding_team:r.fielding_team,BF:0,AB:0,H:0,singles:0,doubles:0,triples:0,HR:0,BB:0,IBB:0,SO:0,HBP:0,SF:0,outs:0}};
    const a=m[k];
    a.BF+=r.BF;a.AB+=r.AB;a.H+=r.H;a.singles+=r.singles;
    a.doubles+=r.doubles;a.triples+=r.triples;a.HR+=r.HR;
    a.BB+=r.BB;a.IBB+=r.IBB;a.SO+=r.SO;a.HBP+=r.HBP;a.SF+=r.SF;
    a.outs+=r.total_outs;
  }}
  return Object.values(m).map(a=>{{
    const baa=a.AB>0?a.H/a.AB:0;
    const obp=(a.AB+a.BB+a.IBB+a.HBP+a.SF)>0?(a.H+a.BB+a.IBB+a.HBP)/(a.AB+a.BB+a.IBB+a.HBP+a.SF):0;
    const slg=a.AB>0?(a.singles+2*a.doubles+3*a.triples+4*a.HR)/a.AB:0;
    const kpct=a.BF>0?a.SO/a.BF:0;
    const bbpct=a.BF>0?(a.BB+a.IBB)/a.BF:0;
    return {{...a,IP:fmtIP(a.outs),BAA:+baa.toFixed(3),OBP:+obp.toFixed(3),SLG:+slg.toFixed(3),OPS:+(obp+slg).toFixed(3),Kpct:+kpct.toFixed(3),BBpct:+bbpct.toFixed(3)}};
  }});
}}

function renderBat(){{
  const q=document.getElementById('b-q').value.toLowerCase();
  const tm=document.getElementById('b-tm').value;
  const ft=document.getElementById('b-ft').value;
  const bs=document.getElementById('b-bs').value;
  const sp=document.getElementById('b-sp').value;
  const mo=document.getElementById('b-mo').value;
  const ha=document.getElementById('b-ha').value;
  const mpa=+document.getElementById('b-mpa').value||1;

  let rows=BRAW.filter(r=>
    (!q||r.batter.toLowerCase().includes(q))&&
    (!tm||r.batting_team===tm)&&(!ft||r.fielding_team===ft)&&
    (!bs||r.bat_side===bs)&&(!sp||r.batter_split===sp)&&
    (!mo||r.men_on_base===mo)&&(!ha||r.home_away_batting===ha)
  );
  let data=aggBat(rows).filter(a=>a.PA>=mpa);
  data.sort((a,b)=>{{
    let av=a[sortK],bv=b[sortK];
    if(typeof av==='string'){{av=av.toLowerCase();bv=bv.toLowerCase();}}
    return sortAsc?(av>bv?1:-1):(av<bv?1:-1);
  }});

  document.getElementById('info').innerHTML=
    `Exibindo <b>${{data.length}}</b> jogadores · <b>${{rows.length}}</b> linhas · Mín. <b>${{mpa}} PA</b>`;

  document.getElementById('thead').innerHTML=`<tr>
    <th data-k="rank">#</th><th data-k="batter">Jogador</th><th data-k="batting_team">Time</th>
    <th data-k="PA">PA</th><th data-k="AB">AB</th><th data-k="H">H</th>
    <th data-k="doubles">2B</th><th data-k="triples">3B</th><th data-k="HR">HR</th>
    <th data-k="RBI">RBI</th><th data-k="BB">BB</th><th data-k="IBB">IBB</th>
    <th data-k="SO">K</th><th data-k="HBP">HBP</th><th data-k="SF">SF</th>
    <th data-k="AVG">AVG</th><th data-k="OBP">OBP</th><th data-k="SLG">SLG</th><th data-k="OPS">OPS</th>
  </tr>`;
  bindSort();

  const emp=document.getElementById('emp');
  if(!data.length){{document.getElementById('tb').innerHTML='';emp.style.display='block';return;}}
  emp.style.display='none';
  document.getElementById('tb').innerHTML=data.map((d,i)=>`<tr>
    <td>${{i+1}}</td><td>${{d.batter}}</td><td>${{d.batting_team}}</td>
    <td>${{d.PA}}</td><td>${{d.AB}}</td><td>${{d.H}}</td>
    <td>${{d.doubles}}</td><td>${{d.triples}}</td><td>${{d.HR}}</td>
    <td>${{d.RBI}}</td><td>${{d.BB}}</td><td>${{d.IBB}}</td>
    <td>${{d.SO}}</td><td>${{d.HBP}}</td><td>${{d.SF}}</td>
    <td class="${{cls(d.AVG,.3,.22)}}">${{fmt3(d.AVG)}}</td>
    <td class="${{cls(d.OBP,.36,.30)}}">${{fmt3(d.OBP)}}</td>
    <td class="${{cls(d.SLG,.45,.35)}}">${{fmt3(d.SLG)}}</td>
    <td class="${{cls(d.OPS,.9,.7)}}">${{fmt3(d.OPS)}}</td>
  </tr>`).join('');
}}

function renderPit(){{
  const q=document.getElementById('p-q').value.toLowerCase();
  const tm=document.getElementById('p-tm').value;
  const ft=document.getElementById('p-ft').value;
  const ph=document.getElementById('p-ph').value;
  const sp=document.getElementById('p-sp').value;
  const mo=document.getElementById('p-mo').value;
  const ha=document.getElementById('p-ha').value;
  const mbf=+document.getElementById('p-mbf').value||1;

  let rows=PRAW.filter(r=>
    (!q||r.pitcher.toLowerCase().includes(q))&&
    (!tm||r.fielding_team===tm)&&(!ft||r.batting_team===ft)&&
    (!ph||r.pitch_hand===ph)&&(!sp||r.pitcher_split===sp)&&
    (!mo||r.men_on_base===mo)&&(!ha||r.home_away_pitching===ha)
  );
  let data=aggPit(rows).filter(a=>a.BF>=mbf);
  data.sort((a,b)=>{{
    const sk=sortK==='IP'?'outs':sortK;
    let av=a[sk],bv=b[sk];
    if(typeof av==='string'){{av=av.toLowerCase();bv=bv.toLowerCase();}}
    return sortAsc?(av>bv?1:-1):(av<bv?1:-1);
  }});

  document.getElementById('info').innerHTML=
    `Exibindo <b>${{data.length}}</b> pitchers · <b>${{rows.length}}</b> linhas · Mín. <b>${{mbf}} BF</b>`;

  document.getElementById('thead').innerHTML=`<tr>
    <th data-k="rank">#</th><th data-k="pitcher">Pitcher</th><th data-k="fielding_team">Time</th>
    <th data-k="IP">IP</th><th data-k="BF">BF</th><th data-k="AB">AB</th>
    <th data-k="H">H</th><th data-k="doubles">2B</th><th data-k="triples">3B</th><th data-k="HR">HR</th>
    <th data-k="BB">BB</th><th data-k="IBB">IBB</th><th data-k="SO">K</th>
    <th data-k="HBP">HBP</th><th data-k="SF">SF</th>
    <th data-k="BAA">BAA</th><th data-k="OBP">OBP</th><th data-k="SLG">SLG</th><th data-k="OPS">OPS</th>
    <th data-k="Kpct">K%</th><th data-k="BBpct">BB%</th>
  </tr>`;
  bindSort();

  const emp=document.getElementById('emp');
  if(!data.length){{document.getElementById('tb').innerHTML='';emp.style.display='block';return;}}
  emp.style.display='none';
  document.getElementById('tb').innerHTML=data.map((d,i)=>`<tr>
    <td>${{i+1}}</td><td>${{d.pitcher}}</td><td>${{d.fielding_team}}</td>
    <td>${{d.IP}}</td><td>${{d.BF}}</td><td>${{d.AB}}</td>
    <td>${{d.H}}</td><td>${{d.doubles}}</td><td>${{d.triples}}</td><td>${{d.HR}}</td>
    <td>${{d.BB}}</td><td>${{d.IBB}}</td><td>${{d.SO}}</td>
    <td>${{d.HBP}}</td><td>${{d.SF}}</td>
    <td class="${{cls(d.BAA,.3,.22,true)}}">${{fmt3(d.BAA)}}</td>
    <td class="${{cls(d.OBP,.36,.30,true)}}">${{fmt3(d.OBP)}}</td>
    <td class="${{cls(d.SLG,.45,.35,true)}}">${{fmt3(d.SLG)}}</td>
    <td class="${{cls(d.OPS,.9,.7,true)}}">${{fmt3(d.OPS)}}</td>
    <td class="${{cls(d.Kpct,.25,.18)}}">${{fmtPct(d.Kpct)}}</td>
    <td class="${{cls(d.BBpct,.1,.08,true)}}">${{fmtPct(d.BBpct)}}</td>
  </tr>`).join('');
}}

function bindSort(){{
  document.querySelectorAll('th[data-k]').forEach(th=>{{
    th.addEventListener('click',()=>{{
      const k=th.dataset.k; if(k==='rank') return;
      if(sortK===k) sortAsc=!sortAsc; else{{sortK=k;sortAsc=false;}}
      document.querySelectorAll('th').forEach(t=>t.className='');
      th.className=sortAsc?'asc':'desc';
      render();
    }});
  }});
  const th=document.querySelector(`th[data-k="${{sortK}}"]`);
  if(th) th.className=sortAsc?'asc':'desc';
}}

function render(){{mode==='bat'?renderBat():renderPit();}}

function switchTab(m){{
  mode=m;
  document.querySelectorAll('.tab').forEach((t,i)=>
    t.className='tab'+((['bat','pit'][i]===m)?' active':'')
  );
  document.getElementById('bat-filters').style.display=m==='bat'?'flex':'none';
  document.getElementById('pit-filters').style.display=m==='pit'?'flex':'none';
  sortK=m==='bat'?'PA':'BF'; sortAsc=false;
  render();
}}

['b-q','b-tm','b-ft','b-bs','b-sp','b-mo','b-ha','b-mpa'].forEach(id=>
  document.getElementById(id).addEventListener('input',render)
);
['p-q','p-tm','p-ft','p-ph','p-sp','p-mo','p-ha','p-mbf'].forEach(id=>
  document.getElementById(id).addEventListener('input',render)
);

render();
</script>
</body>
</html>"""


def main():
    print("Carregando dados...")
    db, dp = load_data()

    print("Gerando HTML...")
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    html = build_html(db, dp)

    out = DOCS_DIR / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"Salvo em {out} ({len(html):,} chars)")


if __name__ == "__main__":
    main()
