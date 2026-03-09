#!/usr/bin/env python3
"""
Termify Glossary Generator (Multi-locale)

Reads JSON term data from data/ directory and generates static HTML pages.
Generates glossary pages for all configured locales and multi-file sitemap output.

Usage:
    python3 scripts/generate-glossary.py

Output:
    glossary/...                                       (default locale pages)
    <locale>/glossary/...                             (localized pages)
    sitemap-main.xml                                  (static URLs)
    sitemap-glossary-<locale>.xml                     (glossary URLs by locale)
    sitemap.xml                                       (sitemap index)
    glossary-sitemap-entries.xml                      (default locale glossary entries)
"""

from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SITE_URL = "https://protermify.com"
TODAY = date.today().isoformat()
TODAY_DISPLAY = date.today().strftime("%B %d, %Y")
MAX_URLS_PER_SITEMAP = 50000
SITEMAP_XSL_HREF = f"/sitemap-style.xsl?v={TODAY.replace('-', '')}"

CATEGORY_COLORS = {
    "aviation": "#38bdf8",
    "maritime": "#22c55e",
    "logistics": "#f59e0b",
    "finance": "#a855f7",
    "cybersecurity": "#ef4444",
    "it-devops": "#0ea5e9",
}

CATEGORY_ICONS = {
    "aviation": "&#9992;",
    "maritime": "&#9875;",
    "logistics": "&#128666;",
    "finance": "&#128200;",
    "cybersecurity": "&#128274;",
    "it-devops": "&#9881;",
}

CATEGORY_ORDER = [
    "aviation",
    "maritime",
    "logistics",
    "finance",
    "cybersecurity",
    "it-devops",
]

# 23 interface locales (as listed in product copy).
# translation_key maps to available term translation keys in source JSON.
LOCALES = [
    {"code": "en", "hreflang": "en", "translation_key": "en", "is_default": True},
    {"code": "en-gb", "hreflang": "en-GB", "translation_key": "en", "is_default": False},
    {"code": "tr", "hreflang": "tr", "translation_key": "tr", "is_default": False},
    {"code": "de", "hreflang": "de", "translation_key": "de", "is_default": False},
    {"code": "fr", "hreflang": "fr", "translation_key": "fr", "is_default": False},
    {"code": "es", "hreflang": "es", "translation_key": "es", "is_default": False},
    {"code": "it", "hreflang": "it", "translation_key": "it", "is_default": False},
    {"code": "pt-br", "hreflang": "pt-BR", "translation_key": "pt", "is_default": False},
    {"code": "pt-pt", "hreflang": "pt-PT", "translation_key": "pt", "is_default": False},
    {"code": "ru", "hreflang": "ru", "translation_key": "ru", "is_default": False},
    {"code": "ar", "hreflang": "ar", "translation_key": "ar", "is_default": False},
    {"code": "hi", "hreflang": "hi", "translation_key": "hi", "is_default": False},
    {"code": "ja", "hreflang": "ja", "translation_key": "ja", "is_default": False},
    {"code": "ko", "hreflang": "ko", "translation_key": "en", "is_default": False},
    {"code": "zh-cn", "hreflang": "zh-CN", "translation_key": "zh", "is_default": False},
    {"code": "zh-tw", "hreflang": "zh-TW", "translation_key": "zh", "is_default": False},
    {"code": "id", "hreflang": "id", "translation_key": "id", "is_default": False},
    {"code": "nl", "hreflang": "nl", "translation_key": "en", "is_default": False},
    {"code": "pl", "hreflang": "pl", "translation_key": "en", "is_default": False},
    {"code": "sv", "hreflang": "sv", "translation_key": "en", "is_default": False},
    {"code": "th", "hreflang": "th", "translation_key": "th", "is_default": False},
    {"code": "vi", "hreflang": "vi", "translation_key": "vi", "is_default": False},
    {"code": "ms", "hreflang": "ms", "translation_key": "en", "is_default": False},
]

DEFAULT_LOCALE = next(locale for locale in LOCALES if locale["is_default"])

WHAT_IS_MAP = {
    "en": "What is {term}?",
    "tr": "{term} nedir?",
    "de": "Was ist {term}?",
    "fr": "Qu'est-ce que {term} ?",
    "es": "¿Qué es {term}?",
    "it": "Che cos'e {term}?",
    "pt": "O que e {term}?",
    "ru": "Что такое {term}?",
    "ar": "ما هو {term}؟",
    "hi": "{term} क्या है?",
    "ja": "{term}とは？",
    "zh": "{term} 是什么？",
    "id": "Apa itu {term}?",
    "th": "{term} คืออะไร?",
    "vi": "{term} la gi?",
}

CATEGORY_NAME_MAP = {
    "tr": {
        "aviation": "Havacilik Ingilizcesi",
        "maritime": "Denizcilik Ingilizcesi",
        "logistics": "Lojistik Ingilizcesi",
        "finance": "Finans Ingilizcesi",
        "cybersecurity": "Siber Guvenlik Ingilizcesi",
        "it-devops": "BT/DevOps Ingilizcesi",
    }
}

CATEGORY_DESC_MAP = {
    "tr": {
        "aviation": "Pilotlar, hava trafik kontrolorleri ve havacilik profesyonelleri icin ICAO Doc 9432 ve FAA PCG kaynakli terminoloji.",
        "maritime": "Gemi ve deniz operasyonlari icin IMO SMCP, STCW ve SOLAS standartlarina dayali denizcilik terminolojisi.",
        "logistics": "Incoterms 2020, tasimacilik ve gumruk sureclerini kapsayan lojistik ve tedarik zinciri terminolojisi.",
        "finance": "Sermaye piyasalari, bankacilik ve finansal raporlama sureclerine yonelik finans terminolojisi.",
        "cybersecurity": "ISO 27001 ve NIST cerceveleri ile uyumlu siber guvenlik ve bilgi guvenligi terminolojisi.",
        "it-devops": "CI/CD, gozlemlenebilirlik, IaC ve ITIL pratiklerini kapsayan BT/DevOps terminolojisi.",
    }
}

STATIC_SITEMAP_URLS = [
    ("/", "2026-02-23", "weekly", "1.0", True),
    ("/pages/aviation-english.html", "2026-02-23", "monthly", "0.9", True),
    ("/pages/maritime-english.html", "2026-02-23", "monthly", "0.9", True),
    ("/pages/logistics-english.html", "2026-02-23", "monthly", "0.9", True),
    ("/pages/finance-english.html", "2026-02-23", "monthly", "0.9", True),
    ("/pages/cybersecurity-english.html", "2026-02-23", "monthly", "0.9", True),
    ("/pages/it-devops-english.html", "2026-02-23", "monthly", "0.9", True),
    ("/pages/compare.html", "2026-02-23", "monthly", "0.8", True),
    ("/pages/legal/", "2026-02-23", "yearly", "0.4", True),
    ("/pages/legal/privacy.html", "2026-02-23", "yearly", "0.3", True),
    ("/pages/legal/terms.html", "2026-02-23", "yearly", "0.3", True),
    ("/llms.txt", "2026-02-23", "monthly", "0.5", False),
    ("/llms-full.txt", "2026-02-23", "monthly", "0.5", False),
]


