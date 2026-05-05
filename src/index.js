// Passthrough Worker: every request is served from the Static Assets
// binding (env.ASSETS), which maps the repo root onto the URL path.
// No auth, no rewrites, no edge logic — the site is fully static. This
// file exists only because Cloudflare Workers requires a `main` entry
// when wrangler.toml declares one.

export default {
  async fetch(request, env, ctx) {
    return env.ASSETS.fetch(request);
  },
};
