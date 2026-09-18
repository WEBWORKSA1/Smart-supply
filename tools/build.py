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
import json, os, re, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "pages")
SITE = "https://smart.supply"
TODAY = datetime.date.today().isoformat()
V = TODAY.replace("-", "")  # cache-buster

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
        ("tools.html", "All 9 tools →", "Reorder point, turnover, CO₂, scorecard"),
    ]),
    ("Learn", [
        ("guides.html", "Guides", "Playbooks for sourcing & logistics"),
        ("glossary.html", "Glossary", "85+ supply-chain terms, A–Z"),
        ("software.html", "Software Directory", "ERP, WMS, TMS, procurement, planning"),
        ("guides/incoterms-2020-explained.html", "Incoterms 2020", "Who pays, who carries risk"),
    ]),
    ("videos.html", None),
    ("Community", [
        ("contests.html", "Contests & Prizes", "Smart Sourcing Challenge"),
        ("careers.html", "Jobs & Talent", "Hire or get hired in supply chain"),
        ("support.html", "Support Smart.Supply", "Donate & become a backer"),
        ("about.html", "About", "Our mission"),
    ]),
    ("advertise.html", None),
]
LABELS = {"videos.html": "Watch", "advertise.html": "Advertise"}


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
    <div><h4>Company</h4><ul><li><a href="{r}about.html">About</a></li><li><a href="{r}contact.html">Contact</a></li><li><a href="{r}privacy.html">Privacy</a></li><li><a href="{r}terms.html">Terms</a></li><li><a href="{r}disclaimer.html">Disclaimer &amp; affiliates</a></li></ul></div>
  </div>
  <div class="footer-bottom"><span>© <span data-year>2026</span> Smart.Supply. All rights reserved.</span><span>Independent editorial — sponsors never influence rankings or advice.</span></div>
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
    pages, index = [], []
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
        body = body.replace("{{root}}", r)
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
{extra}{schema_for(meta, url, body)}
</head>
<body data-root="{r}"{" data-no-exit" if meta.get("noexit") else ""}>
<script src="{r}assets/js/layout.js?v={V}"></script><script>SS_render("h")</script>
<main id="main">
{body}
</main>
<script>SS_render("f")</script>
<script src="{r}assets/js/config.js?v={V}"></script>
<script src="{r}assets/js/data.js?v={V}"></script>
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
    # Shared header/footer shell, rendered synchronously by layout.js (keeps every page small)
    R = "__ROOT__"
    js = ("/* Generated by tools/build.py — edit header()/footer() there, not here. */\n"
          "window.SS_LAYOUT=" + json.dumps({"h": header(R, ""), "f": footer(R)}, ensure_ascii=False) + ";\n"
          "function SS_render(k){var r=document.body.getAttribute('data-root')||'';var s=document.currentScript;"
          "s.insertAdjacentHTML('beforebegin',SS_LAYOUT[k].split('__ROOT__').join(r));"
          "if(k==='h'){var here=location.pathname.split('/').pop()||'index.html';"
          "document.querySelectorAll('.menu>li>a').forEach(function(a){if(a.getAttribute('href').split('/').pop()===here)a.classList.add('active')});}}\n")
    open(os.path.join(ROOT, "assets", "js", "layout.js"), "w", encoding="utf-8").write(js)
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
        sm.append(f"  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>")
    sm.append("</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "w").write("\n".join(sm) + "\n")
    print(f"Built {len(pages)} pages.")


if __name__ == "__main__":
    build()