def load_all_categories() -> dict:
    categories = {}
    for filename in sorted(os.listdir(DATA_DIR)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        slug = data["category"]["slug"]
        categories[slug] = data
    return categories


def escape(text) -> str:
    return html.escape(str(text), quote=True)


def format_term_count(total: int) -> str:
    return f"{total:,}+"


def locale_prefix(locale: dict) -> str:
    return "" if locale["is_default"] else f"/{locale['code']}"


def locale_lang_tag(locale: dict) -> str:
    return locale["hreflang"].lower()


def glossary_output_dir(locale: dict) -> str:
    if locale["is_default"]:
        return os.path.join(BASE_DIR, "glossary")
    return os.path.join(BASE_DIR, locale["code"], "glossary")


def localized_value(mapping: dict, locale: dict, fallback: str) -> str:
    if not isinstance(mapping, dict):
        return fallback
    key = locale["translation_key"].lower()
    if key in mapping and mapping[key]:
        return str(mapping[key])
    base_key = key.split("-")[0]
    if base_key in mapping and mapping[base_key]:
        return str(mapping[base_key])
    if "en" in mapping and mapping["en"]:
        return str(mapping["en"])
    return fallback


def locale_base(locale: dict) -> str:
    return locale["translation_key"].split("-")[0].lower()


def tr_text(locale: dict, en_text: str, tr_value: str) -> str:
    if locale_base(locale) == "tr":
        return tr_value
    return en_text


def localized_category_name(cat_slug: str, fallback: str, locale: dict) -> str:
    by_lang = CATEGORY_NAME_MAP.get(locale_base(locale), {})
    return by_lang.get(cat_slug, fallback)


def localized_category_description(cat_slug: str, fallback: str, locale: dict) -> str:
    by_lang = CATEGORY_DESC_MAP.get(locale_base(locale), {})
    return by_lang.get(cat_slug, fallback)


def localized_term_name(term: dict, locale: dict) -> str:
    return localized_value(term.get("termTranslations", {}), locale, term["term"])


def localized_definition(term: dict, locale: dict) -> str:
    definition = term.get("definition", "")
    return localized_value(term.get("definitionTranslations", {}), locale, definition)


def localized_usage(term: dict, locale: dict) -> str:
    usage = term.get("usage", "")
    return localized_value(term.get("usageTranslations", {}), locale, usage)


def what_is_text(locale: dict, term_name: str) -> str:
    key = locale["translation_key"].split("-")[0]
    template = WHAT_IS_MAP.get(key, WHAT_IS_MAP["en"])
    return template.format(term=term_name)


def page_path(locale: dict, page_type: str, cat_slug: str | None = None, term_slug: str | None = None) -> str:
    prefix = locale_prefix(locale)
    if page_type == "main":
        return f"{prefix}/glossary/"
    if page_type == "category":
        return f"{prefix}/glossary/{cat_slug}/"
    if page_type == "term":
        return f"{prefix}/glossary/{cat_slug}/what-is-{term_slug}.html"
    raise ValueError(f"Unknown page type: {page_type}")


def canonical_url(locale: dict, page_type: str, cat_slug: str | None = None, term_slug: str | None = None) -> str:
    return f"{SITE_URL}{page_path(locale, page_type, cat_slug, term_slug)}"


def localized_static_path(path: str, locale: dict) -> str:
    if locale["is_default"]:
        return path
    prefix = locale_prefix(locale)
    if path == "/":
        return f"{prefix}/"
    return f"{prefix}{path}"


def hreflang_links_html(page_type: str, cat_slug: str | None = None, term_slug: str | None = None) -> str:
    lines = []
    for loc in LOCALES:
        href = canonical_url(loc, page_type, cat_slug, term_slug)
        lines.append(f'    <link rel="alternate" hreflang="{loc["hreflang"]}" href="{href}">')
    default_href = canonical_url(DEFAULT_LOCALE, page_type, cat_slug, term_slug)
    lines.append(f'    <link rel="alternate" hreflang="x-default" href="{default_href}">')
    return "\n".join(lines)


def ordered_category_slugs(all_categories: dict) -> list[str]:
    result = [slug for slug in CATEGORY_ORDER if slug in all_categories]
    for slug in sorted(all_categories.keys()):
        if slug not in result:
            result.append(slug)
    return result


def build_all_terms_map(all_categories: dict) -> dict:
    all_terms = {}
    for cat_slug, cat_data in all_categories.items():
        for term in cat_data["terms"]:
            all_terms[term["slug"]] = (term, cat_slug)
    return all_terms


def get_header_html(locale: dict) -> str:
    p = locale_prefix(locale)
    home = f"{p}/" if p else "/"
    industries = f"{home}#industries"
    features = f"{home}#features"
    comparison = f"{home}#comparison"
    faq = f"{home}#faq"
    download = f"{home}#download"
    glossary_link = page_path(locale, "main")
    industries_label = tr_text(locale, "Industries", "Sektorler")
    glossary_label = tr_text(locale, "Glossary", "Sozluk")
    features_label = tr_text(locale, "Features", "Ozellikler")
    compare_label = tr_text(locale, "Compare", "Karsilastir")
    download_label = tr_text(locale, "Download Free", "Ucretsiz Indir")
    return f"""    <!-- ========== HEADER ========== -->
    <header class="header" role="banner" id="top">
        <nav class="header-inner" role="navigation" aria-label="Main navigation">
            <a href="{home}" class="logo" aria-label="Termify Home">
                <img src="/images/termify_logo.png" alt="Termify Logo" class="logo-img" width="32" height="32">
                <span>Termify</span>
            </a>

            <div class="nav-links">
                <a href="{industries}">{industries_label}</a>
                <a href="{glossary_link}">{glossary_label}</a>
                <a href="{features}">{features_label}</a>
                <a href="{comparison}">{compare_label}</a>
                <a href="{faq}">FAQ</a>
            </div>

            <div class="nav-actions">
                <a href="{download}" class="btn btn-primary">{download_label}</a>
            </div>

            <button class="mobile-toggle" aria-label="Toggle menu" aria-expanded="false" aria-controls="mobile-menu" onclick="toggleMobileMenu()">
                <svg viewBox="0 0 24 24" aria-hidden="true"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
            </button>
        </nav>

        <div class="mobile-overlay" id="mobile-overlay" onclick="closeMobileMenu()"></div>
        <div class="mobile-menu" id="mobile-menu" role="navigation" aria-label="Mobile navigation">
            <a href="{industries}" onclick="closeMobileMenu()">{industries_label}</a>
            <a href="{glossary_link}" onclick="closeMobileMenu()">{glossary_label}</a>
            <a href="{features}" onclick="closeMobileMenu()">{features_label}</a>
            <a href="{comparison}" onclick="closeMobileMenu()">{compare_label}</a>
            <a href="{faq}" onclick="closeMobileMenu()">FAQ</a>
            <a href="{download}" class="btn btn-primary" onclick="closeMobileMenu()">{download_label}</a>
        </div>
    </header>"""


def get_footer_html(locale: dict, total_terms_display: str) -> str:
    p = locale_prefix(locale)
    home = f"{p}/" if p else "/"
    aviation = localized_static_path("/pages/aviation-english.html", locale)
    maritime = localized_static_path("/pages/maritime-english.html", locale)
    logistics = localized_static_path("/pages/logistics-english.html", locale)
    finance = localized_static_path("/pages/finance-english.html", locale)
    cyber = localized_static_path("/pages/cybersecurity-english.html", locale)
    it_devops = localized_static_path("/pages/it-devops-english.html", locale)
    privacy = localized_static_path("/pages/legal/privacy.html", locale)
    terms = localized_static_path("/pages/legal/terms.html", locale)
    aviation_name = localized_category_name("aviation", "Aviation English", locale)
    maritime_name = localized_category_name("maritime", "Maritime English", locale)
    logistics_name = localized_category_name("logistics", "Logistics English", locale)
    finance_name = localized_category_name("finance", "Finance English", locale)
    cyber_name = localized_category_name("cybersecurity", "Cybersecurity English", locale)
    it_devops_name = localized_category_name("it-devops", "IT/DevOps English", locale)
    industries_label = tr_text(locale, "Industries", "Sektorler")
    glossary_label = tr_text(locale, "Glossary", "Sozluk")
    contact_label = tr_text(locale, "Contact Us", "Iletisim")
    all_terms_label = tr_text(locale, "All Terms", "Tum Terimler")
    privacy_label = tr_text(locale, "Privacy Policy", "Gizlilik Politikasi")
    terms_label = tr_text(locale, "Terms of Use", "Kullanim Kosullari")
    download_label = tr_text(locale, "Download Free", "Ucretsiz Indir")
    privacy_short = tr_text(locale, "Privacy", "Gizlilik")
    terms_short = tr_text(locale, "Terms", "Kosullar")
    tagline = tr_text(
        locale,
        "The <strong>100% free</strong> professional English app. Learn {count} industry terms for Aviation, Maritime, Logistics, Finance, Cybersecurity and IT/DevOps.",
        "<strong>%100 ucretsiz</strong> profesyonel Ingilizce uygulamasi. Havacilik, denizcilik, lojistik, finans, siber guvenlik ve BT/DevOps alanlarinda {count} terim ogrenin.",
    ).format(count=total_terms_display)
    footer_tagline = tr_text(
        locale,
        "<strong>Termify</strong> &mdash; 100% Free Professional English for Aviation, Maritime, Logistics, Finance, Cybersecurity &amp; IT/DevOps",
        "<strong>Termify</strong> &mdash; Havacilik, denizcilik, lojistik, finans, siber guvenlik ve BT/DevOps icin %100 ucretsiz profesyonel Ingilizce",
    )
    sitemap_label = tr_text(locale, "Sitemap", "Site Haritasi")
    return f"""    <!-- ========== FOOTER ========== -->
    <footer class="footer" role="contentinfo">
        <div class="container">
            <div class="footer-top">
                <div class="footer-grid">
                    <div class="footer-brand">
                        <a href="{home}" class="footer-logo" aria-label="Termify Home">
                            <img src="/images/termify_logo.png" alt="Termify Logo" class="footer-logo-img" width="36" height="36">
                            <span class="footer-logo-text">Termify</span>
                        </a>
                        <p class="footer-brand-desc">{tagline}</p>
                    </div>

                    <nav class="footer-col" aria-label="Industry modules">
                        <h4>{industries_label}</h4>
                        <a href="{aviation}">{aviation_name}</a>
                        <a href="{maritime}">{maritime_name}</a>
                        <a href="{logistics}">{logistics_name}</a>
                        <a href="{finance}">{finance_name}</a>
                        <a href="{cyber}">{cyber_name}</a>
                        <a href="{it_devops}">{it_devops_name}</a>
                    </nav>

                    <nav class="footer-col" aria-label="Glossary">
                        <h4>{glossary_label}</h4>
                        <a href="{p}/glossary/">{all_terms_label}</a>
                        <a href="{p}/glossary/aviation/">{aviation_name}</a>
                        <a href="{p}/glossary/maritime/">{maritime_name}</a>
                        <a href="{p}/glossary/logistics/">{logistics_name}</a>
                        <a href="{p}/glossary/finance/">{finance_name}</a>
                        <a href="{p}/glossary/cybersecurity/">{cyber_name}</a>
                        <a href="{p}/glossary/it-devops/">{it_devops_name}</a>
                    </nav>

                    <div class="footer-col footer-contact">
                        <h4>{contact_label}</h4>
                        <ul>
                            <li><a href="mailto:support@protermify.com" class="footer-contact-item"><span>support@protermify.com</span></a></li>
                            <li><a href="{privacy}" class="footer-contact-item"><span>{privacy_label}</span></a></li>
                            <li><a href="{terms}" class="footer-contact-item"><span>{terms_label}</span></a></li>
                        </ul>
                        <a href="https://apps.apple.com/app/professional-english-termify/id6744872522" class="footer-download-btn" aria-label="Download Termify free on the App Store">{download_label}</a>
                    </div>
                </div>
            </div>

            <div class="footer-bottom">
                <p class="footer-copyright">&copy; 2025 BipBoo Corporation. All rights reserved.</p>
                <p class="footer-tagline">{footer_tagline}</p>
                <div class="footer-bottom-links">
                    <a href="{privacy}">{privacy_short}</a>
                    <a href="{terms}">{terms_short}</a>
                    <a href="/llms.txt">llms.txt</a>
                    <a href="/sitemap.xml">{sitemap_label}</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="/js/main.js" defer></script>"""


def generate_term_page(term: dict, category_data: dict, all_terms_map: dict, locale: dict, total_terms_display: str) -> str:
    cat = category_data["category"]
    cat_slug = cat["slug"]
    cat_name = localized_category_name(cat_slug, cat["name"], locale)
    cat_icon = CATEGORY_ICONS.get(cat_slug, "&#128218;")

    term_name = term["term"]
    term_localized = localized_term_name(term, locale)
    term_slug = term["slug"]
    term_def = localized_definition(term, locale)
    abbreviation = term.get("abbreviation", "")
    subcategory = term.get("subcategory", "")
    source = term.get("source", cat.get("source", ""))
    usage = localized_usage(term, locale)
    related = term.get("relatedTerms", [])
    exam_relevance = term.get("examRelevance", [])
    target_audience = term.get("targetAudience", [])

    title_term = f"{term_localized} ({abbreviation})" if abbreviation else term_localized
    page_title_h1 = what_is_text(locale, title_term)
    page_title = tr_text(
        locale,
        f"{page_title_h1} &mdash; {cat_name} Definition | Termify",
        f"{page_title_h1} &mdash; {cat_name} Tanimi | Termify",
    )
    meta_title = tr_text(
        locale,
        f"{page_title_h1} — {cat_name} Definition | Termify",
        f"{page_title_h1} — {cat_name} Tanimi | Termify",
    )
    meta_description = term_def[:155].rstrip(".") + "." if len(term_def) > 155 else term_def
    page_url = canonical_url(locale, "term", cat_slug, term_slug)

    related_html = ""
    if related:
        related_items = []
        for r_slug in related:
            if r_slug not in all_terms_map:
                continue
            r_term, r_cat_slug = all_terms_map[r_slug]
            r_name = localized_term_name(r_term, locale)
            r_url = page_path(locale, "term", r_cat_slug, r_slug)
            related_items.append(f'<a href="{r_url}" class="glossary-related-link">{escape(r_name)}</a>')
        if related_items:
            related_html = f"""
                <section class="glossary-related">
                    <h2>{tr_text(locale, f"Related {escape(cat_name)} Terms", "Ilgili Terimler")}</h2>
                    <div class="glossary-related-grid">
                        {"".join(related_items)}
                    </div>
                </section>"""

    exam_html = ""
    if exam_relevance:
        tags = "".join(f'<span class="glossary-exam-tag">{escape(tag)}</span>' for tag in exam_relevance)
        exam_html = f"""
                <div class="glossary-exam-section">
                    <h3>{tr_text(locale, "Certification Exam Relevance", "Sertifika Sinav Iliskisi")}</h3>
                    <div class="glossary-exam-tags">{tags}</div>
                </div>"""

    usage_html = ""
    if usage:
        usage_html = f"""
                <section class="glossary-usage">
                    <h2>{tr_text(locale, f'How is &ldquo;{escape(term_localized)}&rdquo; Used in Practice?', f'&ldquo;{escape(term_localized)}&rdquo; Pratikte Nasil Kullanilir?')}</h2>
                    <blockquote class="glossary-usage-quote">
                        <p>{escape(usage)}</p>
                    </blockquote>
                </section>"""

    audience_html = ""
    if target_audience:
        items = "".join(f"<li>{escape(item)}</li>" for item in target_audience)
        audience_html = f"""
                <section class="glossary-audience">
                    <h3>{tr_text(locale, "Who Needs to Know This Term?", "Bu Terimi Kimlerin Bilmesi Gerekir?")}</h3>
                    <ul class="glossary-audience-list">{items}</ul>
                </section>"""

    related_jsonld = ""
    if related:
        related_urls = []
        for r_slug in related:
            if r_slug in all_terms_map:
                _, r_cat_slug = all_terms_map[r_slug]
                related_urls.append(canonical_url(locale, "term", r_cat_slug, r_slug))
        if related_urls:
            related_jsonld = ',\n                "relatedLink": ' + json.dumps(related_urls)

    in_lang = locale["hreflang"]
    question_1 = what_is_text(locale, term_localized)

    jsonld = f"""    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@graph": [
            {{
                "@type": "DefinedTerm",
                "@id": "{page_url}#term",
                "name": {json.dumps(term_localized)},
                "description": {json.dumps(term_def)},
                "inDefinedTermSet": {{
                    "@type": "DefinedTermSet",
                    "name": "Termify {escape(cat_name)} Glossary",
                    "url": "{canonical_url(locale, 'category', cat_slug)}"
                }}{related_jsonld}
            }},
            {{
                "@type": "WebPage",
                "@id": "{page_url}#webpage",
                "url": "{page_url}",
                "name": {json.dumps(meta_title)},
                "description": {json.dumps(meta_description)},
                "datePublished": "{TODAY}",
                "dateModified": "{TODAY}",
                "inLanguage": "{in_lang}",
                "isPartOf": {{ "@id": "{SITE_URL}/#website" }},
                "breadcrumb": {{ "@id": "{page_url}#breadcrumb" }},
                "mainEntity": {{ "@id": "{page_url}#term" }}
            }},
            {{
                "@type": "BreadcrumbList",
                "@id": "{page_url}#breadcrumb",
                "itemListElement": [
                    {{ "@type": "ListItem", "position": 1, "name": {json.dumps(tr_text(locale, "Home", "Ana Sayfa"))}, "item": "{SITE_URL}/" }},
                    {{ "@type": "ListItem", "position": 2, "name": {json.dumps(tr_text(locale, "Glossary", "Sozluk"))}, "item": "{canonical_url(locale, 'main')}" }},
                    {{ "@type": "ListItem", "position": 3, "name": {json.dumps(cat_name)}, "item": "{canonical_url(locale, 'category', cat_slug)}" }},
                    {{ "@type": "ListItem", "position": 4, "name": {json.dumps(page_title_h1)} }}
                ]
            }},
            {{
                "@type": "FAQPage",
                "@id": "{page_url}#faq",
                "mainEntity": [
                    {{
                        "@type": "Question",
                        "name": {json.dumps(question_1)},
                        "acceptedAnswer": {{
                            "@type": "Answer",
                            "text": {json.dumps(term_def)}
                        }}
                    }},
                    {{
                        "@type": "Question",
                        "name": {json.dumps(tr_text(locale, 'Where can I learn this term for free?', 'Bu terimi ucretsiz nerede ogrenebilirim?'))},
                        "acceptedAnswer": {{
                            "@type": "Answer",
                            "text": {json.dumps(tr_text(
                                locale,
                                f'Termify is a 100% free professional English app that teaches {term_localized} and {total_terms_display} other industry terms with native pronunciation, IPA transcriptions and career quizzes. Available on iOS in 23 languages.',
                                f"Termify, {term_localized} ve {total_terms_display} sektor terimini ana dil telaffuzu, IPA transkripsiyonlari ve kariyer quizleri ile ogreten %100 ucretsiz profesyonel Ingilizce uygulamasidir. iOS'ta 23 dilde kullanilabilir."
                            ))}
                        }}
                    }}
                ]
            }}
        ]
    }}
    </script>"""

    subcategory_html = f'<span class="glossary-subcategory">{escape(subcategory)}</span>' if subcategory else ""
    source_html = f'<p class="glossary-source"><strong>{tr_text(locale, "Source:", "Kaynak:")}</strong> {escape(source)}</p>' if source else ""

    return f"""<!DOCTYPE html>
<html lang="{locale_lang_tag(locale)}" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>{page_title}</title>
    <meta name="description" content="{escape(meta_description)}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">

    <link rel="canonical" href="{page_url}">
{hreflang_links_html('term', cat_slug, term_slug)}

    <meta property="og:type" content="article">
    <meta property="og:url" content="{page_url}">
    <meta property="og:title" content="{escape(meta_title)}">
    <meta property="og:description" content="{escape(meta_description)}">
    <meta property="og:image" content="{SITE_URL}/images/termify_logo.png">
    <meta property="og:site_name" content="Termify">
    <meta property="article:published_time" content="{TODAY}T00:00:00+00:00">
    <meta property="article:modified_time" content="{TODAY}T00:00:00+00:00">

    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{escape(meta_title)}">
    <meta name="twitter:description" content="{escape(meta_description)}">

    <meta name="apple-itunes-app" content="app-id=6744872522">

    <link rel="icon" type="image/png" href="/images/termify_logo.png">
    <link rel="apple-touch-icon" href="/images/termify_logo.png">
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#09090b">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">

    <link rel="stylesheet" href="/css/style.css">

{jsonld}
</head>

<body>
    <a href="#content" class="skip-link">{tr_text(locale, "Skip to main content", "Ana icerige gec")}</a>

{get_header_html(locale)}

    <main role="main" id="content">

        <nav class="breadcrumb-nav" aria-label="Breadcrumb">
            <div class="container">
                <ol class="breadcrumb-list">
                    <li><a href="/">{tr_text(locale, "Home", "Ana Sayfa")}</a></li>
                    <li><a href="{page_path(locale, 'main')}">{tr_text(locale, "Glossary", "Sozluk")}</a></li>
                    <li><a href="{page_path(locale, 'category', cat_slug)}">{escape(cat_name)}</a></li>
                    <li aria-current="page">{escape(page_title_h1)}</li>
                </ol>
            </div>
        </nav>

        <article class="glossary-article" data-field="{cat_slug}">
            <div class="container">
                <div class="glossary-header">
                    <div class="glossary-category-badge" data-field="{cat_slug}">
                        <span class="glossary-cat-icon" aria-hidden="true">{cat_icon}</span>
                        <span>{escape(cat_name)}</span>
                    </div>
                    {subcategory_html}

                    <h1 id="main-heading">{escape(page_title_h1)}</h1>

                    <p class="glossary-definition-lead"><strong>{escape(term_localized)}</strong> {escape(term_def)}</p>

                    {source_html}
                </div>

                {usage_html}

                {exam_html}

                {audience_html}

                {related_html}

                <section class="glossary-cta">
                    <div class="glossary-cta-card">
                        <img src="/images/termify_logo.png" alt="Termify Logo" width="56" height="56" class="glossary-cta-logo">
                        <h2>{tr_text(locale, f'Learn &ldquo;{escape(term_localized)}&rdquo; Free with Termify', f'Termify ile &ldquo;{escape(term_localized)}&rdquo; terimini ucretsiz ogrenin')}</h2>
                        <p>{tr_text(locale, f'Master <strong>{escape(term_localized)}</strong> and {total_terms_display} professional terms with native pronunciation, IPA transcriptions and career quizzes. <strong>100% free, forever.</strong>', f'<strong>{escape(term_localized)}</strong> ve {total_terms_display} profesyonel terimi ana dil telaffuzu, IPA transkripsiyonlari ve kariyer quizleri ile ogrenin. <strong>%100 ucretsiz, daima.</strong>')}</p>
                        <a href="https://apps.apple.com/app/professional-english-termify/id6744872522" class="btn btn-primary btn-lg">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/></svg>
                            {tr_text(locale, "Download Free for iOS", "iOS icin Ucretsiz Indir")}
                        </a>
                    </div>
                </section>

                <section class="glossary-faq">
                    <h2>{tr_text(locale, "Frequently Asked Questions", "Sik Sorulan Sorular")}</h2>
                    <div class="faq-grid">
                        <details class="faq-item" open>
                            <summary><strong>{escape(question_1)}</strong></summary>
                            <div class="faq-answer">
                                <p>{escape(term_def)}</p>
                            </div>
                        </details>
                        <details class="faq-item">
                            <summary><strong>{tr_text(locale, "Where can I learn this term for free?", "Bu terimi ucretsiz nerede ogrenebilirim?")}</strong></summary>
                            <div class="faq-answer">
                                <p>{tr_text(locale, f'Termify is a 100% free professional English app that teaches {escape(term_localized)} and {total_terms_display} other industry terms with native pronunciation, IPA transcriptions and career quizzes. Available on iOS in 23 languages. No subscription, no credit card required.', f"Termify, {escape(term_localized)} ve {total_terms_display} sektor terimini ana dil telaffuzu, IPA transkripsiyonlari ve kariyer quizleri ile ogreten %100 ucretsiz profesyonel Ingilizce uygulamasidir. iOS'ta 23 dilde kullanilabilir. Abonelik veya kredi karti gerekmez.")}</p>
                            </div>
                        </details>
                    </div>
                </section>

                <p class="page-last-updated">{tr_text(locale, "Last updated:", "Son guncelleme:")} <time datetime="{TODAY}">{TODAY_DISPLAY}</time></p>
            </div>
        </article>

    </main>

{get_footer_html(locale, total_terms_display)}
</body>
</html>"""


def generate_category_index(category_data: dict, all_categories: dict, locale: dict, total_terms_display: str) -> str:
    cat = category_data["category"]
    cat_slug = cat["slug"]
    cat_name = localized_category_name(cat_slug, cat["name"], locale)
    cat_icon = CATEGORY_ICONS.get(cat_slug, "&#128218;")

    terms = sorted(category_data["terms"], key=lambda t: localized_term_name(t, locale).lower())

    page_url = canonical_url(locale, "category", cat_slug)
    page_title = tr_text(
        locale,
        f"{cat_name} Glossary &mdash; {len(terms)}+ Professional Terms | Termify",
        f"{cat_name} Sozlugu &mdash; {len(terms)}+ Profesyonel Terim | Termify",
    )
    meta_title = tr_text(
        locale,
        f"{cat_name} Glossary — {len(terms)}+ Professional Terms | Termify",
        f"{cat_name} Sozlugu — {len(terms)}+ Profesyonel Terim | Termify",
    )
    meta_description = tr_text(
        locale,
        f"Complete {cat_name.lower()} glossary with {len(terms)}+ professional term definitions. Learn what each term means with free pronunciation and examples from Termify.",
        f"{cat_name.lower()} alaninda {len(terms)}+ profesyonel terimin bulundugu kapsamli sozluk. Her terimin anlamini, telaffuzunu ve ornek kullanimini Termify ile ogrenin.",
    )

    letters: dict[str, list[dict]] = {}
    for term in terms:
        name = localized_term_name(term, locale)
        first = name[0].upper() if name else "#"
        letters.setdefault(first, []).append(term)

    all_letters = sorted(letters.keys())
    letter_nav = "".join(f'<a href="#letter-{escape(letter)}" class="glossary-letter-link">{escape(letter)}</a>' for letter in all_letters)

    term_sections = ""
    for letter in all_letters:
        items = ""
        for term in letters[letter]:
            local_name = localized_term_name(term, locale)
            term_def = localized_definition(term, locale)
            short_def = term_def[:120].rstrip(".") + "..." if len(term_def) > 120 else term_def
            term_url = page_path(locale, "term", cat_slug, term["slug"])
            what_is_local = what_is_text(locale, local_name)
            items += f"""
                        <li class="glossary-index-item">
                            <a href="{term_url}">
                                <strong>{escape(what_is_local)}</strong>
                                <span class="glossary-index-def">{escape(short_def)}</span>
                            </a>
                        </li>"""
        term_sections += f"""
                    <div class="glossary-letter-group" id="letter-{escape(letter)}">
                        <h2 class="glossary-letter-heading">{escape(letter)}</h2>
                        <ul class="glossary-index-list">{items}
                        </ul>
                    </div>"""

    term_items_jsonld = []
    for term in terms[:50]:
        term_items_jsonld.append(
            f"""
                    {{
                        "@type": "DefinedTerm",
                        "name": {json.dumps(localized_term_name(term, locale))},
                        "description": {json.dumps(localized_definition(term, locale)[:200])},
                        "url": "{canonical_url(locale, 'term', cat_slug, term['slug'])}"
                    }}"""
        )

    jsonld = f"""    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@graph": [
            {{
                "@type": "DefinedTermSet",
                "@id": "{page_url}#termset",
                "name": "Termify {escape(cat_name)} Glossary",
                "description": {json.dumps(meta_description)},
                "url": "{page_url}",
                "hasDefinedTerm": [{','.join(term_items_jsonld)}
                ]
            }},
            {{
                "@type": "WebPage",
                "@id": "{page_url}#webpage",
                "url": "{page_url}",
                "name": {json.dumps(meta_title)},
                "datePublished": "{TODAY}",
                "dateModified": "{TODAY}",
                "inLanguage": "{locale['hreflang']}",
                "isPartOf": {{ "@id": "{SITE_URL}/#website" }},
                "breadcrumb": {{ "@id": "{page_url}#breadcrumb" }}
            }},
            {{
                "@type": "BreadcrumbList",
                "@id": "{page_url}#breadcrumb",
                "itemListElement": [
                    {{ "@type": "ListItem", "position": 1, "name": {json.dumps(tr_text(locale, "Home", "Ana Sayfa"))}, "item": "{SITE_URL}/" }},
                    {{ "@type": "ListItem", "position": 2, "name": {json.dumps(tr_text(locale, "Glossary", "Sozluk"))}, "item": "{canonical_url(locale, 'main')}" }},
                    {{ "@type": "ListItem", "position": 3, "name": {json.dumps(cat_name)} }}
                ]
            }}
        ]
    }}
    </script>"""

    cat_nav = ""
    for c_slug in ordered_category_slugs(all_categories):
        c_data = all_categories[c_slug]
        c_name = localized_category_name(c_slug, c_data["category"]["name"], locale)
        c_count = len(c_data["terms"])
        c_icon_html = CATEGORY_ICONS.get(c_slug, "")
        active = ' class="active"' if c_slug == cat_slug else ""
        c_href = page_path(locale, "category", c_slug)
        cat_nav += f'<a href="{c_href}"{active}><span>{c_icon_html} {escape(c_name)}</span><span class="glossary-count">{c_count}</span></a>\n'

    return f"""<!DOCTYPE html>
<html lang="{locale_lang_tag(locale)}" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>{page_title}</title>
    <meta name="description" content="{escape(meta_description)}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">

    <link rel="canonical" href="{page_url}">
{hreflang_links_html('category', cat_slug)}

    <meta property="og:type" content="website">
    <meta property="og:url" content="{page_url}">
    <meta property="og:title" content="{escape(meta_title)}">
    <meta property="og:description" content="{escape(meta_description)}">
    <meta property="og:image" content="{SITE_URL}/images/termify_logo.png">
    <meta property="og:site_name" content="Termify">

    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{escape(meta_title)}">
    <meta name="twitter:description" content="{escape(meta_description)}">

    <meta name="apple-itunes-app" content="app-id=6744872522">

    <link rel="icon" type="image/png" href="/images/termify_logo.png">
    <link rel="apple-touch-icon" href="/images/termify_logo.png">
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#09090b">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">

    <link rel="stylesheet" href="/css/style.css">

{jsonld}
</head>

<body>
    <a href="#content" class="skip-link">{tr_text(locale, "Skip to main content", "Ana icerige gec")}</a>

{get_header_html(locale)}

    <main role="main" id="content">

        <nav class="breadcrumb-nav" aria-label="Breadcrumb">
            <div class="container">
                <ol class="breadcrumb-list">
                    <li><a href="/">{tr_text(locale, "Home", "Ana Sayfa")}</a></li>
                    <li><a href="{page_path(locale, 'main')}">{tr_text(locale, "Glossary", "Sozluk")}</a></li>
                    <li aria-current="page">{escape(cat_name)}</li>
                </ol>
            </div>
        </nav>

        <section class="glossary-index-section">
            <div class="container">
                <div class="glossary-index-header">
                    <span class="glossary-category-badge" data-field="{cat_slug}">
                        <span class="glossary-cat-icon" aria-hidden="true">{cat_icon}</span>
                        <span>{escape(cat_name)}</span>
                    </span>
                    <h1>{tr_text(locale, f"{escape(cat_name)} Glossary", f"{escape(cat_name)} Sozlugu")}</h1>
                    <p class="glossary-index-desc">{tr_text(locale, f'{len(terms)} professional {escape(cat_name.lower())} terms with definitions, pronunciation and examples. Learn what each term means &mdash; free with Termify.', f'{len(terms)} profesyonel {escape(cat_name.lower())} terimin tanim, telaffuz ve ornek kullanimlari. Her terimin anlamini Termify ile ucretsiz ogrenin.')}</p>
                </div>

                <div class="glossary-index-layout">
                    <aside class="glossary-sidebar">
                        <nav class="glossary-cat-nav" aria-label="Glossary categories">
                            <h3>{tr_text(locale, "Categories", "Kategoriler")}</h3>
                            {cat_nav}
                        </nav>
                        <nav class="glossary-letter-nav" aria-label="Jump to letter">
                            <h3>{tr_text(locale, "Jump to Letter", "Harfe Git")}</h3>
                            <div class="glossary-letters">{letter_nav}</div>
                        </nav>
                    </aside>

                    <div class="glossary-index-content">
                        {term_sections}
                    </div>
                </div>

                <div class="glossary-cta" style="margin-top: 3rem;">
                    <div class="glossary-cta-card">
                        <h2>{tr_text(locale, f"Learn All {escape(cat_name)} Terms Free", f"{escape(cat_name)} terimlerinin tumunu ucretsiz ogrenin")}</h2>
                        <p>{tr_text(locale, "Master every term with native pronunciation, IPA transcriptions and career quizzes. <strong>100% free, forever.</strong>", "Tum terimleri ana dil telaffuzu, IPA transkripsiyonlari ve kariyer quizleri ile ogrenin. <strong>%100 ucretsiz, daima.</strong>")}</p>
                        <a href="https://apps.apple.com/app/professional-english-termify/id6744872522" class="btn btn-primary btn-lg">{tr_text(locale, "Download Free for iOS", "iOS icin Ucretsiz Indir")}</a>
                    </div>
                </div>
            </div>
        </section>

    </main>

{get_footer_html(locale, total_terms_display)}
</body>
</html>"""


def generate_main_index(all_categories: dict, locale: dict, total_terms_display: str) -> str:
    total_terms = sum(len(c["terms"]) for c in all_categories.values())
    page_url = canonical_url(locale, "main")
    page_title = tr_text(
        locale,
        f"Professional English Glossary &mdash; {total_terms_display} Industry Terms | Termify",
        f"Profesyonel Ingilizce Sozlugu &mdash; {total_terms_display} Sektor Terimi | Termify",
    )
    meta_title = tr_text(
        locale,
        f"Professional English Glossary — {total_terms_display} Industry Terms | Termify",
        f"Profesyonel Ingilizce Sozlugu — {total_terms_display} Sektor Terimi | Termify",
    )
    meta_description = tr_text(
        locale,
        f"Free professional English glossary with {total_terms}+ term definitions across Aviation, Maritime, Logistics, Finance, Cybersecurity and IT/DevOps. Learn what each term means.",
        f"Havacilik, denizcilik, lojistik, finans, siber guvenlik ve BT/DevOps alanlarinda {total_terms}+ terimi kapsayan ucretsiz profesyonel Ingilizce sozluk. Her terimin anlamini ogrenin.",
    )

    cat_cards = ""
    for slug in ordered_category_slugs(all_categories):
        data = all_categories[slug]
        cat = data["category"]
        icon = CATEGORY_ICONS.get(slug, "")
        count = len(data["terms"])
        desc = localized_category_description(slug, cat.get("description", ""), locale)[:140]
        cat_href = page_path(locale, "category", slug)
        cat_name = localized_category_name(slug, cat["name"], locale)
        cat_cards += f"""
                    <a href="{cat_href}" class="glossary-cat-card" data-field="{slug}">
                        <div class="glossary-cat-card-icon" aria-hidden="true">{icon}</div>
                        <h2>{escape(cat_name)}</h2>
                        <p>{escape(desc)}</p>
                        <span class="glossary-cat-card-count">{tr_text(locale, f"{count} terms", f"{count} terim")}</span>
                    </a>"""

    popular_html = ""
    sample_terms = []
    for slug in ["aviation", "finance", "cybersecurity", "it-devops", "maritime", "logistics"]:
        if slug not in all_categories:
            continue
        for term in all_categories[slug]["terms"][:5]:
            sample_terms.append((term, slug))

    if sample_terms:
        items = ""
        for term, c_slug in sample_terms[:18]:
            local_name = localized_term_name(term, locale)
            term_def = localized_definition(term, locale)
            short_def = term_def[:80] + "..." if len(term_def) > 80 else term_def
            c_name = localized_category_name(c_slug, all_categories[c_slug]["category"]["name"], locale)
            term_href = page_path(locale, "term", c_slug, term["slug"])
            items += f"""
                        <a href="{term_href}" class="glossary-popular-item" data-field="{c_slug}">
                            <strong>{escape(local_name)}</strong>
                            <span class="glossary-popular-cat">{escape(c_name)}</span>
                            <span class="glossary-popular-def">{escape(short_def)}</span>
                        </a>"""
        popular_html = f"""
                <section class="glossary-popular">
                    <h2>{tr_text(locale, "Popular Terms", "Populer Terimler")}</h2>
                    <div class="glossary-popular-grid">{items}
                    </div>
                </section>"""

    jsonld = f"""    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@graph": [
            {{
                "@type": "WebPage",
                "@id": "{page_url}#webpage",
                "url": "{page_url}",
                "name": {json.dumps(meta_title)},
                "description": {json.dumps(meta_description)},
                "datePublished": "{TODAY}",
                "dateModified": "{TODAY}",
                "inLanguage": "{locale['hreflang']}",
                "isPartOf": {{ "@id": "{SITE_URL}/#website" }},
                "breadcrumb": {{ "@id": "{page_url}#breadcrumb" }}
            }},
            {{
                "@type": "BreadcrumbList",
                "@id": "{page_url}#breadcrumb",
                "itemListElement": [
                    {{ "@type": "ListItem", "position": 1, "name": {json.dumps(tr_text(locale, "Home", "Ana Sayfa"))}, "item": "{SITE_URL}/" }},
                    {{ "@type": "ListItem", "position": 2, "name": {json.dumps(tr_text(locale, "Glossary", "Sozluk"))} }}
                ]
            }}
        ]
    }}
    </script>"""

    return f"""<!DOCTYPE html>
<html lang="{locale_lang_tag(locale)}" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>{page_title}</title>
    <meta name="description" content="{escape(meta_description)}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">

    <link rel="canonical" href="{page_url}">
{hreflang_links_html('main')}

    <meta property="og:type" content="website">
    <meta property="og:url" content="{page_url}">
    <meta property="og:title" content="{escape(meta_title)}">
    <meta property="og:description" content="{escape(meta_description)}">
    <meta property="og:image" content="{SITE_URL}/images/termify_logo.png">
    <meta property="og:site_name" content="Termify">

    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{escape(meta_title)}">

    <meta name="apple-itunes-app" content="app-id=6744872522">

    <link rel="icon" type="image/png" href="/images/termify_logo.png">
    <link rel="apple-touch-icon" href="/images/termify_logo.png">
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#09090b">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">

    <link rel="stylesheet" href="/css/style.css">

{jsonld}
</head>

<body>
    <a href="#content" class="skip-link">{tr_text(locale, "Skip to main content", "Ana icerige gec")}</a>

{get_header_html(locale)}

    <main role="main" id="content">

        <nav class="breadcrumb-nav" aria-label="Breadcrumb">
            <div class="container">
                <ol class="breadcrumb-list">
                    <li><a href="/">{tr_text(locale, "Home", "Ana Sayfa")}</a></li>
                    <li aria-current="page">{tr_text(locale, "Glossary", "Sozluk")}</li>
                </ol>
            </div>
        </nav>

        <section class="glossary-hero">
            <div class="container">
                <h1>{tr_text(locale, 'Professional English <span class="gradient-text">Glossary</span>', 'Profesyonel Ingilizce <span class="gradient-text">Sozlugu</span>')}</h1>
                <p class="glossary-hero-desc">{tr_text(locale, f'Explore {total_terms_display} professional English term definitions across 6 industries. Every term explained clearly &mdash; sourced from official standards like ICAO, IMO, ISO 27001 and NIST.', f'6 sektorde {total_terms_display} profesyonel Ingilizce terim tanimini kesfedin. Her terim acik ve anlasilir sekilde, ICAO, IMO, ISO 27001 ve NIST gibi resmi standartlara dayanarak sunulur.')}</p>
            </div>
        </section>

        <section class="glossary-categories-section">
            <div class="container">
                <div class="glossary-cat-grid">{cat_cards}
                </div>

                {popular_html}

                <div class="glossary-cta" style="margin-top: 3rem;">
                    <div class="glossary-cta-card">
                        <h2>{tr_text(locale, "Learn All Terms Free with Termify", "Tum Terimleri Termify ile Ucretsiz Ogrenin")}</h2>
                        <p>{tr_text(locale, f"{total_terms_display} professional terms with native pronunciation, IPA transcriptions and career quizzes. <strong>100% free, forever.</strong>", f"{total_terms_display} profesyonel terim; ana dil telaffuzu, IPA transkripsiyonlari ve kariyer quizleri ile. <strong>%100 ucretsiz, daima.</strong>")}</p>
                        <a href="https://apps.apple.com/app/professional-english-termify/id6744872522" class="btn btn-primary btn-lg">{tr_text(locale, "Download Free for iOS", "iOS icin Ucretsiz Indir")}</a>
                    </div>
                </div>
            </div>
        </section>

    </main>

{get_footer_html(locale, total_terms_display)}
</body>
</html>"""


def generate_locale_sitemap_entries(all_categories: dict, locale: dict) -> list[str]:
    entries = [
        f"    <url><loc>{canonical_url(locale, 'main')}</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>"
    ]
    for cat_slug in ordered_category_slugs(all_categories):
        cat_data = all_categories[cat_slug]
        entries.append(
            f"    <url><loc>{canonical_url(locale, 'category', cat_slug)}</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>"
        )
        for term in cat_data["terms"]:
            entries.append(
                f"    <url><loc>{canonical_url(locale, 'term', cat_slug, term['slug'])}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>"
            )
    return entries


def write_urlset(path: str, entries: list[str]) -> None:
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<?xml-stylesheet type="text/xsl" href="{SITEMAP_XSL_HREF}"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)


