// Serves the repo root from the Static Assets binding (env.ASSETS), and puts one notice at the top of every
// HTML page: this site stopped being maintained in May 2026 and was superseded. The pages stay readable as a
// record; the notice says where the live work is.

const NOTICE = `<div role="note" style="background:#171717;color:#fafafa;font:15px/1.5 system-ui,sans-serif;padding:12px 16px;text-align:center">
<strong>Superseded.</strong> This coordination site has not been updated since May 2026 and is kept as a record.
PLANETAI now lives at <a href="https://planetai.fab.city/" style="color:#fafafa">planetai.fab.city</a>; its decisions,
code and docs at <a href="https://github.com/fabcity/planetai-node" style="color:#fafafa">fabcity/planetai-node</a>.
</div>`;

export default {
  async fetch(request, env, ctx) {
    const res = await env.ASSETS.fetch(request);
    if (!(res.headers.get("content-type") || "").includes("text/html")) return res;
    return new HTMLRewriter()
      .on("body", { element(el) { el.prepend(NOTICE, { html: true }); } })
      .transform(res);
  },
};
