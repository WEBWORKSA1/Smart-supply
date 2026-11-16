#!/usr/bin/env python3
"""Smart.Supply static site builder.

Wraps every fragment in src/pages/**.html with the shared shell and writes
the final page to the repo root (same relative path). Also generates
assets/js/layout.js (shared header/footer), assets/js/search-index.js and sitemap.xml.

Fragment front matter (first HTML comment):
<!--
title: Page title
description: Meta description
nav: tools            (optional, highlights menu item)
schema: article       (optional: article | faq | none)
layout: guide         (optional: wraps in article layout with TOC, ads, CTA)
category: Sourcing    (guides only)
noexit: 1             (optional, disables exit-intent modal)
date: 2026-09-18      (optional)
-->

Usage:  python3 tools/build.py
"""
import json, os, re, html, datetime, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "pages")
SITE = "https://smart.supply"
TODAY = datetime.date.today().isoformat()
LASTMOD = "2026-11-16"  # default lastmod for evergreen pages (override with `updated:` front matter)
ADSENSE = "ca-pub-6620975821265271"
OWNER_CONTACT = "https://web.works/contact"


def asset_version():
    h = hashlib.sha1()
    for f in ["assets/css/style.css", "assets/js/app.js", "assets/js/data.js", "assets/js/config.js", "assets/js/layout.js", "assets/js/search-index.js"]:
        fp = os.path.join(ROOT, f)
        if os.path.exists(fp):
            h.update(open(fp, "rb").read())
    return h.hexdigest()[:8]


def load_daily():
    fp = os.path.join(ROOT, "assets", "js", "daily.js")
    if not os.path.exists(fp):
        return {}
    raw = open(fp, encoding="utf-8").read()
    return json.loads(raw[raw.index("=") + 1:].strip().rstrip(";"))


V = "1"  # set in build()

MENU = [
    ("Source", [
        ("get-quotes.html", "Get Free Quotes", "Post one RFQ, get quotes from vetted suppliers"),
        ("suppliers.html", "Supplier Directory", "Filter by category, country, certification, MOQ"),
        ("get-quotes.html#freight", "Freight & 3PL Quotes", "Ocean, air, trucking, fulfillment"),
        ("list-your-company.html", "List Your Company", "Suppliers: reach buyers with live RFQs"),
    ]),
    ("Tools", [
        ("tools.html#tool-eoq", "EOQ Calculator", "Optimal order quantity"),
        ("tools.html#tool-ss", "Safety Stock", "Buffer by service level"),
        ("tools.html#tool-lc", "Landed Cost", "True cost per unit, duty included"),
        ("tools.html#tool-cbm", "Container Load (CBM)", "20ft / 40ft / 40HC fit"),
        ("tools.html#tool-vol", "Chargeable Weight", "Air & courier volumetric"),
        ("tools.html#tool-fx", "Currency Converter", "Live ECB exchange rates"),
        ("tools.html", "All 10 tools →", "Reorder point, turnover, CO₂, scorecard"),
    ]),
    ("Learn", [
        ("guides.html", "Guides", "Playbooks for sourcing & logistics"),
        ("news.html", "Today's Brief", "Daily supply-chain headlines, explained"),
        ("markets.html", "Market Pulse", "Diesel, freight indices, FX — updated daily"),
        ("glossary.html", "Glossary", "85+ supply-chain terms, A–Z"),
        ("software.html", "Software Directory", "ERP, WMS, TMS, procurement, planning"),
        ("guides/incoterms-2020-explained.html", "Incoterms 2020", "Who pays, who carries risk"),
    ]),
    ("news.html", None),
    ("videos.html", None),
    ("Community", [
        ("contests.html", "Contests & Prizes", "Smart Sourcing Challenge"),
        ("careers.html", "Jobs & Talent", "Hire or get hired in supply chain"),
        ("support.html", "Support Smart.Supply", "Donate & become a backer"),
        ("about.html", "About", "Our mission"),
    ]),
    ("advertise.html", None),
]
LABELS = {"videos.html": "Watch", "advertise.html": "Advertise", "news.html": "Today"}