def write_sitemap_index(path: str, sitemap_files: list[str]) -> None:
    items = []
    for filename in sitemap_files:
        items.append(
            f"  <sitemap><loc>{SITE_URL}/{filename}</loc><lastmod>{TODAY}</lastmod></sitemap>"
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<?xml-stylesheet type="text/xsl" href="{SITEMAP_XSL_HREF}"?>\n'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(items)
        + "\n</sitemapindex>\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)


def write_large_sitemap(base_filename: str, entries: list[str]) -> list[str]:
    sitemap_files = []
    if not entries:
        write_urlset(os.path.join(BASE_DIR, base_filename), entries)
        return [base_filename]

    chunk_count = (len(entries) + MAX_URLS_PER_SITEMAP - 1) // MAX_URLS_PER_SITEMAP
    if chunk_count == 1:
        write_urlset(os.path.join(BASE_DIR, base_filename), entries)
        return [base_filename]

    stem, ext = os.path.splitext(base_filename)
    for i in range(chunk_count):
        chunk = entries[i * MAX_URLS_PER_SITEMAP : (i + 1) * MAX_URLS_PER_SITEMAP]
        chunk_name = f"{stem}-{i + 1}{ext}"
        write_urlset(os.path.join(BASE_DIR, chunk_name), chunk)
        sitemap_files.append(chunk_name)
    return sitemap_files


def cleanup_generated_output() -> None:
    default_glossary_dir = os.path.join(BASE_DIR, "glossary")
    if os.path.isdir(default_glossary_dir):
        shutil.rmtree(default_glossary_dir)

    for locale in LOCALES:
        if locale["is_default"]:
            continue
        locale_glossary_dir = os.path.join(BASE_DIR, locale["code"], "glossary")
        if os.path.isdir(locale_glossary_dir):
            shutil.rmtree(locale_glossary_dir)


def generate_locale_pages(all_categories: dict, all_terms_map: dict, locale: dict, total_terms_display: str) -> tuple[int, int]:
    glossary_dir = glossary_output_dir(locale)
    os.makedirs(glossary_dir, exist_ok=True)

    main_index = generate_main_index(all_categories, locale, total_terms_display)
    with open(os.path.join(glossary_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(main_index)

    cat_count = 0
    term_count = 0
    for cat_slug in ordered_category_slugs(all_categories):
        cat_data = all_categories[cat_slug]
        cat_dir = os.path.join(glossary_dir, cat_slug)
        os.makedirs(cat_dir, exist_ok=True)

        cat_index = generate_category_index(cat_data, all_categories, locale, total_terms_display)
        with open(os.path.join(cat_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(cat_index)
        cat_count += 1

        for term in cat_data["terms"]:
            filename = f"what-is-{term['slug']}.html"
            filepath = os.path.join(cat_dir, filename)
            page = generate_term_page(term, cat_data, all_terms_map, locale, total_terms_display)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(page)
            term_count += 1

    return cat_count, term_count


def generate_localized_static_pages() -> None:
    script = os.path.join(BASE_DIR, "scripts", "localize-static-pages.py")
    if not os.path.exists(script):
        print("Warning: scripts/localize-static-pages.py not found, skipping static localization.")
        return
    subprocess.run(["python3", script], check=True)


def generate_sitemaps(all_categories: dict) -> tuple[list[str], int]:
    sitemap_files = []

    static_entries = []
    for path, lastmod, changefreq, priority, localize_all in STATIC_SITEMAP_URLS:
        locales_for_path = LOCALES if localize_all else [DEFAULT_LOCALE]
        for locale in locales_for_path:
            loc_path = localized_static_path(path, locale)
            static_entries.append(
                f"    <url><loc>{SITE_URL}{loc_path}</loc><lastmod>{lastmod}</lastmod><changefreq>{changefreq}</changefreq><priority>{priority}</priority></url>"
            )

    sitemap_main = "sitemap-main.xml"
    write_urlset(os.path.join(BASE_DIR, sitemap_main), static_entries)
    sitemap_files.append(sitemap_main)

    total_glossary_urls = 0
    for locale in LOCALES:
        entries = generate_locale_sitemap_entries(all_categories, locale)
        total_glossary_urls += len(entries)
        locale_file = f"sitemap-glossary-{locale['code']}.xml"
        generated_files = write_large_sitemap(locale_file, entries)
        sitemap_files.extend(generated_files)

        if locale["is_default"]:
            with open(os.path.join(BASE_DIR, "glossary-sitemap-entries.xml"), "w", encoding="utf-8") as f:
                f.write("\n".join(entries))

    write_sitemap_index(os.path.join(BASE_DIR, "sitemap.xml"), sitemap_files)
    return sitemap_files, total_glossary_urls


def main() -> None:
    print("Loading term data...")
    all_categories = load_all_categories()

    total_terms = sum(len(c["terms"]) for c in all_categories.values())
    total_terms_display = format_term_count(total_terms)
    print(f"Found {len(all_categories)} categories, {total_terms} terms total.")
    print(f"Generating locales: {len(LOCALES)}")

    all_terms_map = build_all_terms_map(all_categories)
    cleanup_generated_output()

    total_category_pages = 0
    total_term_pages = 0

    for locale in LOCALES:
        print(f"Generating locale '{locale['code']}'...")
        cat_count, term_count = generate_locale_pages(
            all_categories, all_terms_map, locale, total_terms_display
        )
        total_category_pages += cat_count
        total_term_pages += term_count

    print("Generating localized static pages...")
    generate_localized_static_pages()

    sitemap_files, total_glossary_urls = generate_sitemaps(all_categories)

    print("\nDone! Generated:")
    print(f"  - {len(LOCALES)} glossary main indexes")
    print(f"  - {total_category_pages} category indexes")
    print(f"  - {total_term_pages} individual term pages")
    print(f"  - {len(sitemap_files)} sitemap files")
    print(f"  - {total_glossary_urls} glossary URLs in sitemaps")
    print(f"\nTotal generated glossary HTML pages: {len(LOCALES) + total_category_pages + total_term_pages}")


if __name__ == "__main__":
    main()
