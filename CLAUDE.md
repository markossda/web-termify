# Termify Web - Proje Kuralları

## Proje Amacı

Mobil uygulama için SEO/GEO (Generative Engine Optimization) odaklı bir web sitesi. Botlar ve AI crawlerlar siteye kolayca erişip içeriği anlayabilmeli.

---

## Kesin Kurallar

### Teknoloji

- **SADECE** saf HTML + CSS kullanılacak
- **ASLA** framework kullanılmayacak (React, Next.js, Vue, Angular, Svelte vb. YASAK)
- **ASLA** JavaScript framework/bundler kullanılmayacak (Webpack, Vite, Parcel vb. YASAK)
- Vanilla JavaScript sadece gerektiğinde minimal kullanılacak (analytics, basit interaktiflik)
- CSS framework yasak (Tailwind, Bootstrap vb.) - saf CSS yazılacak
- Build step yok, transpile yok - doğrudan tarayıcıda çalışan kod

### Neden Saf HTML/CSS?

- Botlar ve AI crawlerlar (Google, Bing, ChatGPT, Perplexity, Claude) doğrudan HTML okur
- JavaScript rendering gerektiren siteler crawl edilemez veya geç crawl edilir
- Saf HTML = anında erişilebilir içerik
- Daha hızlı yükleme = daha iyi SEO skor

---

## GEO SEO Stratejisi

### Generative Engine Optimization (GEO)

AI motorları (ChatGPT, Perplexity, Google AI Overview, Claude) için optimize edilecek:

1. **Yapılandırılmış Veri (Structured Data)**
   - Her sayfada JSON-LD schema markup zorunlu
   - `SoftwareApplication` schema mobil uygulama için
   - `Organization` schema marka için
   - `FAQPage` schema SSS sayfaları için
   - `HowTo` schema kullanım kılavuzları için
   - `Review` / `AggregateRating` schema kullanıcı yorumları için

2. **Semantik HTML**
   - `<article>`, `<section>`, `<nav>`, `<header>`, `<footer>`, `<main>`, `<aside>` zorunlu
   - `<h1>` - `<h6>` hiyerarşisi doğru kullanılacak (sayfa başına tek `<h1>`)
   - `<meta>` description, keywords, og:tags her sayfada olacak
   - `<img>` etiketlerinde `alt` attribute zorunlu ve açıklayıcı olacak

3. **AI Crawlerlar İçin Optimizasyon**
   - İçerik doğrudan HTML'de olacak (JS ile render YASAK)
   - Sorulara doğrudan cevap veren paragraflar (featured snippet formatı)
   - Her konuyu kapsayan kapsamlı içerik (thin content YASAK)
   - `robots.txt` ve `sitemap.xml` zorunlu
   - Canonical URL'ler her sayfada tanımlanacak

4. **İçerik Yapısı**
   - Her sayfa bir ana konuya odaklanacak (topic clustering)
   - Sorularla başlayan başlıklar (AI motorları soru-cevap formatını sever)
   - Listeler, tablolar, karşılaştırmalar kullanılacak
   - İç linkler ile sayfalar arası bağlantı kurulacak
   - Breadcrumb navigasyon zorunlu

### Teknik SEO

1. **Performans**
   - Sayfa boyutu < 100KB (HTML + CSS)
   - İlk yükleme < 1 saniye
   - CSS inline veya tek dosya (HTTP request minimize)
   - Görseller optimize edilecek (WebP, lazy loading)
   - Core Web Vitals mükemmel olacak

2. **Mobile First**
   - Responsive tasarım zorunlu (mobile-first yaklaşım)
   - `<meta name="viewport">` zorunlu
   - Touch-friendly buton boyutları (min 44x44px)
   - Okunabilir font boyutu (min 16px body)

3. **App Store Optimization (ASO) Bağlantısı**
   - App Store ve Google Play linkleri belirgin olacak
   - Smart App Banner (`<meta name="apple-itunes-app">`)
   - `.well-known/assetlinks.json` (Android)
   - `apple-app-site-association` (iOS)
   - Deep linking desteği

