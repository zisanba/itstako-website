#!/usr/bin/env python3
"""Builds the static Tako marketing site from the design sources in _source/pages.
Run:  python3 _source/build.py
Output goes to the repo root (index.html, ozellikler/, en/ ...). Commit the output."""
import re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / '_source' / 'pages'

# ---- Settings you may change -------------------------------------------------
DOMAIN = 'https://itstako.com'          # used for canonical / hreflang / sitemap
CONTACT_EMAIL = ''                      # empty = the "[E-posta adresi]" placeholder stays visible
FORM_ENDPOINT = ''                      # URL that receives the demo form (e.g. a Formspree endpoint)
# ------------------------------------------------------------------------------

# page key -> (source file, output folder)
PAGES = {
    ('Home', 'tr'): ('Main.dc.html', ''),
    ('Features', 'tr'): ('Features-TR.dc.html', 'ozellikler'),
    ('Pricing', 'tr'): ('Pricing-TR.dc.html', 'fiyatlandirma'),
    ('Demo', 'tr'): ('Demo-TR.dc.html', 'demo'),
    ('Home', 'en'): ('Home-EN.dc.html', 'en'),
    ('Features', 'en'): ('Features-EN.dc.html', 'en/features'),
    ('Pricing', 'en'): ('Pricing-EN.dc.html', 'en/pricing'),
    ('Demo', 'en'): ('Demo-EN.dc.html', 'en/demo'),
}
DESC = {
    ('Home', 'tr'): 'Tako ile kendi online mağazanızı kurun: tasarım, satış ve sipariş yönetimi tek yerde.',
    ('Features', 'tr'): 'Tako özellikleri: mağaza tasarımı, satış ve sipariş yönetimi.',
    ('Pricing', 'tr'): 'Tako fiyatlandırması: Advanced, Pro ve Premium planları.',
    ('Demo', 'tr'): 'Tako’yu 1 ay ücretsiz deneyin.',
    ('Home', 'en'): 'Build your own online store with Tako: design, selling and order management in one place.',
    ('Features', 'en'): 'Tako features: store design, selling and order management.',
    ('Pricing', 'en'): 'Tako pricing: Advanced, Pro and Premium plans.',
    ('Demo', 'en'): 'Try Tako free for 1 month.',
}
def out_dir(page, lang): return PAGES[(page, lang)][1]
def depth(folder): return len([p for p in folder.split('/') if p])
def url(page, lang, from_folder):
    target = out_dir(page, lang)
    up = '../' * depth(from_folder) or './'
    return up + (target + '/' if target else '')

def read(name): return (SRC / name).read_text(encoding='utf-8')
def body_of(src):
    m = re.search(r'<x-dc>(.*?)</x-dc>', src, re.S)
    inner = m.group(1)
    inner = re.sub(r'<helmet>.*?</helmet>', '', inner, flags=re.S)
    return inner.strip()
def fill(tpl, vals): return re.sub(r'\{\{(\w+)\}\}', lambda m: str(vals[m.group(1)]), tpl)

HEADER, FOOTER, OCTO = (body_of(read(f'{n}.dc.html')) for n in ('Header', 'Footer', 'Octopus'))

def header_html(lang, page, folder):
    tr = lang == 'tr'; navy, body = '#2A2968', '#47466F'
    on = lambda p: page == p
    act = 'background:#fff;color:#2A2968;box-shadow:0 2px 8px rgba(42,41,104,.15)'; idle = 'color:#47466F'
    return fill(HEADER, dict(
        home=url('Home', lang, folder), features=url('Features', lang, folder), pricing=url('Pricing', lang, folder), demo=url('Demo', lang, folder),
        hrefTR=url(page, 'tr', folder), hrefEN=url(page, 'en', folder),
        tFeatures='Özellikler' if tr else 'Features', tPricing='Fiyatlandırma' if tr else 'Pricing', tDemo='Demo',
        tCta='Ücretsiz demoyu başlat' if tr else 'Start free demo',
        cF=navy if on('Features') else body, cP=navy if on('Pricing') else body, cD=navy if on('Demo') else body,
        wF=700 if on('Features') else 500, wP=700 if on('Pricing') else 500, wD=700 if on('Demo') else 500,
        stTR=act if tr else idle, stEN=idle if tr else act))

def footer_html(lang, folder):
    tr = lang == 'tr'
    return fill(FOOTER, dict(
        features=url('Features', lang, folder), pricing=url('Pricing', lang, folder), demo=url('Demo', lang, folder),
        tFeatures='Özellikler' if tr else 'Features', tPricing='Fiyatlandırma' if tr else 'Pricing', tDemo='Demo',
        hProd='ÜRÜN' if tr else 'PRODUCT', hLegal='YASAL' if tr else 'LEGAL',
        tPriv='Gizlilik Politikası' if tr else 'Privacy Policy', tTerms='Kullanım Koşulları' if tr else 'Terms of Use', tCook='Çerez Politikası' if tr else 'Cookie Policy',
        tag='Modern ticaret için geliştirildi.' if tr else 'Built for modern commerce.',
        pow='Techne tarafından desteklenir.' if tr else 'Powered by Techne.',
        copy='© 2026 Techne. Tüm hakları saklıdır.' if tr else '© 2026 Techne. All rights reserved.'))

