# Smart.Supply

**The AI-powered sourcing, procurement & supply-chain intelligence hub.**
Source smarter. Ship cheaper. Decide faster.

Static, dependency-free website (HTML + CSS + vanilla JS) built for **lead generation, AdSense, YouTube, sponsorships, affiliates, donations, jobs and contests**.

## What's inside
| Area | Pages |
|---|---|
| Lead generation | `get-quotes.html` (4-step RFQ wizard, freight/3PL quote, software advisor), `list-your-company.html`, exit-intent lead magnet, newsletters |
| Directories | `suppliers.html` (filters + shortlist), `software.html` |
| Tools | `tools.html` — EOQ, safety stock, reorder point, landed cost, CBM, chargeable weight, turnover, CO₂, supplier scorecard |
| Content / SEO | `guides.html` + 8 guides in `/guides`, `glossary.html` (85+ terms), sitemap, schema.org |
| Video | `videos.html` — lite YouTube embeds driven by config |
| Community | `contests.html`, `careers.html` (jobs, talent network, hiring) |
| Revenue | `support.html` (donations), `advertise.html` (media kit), AdSense slots site-wide |
| Legal | privacy (AdSense/GDPR/CCPA/PIPEDA), terms, disclaimer, 404 |

## Go-live checklist (edit `assets/js/config.js` only)
1. **Leads:** set `formEndpoint` (Formspree / Web3Forms / Getform / webhook). Until set, forms run in demo mode (stored in the visitor's browser only).
2. **AdSense:** set `adsenseClient` + `adSlots`, and uncomment your line in `ads.txt`.
3. **Donations:** add PayPal / Stripe Payment Link / Buy Me a Coffee / Ko-fi / GitHub Sponsors URLs.
4. **YouTube:** set `channelUrl`, `featured` and `videos` IDs.
5. **Analytics:** set `ga4`.
6. **Custom domain:** add a `CNAME` file containing `smart.supply`, point DNS to GitHub Pages, enable "Enforce HTTPS".

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
- `docs/RESEARCH.md` — 32-site competitive research
- `docs/BUILD-PROMPT.md` — phase-wise build prompt