4. **Uluslararasılaştırma**
   - `<html lang="tr">` zorunlu
   - `hreflang` etiketleri çoklu dil desteği için
   - Her dilin kendi URL yapısı olacak (`/tr/`, `/en/` vb.)

---

## Dosya Yapısı

```
web-termify/
├── CLAUDE.md
├── index.html                 # Ana sayfa
├── robots.txt                 # Crawler kuralları
├── sitemap.xml                # Site haritası
├── .well-known/
│   ├── assetlinks.json        # Android deep link
│   └── apple-app-site-association  # iOS deep link
├── css/
│   └── style.css              # Tek CSS dosyası
├── images/
│   └── (optimize edilmiş görseller)
├── pages/
│   ├── features.html          # Özellikler sayfası
│   ├── pricing.html           # Fiyatlandırma
│   ├── about.html             # Hakkımızda
│   ├── contact.html           # İletişim
│   ├── faq.html               # SSS
│   ├── blog/                  # Blog yazıları
│   │   └── *.html
│   └── legal/
│       ├── privacy.html       # Gizlilik politikası
│       └── terms.html         # Kullanım şartları
└── js/
    └── main.js                # Minimal JS (analytics vb.)
```

---

## HTML Şablonu (Her Sayfa İçin)

```html
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Sayfa açıklaması - 150-160 karakter">
    <meta name="keywords" content="anahtar, kelimeler">
    <link rel="canonical" href="https://termify.app/sayfa">

    <!-- Open Graph -->
    <meta property="og:title" content="Başlık">
    <meta property="og:description" content="Açıklama">
    <meta property="og:image" content="https://termify.app/images/og.png">
    <meta property="og:url" content="https://termify.app/sayfa">
    <meta property="og:type" content="website">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">

    <!-- Smart App Banner -->
    <meta name="apple-itunes-app" content="app-id=APPID">

    <title>Sayfa Başlığı | Termify</title>
    <link rel="stylesheet" href="/css/style.css">

    <!-- JSON-LD Structured Data -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Termify",
        "operatingSystem": "iOS, Android",
        "applicationCategory": "LifestyleApplication"
    }
    </script>
</head>
<body>
    <header>
        <nav aria-label="Ana navigasyon">
            <!-- Breadcrumb + Ana menü -->
        </nav>
    </header>
    <main>
        <h1>Tek Ana Başlık</h1>
        <!-- İçerik -->
    </main>
    <footer>
        <!-- Footer -->
    </footer>
</body>
</html>
```

---

## Yasaklar

| Yasak | Sebep |
|-------|-------|
| JavaScript ile içerik render etme | Botlar göremez |
| SPA (Single Page Application) | Crawl edilemez |
| CSS/JS framework | Gereksiz ağırlık |
| Placeholder/dummy içerik | SEO zararlı |
| Görsel alt text eksikliği | Erişilebilirlik + SEO |
| Inline style (aşırı) | Bakım zorluğu |
| `display:none` ile gizli içerik | SEO ceza riski |
| Thin content (az içerikli sayfa) | SEO zararlı |
| Duplicate content | SEO ceza |
| Build/transpile gerektiren kod | Karmaşıklık |

---

## Kontrol Listesi (Her Sayfa İçin)

```
[  ] Semantik HTML etiketleri kullanıldı
[  ] Tek <h1> ve doğru başlık hiyerarşisi
[  ] Meta description (150-160 karakter)
[  ] Canonical URL tanımlı
[  ] Open Graph etiketleri var
[  ] JSON-LD structured data var
[  ] Tüm görsellerde alt text var
[  ] Mobile responsive test edildi
[  ] Sayfa boyutu < 100KB
[  ] İç linkler mevcut
[  ] Breadcrumb navigasyon var
[  ] robots.txt'te indekslenebilir
[  ] sitemap.xml'e eklendi
```

---

## SEO İçerik Kuralları

- Her blog yazısı min 800 kelime
- Başlıklar soru formatında olabilir ("Termify nedir?", "Nasıl kullanılır?")
- İlk paragraf doğrudan konuyu özetlemeli (AI snippet için)
- Listeler ve tablolar kullanılmalı (yapılandırılmış bilgi)
- İç ve dış linkler dengeli olmalı
- Her sayfa tek bir anahtar kelimeye odaklanmalı
