<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
  xmlns:xhtml="http://www.w3.org/1999/xhtml"
  exclude-result-prefixes="sitemap image xhtml">

  <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>

  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml" lang="en">
      <head>
        <title>XML Sitemap — protermify.com</title>
        <meta name="robots" content="noindex, nofollow"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <style type="text/css">
          *{margin:0;padding:0;box-sizing:border-box}
          body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;background:#09090b;color:#fafafa;line-height:1.6;-webkit-font-smoothing:antialiased}
          a{color:#6d5cff;text-decoration:none}
          a:hover{text-decoration:underline;color:#7f71ff}
          .wrap{max-width:1060px;margin:0 auto;padding:2.5rem 1.5rem 4rem}
          .hd{margin-bottom:2rem;padding-bottom:1.5rem;border-bottom:1px solid #2e2e33}
          .hd h1{font-size:1.5rem;font-weight:700;letter-spacing:-0.02em;margin-bottom:0.375rem}
          .hd h1 em{font-style:normal;color:#6d5cff}
          .hd p{font-size:0.875rem;color:#a1a1aa}
          .hd p strong{color:#fafafa}
          .meta{display:flex;gap:1.5rem;margin-top:0.75rem;font-size:0.8125rem;color:#71717a}
          .meta b{color:#a1a1aa;font-weight:600}
          table{width:100%;border-collapse:separate;border-spacing:0;border:1px solid #2e2e33;border-radius:8px;overflow:hidden;margin-top:0.25rem}
          thead th{background:#18181b;padding:0.75rem 1rem;font-size:0.6875rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:#71717a;text-align:left;border-bottom:1px solid #2e2e33}
          tbody tr{border-bottom:1px solid #1f1f23}
          tbody tr:last-child{border-bottom:none}
          tbody tr:hover{background:#141416}
          td{padding:0.625rem 1rem;font-size:0.8125rem;color:#a1a1aa;vertical-align:middle}
          .n{text-align:center;color:#52525b;width:2.5rem;font-variant-numeric:tabular-nums}
          .u{word-break:break-all}
          .u a{font-weight:500}
          .p{width:6rem}
          .bar{display:flex;align-items:center;gap:6px}
          .fill{height:5px;border-radius:3px;background:#6d5cff;display:block}
          .f10{width:50px}.f09{width:45px}.f08{width:40px}.f05{width:25px}.f03{width:15px}
          .pv{font-size:0.75rem;color:#71717a;font-variant-numeric:tabular-nums}
          .bg{display:inline-block;padding:2px 8px;border-radius:9999px;font-size:0.6875rem;font-weight:500;line-height:1.5}
          .bg-w{background:rgba(34,197,94,0.12);color:#4ade80}
          .bg-m{background:rgba(56,189,248,0.12);color:#38bdf8}
          .bg-y{background:rgba(161,161,170,0.12);color:#a1a1aa}
          .bg-d{background:rgba(245,158,11,0.12);color:#fbbf24}
          .ft{margin-top:2rem;padding-top:1.25rem;border-top:1px solid #2e2e33;font-size:0.75rem;color:#52525b;text-align:center}
          @media(max-width:700px){.wrap{padding:1.25rem 1rem 3rem}.hd h1{font-size:1.25rem}.meta{flex-direction:column;gap:0.125rem}th:nth-child(3),td:nth-child(3){display:none}thead th,td{padding:0.5rem 0.625rem;font-size:0.75rem}}
        </style>
      </head>
      <body>
        <div class="wrap">
          <div class="hd">
            <h1><em>Termify</em> — XML Sitemap</h1>
            <p>This sitemap contains <strong><xsl:value-of select="count(sitemap:urlset/sitemap:url)"/></strong> URLs for <a href="https://protermify.com">protermify.com</a></p>
            <div class="meta">
              <span>Last updated: <b><xsl:value-of select="sitemap:urlset/sitemap:url[1]/sitemap:lastmod"/></b></span>
              <span>Protocol: <b>Sitemaps 0.9</b></span>
            </div>
          </div>
          <table>
            <thead>
              <tr>
                <th class="n">#</th>
                <th>URL</th>
                <th>Priority</th>
                <th>Frequency</th>
                <th>Last Modified</th>
              </tr>
            </thead>
            <tbody>
              <xsl:for-each select="sitemap:urlset/sitemap:url">
                <xsl:sort select="sitemap:priority" order="descending" data-type="number"/>
                <tr>
                  <td class="n"><xsl:value-of select="position()"/></td>
                  <td class="u"><a href="{sitemap:loc}"><xsl:value-of select="sitemap:loc"/></a></td>
                  <td class="p">
                    <div class="bar">
                      <xsl:choose>
                        <xsl:when test="sitemap:priority = 1.0 or sitemap:priority = '1.0'"><span class="fill f10"></span></xsl:when>
                        <xsl:when test="sitemap:priority = 0.9 or sitemap:priority = '0.9'"><span class="fill f09"></span></xsl:when>
                        <xsl:when test="sitemap:priority = 0.8 or sitemap:priority = '0.8'"><span class="fill f08"></span></xsl:when>
                        <xsl:when test="sitemap:priority = 0.5 or sitemap:priority = '0.5'"><span class="fill f05"></span></xsl:when>
                        <xsl:when test="sitemap:priority = 0.3 or sitemap:priority = '0.3'"><span class="fill f03"></span></xsl:when>
                        <xsl:otherwise><span class="fill f05"></span></xsl:otherwise>
                      </xsl:choose>
                      <span class="pv"><xsl:value-of select="sitemap:priority"/></span>
                    </div>
                  </td>
                  <td>
                    <xsl:choose>
                      <xsl:when test="sitemap:changefreq = 'daily'"><span class="bg bg-d">daily</span></xsl:when>
                      <xsl:when test="sitemap:changefreq = 'weekly'"><span class="bg bg-w">weekly</span></xsl:when>
                      <xsl:when test="sitemap:changefreq = 'monthly'"><span class="bg bg-m">monthly</span></xsl:when>
                      <xsl:when test="sitemap:changefreq = 'yearly'"><span class="bg bg-y">yearly</span></xsl:when>
                      <xsl:otherwise><span class="bg bg-m"><xsl:value-of select="sitemap:changefreq"/></span></xsl:otherwise>
                    </xsl:choose>
                  </td>
                  <td><xsl:value-of select="sitemap:lastmod"/></td>
                </tr>
              </xsl:for-each>
            </tbody>
          </table>
          <div class="ft">
            Generated for <a href="https://protermify.com">protermify.com</a> — Termify: 100% Free Professional English Learning App
          </div>
        </div>
      </body>
    </html>
  </xsl:template>

</xsl:stylesheet>
