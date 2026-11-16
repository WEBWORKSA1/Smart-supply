# Smart.Supply — Daily Agent Runbook

The site refreshes itself every day through a scheduled Claude task (GitHub Actions is not used).
Everything the agent needs is in this file. Run it top to bottom.

## 1. Get the repo
Clone or download `webworksa1/Smart-supply` (branch `main`) into a working folder.

## 2. Gather fresh inputs (WebFetch)
Write `data/inbox.json` with three keys. Any key may be omitted if a source fails; the updater keeps the previous data.

### news — 8 to 15 items from the last 72 hours
Feeds (RSS/Atom):
- https://www.supplychaindive.com/feeds/news/
- https://www.freightwaves.com/news/feed  (drop items older than 3 days)
- https://www.supplychainbrain.com/rss/articles
- https://www.dcvelocity.com/rss
- https://gcaptain.com/feed/
- https://www.inboundlogistics.com/articles/feed/  (no dates — use today)

Per item: `title`, `url` (the original article), `source`, `date` (YYYY-MM-DD), `summary`, `why`.
- `summary`: ONE original sentence in your own words. Never copy the publisher's text.
- `why`: ONE original sentence on what it means for buyers, importers or supply-chain managers.
These two original lines are what keeps the brief AdSense-compliant (not scraped/thin content).
Skip press releases, sponsored posts, duplicates and anything off-topic.

### market — FRED series (CSV via WebFetch)
`https://fred.stlouisfed.org/graph/fredgraph.csv?id=<ID>` — keep the last ~12 observations.
| ID | name | unit |
|---|---|---|
| GASDESW | US diesel retail price (weekly) | $/gal |
| DCOILWTICO | WTI crude oil spot price | $/bbl |
| TSIFRGHT | Freight Transportation Services Index | index |
| FRGSHPUSM649NCIS | Cass Freight Index: Shipments | index |
| PCU483111483111 | Ocean freight producer prices (deep sea PPI) | index |
| GSCPI | Global Supply Chain Pressure Index (NY Fed) | std dev |

GSCPI is not on FRED: take it from https://www.newyorkfed.org/research/policy/gscpi (latest monthly values). If unavailable, omit it.
Shape: `{"id","name","unit","points":[["YYYY-MM-DD", value], ...]}` (oldest first, skip "." values).

### fx
`https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR,GBP,CNY,INR,CAD,MXN,JPY`
Shape: `{"base":"USD","date":"YYYY-MM-DD","rates":{...}}`

## 3. Build
```bash
python3 tools/daily_update.py
```
Merges the inbox into `assets/js/daily.js`, tags topics, keeps 10 days / 48 items, and rebuilds every page.
Check the output says "Daily update done". Then confirm no address leak:
`grep -rIl "webworksa1" --exclude-dir=.git .` must print nothing.

## 4. Publish (GitHub MCP — git push is not available)
1. `push_files` to `webworksa1/Smart-supply`, branch `main`, message `Daily update YYYY-MM-DD`, with:
   `assets/js/daily.js`, `news.html`, `markets.html`, `index.html`, `sitemap.xml`, `data/inbox.json`
   (plus `assets/js/search-index.js` and `assets/js/layout.js` if they changed).
2. `create_pull_request` head `main` → base `gh-pages`, title `Daily update YYYY-MM-DD`.
3. `merge_pull_request` (merge method `merge`). GitHub Pages serves `gh-pages`.

## Rules
- Never write the owner's email address in plain text anywhere. Forms read it encoded from `config.js`.
- Never add ads code near forms; `get-quotes` and `contact` are `noads`.
- If a step fails, skip it and keep yesterday's data — never publish an empty brief.
