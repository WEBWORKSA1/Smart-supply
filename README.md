# Smart.Supply

**The AI-powered sourcing, procurement & supply-chain intelligence hub.**
Source smarter. Ship cheaper. Decide faster.

Static, dependency-free website (HTML + CSS + vanilla JS) built for **lead generation, AdSense, YouTube, sponsorships, affiliates, donations, jobs and contests**.

## What's inside
| Area | Pages |
|---|---|
| Lead generation | `get-quotes.html` (4-step RFQ wizard, freight/3PL quote, software advisor), `list-your-company.html`, exit-intent lead magnet, newsletters |
| Directories | `suppliers.html` (44 established companies described from public information, filters + shortlist; company applications are listed only after the checks in `AGENT.md`), `software.html` |
| Daily (auto) | `news.html` daily brief, `markets.html` market pulse + FX, home-page ticker, tip/term/tool of the day, closures countdown — see `AGENT.md` |
| Tools | `tools.html` — EOQ, safety stock, reorder point, landed cost, CBM, chargeable weight, turnover, CO₂, supplier scorecard, live currency converter |
| Content / SEO | `guides.html` + 14 guides in `/guides`, `glossary.html` (85+ terms), sitemap, schema.org |
| Video | `videos.html` — 10 curated channels; each embeds its latest uploads automatically |
| Community | `contests.html`, `careers.html` (jobs, talent network, hiring) |
| Revenue | `support.html` (donations), `advertise.html` (media kit), AdSense slots site-wide |
| Legal | privacy (AdSense/GDPR/CCPA/PIPEDA), terms, disclaimer, `legal.html` (trademark & copyright), `editorial.html`, 404 |

## Status & owner checklist
- **AdSense:** publisher `ca-pub-6620975821265271` is in the `<head>` of every page (except 404, get-quotes, contact) and in `ads.txt`. In AdSense: add the site `smart.supply`, turn on **Auto ads**, and enable **Privacy & messaging → European regulations** (Google-certified CMP).
- **Forms:** every form is relayed by FormSubmit to the owner inbox (address stored encoded in `config.js`). The first submission triggers a one-time **Activate** email — click it.
- **Domain:** point `smart.supply` DNS to GitHub Pages, then add a `CNAME` file containing `smart.supply` and enable *Enforce HTTPS*. AdSense review needs the domain live.
- **Optional:** donation links, GA4 id, own YouTube channel — all in `assets/js/config.js`.

## Daily automation
A scheduled Claude task runs `AGENT.md` every day: gathers news, FRED market data and FX into `data/inbox.json`, writes original summaries, runs `tools/daily_update.py`, and publishes to `main` + `gh-pages`. Pages also rotate daily content client-side and pull live FX and the latest YouTube uploads in the browser.

## Editing & building
Page sources live in `src/pages/**` (HTML fragments with a front-matter comment). Shared header/footer/SEO are in `tools/build.py`.
```bash
python3 tools/build.py   # regenerates root HTML, search index and sitemap
python3 tools/make_og.py # regenerates assets/img/og.png (needs Pillow)
```
Add a guide: drop `src/pages/guides/my-guide.html` with `layout: guide` in its front matter, then rebuild.

## Hosting
Served by GitHub Pages from the repo root. After editing `src/pages`, run the build and commit the regenerated HTML.

## Docs
- `docs/STRATEGY.md` — concept & revenue model
- `docs/RESEARCH.md` — 45-site competitive research
- `AGENT.md` — daily update runbook
- `docs/BUILD-PROMPT.md` — phase-wise build prompt