def parse(path):
    raw = open(path, encoding="utf-8").read()
    meta = {}
    m = re.match(r"\s*<!--(.*?)-->", raw, re.S)
    if m:
        for line in m.group(1).strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        raw = raw[m.end():]
    return meta, raw


def header(r, nav):
    items = []
    for label, sub in MENU:
        if sub is None:
            href = label
            active = ' class="active"' if nav and nav in href else ""
            items.append(f'<li><a href="{r}{href}"{active}>{LABELS[href]}</a></li>')
        else:
            links = "".join(f'<a href="{r}{h}"><b>{t}</b><span>{d}</span></a>' for h, t, d in sub)
            items.append(f'<li><button aria-haspopup="true">{label} ▾</button><div class="mega">{links}</div></li>')
    drawer = []
    for label, sub in MENU:
        if sub is None:
            drawer.append(f'<a href="{r}{label}">{LABELS[label]}</a>')
        else:
            drawer.append(f"<h4>{label}</h4>" + "".join(f'<a href="{r}{h}">{t}</a>' for h, t, d in sub))
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="container nav">
  <a class="logo" href="{r}index.html" aria-label="Smart.Supply home"><span class="logo-mark">⚡</span><span>Smart<span class="dot">.</span>Supply</span></a>
  <ul class="menu">{"".join(items)}</ul>
  <div class="nav-actions">
    <button class="search-trigger" data-search-open aria-label="Search">🔍 <span>Search</span> <kbd>⌘K</kbd></button>
    <button class="icon-btn" data-theme-toggle aria-label="Toggle dark mode">🌓</button>
    <a class="btn btn-accent btn-sm nav-cta" href="{r}get-quotes.html">Get Free Quotes</a>
    <button class="icon-btn burger" data-drawer-open aria-label="Open menu">☰</button>
  </div>
</div></header>
<div class="drawer" id="drawer" aria-hidden="true"><div class="drawer-panel">
  <div class="flex between"><a class="logo" href="{r}index.html"><span class="logo-mark">⚡</span><span>Smart<span class="dot">.</span>Supply</span></a><button class="icon-btn" data-drawer-close aria-label="Close menu">✕</button></div>
  <a class="btn btn-accent btn-block mt2" href="{r}get-quotes.html" style="border:0;color:#fff">Get Free Quotes</a>
  {"".join(drawer)}
  <h4>More</h4><a href="{r}contact.html">Contact</a><a href="{r}privacy.html">Privacy</a>
