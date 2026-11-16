/* ============================================================
   Smart.Supply — SINGLE CONFIG FILE
   ============================================================ */
window.SS_CONFIG = {
  siteName: "Smart.Supply",
  siteUrl: "https://smart.supply",

  /* Interest / partnership link shown in the top bar of every page */
  ownerContactUrl: "https://web.works/contact",

  /* Google AdSense. The loader script is placed in <head> of every page by
     tools/build.py. Leave adSlots empty to rely on Auto ads (enable Auto ads in
     the AdSense dashboard). Add slot IDs to render manual units. */
  adsenseClient: "ca-pub-6620975821265271",
  adSlots: { leaderboard: "", inArticle: "", sidebar: "", inFeed: "" },

  /* Google Analytics 4 measurement ID, e.g. "G-XXXXXXX" (optional) */
  ga4: "",

  /* Form delivery. All forms are relayed by FormSubmit to the owner's inbox.
     The destination is stored encoded (never shown on the site). After the
     first submission FormSubmit emails an activation link — click it once.
     If FormSubmit later gives you a random-string alias, paste it into
     formAlias and it will be used instead of the encoded address. */
  formRelay: "https://formsubmit.co/ajax/",
  formAlias: "",
  formKey: "bW9jLmxpYW1nQDFhc2tyb3diZXc=",

  /* Donation / payment links (leave "" to hide a button). Without links,
     the support page collects pledges by form and you reply with a link. */
  donate: { paypal: "", stripe: "", buymeacoffee: "", kofi: "", githubSponsors: "", patreon: "" },

  /* YouTube — your own channel (optional). The video hub also embeds the
     latest uploads of curated channels automatically (see data.js). */
  youtube: { channelUrl: "", featured: "", videos: [] },

  social: { linkedin: "", x: "", youtube: "", instagram: "", facebook: "" }
};
