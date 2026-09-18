# Smart.Supply — Phase-Wise Build Prompt

Use these prompts in order. Each phase is self-contained and can be handed to an AI builder or developer. Stack: static HTML5 + CSS3 + vanilla JS (no framework), templated by a tiny Python build script, hosted on GitHub Pages (later Netlify/Vercel + custom domain smart.supply).

---

## PHASE 0 — Positioning & Architecture
> Build **Smart.Supply**, "the AI-powered sourcing & supply-chain intelligence hub". Audience: procurement managers, importers, e-commerce operators, manufacturers, logistics pros, students of supply chain. Value promise: *"Source smarter. Ship cheaper. Decide faster."*
> Create a static multi-page site with a Python build step (`tools/build.py`) that wraps page fragments in `src/pages/**` with a shared header, footer, SEO meta, Open Graph, JSON-LD, and relative asset paths so it works on any sub-path (GitHub Pages) or root domain.
> All third-party IDs (AdSense publisher ID, form endpoint, donation links, YouTube channel, analytics) live in ONE file: `assets/js/config.js`.

## PHASE 1 — Design System & Global Shell
> Create `assets/css/style.css`: CSS custom properties for light/dark themes (navy #0b1530, electric teal #14e0c4, lime accent #b8f35a), Inter + Space Grotesk, 8-pt spacing, radius 14px, glass cards, gradient hero mesh, focus-visible rings, reduced-motion support.
> Global shell: sticky header with logo, mega-menu (Source · Tools · Learn · Watch · Community · Advertise), site search (⌘K), dark-mode toggle, primary CTA "Get Free Quotes". Mobile drawer nav. Footer with 5 link columns, newsletter, social, legal. Cookie-consent banner (required for AdSense in EU/UK/CA). Back-to-top. Toast notifications. Sticky mobile CTA bar.

## PHASE 2 — Home Page (conversion-first)
> Hero with rotating headline, role switcher (I'm a Buyer / Supplier / Logistics pro), and an inline mini-RFQ (product, quantity, email → continues on /get-quotes). Proof/metrics strip (animated counters). Category grid (12 sourcing categories). Tools showcase. "How it works" 3 steps. Latest guides cards. Video hub teaser. Supplier CTA band ("List your company — reach buyers with live RFQs"). Contest teaser. Newsletter with multi-list checkboxes. Sponsor strip. Donation/support band. FAQ with FAQPage schema. AdSense leaderboard + in-feed slots.

## PHASE 3 — Lead Generation Engine (highest priority revenue)
> `get-quotes.html`: 4-step RFQ wizard with progress bar and autosave (localStorage): 1) What you need (category, product description, quantity+unit, target unit price, certifications multi-select) 2) Logistics (destination country, required-by date, Incoterm, shipping mode) 3) About you (name, work email, company, phone with country code, role, company size) 4) Review + consent ("share with up to 5 matched, vetted suppliers") → thank-you with next steps & upsell (free Software Advisor call).
> Additional lead forms: Freight & 3PL quote (origin, destination, mode, weight, CBM, cargo type), Software Advisor (category, users, budget, timeline — "Free 15-min match call"), Supplier Listing application (company, categories, certifications, MOQ, countries served, tier interest), Sponsorship/advertising inquiry, Contact. Exit-intent modal offering the free "2026 Sourcing Checklist". Every form: validation, honeypot anti-spam, UTM capture (source/medium/campaign/referrer/landing page stored in hidden fields), single configurable endpoint (Formspree / Web3Forms / Getform / Supabase), local fallback.

## PHASE 4 — Supplier & Software Directories
> `suppliers.html`: searchable, filterable directory (category, country, certification, MOQ, verification tier) with shortlist (compare up to 3) and "Request quote" buttons that deep-link the RFQ wizard with prefilled supplier/category. Demo listings clearly labelled until real suppliers onboard. Tier cards: Free / Verified ($49/mo) / Premium ($199/mo) / Enterprise.
> `software.html`: SCM software directory by category (ERP, WMS, TMS, Procurement/S2P, Planning, Visibility, Inventory) with filters (deployment, SMB/enterprise, pricing model), editorial notes, "Visit site" (affiliate-ready) and "Get matched" CTA.

## PHASE 5 — Tools (traffic + dwell time)
> `tools.html` with 9 working calculators: EOQ, Safety Stock (service-level Z), Reorder Point, Landed Cost (FOB + freight + insurance + duty + fees), Container Load/CBM (20ft/40ft/40HC fit), Volumetric/Chargeable weight (air 6000, courier 5000), Inventory Turnover & Days of Inventory, Shipping CO₂ estimate (per tonne-km factors by mode), Supplier Scorecard (weighted). Each tool: formula explained, result card, "Email me this result" micro-lead, AdSense slot beside results, share link with query params.

## PHASE 6 — Content & SEO Hub
> `guides.html` hub + long-form guides in `/guides/` (Supply chain management basics, EOQ, Safety stock, Incoterms 2020, How to write an RFQ, Nearshoring & China+1, Landed cost, How to vet a supplier). Each guide: TOC, reading time, in-article ad slots, related tools CTA, RFQ CTA, Article schema. `glossary.html` with 80+ terms, A–Z filter and instant search, DefinedTermSet schema. `sitemap.xml`, `robots.txt`, `ads.txt`, canonical tags, OG images, breadcrumbs.

## PHASE 7 — Video Hub (YouTube monetization)
> `videos.html`: featured video (lite embed — thumbnail first, iframe on click to protect Core Web Vitals), playlists by topic, curated education channels directory, Subscribe CTA to the Smart.Supply channel, "Submit your video" form, sponsor slot. Video IDs managed in `config.js`.

## PHASE 8 — Community, Talent & Contests
> `careers.html`: jobs board (post-a-job form with paid featured option), talent network signup (resume link, skills, availability), "We're hiring" roles for Smart.Supply (writers, video creators, sales, developers).
> `contests.html`: active contest (e.g., "Smart Sourcing Challenge — $1,000 prize pool"), rules, judging criteria, timeline, prize tiers, entry form, past winners, sponsor-a-prize CTA, official rules link.

## PHASE 9 — Support, Donations & Advertising
> `support.html`: donation tiers (Coffee $5 / Backer $25/mo / Champion $100/mo / Custom), one-time vs monthly toggle, where-money-goes breakdown (operations, marketing, contest prizes, hiring), links to PayPal / Stripe Payment Link / Buy Me a Coffee / Ko-fi / GitHub Sponsors (config-driven), supporter wall.
> `advertise.html`: media kit — audience, placements (leaderboard, sponsored guide, newsletter, video integration, category sponsorship, Top-100 list), sponsor tiers Charter / Platinum / Gold, editorial-independence statement, inquiry form.

## PHASE 10 — Trust, Legal & Launch
> about, contact, privacy (AdSense/cookies/GDPR/CCPA/PIPEDA wording), terms, disclaimer, affiliate disclosure, 404. Performance: < 100 KB CSS+JS, lazy images, no render-blocking JS, Lighthouse 95+. Accessibility: semantic landmarks, labels, contrast AA, keyboard nav.
> Deploy: push to GitHub `WEBWORKSA1/smart-supply`, enable GitHub Pages (main / root). Later: add `CNAME` = smart.supply, DNS A records to GitHub Pages IPs, enforce HTTPS.

## PHASE 11 — Growth Roadmap (post-launch)
> Supabase backend for leads + supplier accounts; lead routing & billing; AI sourcing assistant (LLM over directory); weekly newsletter automation; programmatic SEO pages (category × country); annual "Smart Supply 100" awards; paid membership.
