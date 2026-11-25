/* Smart.Supply — app.js (vanilla, no dependencies) */
(function () {
  "use strict";
  var C = window.SS_CONFIG || {}, D = window.SS_DATA || {};
  var ROOT = document.body.getAttribute("data-root") || "";
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };
  var store = {
    get: function (k, d) { try { var v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} },
    ss: function (k, v) { try { if (v === undefined) return sessionStorage.getItem(k); sessionStorage.setItem(k, v); } catch (e) { return null; } }
  };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var fmt = function (n, d) { return Number(n).toLocaleString(undefined, { maximumFractionDigits: d == null ? 2 : d, minimumFractionDigits: 0 }); };
  var qs = new URLSearchParams(location.search);

  /* ---------- Toast ---------- */
  var toastEl;
  function toast(msg) {
    if (!toastEl) { toastEl = document.createElement("div"); toastEl.className = "toast"; toastEl.setAttribute("role", "status"); document.body.appendChild(toastEl); }
    toastEl.textContent = msg; toastEl.classList.add("show");
    clearTimeout(toastEl._t); toastEl._t = setTimeout(function () { toastEl.classList.remove("show"); }, 3200);
  }
  window.SS_toast = toast;

  /* ---------- Theme ---------- */
  var savedTheme = store.get("ss-theme", null);
  if (savedTheme) document.documentElement.setAttribute("data-theme", savedTheme);
  $$("[data-theme-toggle]").forEach(function (b) {
    b.addEventListener("click", function () {
      var cur = document.documentElement.getAttribute("data-theme") || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      var nxt = cur === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", nxt); store.set("ss-theme", nxt);
    });
  });

  /* ---------- Drawer ---------- */
  var drawer = $("#drawer");
  $$("[data-drawer-open]").forEach(function (b) { b.addEventListener("click", function () { drawer.classList.add("open"); drawer.setAttribute("aria-hidden", "false"); }); });
  if (drawer) drawer.addEventListener("click", function (e) { if (e.target === drawer || e.target.closest("[data-drawer-close]") || e.target.tagName === "A") { drawer.classList.remove("open"); drawer.setAttribute("aria-hidden", "true"); } });

  /* ---------- Modals ---------- */
  function openModal(id) { var m = document.getElementById(id); if (m) { m.classList.add("open"); var f = m.querySelector("input,button"); if (f) setTimeout(function () { f.focus(); }, 50); } }
  function closeModal(m) { m.classList.remove("open"); }
  $$(".modal").forEach(function (m) { m.addEventListener("click", function (e) { if (e.target === m || e.target.closest(".modal-close")) closeModal(m); }); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { $$(".modal.open").forEach(closeModal); if (drawer) drawer.classList.remove("open"); }
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); openSearch(); }
    if (e.key === "/" && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) { e.preventDefault(); openSearch(); }
  });
  $$("[data-modal]").forEach(function (b) { b.addEventListener("click", function (e) { e.preventDefault(); openModal(b.getAttribute("data-modal")); }); });

  /* ---------- Search ---------- */
  var SI = window.SS_SEARCH || [];
  (D.glossary || []).forEach(function (g) { SI.push({ t: g[0] + " — glossary", u: "glossary.html#" + slug(g[0]), d: g[1] }); });
  function slug(s) { return String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, ""); }
  function openSearch() { openModal("search-modal"); }
  $$("[data-search-open]").forEach(function (b) { b.addEventListener("click", openSearch); });
  var sInput = $("#search-input"), sRes = $("#search-results");
  if (sInput) {
    var run = function () {
      var q = sInput.value.trim().toLowerCase();
      if (!q) { sRes.innerHTML = '<p class="muted small">Try “EOQ”, “Incoterms”, “landed cost”, “RFQ”, “WMS”…</p>'; return; }
      var words = q.split(/\s+/);
      var hits = SI.map(function (it) {
        var hay = (it.t + " " + it.d + " " + (it.k || "")).toLowerCase(), sc = 0;
        words.forEach(function (w) { if (hay.indexOf(w) > -1) sc += (it.t.toLowerCase().indexOf(w) > -1 ? 3 : 1); else sc -= 5; });
        return { it: it, sc: sc };
      }).filter(function (h) { return h.sc > 0; }).sort(function (a, b) { return b.sc - a.sc; }).slice(0, 10);
      sRes.innerHTML = hits.length ? hits.map(function (h, i) { return '<a href="' + ROOT + h.it.u + '"' + (i === 0 ? ' class="hl"' : "") + "><b>" + esc(h.it.t) + "</b><small>" + esc((h.it.d || "").slice(0, 120)) + "</small></a>"; }).join("") : '<p class="muted">No results. <a href="' + ROOT + 'get-quotes.html">Ask our sourcing team →</a></p>';
    };
    sInput.addEventListener("input", run); run();
    sInput.addEventListener("keydown", function (e) { if (e.key === "Enter") { var a = $("a", sRes); if (a) location.href = a.href; } });
  }

  /* ---------- Consent, AdSense, GA ---------- */
  var consent = store.get("ss-consent", null);
  var cookieBox = $("#cookie");
  if (cookieBox && consent === null) cookieBox.classList.add("show");
  $$("[data-consent]").forEach(function (b) {
    b.addEventListener("click", function () { consent = b.getAttribute("data-consent"); store.set("ss-consent", consent); cookieBox.classList.remove("show"); loadThirdParty(); });
  });
  function loadScript(src, attrs) { var s = document.createElement("script"); s.async = true; s.src = src; if (attrs) Object.keys(attrs).forEach(function (k) { s.setAttribute(k, attrs[k]); }); document.head.appendChild(s); }
  var tpLoaded = false;
  /* AdSense loader lives in <head> (added by tools/build.py) so Google can verify the site.
     Personalization follows the visitor's choice; it takes effect from the next page view. */
  function loadThirdParty() {
    if (tpLoaded) return; tpLoaded = true;
    try { if (consent !== "all") (window.adsbygoogle = window.adsbygoogle || []).requestNonPersonalizedAds = 1; } catch (e) {}
    if (C.ga4 && consent === "all") {
      loadScript("https://www.googletagmanager.com/gtag/js?id=" + C.ga4);
      window.dataLayer = window.dataLayer || []; window.gtag = function () { dataLayer.push(arguments); }; gtag("js", new Date()); gtag("config", C.ga4);
    }
  }
  var houseAds = [
    ["📣", "Reach procurement & logistics buyers on Smart.Supply.", "advertise.html", "Advertise with us"],
    ["🏭", "Suppliers: get matched to live buyer RFQs.", "list-your-company.html", "List your company"],
    ["💚", "Keep Smart.Supply free — become a supporter.", "support.html", "Support us"],
    ["🏆", "Enter the Smart Sourcing Challenge — win prizes.", "contests.html", "Enter now"]
  ];
  $$(".ad-slot").forEach(function (slot, i) {
    var type = slot.getAttribute("data-ad") || "leaderboard";
    var slotId = (C.adSlots || {})[type];
    if (C.adsenseClient && slotId) {
      slot.innerHTML = '<div class="ad-label">Advertisement</div><ins class="adsbygoogle" style="display:block" data-ad-client="' + esc(C.adsenseClient) + '" data-ad-slot="' + esc(slotId) + '" data-ad-format="' + (type === "inArticle" ? "fluid" : "auto") + '"' + (type === "inArticle" ? ' data-ad-layout="in-article"' : "") + ' data-full-width-responsive="true"></ins>';
      try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (e) {}
    } else {
      var h = houseAds[i % houseAds.length];
      slot.innerHTML = '<div class="ad-label">From Smart.Supply</div><div class="ad-placeholder"><span style="font-size:1.3rem">' + h[0] + "</span><span>" + h[1] + '</span><a class="btn btn-sm btn-ghost" href="' + ROOT + h[2] + '">' + h[3] + "</a></div>";
    }
  });
  if (consent !== null) loadThirdParty();

  /* ---------- Forms (lead capture) ---------- */
  var utm = store.get("ss-utm", null);
  if (!utm) {
    utm = { landing: location.pathname, referrer: document.referrer || "direct" };
    ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid"].forEach(function (k) { if (qs.get(k)) utm[k] = qs.get(k); });
    store.set("ss-utm", utm);
  }
  function validate(form) {
    var ok = true;
    $$("input,select,textarea", form).forEach(function (el) {
      if (el.closest(".step") && !el.closest(".step").classList.contains("on") && !form._validateAll) return;
      var err = el.parentElement.querySelector(".err"); var msg = "";
      if (el.hasAttribute("required") && !(el.type === "checkbox" ? el.checked : el.value.trim())) msg = "Required";
      else if (el.type === "email" && el.value && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(el.value)) msg = "Enter a valid email";
      else if (el.type === "url" && el.value && !/^https?:\/\//i.test(el.value)) msg = "Start with https://";
      el.classList.toggle("invalid", !!msg); if (err) err.textContent = msg;
      if (msg && ok) { ok = false; el.focus(); }
    });
    return ok;
  }
  function collect(form) {
    var data = {};
    new FormData(form).forEach(function (v, k) { if (data[k]) data[k] = [].concat(data[k], v); else data[k] = v; });
    data._form = form.getAttribute("data-form"); data._page = location.href; data._ts = new Date().toISOString();
    Object.keys(utm).forEach(function (k) { data["_" + k] = utm[k]; });
    return data;
  }
  function relayAddress() {
    if (C.formAlias) return C.formAlias;
    try { return atob(C.formKey || "").split("").reverse().join(""); } catch (e) { return ""; }
  }
  function send(data) {
    var leads = store.get("ss-leads", []); leads.push(data); store.set("ss-leads", leads.slice(-50));
    if (window.gtag) gtag("event", "generate_lead", { form_name: data._form });
    var to = relayAddress();
    if (!to || !C.formRelay) return Promise.resolve({ local: true });
    var payload = {};
    Object.keys(data).forEach(function (k) { if (k !== "website_hp" && !(k === "website" && !data[k])) payload[k.replace(/^_/, "meta_")] = Array.isArray(data[k]) ? data[k].join(", ") : data[k]; });
    payload._subject = "Smart.Supply — " + (data._form || "form") + (data.email ? " — " + data.email : "");
    payload._template = "table";
    payload._captcha = "false";
    if (data.email) payload._replyto = data.email;
    return fetch(C.formRelay + encodeURIComponent(to), { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(payload) })
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r; });
  }
  window.SS_send = send;
  $$("form[data-form]").forEach(function (form) {
    if (form.id === "rfq-wizard") return;
    form.setAttribute("novalidate", "");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (form.querySelector(".hp input") && form.querySelector(".hp input").value) return;
      if (!validate(form)) return;
      var btn = form.querySelector('[type="submit"]'); var txt = btn ? btn.innerHTML : "";
      if (btn) { btn.disabled = true; btn.innerHTML = "Sending…"; }
      send(collect(form)).then(function () {
        var succ = form.getAttribute("data-success");
        if (succ && document.getElementById(succ)) { form.classList.add("hidden"); document.getElementById(succ).classList.remove("hidden"); }
        else { toast(form.getAttribute("data-thanks") || "Thanks! We'll be in touch shortly."); form.reset(); }
        var m = form.closest(".modal"); if (m) setTimeout(function () { closeModal(m); }, 1400);
      }).catch(function () { toast("Network error — please try again in a moment."); })
        .then(function () { if (btn) { btn.disabled = false; btn.innerHTML = txt; } });
    });
  });

  /* ---------- RFQ wizard ---------- */
  var wiz = $("#rfq-wizard");
  if (wiz) {
    wiz.setAttribute("novalidate", "");
    var steps = $$(".step", wiz), cur = 0, bar = $(".progress i"), labels = $$(".steps-labels span");
    var saved = store.get("ss-rfq-draft", {});
    $$("input,select,textarea", wiz).forEach(function (el) {
      var n = el.name; if (!n) return;
      var pv = qs.get(n) || (n === "category" && qs.get("cat")) || (saved[n] !== undefined ? saved[n] : null);
      if (pv === null || pv === undefined) return;
      if (el.type === "checkbox") el.checked = [].concat(pv).indexOf(el.value) > -1; else el.value = pv;
    });
    if (qs.get("supplier")) { var sp = $("#rfq-supplier"); if (sp) sp.value = qs.get("supplier"); }
    wiz.addEventListener("input", function () { var d = collect(wiz); delete d._page; store.set("ss-rfq-draft", d); });
    var show = function (i) {
      cur = i; steps.forEach(function (s, j) { s.classList.toggle("on", j === i); });
      labels.forEach(function (l, j) { l.classList.toggle("on", j <= i); });
      if (bar) bar.style.width = ((i + 1) / steps.length * 100) + "%";
      $("[data-prev]", wiz).classList.toggle("hidden", i === 0);
      $("[data-next]", wiz).classList.toggle("hidden", i === steps.length - 1);
      $("[data-submit]", wiz).classList.toggle("hidden", i !== steps.length - 1);
      if (i === steps.length - 1) review();
      var top = wiz.getBoundingClientRect().top + scrollY - 100; if (scrollY > top) scrollTo({ top: top, behavior: "smooth" });
    };
    var review = function () {
      var d = collect(wiz), map = { category: "Category", product: "Product", specs: "Specifications", quantity: "Quantity", unit: "Unit", target_price: "Target unit price", certifications: "Certifications", destination: "Destination", needed_by: "Needed by", incoterm: "Incoterm", mode: "Shipping mode", name: "Name", email: "Email", company: "Company", phone: "Phone", role: "Role", company_size: "Company size", supplier: "Preferred supplier" };
      $("#rfq-review").innerHTML = Object.keys(map).filter(function (k) { return d[k] && String(d[k]).trim(); }).map(function (k) { return "<dt>" + map[k] + "</dt><dd>" + esc([].concat(d[k]).join(", ")) + "</dd>"; }).join("");
    };
    $("[data-next]", wiz).addEventListener("click", function () { if (validate(wiz)) show(cur + 1); });
    $("[data-prev]", wiz).addEventListener("click", function () { show(cur - 1); });
    wiz.addEventListener("submit", function (e) {
      e.preventDefault();
      if (cur !== steps.length - 1) { if (validate(wiz)) show(cur + 1); return; }
      if (wiz.querySelector(".hp input").value) return;
      if (!validate(wiz)) return;
      var btn = $("[data-submit]", wiz); btn.disabled = true; btn.textContent = "Submitting…";
      var data = collect(wiz);
      send(data).then(function () {
        store.set("ss-rfq-draft", {}); wiz.classList.add("hidden"); $("#rfq-success").classList.remove("hidden");
        var ref = "SS-" + Date.now().toString(36).toUpperCase().slice(-6); $("#rfq-ref").textContent = ref;
        scrollTo({ top: 0, behavior: "smooth" });
      }).catch(function () { btn.disabled = false; btn.textContent = "Submit RFQ"; toast("Network error — please try again."); });
    });
    show(0);
  }

  /* Mini RFQ (home hero) → wizard */
  var mini = $("#mini-rfq");
  if (mini) mini.addEventListener("submit", function (e) {
    e.preventDefault(); var p = new URLSearchParams();
    $$("input,select", mini).forEach(function (el) { if (el.value) p.set(el.name, el.value); });
    location.href = ROOT + "get-quotes.html?" + p.toString();
  });

  /* ---------- Hero rotator & role switch ---------- */
  var rot = $(".rotator");
  if (rot) {
    var words = (rot.getAttribute("data-words") || "").split("|"), wi = 0;
    setInterval(function () { wi = (wi + 1) % words.length; rot.style.opacity = 0; setTimeout(function () { rot.textContent = words[wi]; rot.style.opacity = 1; }, 200); }, 2600);
    rot.style.transition = "opacity .2s";
  }
  $$(".role-switch button").forEach(function (b) {
    b.addEventListener("click", function () {
      $$(".role-switch button").forEach(function (x) { x.classList.toggle("on", x === b); x.setAttribute("aria-pressed", x === b); });
      var r = b.getAttribute("data-role");
      $$("[data-role-panel]").forEach(function (p) { p.classList.toggle("hidden", p.getAttribute("data-role-panel") !== r); });
    });
  });

  /* ---------- Tabs ---------- */
  $$("[data-tabs]").forEach(function (t) {
    var btns = $$(".tabs button", t);
    btns.forEach(function (b) {
      b.addEventListener("click", function () {
        btns.forEach(function (x) { x.classList.toggle("on", x === b); x.setAttribute("aria-selected", x === b); });
        $$(".tab-panel", t).forEach(function (p) { p.classList.toggle("on", p.id === b.getAttribute("data-tab")); });
      });
    });
    var h = location.hash.slice(1); var hb = btns.filter(function (b) { return b.getAttribute("data-tab") === h; })[0]; if (hb) hb.click();
  });

  /* ---------- Counters & reveal ---------- */
  var io = "IntersectionObserver" in window ? new IntersectionObserver(function (ents) {
    ents.forEach(function (en) {
      if (!en.isIntersecting) return; var el = en.target; io.unobserve(el);
      el.classList.add("in");
      if (el.hasAttribute("data-count")) {
        var end = parseFloat(el.getAttribute("data-count")), suf = el.getAttribute("data-suffix") || "", st = null;
        var step = function (ts) { if (!st) st = ts; var p = Math.min((ts - st) / 1400, 1); el.textContent = fmt(Math.round(end * (1 - Math.pow(1 - p, 3))), 0) + suf; if (p < 1) requestAnimationFrame(step); };
        requestAnimationFrame(step);
      }
    });
  }, { threshold: .2 }) : null;
  $$(".reveal,[data-count]").forEach(function (el) { if (io) io.observe(el); else el.classList.add("in"); });

  /* ---------- Suppliers directory ---------- */
  var supList = $("#supplier-list");
  if (supList) {
    var cats = D.categories || [], catName = {}; cats.forEach(function (c) { catName[c.id] = c.name; });
    var fCat = $("#f-cat"), fCountry = $("#f-country"), fType = $("#f-type"), fQ = $("#f-q");
    var usedCats = cats.filter(function (c) { return D.suppliers.some(function (s) { return s.cat === c.id; }); });
    fCat.innerHTML = '<option value="">All categories</option>' + usedCats.map(function (c) { return '<option value="' + c.id + '">' + c.icon + " " + c.name + "</option>"; }).join("");
    var uniq = function (k) { return Array.from(new Set(D.suppliers.map(function (s) { return s[k]; }))).sort(); };
    fCountry.innerHTML = '<option value="">All countries</option>' + uniq("country").map(function (c) { return "<option>" + esc(c) + "</option>"; }).join("");
    fType.innerHTML = '<option value="">All company types</option>' + uniq("type").map(function (c) { return "<option>" + esc(c) + "</option>"; }).join("");
    if (qs.get("cat")) fCat.value = qs.get("cat");
    if (qs.get("q")) fQ.value = qs.get("q");
    var compare = [];
    var render = function () {
      var q = fQ.value.toLowerCase();
      var list = D.suppliers.filter(function (s) {
        return (!fCat.value || s.cat === fCat.value) && (!fCountry.value || s.country === fCountry.value) && (!fType.value || s.type === fType.value) && (!q || (s.name + " " + s.desc + " " + s.country + " " + s.type + " " + catName[s.cat]).toLowerCase().indexOf(q) > -1);
      });
      $("#sup-count").textContent = list.length + " compan" + (list.length === 1 ? "y" : "ies");
      supList.innerHTML = list.length ? list.map(function (s) {
        var init = s.name.replace(/[^A-Za-z0-9 ]/g, "").split(" ").filter(Boolean).map(function (w) { return w[0]; }).slice(0, 2).join("").toUpperCase();
        return '<article class="card list-card"><div class="avatar">' + esc(init) + '</div><div style="flex:1;min-width:0"><h3 style="margin:0">' + esc(s.name) + '</h3><div class="meta"><span class="tag tag-brand">' + esc(s.type) + '</span><span class="tag">' + esc(catName[s.cat] || "") + '</span><span class="tag">📍 ' + esc(s.country) + '</span></div><p class="muted small mb0">' + esc(s.desc) + '</p></div><div class="actions"><a class="btn btn-sm btn-primary" href="get-quotes.html?category=' + encodeURIComponent(s.cat) + "&supplier=" + encodeURIComponent(s.name) + '">Request quotes</a><a class="btn btn-sm btn-ghost" href="' + esc(s.url) + '" target="_blank" rel="noopener nofollow' + (s.ugc ? " ugc" : "") + '">Website ↗</a><button class="btn btn-sm btn-ghost" data-compare="' + esc(s.name) + '">' + (compare.indexOf(s.name) > -1 ? "✓ Shortlisted" : "+ Shortlist") + "</button></div></article>";
      }).join("") : '<div class="card center"><h3>No match yet</h3><p class="muted">Post an RFQ and our team will source suppliers for you.</p><a class="btn btn-accent" href="get-quotes.html">Post a free RFQ</a></div>';
    };
    [fCat, fCountry, fType].forEach(function (el) { el.addEventListener("change", render); });
    fQ.addEventListener("input", render);
    $("#f-reset").addEventListener("click", function () { [fCat, fCountry, fType, fQ].forEach(function (el) { el.value = ""; }); render(); });
    var cbar = $("#compare-bar");
    supList.addEventListener("click", function (e) {
      var b = e.target.closest("[data-compare]"); if (!b) return;
      var n = b.getAttribute("data-compare"), i = compare.indexOf(n);
      if (i > -1) compare.splice(i, 1); else { if (compare.length >= 3) { toast("Shortlist up to 3 companies"); return; } compare.push(n); }
      $("#compare-count").textContent = compare.length; cbar.classList.toggle("show", compare.length > 0); render();
    });
    $("#compare-go").addEventListener("click", function () { location.href = "get-quotes.html?supplier=" + encodeURIComponent(compare.join("; ")); });
    render();
  }

  /* ---------- Software directory ---------- */
  var swList = $("#software-list");
  if (swList) {
    var swCat = $("#sw-cat"), swSize = $("#sw-size"), swQ = $("#sw-q");
    var swCats = Array.from(new Set(D.software.map(function (s) { return s.cat; })));
    swCat.innerHTML = '<option value="">All categories</option>' + swCats.map(function (c) { return "<option>" + c + "</option>"; }).join("");
    if (qs.get("cat")) swCat.value = qs.get("cat");
    var swRender = function () {
      var q = swQ.value.toLowerCase();
      var list = D.software.filter(function (s) { return (!swCat.value || s.cat === swCat.value) && (!swSize.value || s.size.indexOf(swSize.value) > -1) && (!q || (s.name + s.note + s.cat).toLowerCase().indexOf(q) > -1); });
      swList.innerHTML = list.map(function (s) {
        return '<article class="card"><div class="flex between"><span class="tag tag-brand">' + esc(s.cat) + '</span><span class="tag">' + esc(s.pricing) + '</span></div><h3 class="mt1">' + esc(s.name) + '</h3><p class="muted small">' + esc(s.note) + '</p><p class="small mb0"><b>Best for:</b> ' + esc(s.size) + "<br><b>Deployment:</b> " + esc(s.deploy) + '</p><div class="flex mt1"><a class="btn btn-sm btn-ghost" href="' + esc(s.url) + '" target="_blank" rel="noopener sponsored">Visit site ↗</a><a class="btn btn-sm btn-primary" href="#advisor" data-sw="' + esc(s.name) + '">Get matched</a></div></article>';
      }).join("") || '<p class="muted">No tools match — ask our advisor below.</p>';
    };
    [swCat, swSize].forEach(function (el) { el.addEventListener("change", swRender); }); swQ.addEventListener("input", swRender);
    swList.addEventListener("click", function (e) { var b = e.target.closest("[data-sw]"); if (b) { var f = $("#advisor-tools"); if (f) f.value = b.getAttribute("data-sw"); } });
    swRender();
  }

  /* ---------- Glossary ---------- */
  var gl = $("#glossary-list");
  if (gl) {
    var terms = D.glossary.slice().sort(function (a, b) { return a[0].localeCompare(b[0]); }), letter = "";
    var az = $("#az"), gq = $("#g-q");
    var letters = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
    az.innerHTML = '<button class="on" data-l="">All</button>' + letters.map(function (l) { return '<button data-l="' + l + '">' + l + "</button>"; }).join("");
    az.firstChild.style.width = "auto"; az.firstChild.style.padding = "0 10px";
    var gRender = function () {
      var q = gq.value.toLowerCase();
      var list = terms.filter(function (t) { var f = t[0][0].toUpperCase(); if (/[0-9]/.test(f)) f = "#"; return (!letter || f === letter) && (!q || (t[0] + " " + t[1]).toLowerCase().indexOf(q) > -1); });
      $("#g-count").textContent = list.length + " terms";
      gl.innerHTML = list.map(function (t) { return '<div class="term" id="' + slug(t[0]) + '"><dt>' + esc(t[0]) + "</dt><dd>" + esc(t[1]) + "</dd></div>"; }).join("") || '<p class="muted">No terms found.</p>';
    };
    az.addEventListener("click", function (e) { var b = e.target.closest("button"); if (!b) return; letter = b.getAttribute("data-l"); $$("button", az).forEach(function (x) { x.classList.toggle("on", x === b); }); gRender(); });
    gq.addEventListener("input", gRender); gRender();
    if (location.hash) { var t = document.getElementById(location.hash.slice(1)); if (t) { t.scrollIntoView(); t.style.background = "var(--surface-2)"; } }
  }

  /* ---------- Calculators ---------- */
  function num(id) { var el = document.getElementById(id); return el ? parseFloat(el.value) || 0 : 0; }
  function out(id, html) { var el = document.getElementById(id); if (el) el.innerHTML = html; }
  function rows(arr) { return '<div class="rows">' + arr.map(function (r) { return "<div><span>" + r[0] + "</span><b>" + r[1] + "</b></div>"; }).join("") + "</div>"; }
  var Z = { 80: 0.842, 85: 1.036, 90: 1.282, 95: 1.645, 97: 1.881, 98: 2.054, 99: 2.326, 99.9: 3.09 };
  var calcs = {
    eoq: function () {
      var D1 = num("eoq-d"), S = num("eoq-s"), H = num("eoq-h");
      if (!D1 || !S || !H) return out("eoq-out", '<p>Enter annual demand, order cost and holding cost.</p>');
      var q = Math.sqrt(2 * D1 * S / H), n = D1 / q, tc = n * S + (q / 2) * H;
      out("eoq-out", '<div class="small">Economic order quantity</div><div class="val">' + fmt(q, 0) + ' units</div>' + rows([["Orders per year", fmt(n, 1)], ["Days between orders", fmt(365 / n, 1)], ["Annual ordering cost", "$" + fmt(n * S)], ["Annual holding cost", "$" + fmt(q / 2 * H)], ["Total annual cost", "$" + fmt(tc)]]));
    },
    ss: function () {
      var z = Z[document.getElementById("ss-sl").value] || 1.645, sd = num("ss-sd"), lt = num("ss-lt"), d = num("ss-d"), sdl = num("ss-sdl");
      var ss = z * Math.sqrt(lt * sd * sd + d * d * sdl * sdl);
      out("ss-out", '<div class="small">Safety stock</div><div class="val">' + fmt(Math.ceil(ss), 0) + ' units</div>' + rows([["Z-score", z], ["Reorder point", fmt(Math.ceil(d * lt + ss), 0) + " units"], ["Days of cover", d ? fmt(ss / d, 1) : "—"]]));
    },
    rop: function () {
      var d = num("rop-d"), lt = num("rop-lt"), ss = num("rop-ss"), onhand = num("rop-oh");
      var rop = d * lt + ss;
      out("rop-out", '<div class="small">Reorder point</div><div class="val">' + fmt(rop, 0) + ' units</div>' + rows([["Lead-time demand", fmt(d * lt, 0)], ["Safety stock", fmt(ss, 0)], ["Status", onhand ? (onhand <= rop ? "⚠️ Reorder now" : "✅ OK — " + fmt((onhand - rop) / (d || 1), 1) + " days until reorder") : "Enter on-hand qty"]]));
    },
    lc: function () {
      var qty = num("lc-qty") || 1, unit = num("lc-unit"), fr = num("lc-freight"), ins = num("lc-ins"), dutyP = num("lc-duty"), fees = num("lc-fees"), inland = num("lc-inland"), taxP = num("lc-tax");
      var goods = qty * unit, customsVal = goods + fr + ins, duty = customsVal * dutyP / 100, tax = (customsVal + duty) * taxP / 100, total = customsVal + duty + fees + inland + tax;
      out("lc-out", '<div class="small">Landed cost per unit</div><div class="val">$' + fmt(total / qty) + '</div>' + rows([["Goods value", "$" + fmt(goods)], ["Freight + insurance", "$" + fmt(fr + ins)], ["Duty (" + dutyP + "% of CIF)", "$" + fmt(duty)], ["Import tax/VAT", "$" + fmt(tax)], ["Fees + inland", "$" + fmt(fees + inland)], ["Total landed cost", "$" + fmt(total)], ["Markup over unit price", unit ? fmt((total / qty / unit - 1) * 100, 1) + "%" : "—"]]));
    },
    cbm: function () {
      var l = num("cbm-l"), w = num("cbm-w"), h = num("cbm-h"), n = num("cbm-n") || 1, kg = num("cbm-kg");
      var one = l * w * h / 1e6, tot = one * n, wt = kg * n;
      var cont = [["20ft (≈33 m³ / 28,000 kg)", 33, 28000, 28], ["40ft (≈67 m³ / 26,500 kg)", 67, 26500, 58], ["40ft HC (≈76 m³ / 26,500 kg)", 76, 26500, 68]];
      out("cbm-out", '<div class="small">Total volume</div><div class="val">' + fmt(tot, 3) + ' m³</div>' + rows([["Per carton", fmt(one, 4) + " m³"], ["Total weight", fmt(wt, 1) + " kg"]].concat(cont.map(function (c) { var cap = Math.min(Math.floor(c[3] / (one || 1)), kg ? Math.floor(c[2] / kg) : 1e9); return [c[0], "≈" + fmt(cap, 0) + " cartons · " + fmt(tot / c[3] * 100, 0) + "% used"]; }))) + '<p class="small" style="margin:10px 0 0;color:#c5cee6">Usable volume assumed ≈85% of internal capacity. ' + (tot < 15 ? "Tip: under ~15 m³, LCL is usually cheaper than FCL." : "Tip: above ~15 m³, compare FCL pricing.") + "</p>");
    },
    vol: function () {
      var l = num("vol-l"), w = num("vol-w"), h = num("vol-h"), n = num("vol-n") || 1, kg = num("vol-kg");
      var air = l * w * h / 6000 * n, cour = l * w * h / 5000 * n, act = kg * n;
      out("vol-out", '<div class="small">Chargeable weight (air)</div><div class="val">' + fmt(Math.max(air, act), 1) + ' kg</div>' + rows([["Actual weight", fmt(act, 1) + " kg"], ["Volumetric (air ÷6000)", fmt(air, 1) + " kg"], ["Volumetric (courier ÷5000)", fmt(cour, 1) + " kg"], ["Courier chargeable", fmt(Math.max(cour, act), 1) + " kg"], ["Billed on", Math.max(air, act) === act ? "Actual weight" : "Volume — consider smaller cartons"]]));
    },
    turn: function () {
      var cogs = num("turn-cogs"), b = num("turn-b"), e = num("turn-e");
      var avg = (b + e) / 2, t = avg ? cogs / avg : 0;
      out("turn-out", '<div class="small">Inventory turnover</div><div class="val">' + fmt(t, 2) + '×</div>' + rows([["Average inventory", "$" + fmt(avg)], ["Days of inventory", t ? fmt(365 / t, 1) + " days" : "—"], ["Annual carrying cost @25%", "$" + fmt(avg * .25)]]));
    },
    co2: function () {
      var t = num("co2-t"), km = num("co2-km"), f = parseFloat(document.getElementById("co2-mode").value);
      var kg = t * km * f / 1000;
      out("co2-out", '<div class="small">Estimated emissions</div><div class="val">' + fmt(kg, 1) + ' kg CO₂e</div>' + rows([["Tonne-km", fmt(t * km, 0)], ["Factor used", f + " g CO₂e / t-km"], ["Tonnes CO₂e", fmt(kg / 1000, 3)]]) + '<p class="small" style="margin:10px 0 0;color:#c5cee6">Indicative average factors; use GLEC-accredited data for reporting.</p>');
    },
    score: function () {
      var crit = ["q", "p", "d", "s", "r"], tot = 0, wsum = 0;
      crit.forEach(function (c) { var w = num("sc-w-" + c), s = num("sc-s-" + c); tot += w * s; wsum += w; });
      var sc = wsum ? tot / wsum : 0, grade = sc >= 4.5 ? "A — Strategic partner" : sc >= 3.5 ? "B — Preferred" : sc >= 2.5 ? "C — Approved, monitor" : "D — Improvement plan / exit";
      out("score-out", '<div class="small">Weighted supplier score</div><div class="val">' + fmt(sc, 2) + ' / 5</div>' + rows([["Grade", grade], ["Total weight", fmt(wsum, 0) + "%"]]));
    }
  };
  Object.keys(calcs).forEach(function (k) {
    var box = document.getElementById("tool-" + k); if (!box) return;
    $$("input,select", box).forEach(function (el) { var v = qs.get(el.id); if (v) el.value = v; el.addEventListener("input", calcs[k]); });
    calcs[k]();
    var sh = box.querySelector("[data-share]");
    if (sh) sh.addEventListener("click", function () {
      var p = new URLSearchParams(); $$("input,select", box).forEach(function (el) { if (el.id && el.value) p.set(el.id, el.value); });
      var url = location.origin + location.pathname + "?" + p.toString() + "#tool-" + k;
      (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject()).then(function () { toast("Link copied — share your calculation"); }, function () { prompt("Copy this link:", url); });
    });
  });

  /* ---------- Video hub ---------- */
  function liteEmbed(el, id, title) {
    el.style.backgroundImage = "url(https://i.ytimg.com/vi/" + id + "/hqdefault.jpg)";
    el.innerHTML = '<button class="play" aria-label="Play ' + esc(title || "video") + '" style="background:none;border:0;cursor:pointer"><span>▶</span></button>';
    el.addEventListener("click", function () { el.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0" title="' + esc(title || "YouTube video") + '" allow="accelerometer;autoplay;encrypted-media;gyroscope;picture-in-picture" allowfullscreen></iframe>'; }, { once: true });
  }
  var yt = C.youtube || {};
  $$("[data-yt-featured]").forEach(function (el) {
    if (yt.featured) liteEmbed(el, yt.featured, "Featured video");
    else { el.classList.add("empty"); el.innerHTML = '<div><div style="font-size:2.4rem">▶</div><h3 style="color:#fff">Smart.Supply TV — launching soon</h3><p style="color:#eef">Weekly 5-minute breakdowns: sourcing, freight, inventory and AI in supply chains.</p>' + (yt.channelUrl ? '<a class="btn btn-lime" href="' + esc(yt.channelUrl) + '?sub_confirmation=1" target="_blank" rel="noopener">Subscribe on YouTube</a>' : '<a class="btn btn-lime" href="#notify">Get notified</a>') + "</div>"; }
  });
  var vg = $("#video-grid");
  if (vg && yt.videos && yt.videos.length) {
    vg.innerHTML = yt.videos.map(function (v, i) { return '<div class="card" style="padding:12px"><div class="video-embed" data-v="' + i + '"></div><h3 class="mt1" style="font-size:1rem">' + esc(v.title) + '</h3><span class="tag">' + esc(v.topic || "") + "</span></div>"; }).join("");
    $$("[data-v]", vg).forEach(function (el) { var v = yt.videos[+el.getAttribute("data-v")]; liteEmbed(el, v.id, v.title); });
  }
  $$("[data-yt-sub]").forEach(function (a) { if (yt.channelUrl) { a.href = yt.channelUrl + "?sub_confirmation=1"; a.target = "_blank"; a.rel = "noopener"; } });

  /* ---------- Donations ---------- */
  var don = $("#donate-box");
  if (don) {
    var amt = 25, freq = "monthly";
    $$(".amount-grid button", don).forEach(function (b) { b.addEventListener("click", function () { $$(".amount-grid button", don).forEach(function (x) { x.classList.toggle("on", x === b); }); amt = +b.getAttribute("data-amt"); $("#don-custom").value = ""; upd(); }); });
    $("#don-custom").addEventListener("input", function (e) { amt = +e.target.value || 0; $$(".amount-grid button", don).forEach(function (x) { x.classList.remove("on"); }); upd(); });
    $$("[data-freq]", don).forEach(function (b) { b.addEventListener("click", function () { freq = b.getAttribute("data-freq"); $$("[data-freq]", don).forEach(function (x) { x.classList.toggle("on", x === b); }); upd(); }); });
    var upd = function () { $("#don-summary").textContent = "$" + fmt(amt, 0) + (freq === "monthly" ? " / month" : " one-time"); };
    var dl = C.donate || {}, names = { stripe: "💳 Card (Stripe)", paypal: "PayPal", buymeacoffee: "☕ Buy Me a Coffee", kofi: "Ko-fi", githubSponsors: "GitHub Sponsors", patreon: "Patreon" };
    var btns = Object.keys(names).filter(function (k) { return dl[k]; });
    $("#don-methods").innerHTML = btns.length ? btns.map(function (k, i) { return '<a class="btn ' + (i === 0 ? "btn-accent" : "btn-ghost") + ' btn-block" target="_blank" rel="noopener" data-don="' + k + '" href="' + esc(dl[k]) + '">' + names[k] + "</a>"; }).join("") : '<button type="button" class="btn btn-accent btn-block" data-modal="pledge-modal">Pledge your support</button><p class="small muted mt1">Payment links go live shortly — pledge now and we\'ll send your secure link.</p>';
    $$("[data-modal]", don).forEach(function (b) { b.addEventListener("click", function (e) { e.preventDefault(); var pa = $("#pledge-amount"); if (pa) pa.value = $("#don-summary").textContent; openModal("pledge-modal"); }); });
    $$("[data-don]", don).forEach(function (a) { a.addEventListener("click", function () { if (a.getAttribute("data-don") === "paypal" && /paypal\.me/.test(a.href)) a.href = dl.paypal.replace(/\/$/, "") + "/" + amt; }); });
    upd();
  }

  /* ---------- Countdown ---------- */
  $$("[data-countdown]").forEach(function (el) {
    var end = new Date(el.getAttribute("data-countdown")).getTime();
    var tick = function () {
      var s = Math.max(0, Math.floor((end - Date.now()) / 1000));
      var p = [Math.floor(s / 86400), Math.floor(s % 86400 / 3600), Math.floor(s % 3600 / 60), s % 60];
      el.innerHTML = ["Days", "Hours", "Mins", "Secs"].map(function (l, i) { return "<div><b>" + String(p[i]).padStart(2, "0") + "</b><span>" + l + "</span></div>"; }).join("");
    };
    tick(); setInterval(tick, 1000);
  });

  /* ---------- Exit intent (lead magnet) ---------- */
  if ($("#exit-modal") && !document.body.hasAttribute("data-no-exit") && !store.ss("ss-exit") && matchMedia("(pointer:fine)").matches) {
    var armed = false; setTimeout(function () { armed = true; }, 8000);
    document.addEventListener("mouseout", function h(e) { if (armed && !e.relatedTarget && e.clientY < 10) { store.ss("ss-exit", "1"); openModal("exit-modal"); document.removeEventListener("mouseout", h); } });
  }

  /* ---------- Daily, self-updating content ---------- */
  var DY = window.SS_DAILY || {};
  var dayIdx = Math.floor(Date.now() / 864e5);
  var pick = function (arr, off) { return arr && arr.length ? arr[(dayIdx + (off || 0)) % arr.length] : null; };
  var fmtDate = function (d) { try { return new Date(d + (d.length === 10 ? "T12:00:00Z" : "")).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" }); } catch (e) { return d; } };
  $$("[data-updated]").forEach(function (el) { if (DY.updated) el.textContent = fmtDate(DY.updated); });
  var mk = function (id) { return (DY.market || []).filter(function (m) { return m.id === id; })[0]; };
  function chg(m) { var p = m && m.points; if (!p || p.length < 2) return ""; var a = p[p.length - 1][1], b = p[p.length - 2][1]; var d = (a - b) / b * 100; return '<span class="' + (d >= 0 ? "up" : "down") + '">' + (d >= 0 ? "▲" : "▼") + " " + Math.abs(d).toFixed(1) + "%</span>"; }
  function last(m) { var p = m && m.points; return p && p.length ? p[p.length - 1][1] : null; }
  $$("[data-ticker]").forEach(function (el) {
    var items = [];
    var dsl = mk("GASDESW"), wti = mk("DCOILWTICO"), gs = mk("GSCPI"), ppi = mk("PCU483111483111"), cass = mk("FRGSHPUSM649NCIS");
    if (dsl) items.push(["US diesel", "$" + last(dsl).toFixed(3) + "/gal", chg(dsl)]);
    if (wti) items.push(["WTI crude", "$" + last(wti).toFixed(2), chg(wti)]);
    if (gs) items.push(["Supply-chain pressure (GSCPI)", last(gs).toFixed(2), chg(gs)]);
    if (cass) items.push(["Cass shipments", last(cass).toFixed(3), chg(cass)]);
    if (ppi) items.push(["Ocean freight PPI", last(ppi).toFixed(0), chg(ppi)]);
    var fx = DY.fx && DY.fx.rates;
    if (fx) ["CNY", "INR", "EUR", "MXN", "CAD"].forEach(function (c) { if (fx[c]) items.push(["USD/" + c, Number(fx[c]).toFixed(c === "INR" || c === "JPY" ? 2 : 4), ""]); });
    if (!items.length) { el.classList.add("hidden"); return; }
    var html = items.map(function (i) { return '<span class="tick"><b>' + i[0] + "</b> " + i[1] + " " + i[2] + "</span>"; }).join("");
    el.innerHTML = '<div class="ticker-track">' + html + html + '</div><a class="ticker-more" href="' + ROOT + 'markets.html">Market pulse →</a>';
  });
  var brief = $("#today-brief");
  if (brief && DY.news && DY.news.length) {
    brief.innerHTML = DY.news.slice(0, 6).map(function (n) {
      return '<a class="card card-link news-card" href="' + esc(n.url) + '" target="_blank" rel="noopener"><div class="flex between small muted"><span class="tag tag-brand">' + esc(n.topic || "News") + "</span><span>" + esc(n.source) + (n.date ? " · " + fmtDate(n.date) : "") + '</span></div><h3 class="mt1">' + esc(n.title) + '</h3><p class="muted small mb0">' + esc(n.summary || "") + "</p></a>";
    }).join("");
  }
  var tip = $("#tip-of-day"); if (tip && D.tips) tip.textContent = pick(D.tips);
  var term = $("#term-of-day");
  if (term && D.glossary) { var t = pick(D.glossary, 7); term.innerHTML = "<b>" + esc(t[0]) + "</b> — " + esc(t[1]) + ' <a href="' + ROOT + "glossary.html#" + slug(t[0]) + '">Glossary →</a>'; }
  var toolOfDay = $("#tool-of-day");
  if (toolOfDay) { var tools = [["Landed cost", "lc"], ["EOQ", "eoq"], ["Safety stock", "ss"], ["Reorder point", "rop"], ["CBM & container load", "cbm"], ["Chargeable weight", "vol"], ["Inventory turnover", "turn"], ["Shipping CO₂", "co2"], ["Supplier scorecard", "score"], ["Currency converter", "fx"]]; var tt2 = pick(tools, 3); toolOfDay.innerHTML = '<a href="' + ROOT + "tools.html#tool-" + tt2[1] + '">' + tt2[0] + " calculator →</a>"; }
  var cl = $("#closures");
  if (cl && D.closures) {
    var now = Date.now();
    var up = D.closures.filter(function (c) { return new Date(c.date + "T23:59:59Z").getTime() >= now; }).slice(0, 4);
    cl.innerHTML = up.map(function (c) { var days = Math.max(0, Math.ceil((new Date(c.date + "T00:00:00Z").getTime() - now) / 864e5)); return '<div class="closure"><div class="days"><b>' + days + "</b><span>days</span></div><div><b>" + esc(c.name) + '</b> <span class="muted small">' + fmtDate(c.date) + '</span><p class="small muted mb0">' + esc(c.note) + "</p></div></div>"; }).join("") || '<p class="muted">No closures in the calendar.</p>';
  }

  /* Live currency converter (ECB reference rates via Frankfurter; falls back to the daily snapshot) */
  var fxBox = $("#tool-fx");
  if (fxBox) {
    var fa = $("#fx-amt"), ff = $("#fx-from"), ft = $("#fx-to"), fo = $("#fx-out"), cache = {};
    var snap = DY.fx && DY.fx.rates ? Object.assign({ USD: 1 }, DY.fx.rates) : null;
    var calcFx = function () {
      var amt = parseFloat(fa.value) || 0, f = ff.value, t = ft.value;
      var show = function (rate, src, date) { fo.innerHTML = '<div class="small">' + fmt(amt) + " " + f + ' =</div><div class="val">' + fmt(amt * rate, 2) + " " + t + "</div>" + rows([["Rate", "1 " + f + " = " + fmt(rate, 5) + " " + t], ["Source", src], ["Rate date", date || "—"]]); };
      if (f === t) return show(1, "—", "");
      if (cache[f]) return show(cache[f].rates[t], "ECB reference (live)", cache[f].date);
      fetch("https://api.frankfurter.dev/v1/latest?base=" + f).then(function (r) { return r.json(); }).then(function (j) { if (!j.rates) throw 0; j.rates[f] = 1; cache[f] = j; show(j.rates[t], "ECB reference (live)", j.date); })
        .catch(function () { if (snap && snap[f] && snap[t]) show(snap[t] / snap[f], "Daily snapshot", DY.fx.date); else fo.innerHTML = "<p>Rates unavailable right now.</p>"; });
    };
    [fa, ff, ft].forEach(function (el) { el.addEventListener("input", calcFx); });
    calcFx();
  }

  /* Curated channels: each card embeds the channel's latest uploads (always current) */
  var chGrid = $("#channel-grid");
  if (chGrid && D.channels) {
    chGrid.innerHTML = D.channels.map(function (c, i) {
      return '<div class="card" style="padding:14px"><div class="video-embed channel-embed" data-ch="' + i + '" role="button" tabindex="0" aria-label="Play latest videos from ' + esc(c.name) + '"><div class="play"><span>▶</span></div><div class="ch-name">' + esc(c.name) + '<small>Latest uploads</small></div></div><div class="flex between mt1"><h3 style="font-size:1.05rem;margin:0">' + esc(c.name) + '</h3><span class="tag">' + esc(c.topic) + '</span></div><p class="muted small">' + esc(c.desc) + '</p><a class="small" href="https://www.youtube.com/channel/' + esc(c.id) + '" target="_blank" rel="noopener">Open channel on YouTube ↗</a></div>';
    }).join("");
    $$("[data-ch]", chGrid).forEach(function (el) {
      var go = function () { var c = D.channels[+el.getAttribute("data-ch")]; el.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/videoseries?list=UU' + c.id.slice(2) + '&rel=0" title="Latest videos from ' + esc(c.name) + '" allow="accelerometer;autoplay;encrypted-media;gyroscope;picture-in-picture" allowfullscreen loading="lazy"></iframe>'; };
      el.addEventListener("click", go, { once: true });
      el.addEventListener("keydown", function (e) { if (e.key === "Enter") go(); }, { once: true });
    });
  }

  /* Quick-quote slide-in on content pages (once per session) */
  if (document.body.hasAttribute("data-slidein") && !store.ss("ss-slide")) {
    var si = document.createElement("div");
    si.className = "slidein"; si.setAttribute("role", "dialog"); si.setAttribute("aria-label", "Get supplier quotes");
    si.innerHTML = '<button class="icon-btn modal-close" aria-label="Close">✕</button><b>Sourcing something?</b><p class="small muted">Post one free RFQ and get competing quotes from matched suppliers.</p><form><input name="product" required placeholder="What do you need?" aria-label="Product"><button class="btn btn-accent btn-block mt1" type="submit">Get free quotes →</button></form>';
    document.body.appendChild(si);
    var shown = false;
    addEventListener("scroll", function () { if (shown) return; var h = document.documentElement; if ((h.scrollTop + innerHeight) / h.scrollHeight > 0.55) { shown = true; si.classList.add("show"); store.ss("ss-slide", "1"); } }, { passive: true });
    si.querySelector(".modal-close").addEventListener("click", function () { si.classList.remove("show"); });
    si.querySelector("form").addEventListener("submit", function (e) { e.preventDefault(); location.href = ROOT + "get-quotes.html?product=" + encodeURIComponent(si.querySelector("input").value); });
  }

  /* ---------- Misc ---------- */
  var tt = $(".to-top");
  addEventListener("scroll", function () { if (tt) tt.classList.toggle("show", scrollY > 800); }, { passive: true });
  if (tt) tt.addEventListener("click", function () { scrollTo({ top: 0, behavior: "smooth" }); });
  $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
  $$("[data-social]").forEach(function (a) { var u = (C.social || {})[a.getAttribute("data-social")]; if (u) { a.href = u; a.target = "_blank"; a.rel = "noopener"; } else a.classList.add("hidden"); });
  $$("[data-share-page]").forEach(function (b) {
    b.addEventListener("click", function () {
      if (navigator.share) navigator.share({ title: document.title, url: location.href }).catch(function () {});
      else if (navigator.clipboard) navigator.clipboard.writeText(location.href).then(function () { toast("Link copied"); });
    });
  });
})();
