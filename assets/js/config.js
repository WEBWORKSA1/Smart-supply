/* ============================================================
   Smart.Supply — SINGLE CONFIG FILE
   Paste your IDs here. Everything else reads from this object.
   ============================================================ */
window.SS_CONFIG = {
  siteName: "Smart.Supply",
  siteUrl: "https://smart.supply",
  contactEmail: "hello@smart.supply",

  /* Google AdSense — e.g. "ca-pub-1234567890123456".
     Leave empty to show "Advertise here" house ads instead. */
  adsenseClient: "",
  adSlots: { leaderboard: "", inArticle: "", sidebar: "", inFeed: "" },

  /* Google Analytics 4 measurement ID, e.g. "G-XXXXXXX" (optional) */
  ga4: "",

  /* Lead & form capture. Any endpoint that accepts POST (JSON):
     Formspree  -> "https://formspree.io/f/xxxxxxx"
     Web3Forms  -> "https://api.web3forms.com/submit" (+ set web3formsKey)
     Getform, Basin, Supabase edge function, Make/Zapier webhook, etc.
     Empty = submissions are stored in the visitor's browser only (demo mode). */
  formEndpoint: "",
  web3formsKey: "",

  /* Donations / support links (leave "" to hide a button) */
  donate: {
    paypal: "",          // https://paypal.me/yourname
    stripe: "",          // Stripe Payment Link
    buymeacoffee: "",    // https://buymeacoffee.com/yourname
    kofi: "",            // https://ko-fi.com/yourname
    githubSponsors: "",  // https://github.com/sponsors/WEBWORKSA1
    patreon: ""
  },

  /* YouTube — your channel URL + video IDs for the hub */
  youtube: {
    channelUrl: "",                 // https://www.youtube.com/@SmartSupply
    featured: "",                   // video ID, e.g. "dQw4w9WgXcQ"
    videos: [
      /* { id: "VIDEO_ID", title: "EOQ explained in 6 minutes", topic: "Inventory" } */
    ]
  },

  social: { linkedin: "", x: "", youtube: "", instagram: "", facebook: "" }
};
