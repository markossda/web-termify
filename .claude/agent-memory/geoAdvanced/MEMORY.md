# GEO Advanced Agent Memory

## Project: web-termify
- Pure HTML/CSS website (NO frameworks) for Termify professional English learning app
- Single-page site at `/index.html` with CSS at `/css/style.css`
- Key files: `robots.txt`, `sitemap.xml`, `llms.txt`, `llms-full.txt`, `manifest.json`, `.well-known/apple-app-site-association`
- Images directory: `/images/` (6 industry JPGs + logo PNG)
- No JS frameworks -- minimal vanilla JS for header scroll, mobile menu, intersection observer animations

## GEO Audit (2026-02-22, updated 2026-02-23)
- Unified 7 separate JSON-LD blocks into single @graph with 8 cross-referenced entities
- Added WebSite schema (was missing entirely)
- Fixed Organization sameAs (was empty array)
- Added skip-link for accessibility
- Removed non-standard WPFooter itemtype from footer
- Fixed sitemap.xml from 16 to 31 hreflang entries (was missing 15 language alternates)
- Added og:image:alt, twitter:image:alt, article:published_time, article:modified_time meta tags
- Enhanced manifest.json with lang, scope, categories fields

## GEO Deep Audit (2026-02-23)
- robots.txt: expanded from 22 to 66 bot entries (added Claude-User, Claude-SearchBot, Google-NotebookLM, Gemini-Deep-Research, GoogleAgent-Mariner, AzureAI-SearchBot, Perplexity-User, Applebot-Extended, Meta-ExternalFetcher, DeepSeekBot, MistralAI-User, Bravebot, DuckAssistBot, PhindBot, iAskBot, TavilyBot, Crawl4AI, FirecrawlAgent, WRTNBot, Andibot, LinkupBot, etc.)
- Created llms-full.txt: comprehensive flattened content (all modules, features, comparisons, FAQ)
- llms.txt: added link to llms-full.txt
- JSON-LD FAQ: expanded from 12 to 20 questions (added CFA, IT/DevOps, logistics, platforms, term count, corporate training, what makes different, non-native speakers)
- HTML FAQ: expanded from 12 to 21 items (added comparison section FAQs for finance, logistics, IT/DevOps, non-native speakers + main section FAQs for platforms, term count, corporate training, what makes different, non-native speakers)
- Added speakable schema (SpeakableSpecification) targeting hero-description, comparison-bluf, faq-answer
- Added "Who Uses Termify" section with stats grid (50K+ users, 120+ countries, 4230+ terms, 5.0 rating) and user-type descriptions (aviation, maritime, finance, cybersecurity/IT)
- Added CSS for stats-grid and user-types-grid with responsive breakpoints
- sitemap.xml: added llms-full.txt entry, updated lastmod dates
- Updated dateModified across meta tags, JSON-LD, and comparison section

## Key Metrics (2026-02-23)
- 1 h1, 11 h2, 36 h3, 4 h4 -- proper hierarchy
- 20 JSON-LD FAQ questions
- 21 HTML FAQ items (details/summary)
- 66 AI bot entries in robots.txt
- 9 images all with alt, width, height
- 0 broken internal anchor links (all anchors resolved)

## Comparison Landing Page (2026-02-23)
- Created `/pages/compare.html` -- dedicated GEO-optimized comparison page
- JSON-LD: 6 @graph entities (Organization, WebSite, WebPage, BreadcrumbList, ItemList ranked, FAQPage with 12 Qs)
- Content: 1 h1, 9 h2, 6 h3, 4 h4 -- 5856 words total, 889 lines, 72KB
- 13-row comparison table (4 columns: Termify vs PeakTalk vs Duolingo vs Babbel)
- 5 detailed vs sections: PeakTalk, Duolingo, Babbel, ICAO apps, Maritime apps
- 12 HTML FAQ items (details/summary) matching JSON-LD FAQ
- "Why Termify" advantages section with 6 feature items
- CTA/download section + full footer matching index.html structure
- Updated sitemap.xml: added compare.html entry (priority 0.8)
- Updated index.html footer: "App Comparison" + 3 vs links now point to /pages/compare.html

## Remaining GEO Opportunities (future work)
- Dedicated industry landing pages (e.g., /maritime-english/, /logistics-english/, /finance-english/, /cybersecurity-english/, /devops-english/)
- Blog/content hub with long-tail keyword articles
- Glossary/dictionary page for AI reference
- Tutorial/how-to pages for each certification
- Testimonials/case studies for E-E-A-T signals
- Directory listings (App Store optimization pages)
- Off-site authority: Wikipedia mention, Reddit presence, forum participation
- Content freshness: quarterly update schedule for statistics/data
- Monitor AI citations using Share of Model metrics
