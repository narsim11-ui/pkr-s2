"""Build the public Season 02 page from the Claude dashboard's page code and the session rows.

usage: python3 build_page.py <dashboard index.html> <season02-sessions.json> <out.html>
The output is the UNLOCKED page: lock it with StatiCrypt before publishing. Never commit it or the JSON.
"""
import json, re, sys, os, datetime

page_path, data_path, out_path = sys.argv[1:4]
here = os.path.dirname(os.path.abspath(__file__))
page = open(page_path, encoding='utf-8').read()
rows = json.load(open(data_path, encoding='utf-8'))
d3 = open(os.path.join(here, 'd3.min.js'), encoding='utf-8').read()

dates = sorted({r['date'] for r in rows})
last = datetime.date.fromisoformat(dates[-1]).strftime('%-d %b %Y')
styles = ''.join(re.findall(r'<style>.*?</style>', page, re.S))
scripts = re.findall(r'<script>(.*?)</script>', page, re.S)
markup = re.sub(r'<script>.*?</script>|<style>.*?</style>', '', page, flags=re.S)

tokens = """
:root{--color-fg:#1f1e1d;--color-fg-muted:#73726c;--color-bg:#f5f4ef;--color-panel:#ffffff;--color-border-line:#e6e4dc;
--color-ok:#2f7d4f;--color-warn:#a26a12;--color-bad:#bf3b2f;--cds-chart-muted:#d9d6cc;--cds-chart-grid:#efede6;--cds-chart-axis:#bdbab0;
--cds-chart-reference:#9a978e;--cds-chart-status-critical:#d0543f;--cds-surface-popover:#ffffff;--cds-border:#e6e4dc;
--cds-shadow-popover:0 4px 14px rgba(0,0,0,.08);--cds-text-secondary:#73726c;
--font-anthropic-sans:'Inter',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;--font-anthropic-serif:'Source Serif 4',Georgia,serif;
--cds-font-size-caption:11.5px;--cds-font-size-body:13px;--cds-font-size-heading:15px;--cds-font-size-title:26px;--cds-font-weight-medium:600;
--cds-gap-xs:4px;--cds-gap-sm:8px;--cds-gap-md:14px;--cds-gap-lg:22px;--cds-gap-xl:32px;--cds-pad-xs:4px;--cds-pad-sm:8px;--cds-pad-md:12px;
--cds-pad-lg:18px;--cds-pad-xl:24px;--cds-radius:10px;--cds-dur-slow:.3s;--cds-ease-out:ease-out;color-scheme:light dark}
@media (prefers-color-scheme:dark){:root{--color-fg:#ecebe6;--color-fg-muted:#a3a29b;--color-bg:#1c1b19;--color-panel:#262522;
--color-border-line:#3a3935;--color-ok:#6cc08a;--color-warn:#e0ab4f;--color-bad:#ef7a6c;--cds-chart-muted:#4a4843;--cds-chart-grid:#33322e;
--cds-chart-axis:#5c5a54;--cds-chart-reference:#85837b;--cds-chart-status-critical:#e2705b;--cds-surface-popover:#2e2d29;--cds-border:#3a3935;
--cds-shadow-popover:0 4px 14px rgba(0,0,0,.4);--cds-text-secondary:#a3a29b}}
html,body{margin:0;background:var(--color-bg);color:var(--color-fg);font-family:var(--font-anthropic-sans);-webkit-text-size-adjust:100%}
#dash-root{padding:24px clamp(16px,3vw,40px) 40px;max-width:1280px;margin:0 auto}
.dash-skeleton{background:var(--cds-chart-grid);border-radius:6px;color:transparent}
.pk-updated{font-size:var(--cds-font-size-caption);color:var(--color-fg-muted);margin-top:var(--cds-gap-xs)}
"""
shim = """
window.dash=(()=>{const ds={sessions:%s};const calcs={},res={},cbs=[];
function comp(id){if(id in res)return res[id];if(ds[id])return res[id]=ds[id];const c=calcs[id];if(!c)throw new Error('missing '+id);return res[id]=c.fn(...c.inputs.map(comp));}
let w=innerWidth;addEventListener('resize',()=>{if(innerWidth!==w){w=innerWidth;cbs.forEach(f=>f());}});
return{colors:['#c96442','#5b7fa6','#6a9a6a','#b58a3c','#8a6aa8','#4f9a9a','#b5677d','#8f8e86'],
calc(id,c){calcs[id]=c},loader(){},data(id){try{return{status:'ok',data:comp(id)}}catch(e){console.error(e);return{status:'error',data:[]}}},
onData(f){cbs.push(f);f()},setLink(n){history.replaceState(null,'','#'+n)},params(){return{}},setParams(){},resetParams(){},refresh(){}};})();
""" % json.dumps(rows, ensure_ascii=False)

updated = f'<p class="pk-updated">Updated through {last} · {len(dates)} sessions</p>'
markup = markup.replace('</header>', updated + '</header>', 1)
html = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">'
        '<title>Poker Season 02</title>'
        '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Source+Serif+4:wght@400&display=swap" rel="stylesheet">'
        f'<style>{tokens}</style>{styles}<script>{d3}</script><script>{shim}</script></head>'
        f'<body><div id="dash-root">{markup}</div>' + ''.join(f'<script>{s}</script>' for s in scripts) + '</body></html>')
open(out_path, 'w', encoding='utf-8').write(html)
print(f'built {out_path}: {len(rows)} rows, {len(dates)} sessions, through {last}')
