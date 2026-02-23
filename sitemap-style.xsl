<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
  xmlns:xhtml="http://www.w3.org/1999/xhtml">

  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>

  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml" lang="en">
      <head>
        <title>Sitemap &mdash; Termify</title>
        <meta name="robots" content="noindex, nofollow"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <style type="text/css">
          * { margin: 0; padding: 0; box-sizing: border-box; }

          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #09090b;
            color: #fafafa;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
          }

          .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 2.5rem 1.5rem 4rem;
          }

          .header {
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid #2e2e33;
          }

          .header h1 {
            font-size: 1.5rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            margin-bottom: 0.5rem;
            color: #fafafa;
          }

          .header h1 span {
            color: #6d5cff;
          }

          .header p {
            font-size: 0.875rem;
            color: #a1a1aa;
          }

          .header p a {
            color: #6d5cff;
            text-decoration: none;
          }

          .header p a:hover {
            text-decoration: underline;
          }

          .stats {
            display: flex;
            gap: 1.5rem;
            margin-top: 1rem;
          }

          .stat {
            font-size: 0.8125rem;
            color: #71717a;
          }

          .stat strong {
            color: #fafafa;
            font-weight: 600;
          }

          table {
            width: 100%;
            border-collapse: collapse;
            border-spacing: 0;
            border: 1px solid #2e2e33;
            border-radius: 8px;
            overflow: hidden;
          }

          thead th {
            background: #18181b;
            padding: 0.75rem 1rem;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #a1a1aa;
            text-align: left;
            border-bottom: 1px solid #2e2e33;
          }

          tbody tr {
            border-bottom: 1px solid #1f1f23;
            transition: background 0.15s ease;
          }

          tbody tr:last-child {
            border-bottom: none;
          }

          tbody tr:hover {
            background: #18181b;
          }

          tbody td {
            padding: 0.625rem 1rem;
            font-size: 0.8125rem;
            color: #a1a1aa;
            vertical-align: middle;
          }

          td.url {
            word-break: break-all;
          }

          td.url a {
            color: #6d5cff;
            text-decoration: none;
            font-weight: 500;
          }

          td.url a:hover {
            text-decoration: underline;
            color: #7f71ff;
          }

          .priority-bar {
            display: inline-flex;
            align-items: center;
            gap: 0.375rem;
          }

          .priority-fill {
            height: 6px;
            border-radius: 3px;
            background: #6d5cff;
            display: inline-block;
          }

          .badge {
            display: inline-block;
            padding: 0.125rem 0.5rem;
            border-radius: 9999px;
            font-size: 0.6875rem;
            font-weight: 500;
          }

          .badge-weekly { background: rgba(34,197,94,0.15); color: #22c55e; }
          .badge-monthly { background: rgba(56,189,248,0.15); color: #38bdf8; }
          .badge-yearly { background: rgba(161,161,170,0.15); color: #a1a1aa; }
          .badge-daily { background: rgba(245,158,11,0.15); color: #f59e0b; }

          .num { text-align: center; color: #71717a; font-variant-numeric: tabular-nums; }

          .footer {
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid #2e2e33;
            font-size: 0.75rem;
            color: #71717a;
            text-align: center;
          }

          .footer a { color: #6d5cff; text-decoration: none; }
          .footer a:hover { text-decoration: underline; }

          @media (max-width: 640px) {
            .container { padding: 1.5rem 1rem 3rem; }
            .header h1 { font-size: 1.25rem; }
            .stats { flex-direction: column; gap: 0.25rem; }
            table { font-size: 0.75rem; }
            thead th, tbody td { padding: 0.5rem 0.625rem; }
            .priority-fill { display: none; }
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1><span>Termify</span> &mdash; XML Sitemap</h1>
            <p>
              This sitemap contains <strong><xsl:value-of select="count(sitemap:urlset/sitemap:url)"/></strong> URLs
              for <a href="https://protermify.com">protermify.com</a>
            </p>
            <div class="stats">
              <div class="stat">Generated: <strong><xsl:value-of select="sitemap:urlset/sitemap:url[1]/sitemap:lastmod"/></strong></div>
              <div class="stat">Protocol: <strong>Sitemaps 0.9</strong></div>
            </div>
          </div>

          <table>
            <thead>
              <tr>
                <th class="num">#</th>
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
                  <td class="num">
                    <xsl:value-of select="position()"/>
                  </td>
                  <td class="url">
                    <a href="{sitemap:loc}">
                      <xsl:value-of select="sitemap:loc"/>
                    </a>
                  </td>
                  <td>
                    <div class="priority-bar">
                      <span class="priority-fill" style="width:{number(sitemap:priority) * 50}px"></span>
                      <xsl:value-of select="sitemap:priority"/>
                    </div>
                  </td>
                  <td>
                    <xsl:choose>
                      <xsl:when test="sitemap:changefreq = 'daily'">
                        <span class="badge badge-daily">daily</span>
                      </xsl:when>
                      <xsl:when test="sitemap:changefreq = 'weekly'">
                        <span class="badge badge-weekly">weekly</span>
                      </xsl:when>
                      <xsl:when test="sitemap:changefreq = 'monthly'">
                        <span class="badge badge-monthly">monthly</span>
                      </xsl:when>
                      <xsl:when test="sitemap:changefreq = 'yearly'">
                        <span class="badge badge-yearly">yearly</span>
                      </xsl:when>
                      <xsl:otherwise>
                        <span class="badge badge-monthly"><xsl:value-of select="sitemap:changefreq"/></span>
                      </xsl:otherwise>
                    </xsl:choose>
                  </td>
                  <td>
                    <xsl:value-of select="sitemap:lastmod"/>
                  </td>
                </tr>
              </xsl:for-each>
            </tbody>
          </table>

          <div class="footer">
            <p>Sitemap generated for <a href="https://protermify.com">Termify</a> &mdash; 100% Free Professional English Learning App</p>
          </div>
        </div>
      </body>
    </html>
  </xsl:template>

</xsl:stylesheet>