</div></div>'''


def footer(r):
    return f'''<footer class="site-footer"><div class="container">
  <div class="footer-grid">
    <div>
      <a class="logo" href="{r}index.html"><span class="logo-mark">⚡</span><span>Smart<span class="dot">.</span>Supply</span></a>
      <p class="mt1 small">The AI-powered sourcing &amp; supply-chain intelligence hub. Source smarter. Ship cheaper. Decide faster.</p>
      <form class="inline-form mt1" data-form="newsletter-footer" data-thanks="You're in! Check your inbox for the welcome issue.">
        <label class="hp" aria-hidden="true">Leave empty<input name="website" tabindex="-1" autocomplete="off"></label>
        <input type="email" name="email" placeholder="Work email" required aria-label="Email for newsletter">
        <button class="btn btn-lime btn-sm" type="submit">Subscribe</button>
      </form>
      <div class="social"><a data-social="linkedin" href="#" aria-label="LinkedIn">in</a><a data-social="x" href="#" aria-label="X">X</a><a data-social="youtube" href="#" aria-label="YouTube">▶</a><a data-social="instagram" href="#" aria-label="Instagram">IG</a><a data-social="facebook" href="#" aria-label="Facebook">f</a></div>
    </div>
    <div><h4>Source</h4><ul><li><a href="{r}get-quotes.html">Post an RFQ</a></li><li><a href="{r}suppliers.html">Supplier directory</a></li><li><a href="{r}get-quotes.html#freight">Freight quotes</a></li><li><a href="{r}list-your-company.html">List your company</a></li><li><a href="{r}software.html">Software directory</a></li></ul></div>
    <div><h4>Tools &amp; Learn</h4><ul><li><a href="{r}tools.html">Calculators</a></li><li><a href="{r}guides.html">Guides</a></li><li><a href="{r}glossary.html">Glossary</a></li><li><a href="{r}videos.html">Video hub</a></li></ul></div>
    <div><h4>Community</h4><ul><li><a href="{r}contests.html">Contests &amp; prizes</a></li><li><a href="{r}careers.html">Jobs &amp; talent</a></li><li><a href="{r}support.html">Support us</a></li><li><a href="{r}advertise.html">Advertise / sponsor</a></li></ul></div>
    <div><h4>Company</h4><ul><li><a href="{r}about.html">About</a></li><li><a href="{r}news.html">Today's brief</a></li><li><a href="{r}markets.html">Market pulse</a></li><li><a href="{r}contact.html">Contact</a></li><li><a href="{r}privacy.html">Privacy</a></li><li><a href="{r}terms.html">Terms</a></li><li><a href="{r}disclaimer.html">Disclaimer &amp; affiliates</a></li></ul></div>
  </div>
  <div class="footer-bottom"><span>© <span data-year>2026</span> Smart.Supply™. All rights reserved. · <a href="{r}legal.html">Trademark &amp; copyright</a> · <a href="{r}editorial.html">Editorial policy</a></span><span>Independent editorial — sponsors never influence rankings or advice.</span></div>
  <p class="legal-note">Smart.Supply™ and the Smart.Supply logo are trademarks of the site owner. Third-party names, logos, headlines and videos belong to their respective owners and are used for identification, reference or via official embeds; no endorsement or affiliation is implied. Content on this site is for general information only and is not legal, customs, tax or financial advice.</p>
</div></footer>
<div class="mobile-cta"><a class="btn btn-accent" style="flex:1" href="{r}get-quotes.html">Get Free Quotes</a><a class="btn btn-ghost" href="{r}tools.html">Tools</a></div>
<button class="icon-btn to-top" aria-label="Back to top">↑</button>
<div class="cookie" id="cookie" role="dialog" aria-label="Cookie consent"><b>🍪 We value your privacy</b><p class="small muted mb0">We use cookies for analytics and to show ads (Google AdSense). Choose “Accept all” for personalized ads, or “Essential only” for non-personalized ads. <a href="{r}privacy.html">Privacy policy</a></p><div class="row"><button class="btn btn-primary btn-sm" data-consent="all">Accept all</button><button class="btn btn-ghost btn-sm" data-consent="essential">Essential only</button></div></div>
<div class="modal" id="search-modal" role="dialog" aria-label="Search"><div class="modal-box"><button class="icon-btn modal-close" aria-label="Close">✕</button><h3>Search Smart.Supply</h3><input id="search-input" type="search" placeholder="Search guides, tools, glossary…" aria-label="Search"><div id="search-results" class="search-results mt1"></div></div></div>
<div class="modal" id="exit-modal" role="dialog" aria-label="Free sourcing checklist"><div class="modal-box"><button class="icon-btn modal-close" aria-label="Close">✕</button><span class="eyebrow">Free download</span><h2 class="mt1">The 2026 Smart Sourcing Checklist</h2><p class="muted">47 checks to vet suppliers, avoid hidden landed costs and negotiate better terms. Sent to your inbox + our weekly briefing.</p>
<form data-form="lead-magnet-checklist" data-thanks="Checklist on its way — check your inbox!"><label class="hp" aria-hidden="true">Leave empty<input name="website" tabindex="-1" autocomplete="off"></label><div class="field"><label for="ex-email">Work email <span class="req">*</span></label><input id="ex-email" type="email" name="email" required><span class="err"></span></div><div class="field mt1"><label for="ex-role">I am a…</label><select id="ex-role" name="role"><option>Buyer / procurement</option><option>E-commerce / brand owner</option><option>Supplier / manufacturer</option><option>Logistics provider</option><option>Student</option></select></div><button class="btn btn-accent btn-block mt2" type="submit">Send me the checklist</button><p class="small muted mt1 mb0">No spam. Unsubscribe anytime.</p></form></div></div>'''


def slugify(s):
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", re.sub("<.*?>", "", s).lower()))


def guide_layout(meta, body):
    heads = []

    def add_id(m):
        text = m.group(1)
        sid = slugify(text)
        heads.append((sid, re.sub("<.*?>", "", text)))
        return f'<h2 id="{sid}">{text}</h2>'
    body = re.sub(r"<h2>(.*?)</h2>", add_id, body)
    # in-article ad after the 2nd H2 section
    parts = body.split("<h2 ", 3)
    if len(parts) == 4:
        body = parts[0] + "<h2 " + parts[1] + "<h2 " + parts[2] + '<div class="ad-slot" data-ad="inArticle"></div><h2 ' + parts[3]
    words = len(re.sub("<.*?>", " ", body).split())
    mins = max(3, round(words / 220))
    toc = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in heads)
    cat = meta.get("category", "Guide")
    return f'''<section class="page-hero"><div class="container">
