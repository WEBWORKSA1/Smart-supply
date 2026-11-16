#!/usr/bin/env python3
"""Smart.Supply daily refresh.

The daily agent (see AGENT.md) gathers fresh items into data/inbox.json, then runs:
    python3 tools/daily_update.py
This merges the inbox into assets/js/daily.js (news brief, market pulse, FX),
tags topics, trims stale items, and rebuilds the site (news.html, markets.html,
sitemap.xml). Pure standard library — no network access needed here.

inbox.json shape (any key optional):
{
  "news":   [{"title","url","source","date":"YYYY-MM-DD","summary","why"}],
  "market": [{"id","name","unit","points":[["YYYY-MM-DD", value], ...]}],
  "fx":     {"base":"USD","date":"YYYY-MM-DD","rates":{"EUR":0.9,...}}
}
"""
import datetime, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAILY = os.path.join(ROOT, "assets", "js", "daily.js")
INBOX = os.path.join(ROOT, "data", "inbox.json")
KEEP_DAYS, MAX_ITEMS = 10, 48

TOPICS = [
    ("Tariffs & trade", ["tariff", "trade war", "customs", "duty", "import tax", "section 301", "export control", "sanction"]),
    ("Ocean & ports", ["port", "container", "ocean", "vessel", "ship", "teu", "carrier", "maritime", "hormuz", "suez", "red sea", "panama", "tanker"]),
    ("Trucking & rail", ["truck", "spot rate", "ltl", "rail", "driver", "freight rate", "cross-border", "border"]),
    ("Air & parcel", ["air cargo", "parcel", "usps", "ups", "fedex", "dhl", "drone", "last-mile", "last mile"]),
    ("Warehousing & robotics", ["warehouse", "robot", "automation", "fulfillment", "3pl", "forklift", "lift truck", "humanoid"]),
    ("Manufacturing", ["manufactur", "factory", "foxconn", "production", "plant", "reshoring", "nearshor"]),
    ("Technology & AI", ["ai ", " ai", "software", "digital", "cyber", "data", "platform", "outage", "nvidia"]),
    ("Energy & fuel", ["oil", "diesel", "fuel", "energy", "gas", "opec", "iea"]),
    ("Retail & demand", ["retail", "consumer", "holiday", "cyber monday", "black friday", "inventory", "replenish", "walmart"]),
    ("Labor", ["labor", "union", "teamsters", "strike", "workers", "contract expires"]),
    ("Sustainability", ["emission", "zero-emission", "sustainab", "carbon", "green"]),
]

NOTES = {
    "GASDESW": "Weekly US on-highway diesel price. Truckload fuel surcharges are usually indexed to it, so it moves your landed cost within weeks.",
    "DCOILWTICO": "West Texas Intermediate crude. Feeds diesel, bunker fuel and plastic resin costs with a lag of weeks to months.",
    "TSIFRGHT": "US Bureau of Transportation Statistics index of for-hire freight volumes (trucking, rail, water, air, pipeline). Rising = busier freight economy.",
    "FRGSHPUSM649NCIS": "Cass Freight Index shipment volumes from paid freight bills. A practical read on North American freight demand.",
    "PCU483111483111": "Producer price index for deep-sea freight. Tracks what ocean carriers charge — a proxy for container contract-rate pressure.",
    "GSCPI": "New York Fed Global Supply Chain Pressure Index. 0 = historical average; positive values mean tighter-than-normal global supply conditions.",
}


def topic_for(title, summary=""):
    t = f" {title} {summary} ".lower()
    for name, kws in TOPICS:
        if any(k in t for k in kws):
            return name
    return "Supply chain"


def load(path, default):
    if not os.path.exists(path):
        return default
    raw = open(path, encoding="utf-8").read()
    if path.endswith(".js"):
        raw = raw[raw.index("=") + 1:].strip().rstrip(";")
    return json.loads(raw)


def main():
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    state = load(DAILY, {"news": [], "market": [], "fx": {}})
    inbox = load(INBOX, {})
    # --- news
    by_url = {n["url"]: n for n in state.get("news", []) if n.get("url")}
    for n in inbox.get("news", []) or []:
        if not n.get("url") or not n.get("title"):
            continue
        old = by_url.get(n["url"], {})
        item = {**old, **{k: v for k, v in n.items() if v}}
        item.setdefault("date", old.get("date") or today)
        item["topic"] = n.get("topic") or old.get("topic") or topic_for(item["title"], item.get("summary", ""))
        by_url[n["url"]] = item
    news = list(by_url.values())
    newest = max([n.get("date", today) for n in news] + [today])
    cutoff = (datetime.date.fromisoformat(newest[:10]) - datetime.timedelta(days=KEEP_DAYS)).isoformat()
    news = [n for n in news if (n.get("date") or today) >= cutoff]
    news.sort(key=lambda n: (n.get("date") or "", 1 if n.get("why") else 0), reverse=True)
    state["news"] = news[:MAX_ITEMS]
    # --- market
    series = {m["id"]: m for m in state.get("market", [])}
    for m in inbox.get("market", []) or []:
        if m.get("id") and m.get("points"):
            pts = sorted([[str(p[0])[:10], float(p[1])] for p in m["points"] if p and p[1] is not None])[-24:]
            series[m["id"]] = {**series.get(m["id"], {}), **{k: v for k, v in m.items() if k != "points"}, "points": pts}
    for k, m in series.items():
        m["note"] = NOTES.get(k, m.get("note", ""))
    order = ["GASDESW", "DCOILWTICO", "GSCPI", "PCU483111483111", "FRGSHPUSM649NCIS", "TSIFRGHT"]
    state["market"] = sorted(series.values(), key=lambda m: order.index(m["id"]) if m["id"] in order else 99)
    # --- fx
    if inbox.get("fx", {}).get("rates"):
        state["fx"] = {"base": "USD", "date": inbox["fx"].get("date", today), "rates": {k: v for k, v in inbox["fx"]["rates"].items() if v}}
    state["updated"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    with open(DAILY, "w", encoding="utf-8") as f:
        f.write("/* Generated daily by tools/daily_update.py — do not edit by hand. */\nwindow.SS_DAILY=" +
                json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n")
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build.py")], check=True)
    print(f"Daily update done: {len(state['news'])} news items, {len(state['market'])} series, fx {state.get('fx', {}).get('date')}")


if __name__ == "__main__":
    main()
