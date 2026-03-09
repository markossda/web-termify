export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname || "/";

    // Free-plan fallback:
    // Keep EN + TR glossary assets, route other locale glossary requests to EN.
    const glossaryLocaleMatch = path.match(/^\/([a-z]{2}(?:-[a-z]{2})?)\/glossary(\/.*)?$/i);
    if (glossaryLocaleMatch) {
      const locale = glossaryLocaleMatch[1].toLowerCase();
      const glossarySuffix = glossaryLocaleMatch[2] || "/";
      if (locale !== "tr") {
        const target = new URL(request.url);
        target.pathname = `/glossary${glossarySuffix}`;
        return Response.redirect(target.toString(), 302);
      }
    }

    // Sitemap fallback for excluded per-locale glossary sitemap files.
    const glossarySitemapMatch = path.match(/^\/sitemap-glossary-([a-z0-9-]+)\.xml$/i);
    if (glossarySitemapMatch) {
      const locale = glossarySitemapMatch[1].toLowerCase();
      if (locale !== "en" && locale !== "tr") {
        const target = new URL(request.url);
        target.pathname = "/sitemap-glossary-en.xml";
        return Response.redirect(target.toString(), 302);
      }
    }

    const response = await env.ASSETS.fetch(request);

    // Set correct Content-Type for XML and XSL files
    if (url.pathname.endsWith('.xml') || url.pathname.endsWith('.xsl')) {
      const headers = new Headers(response.headers);
      headers.set('Content-Type', 'application/xml; charset=utf-8');
      return new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers
      });
    }

    return response;
  }
};