<div class="breadcrumbs"><a href="{{{{root}}}}index.html">Home</a> › <a href="{{{{root}}}}guides.html">Guides</a> › {html.escape(cat)}</div>
<span class="tag tag-brand">{html.escape(cat)}</span>
<h1 class="mt1">{html.escape(meta.get("title", ""))}</h1>
<div class="article-meta"><span>By Smart.Supply Editorial</span><span>Updated {meta.get("date", TODAY)}</span><span>⏱ {mins} min read</span><button class="btn btn-sm btn-ghost" data-share-page>Share</button></div>
<p>{html.escape(meta.get("description", ""))}</p>
</div></section>
<section class="section-sm"><div class="container article-layout">
<article class="prose">{body}
<div class="band mt3"><h3 style="color:#fff">Ready to put this into practice?</h3><p>Post a free RFQ and get competing quotes from vetted suppliers — or run the numbers with our free calculators.</p><div class="flex"><a class="btn btn-lime" href="{{{{root}}}}get-quotes.html">Get free quotes</a><a class="btn btn-ghost" href="{{{{root}}}}tools.html">Open calculators</a></div></div>
</article>
<aside><div class="toc"><div class="card"><b>On this page</b><ol class="mt1">{toc}</ol></div>
<div class="card mt2"><b>📬 The Smart Supply Brief</b><p class="small muted">Weekly sourcing, freight &amp; tariff intel.</p><form data-form="newsletter-guide" data-thanks="Subscribed — welcome aboard!"><label class="hp" aria-hidden="true">Leave empty<input name="website" tabindex="-1" autocomplete="off"></label><input type="email" name="email" placeholder="Work email" required aria-label="Email"><button class="btn btn-accent btn-block mt1" type="submit">Subscribe</button></form></div>
<div class="ad-slot ad-sidebar" data-ad="sidebar" style="padding:0"></div></div></aside>
</div></section>'''


def layout_js(R):
    return ("/* Generated by tools/build.py — edit header()/footer() there, not here. */\n"
            "window.SS_LAYOUT=" + json.dumps({"h": header(R, ""), "f": footer(R)}, ensure_ascii=False) + ";\n"
            "function SS_render(k){var r=document.body.getAttribute('data-root')||'';var s=document.currentScript;"
            "s.insertAdjacentHTML('beforebegin',SS_LAYOUT[k].split('__ROOT__').join(r));"
            "if(k==='h'){var here=location.pathname.split('/').pop()||'index.html';"
            "document.querySelectorAll('.menu>li>a').forEach(function(a){if(a.getAttribute('href').split('/').pop()===here)a.classList.add('active')});}}\n")


def esc(x):
    return html.escape(str(x if x is not None else ""))


def nice_date(d):
    try:
        return datetime.date.fromisoformat(d[:10]).strftime("%b %d, %Y").replace(" 0", " ")
    except Exception:
        return d or ""


def sparkline(points, w=240, h=56):
    vals = [p[1] for p in points if p[1] is not None]
    if len(vals) < 2:
        return ""
    lo, hi = min(vals), max(vals)
    rng = (hi - lo) or 1
    xs = [i * (w / (len(vals) - 1)) for i in range(len(vals))]
    ys = [h - 4 - (v - lo) / rng * (h - 8) for v in vals]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" role="img" aria-label="Trend">'
            f'<polygon class="sparkfill" points="0,{h} {line} {w},{h}"/><polyline class="spark" points="{line}"/></svg>')


def render_generated(body, d):
    if "{{" not in body:
        return body
    news = d.get("news", [])
    upd = nice_date(d.get("updated", ""))
    body = body.replace("{{daily_updated}}", esc(upd))
    if "{{news_list}}" in body:
        out, cur = [], None
        for n in news:
            day = (n.get("date") or "")[:10]
            if day != cur:
                cur = day
                out.append(f'<h2 class="mt3">{esc(nice_date(day) if day else "Recent")}</h2>')
            why = f'<p class="why"><b>Why it matters:</b> {esc(n["why"])}</p>' if n.get("why") else ""
            out.append(f'<article class="news-item"><div class="flex small muted"><span class="tag tag-brand">{esc(n.get("topic", "News"))}</span><span>{esc(n.get("source"))}</span></div>'
                       f'<h3><a href="{esc(n.get("url"))}" target="_blank" rel="noopener nofollow">{esc(n.get("title"))}</a></h3>'
                       f'<p class="muted mb0">{esc(n.get("summary", ""))}</p>{why}</article>')
        body = body.replace("{{news_list}}", '<div class="news-list">' + "".join(out) + "</div>" if out else '<p class="muted">The brief is being refreshed — check back shortly.</p>')
    if "{{news_themes}}" in body:
        counts = {}
        for n in news:
            counts[n.get("topic", "News")] = counts.get(n.get("topic", "News"), 0) + 1
        chips = "".join(f'<span class="tag">{esc(k)} · {v}</span>' for k, v in sorted(counts.items(), key=lambda x: -x[1]))
        srcs = sorted({n.get("source") for n in news if n.get("source")})
        body = body.replace("{{news_themes}}", f'<div class="checks">{chips}</div><p class="small muted mt1">{len(news)} stories from {len(srcs)} sources: {esc(", ".join(srcs))}.</p>')
    if "{{market_cards}}" in body:
        cards = []
        for m in d.get("market", []):
            pts = m.get("points", [])
            if not pts:
                continue
            last, prev = pts[-1][1], (pts[-2][1] if len(pts) > 1 else None)
            ch = ""
            if prev:
                pct = (last - prev) / abs(prev) * 100
                ch = f'<span class="{"up" if pct >= 0 else "down"}">{"▲" if pct >= 0 else "▼"} {abs(pct):.1f}%</span> vs prior'
            dec = 3 if abs(last) < 10 else (2 if abs(last) < 1000 else 0)
            src = m.get("source_url") or f"https://fred.stlouisfed.org/series/{m['id']}"
            cards.append(f'<div class="card mcard"><div class="small muted">{esc(m.get("name"))}</div><div class="v">{last:,.{dec}f}</div>'
                         f'<div class="small">{ch}</div>{sparkline(pts)}<div class="small muted">{esc(m.get("unit", ""))} · latest {esc(nice_date(str(pts[-1][0])))} · '
                         f'<a href="{esc(src)}" target="_blank" rel="noopener nofollow">source</a></div>'
                         f'<p class="small mt1 mb0">{esc(m.get("note", ""))}</p></div>')
        body = body.replace("{{market_cards}}", '<div class="grid g3">' + "".join(cards) + "</div>")
    if "{{fx_table}}" in body:
        fx = d.get("fx", {})
        rows = "".join(f"<tr><td>USD → {esc(k)}</td><td>{v:,.4f}</td><td>{(1 / v):,.5f}</td></tr>" for k, v in fx.get("rates", {}).items() if v)
        body = body.replace("{{fx_table}}", f'<div class="table-wrap"><table class="table"><thead><tr><th>Pair</th><th>1 USD buys</th><th>USD per unit</th></tr></thead><tbody>{rows}</tbody></table></div>'
                            f'<p class="small muted">ECB reference rates dated {esc(nice_date(fx.get("date", "")))}, via Frankfurter. Live rates: <a href="{{{{root}}}}tools.html#tool-fx">currency converter</a>.</p>')
    return body


def schema_for(meta, url, body):
    t = meta.get("schema", "")
    blocks = []
    if t == "article":
        blocks.append({"@context": "https://schema.org", "@type": "Article", "headline": meta.get("title"), "description": meta.get("description"),
                       "datePublished": meta.get("date", TODAY), "dateModified": TODAY, "mainEntityOfPage": url,
                       "author": {"@type": "Organization", "name": "Smart.Supply Editorial"},
                       "publisher": {"@type": "Organization", "name": "Smart.Supply", "url": SITE}})
    if t == "faq" or 'class="faq"' in body:
        qa = re.findall(r"<summary>(.*?)</summary>\s*<p>(.*?)</p>", body, re.S)
        if qa:
            blocks.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": re.sub("<.*?>", "", q), "acceptedAnswer": {"@type": "Answer", "text": re.sub("<.*?>", "", a)}} for q, a in qa]})
    return "".join(f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>' for b in blocks)


def build():
    global V
    daily = load_daily()
    DV = hashlib.sha1(json.dumps(daily, sort_keys=True).encode()).hexdigest()[:8]
    pages, index, lastmods = [], [], {}
    R0 = "__ROOT__"
    open(os.path.join(ROOT, "assets", "js", "layout.js"), "w", encoding="utf-8").write(layout_js(R0))
    V = asset_version()
    for dp, _, files in os.walk(SRC):
        for f in sorted(files):
            if f.endswith(".html"):
                pages.append(os.path.relpath(os.path.join(dp, f), SRC))
    for rel in sorted(pages):
        meta, body = parse(os.path.join(SRC, rel))
        depth = rel.count(os.sep)
        r = "../" * depth
        url_path = rel.replace(os.sep, "/")
        url = f"{SITE}/{'' if url_path == 'index.html' else url_path}"
        title = meta.get("title", "Smart.Supply")
        full_title = title if "Smart.Supply" in title else f"{title} | Smart.Supply"
        desc = meta.get("description", "")
        org = {"@context": "https://schema.org", "@type": "Organization", "name": "Smart.Supply", "url": SITE, "logo": f"{SITE}/assets/img/icon.svg"} if url_path == "index.html" else None
        web = {"@context": "https://schema.org", "@type": "WebSite", "name": "Smart.Supply", "url": SITE, "potentialAction": {"@type": "SearchAction", "target": f"{SITE}/suppliers.html?q={{search_term_string}}", "query-input": "required name=search_term_string"}} if url_path == "index.html" else None
        extra = "".join(f'<script type="application/ld+json">{json.dumps(o)}</script>' for o in (org, web) if o)
        if meta.get("layout") == "guide":
            meta.setdefault("schema", "article")
            body = guide_layout(meta, body)
        if meta.get("layout") == "guide":
            meta.setdefault("slidein", "1")
        body = render_generated(body, daily)
        body = body.replace("{{root}}", r)
        noads = url_path == "404.html" or meta.get("noads")
        adsense = "" if noads else (f'<meta name="google-adsense-account" content="{ADSENSE}">\n'
                   '<script>try{if(JSON.parse(localStorage.getItem("ss-consent"))!=="all")(window.adsbygoogle=window.adsbygoogle||[]).requestNonPersonalizedAds=1}catch(e){}</script>\n'
                   f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE}" crossorigin="anonymous"></script>\n')
        doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="{"noindex" if url_path == "404.html" else "index, follow, max-image-preview:large"}">
<meta name="theme-color" content="#0b1530">
<meta property="og:type" content="{"article" if meta.get("schema") == "article" else "website"}">
<meta property="og:site_name" content="Smart.Supply">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/img/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{r}assets/img/icon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/css/style.css?v={V}">
<script>try{{var t=localStorage.getItem("ss-theme");if(t)document.documentElement.setAttribute("data-theme",JSON.parse(t))}}catch(e){{}}</script>
{adsense}{extra}{schema_for(meta, url, body)}
</head>
<body data-root="{r}"{" data-no-exit" if meta.get("noexit") else ""}{" data-slidein" if meta.get("slidein") else ""}>
<div class="topbar"><a href="{OWNER_CONTACT}" target="_blank" rel="noopener">Contact, if you are interested in this website/domain name/Sponsorship/Advertisement/Partnership</a></div>
<script src="{r}assets/js/layout.js?v={V}"></script><script>SS_render("h")</script>
{'<div class="ticker" data-ticker aria-label="Market ticker"></div>' if meta.get("ticker") else ""}
<main id="main">
{body}
</main>
<script>SS_render("f")</script>
<script src="{r}assets/js/config.js?v={V}"></script>
<script src="{r}assets/js/data.js?v={V}"></script>
<script src="{r}assets/js/daily.js?v={DV}"></script>
<script src="{r}assets/js/search-index.js?v={V}"></script>
<script src="{r}assets/js/app.js?v={V}"></script>
</body>
</html>
'''
        out = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(doc)
        if url_path != "404.html":
            heads = " ".join(re.sub("<.*?>", "", h) for h in re.findall(r"<h[23][^>]*>(.*?)</h[23]>", body, re.S))
            index.append({"t": title, "u": url_path, "d": desc, "k": heads[:400]})
            lastmods[url_path] = (daily.get("updated", LASTMOD)[:10] if meta.get("daily") else meta.get("updated", LASTMOD))
    # Tools as individual search entries
    for tid, name in [("eoq", "EOQ calculator"), ("ss", "Safety stock calculator"), ("rop", "Reorder point calculator"), ("lc", "Landed cost calculator"),
                      ("cbm", "CBM container load calculator"), ("vol", "Volumetric / chargeable weight calculator"), ("turn", "Inventory turnover calculator"),
                      ("co2", "Shipping CO2 emissions calculator"), ("score", "Supplier scorecard")]:
        index.append({"t": name, "u": f"tools.html#tool-{tid}", "d": "Free interactive calculator", "k": ""})
    open(os.path.join(ROOT, "assets", "js", "search-index.js"), "w", encoding="utf-8").write(
        "window.SS_SEARCH=" + json.dumps(index, ensure_ascii=False) + ";\n")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for it in index:
        if "#" in it["u"]:
            continue
        loc = SITE + "/" + ("" if it["u"] == "index.html" else it["u"])
        pr = "1.0" if it["u"] == "index.html" else ("0.9" if it["u"] in ("get-quotes.html", "tools.html", "suppliers.html") else "0.7")
        sm.append(f"  <url><loc>{loc}</loc><lastmod>{lastmods.get(it['u'], LASTMOD)}</lastmod><priority>{pr}</priority></url>")
    sm.append("</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "w").write("\n".join(sm) + "\n")
    print(f"Built {len(pages)} pages.")


if __name__ == "__main__":
    build()