def octo_html(m):
    a = dict(re.findall(r'(\w[\w-]*)="([^"]*)"', m.group(0)))
    return fill(OCTO, dict(body=a.get('body', '#2A2968'), cheek=a.get('cheek', '#FF4A5F'), mouth=a.get('mouth', '#FF6B7F')))

FORM_JS = """<script>
(function(){
  var f=document.querySelector('form'); if(!f) return;
  var tr=document.documentElement.lang==='tr', EP=%s;
  var names=['name','email','company','website','plan','consent'];
  var fields=f.querySelectorAll('input,select'); fields.forEach(function(el,i){el.name=names[i]||('f'+i);});
  f.querySelectorAll('input[name=name],input[name=email]').forEach(function(el){el.required=true;});
  f.querySelector('input[name=consent]').required=true;
  var btn=f.querySelector('button'); btn.type='submit';
  var note=document.createElement('div'); note.setAttribute('role','status'); note.style.cssText='font-size:15px;font-weight:600;color:#2A2968'; f.appendChild(note);
  f.addEventListener('submit',function(e){
    e.preventDefault(); if(!f.reportValidity()) return;
    if(!EP){note.textContent=tr?'Form henüz bağlı değil.':'The form is not connected yet.'; return;}
    var data={}; fields.forEach(function(el){data[el.name]=el.type==='checkbox'?el.checked:el.value;});
    btn.disabled=true;
    fetch(EP,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(data)})
      .then(function(r){if(!r.ok)throw 0; note.textContent=tr?'Teşekkürler! En kısa sürede size dönüş yapacağız.':'Thank you! We will get back to you shortly.'; f.reset();})
      .catch(function(){note.textContent=tr?'Bir sorun oluştu. Lütfen tekrar deneyin.':'Something went wrong. Please try again.';})
      .then(function(){btn.disabled=false;});
  });
})();
</script>"""

def page_html(page, lang):
    src, folder = PAGES[(page, lang)]
    raw = read(src)
    title = re.search(r'<title>(.*?)</title>', raw).group(1)
    body = body_of(raw)
    body = re.sub(r'<dc-import name="Header"[^>]*></dc-import>', lambda m: header_html(lang, page, folder), body)
    body = re.sub(r'<dc-import name="Footer"[^>]*></dc-import>', lambda m: footer_html(lang, folder), body)
    body = re.sub(r'<dc-import name="Octopus"[^>]*></dc-import>', octo_html, body)
    # links written inside the page content, e.g. ./Pricing-TR.dc.html -> real page URLs
    def fix_link(m):
        name = m.group(1)
        if name == 'Main': return 'href="' + url('Home', 'tr', folder) + '"'
        pg, lg = name.rsplit('-', 1)
        return 'href="' + url(pg, lg.lower(), folder) + '"'
    body = re.sub(r'href="\./([A-Za-z]+(?:-[A-Z]{2})?)\.dc\.html"', fix_link, body)
    if CONTACT_EMAIL:
        body = re.sub(r'\[(E-posta adresi|Email address|email address)\]', CONTACT_EMAIL, body)
    leftovers = re.findall(r'<dc-import|\{\{\w+\}\}', body)
    if leftovers: raise SystemExit(f'{src}: unresolved components or placeholders: {set(leftovers)}')
    canon = DOMAIN + '/' + (out_dir(page, lang) + '/' if out_dir(page, lang) else '')
    alt = lambda l: DOMAIN + '/' + (out_dir(page, l) + '/' if out_dir(page, l) else '')
    up = '../' * depth(folder) or './'
    form_js = FORM_JS % ("'" + FORM_ENDPOINT + "'") if page == 'Demo' else ''
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{DESC[(page, lang)]}">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="tr" href="{alt('tr')}">
<link rel="alternate" hreflang="en" href="{alt('en')}">
<link rel="icon" type="image/svg+xml" href="{up}favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&amp;family=Plus+Jakarta+Sans:wght@600;700;800&amp;display=swap" rel="stylesheet">
<style>body{{margin:0;background:#FAF9FD}}a{{text-decoration:none}}img,svg{{max-width:100%}}</style>
</head>
<body>
{body}
{form_js}
</body>
</html>
'''

def main():
    # clean previously built output (keeps _source, .git, README, CNAME)
    for (page, lang), (_, folder) in PAGES.items():
        d = ROOT / folder if folder else ROOT
        d.mkdir(parents=True, exist_ok=True)
        (d / 'index.html').write_text(page_html(page, lang), encoding='utf-8')
    svg = re.search(r'<svg[^>]*viewBox="250 195 745 630".*?</svg>', HEADER, re.S).group(0)
    svg = re.sub(r'\s(width|height)="[^"]*"', '', svg, count=2)
    (ROOT / 'favicon.svg').write_text(svg, encoding='utf-8')
    urls = [DOMAIN + '/' + (f + '/' if f else '') for _, f in PAGES.values()]
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n', encoding='utf-8')
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n', encoding='utf-8')
    (ROOT / '.nojekyll').write_text('', encoding='utf-8')
    warns = []
    for p in ROOT.rglob('index.html'):
        t = p.read_text(encoding='utf-8')
        if re.search(r'\[(E-posta adresi|Email address|email address)\]', t): warns.append(f'{p.relative_to(ROOT)}: contact email placeholder still visible')
        if 'href="#"' in t: warns.append(f'{p.relative_to(ROOT)}: legal links still point to "#"')
    print(f'Built {len(PAGES)} pages.'); [print('WARNING', w) for w in sorted(set(warns))]

if __name__ == '__main__': main()
