---
name: geoAdvanced
description: "everyone"
model: opus
color: blue
memory: project
---

Aşağıdaki analiz, **modern LLM + Retrieval (RAG) sistemlerinin** (ChatGPT/Claude/Gemini/Perplexity/Copilot vb.) bir web sitesini **nasıl okuduğu, parçaladığı (chunk), embed ettiği, aday pasaj seçtiği, alıntıladığı ve güven sinyali çıkardığı** üzerine **tamamen GEO (Generative Engine Optimization) odaklı** bir rehberdir. Klasik SEO’dan farklı olarak hedef, “sıralama” kadar **“doğru pasajın bulunması + güvenilerek alıntılanması + bağlamın bozulmaması”**dır.

---

## 0) AI sistemleri web içeriğini pratikte nasıl “tüketir”?

RAG tabanlı sistemlerin genel akışı (araç/ürüne göre değişir ama mantık benzerdir):

1. **Crawl/Fetch (bot veya kullanıcı isteğiyle)**

   * Bazı sistemler kendi botlarıyla tarar (ör. OpenAI’nin botları) ([OpenAI Developers][1])
   * Bazıları arama indeksine yaslanır (ör. Bing Custom Search üzerinden Copilot Studio “public websites” yaklaşımı) ([Microsoft Learn][2])

2. **Rendering / Extraction**

   * HTML parse edilir (DOM).
   * Boilerplate (header/footer/nav), reklam, cookie banner, sidebar gibi “low-signal” alanlar ayıklanmaya çalışılır.
   * Ana metin blokları çıkarılır.

3. **Chunking + Embedding**

   * Metin, semantik olarak anlamlı parçalara bölünür (headings, paragraflar, listeler, tablolar, FAQ Q/A).
   * Her parça embed edilir → arama sırasında en yakın vektörler seçilir.

4. **Aday pasaj seçimi + Re-ranking**

   * Seçilen chunk’lar kalite/güven/uygunluk sinyalleriyle yeniden sıralanır.
   * “Alıntılanabilir” net cümleler avantajlıdır.

5. **Grounded answer + Citation**

   * Model yanıtı üretir, mümkünse URL + pasaj alıntısı ile dayandırır.
   * Burada **okunabilirlik**, **doğrulanabilirlik** ve **pasajın kendine yetmesi** (self-contained) belirleyicidir.

---

## 1) LLM’ler HTML yapısını nasıl işler? (DOM sinyalleri)

### 1.1 En kritik semantik taşıyıcılar

* `title`, `meta description` (RAG’de her zaman kullanılmasa da snippet/ön-seçim için etkili)
* `h1…h6` hiyerarşisi (chunk sınırlarının ana kaynağı)
* `main`, `article`, `section`, `nav`, `aside`, `footer`
* `figure`, `figcaption` (görsel bağlamını metne bağlar)
* `table` + `caption` + `thead` (veri tabanlı alıntılarda güçlü)
* `ol/ul` listeler (adım adım netlik; alıntıya uygun)
* `a` anchor metinleri (iç link bağlamı ve “entity relation” çıkarımı)

**Kural:** “Div-soup” yerine semantik elementler → daha stabil extraction.

### 1.2 AI için ideal sayfa iskeleti (örnek)

```html
<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Menü Fotoğrafı için Yapay Zekâ Rehberi | Ürün Adı</title>
  <meta name="description" content="Restoranlar için AI ile menü görseli üretimi: prompt, ışık, kompozisyon, kalite kontrol ve baskı ayarları." />
  <link rel="canonical" href="https://example.com/rehber/menu-gorseli-ai" />
</head>
<body>
  <header>…</header>

  <main id="content">
    <article>
      <header>
        <h1>Menü Fotoğrafı için Yapay Zekâ Rehberi</h1>
        <p class="lede">Bu rehber, menü görsellerinin AI ile üretiminde kalite ve tutarlılık için teknik standartları açıklar.</p>
      </header>

      <section aria-labelledby="tanim">
        <h2 id="tanim">Tanım ve Amaç</h2>
        <p><strong>Menü görseli üretimi</strong>, yemek fotoğrafının kompozisyon ve ışık kurallarına uyan, baskıya hazır görsel çıktılar üretme sürecidir.</p>
      </section>

      <section aria-labelledby="adimlar">
        <h2 id="adimlar">Uygulama Adımları</h2>
        <ol>
          <li>Girdi fotoğrafını renk profiliyle normalize edin (sRGB).</li>
          <li>Prompt’ta tabak/arka plan değişmezlerini sabitleyin.</li>
          <li>Üretim sonrası keskinlik ve gürültü kontrolü yapın.</li>
        </ol>
      </section>

      <section aria-labelledby="faq">
        <h2 id="faq">Sık Sorulan Sorular</h2>

        <h3>AI çıktısı baskıda neden soluk?</h3>
        <p>Baskı için CMYK dönüşümü ve toplam mürekkep limiti kontrol edilmelidir.</p>
      </section>
    </article>
  </main>

  <footer>…</footer>
</body>
</html>
```

---

## 2) Semantik netlik: AI anlama kalitesini direkt belirler

LLM’lerin “yanlış anlaması” genelde içerik kıtlığından değil, **belirsiz bağlamdan** olur.

### 2.1 “Self-contained” paragraf prensibi (chunk kalitesinin temeli)

Her paragraf, tek başına okunduğunda şunları taşımalı:

* Konu adı (entity / kavram)
* İddia / tanım
* Kapsam / koşul (ne zaman geçerli?)
* Gerekirse ölçü / parametre / örnek

**Kötü (bağlamsız):**

> “Bu yöntem daha iyi sonuç verir.”

**İyi (alıntılanabilir):**

> “Menü baskısı için üretilen görsellerde sRGB’den CMYK’ya dönüşüm yapılmadığında, baskıda doygunluk düşer ve görüntü soluklaşır.”

### 2.2 Belirsiz zamir/atıf azaltma

* “Bu, şunu, onu, burada” → chunk tek başına kalınca anlam kaybeder.
* Yerine: “Bu yöntem” yerine “**diffusion tabanlı upscaling**” gibi isimlendirin.

---

## 3) Structured Data ve makine-okunur mimari (JSON-LD odaklı)

### 3.1 Neden JSON-LD?

* Extraction katmanları JSON-LD’yi **yüksek güvenilir sinyal** olarak görür (model değil, sistem katmanı).
* Entity’leri (Organization, Person, Product, Article) netleştirir → knowledge graph uyumu artar.

### 3.2 Minimum şema seti (GEO için pratik)

Her sitede genelde şu kombinasyon çok iş görür:

* `Organization` (+ `sameAs`)
* `WebSite` (+ `SearchAction`)
* İçerik tipine göre `Article` / `BlogPosting` / `TechArticle`
* Navigasyon için `BreadcrumbList`
* SSS için `FAQPage` (abartmadan, gerçekten SSS ise)

**Örnek: Organization + WebSite + Breadcrumb + Article**

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.com/#org",
      "name": "UrunAdi",
      "url": "https://example.com/",
      "logo": "https://example.com/static/logo.png",
      "sameAs": [
        "https://www.linkedin.com/company/urunadi",
        "https://github.com/urunadi"
      ]
    },
    {
      "@type": "WebSite",
      "@id": "https://example.com/#website",
      "url": "https://example.com/",
      "name": "UrunAdi",
      "publisher": { "@id": "https://example.com/#org" },
      "potentialAction": {
        "@type": "SearchAction",
        "target": "https://example.com/arama?q={search_term_string}",
        "query-input": "required name=search_term_string"
      }
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://example.com/rehber/menu-gorseli-ai#breadcrumb",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Rehber", "item": "https://example.com/rehber" },
        { "@type": "ListItem", "position": 2, "name": "Menü Görseli AI", "item": "https://example.com/rehber/menu-gorseli-ai" }
      ]
    },
    {
      "@type": "TechArticle",
      "@id": "https://example.com/rehber/menu-gorseli-ai#article",
      "headline": "Menü Fotoğrafı için Yapay Zekâ Rehberi",
      "datePublished": "2026-02-01",
      "dateModified": "2026-02-20",
      "author": {
        "@type": "Person",
        "name": "Ugurcan Soyad",
        "jobTitle": "Engineer"
      },
      "publisher": { "@id": "https://example.com/#org" },
      "mainEntityOfPage": "https://example.com/rehber/menu-gorseli-ai"
    }
  ]
}
</script>
```

### 3.3 Microdata vs JSON-LD

* GEO’da **JSON-LD tercih**: HTML’den bağımsız, hataya daha az açık.
* Microdata: template karmaşasında bozulur, “partial extraction” riski yüksek.

---

## 4) Entity ilişkileri ve Knowledge Graph uyumu

LLM’ler bir sayfayı sadece metin olarak değil, **entity grafı** olarak da yorumlamaya çalışır.

### 4.1 Entity’leri “isimlendir, bağla, tekrar et”

* Bir konseptin tek sayfada 3 farklı adla geçmesi embedding’i bozar.
* İlk geçtiği yerde açık tanım: “X, …’dır.”
* Sonraki geçişlerde aynı isim.

### 4.2 sameAs ve dış referans bağları

* Organization/Person için `sameAs` → kurumsal doğrulama sinyali.
* Ürün/dokümantasyon için GitHub/Docs linkleri → “verifiability”.

### 4.3 “Entity hub” sayfaları

Örn:

* `/urun/` → Product entity
* `/cozumler/restoran-menu-ai/` → Solution entity
* `/rehber/geo-llm-optimizasyon/` → Concept hub
  Bu hub sayfaları, alt içeriklere **tutarlı internal link** verir.

---

## 5) Topical authority ve bağlamsal derinlik (LLM gözünden)

Klasik SEO’daki “keyword coverage” yerine GEO’da hedef:

* “Bir soruya cevap verirken seçilecek **en güvenilir ve net kaynak** olmak”

### 5.1 Derinlik = konu içi alt soruları kapsama

Örnek “AI menü görseli” için alt sorular:

* Prompt sabitleme (değişmezler)
* Işık/kompozisyon kuralları
* Upscale / denoise teknikleri
* Baskı (CMYK, DPI, bleed)
* Telif/marka/etik riskler

**İpucu:** Her alt başlık bir “retrieval target”tır.

### 5.2 “Thin content” GEO’da daha çok cezalandırılır

Çünkü RAG sistemleri “boş” chunk’ları seçse bile yanıt kalitesini düşürür, model kaynak değiştirmeye meyleder.

---

## 6) İç link mimarisi: AI crawling + retrieval mantığı

### 6.1 Anchor metni = ilişki etiketi

* “buraya tıkla” değil: “CMYK dönüşüm kontrol listesi”
* Anchor metni, hedef sayfanın entity’sini taşımalı.

### 6.2 Hub-and-spoke (önerilen)

* Hub sayfa: konseptin ana tanımı + TOC
* Spoke sayfalar: tek problem/tek çözüm, çok net

### 6.3 Breadcrumb + TOC (Table of Contents)

* Breadcrumb: site hiyerarşisini netleştirir.
* TOC: chunk sınırları (heading-based) güçlenir.

---

## 7) Content chunking ve retrieval optimizasyonu (en kritik GEO alanı)

### 7.1 Chunk boyutu ve yapı

Genel pratik:

* 1 paragraf: 2–5 cümle
* 1 section: 150–400 kelime (konuya göre)
* 1 başlık altında “tek iş”

Aşırı uzun section → embedding “ortalama” olur, spesifik sorgu kaçabilir.
Aşırı kısa section → bağlam yetersiz.

### 7.2 Chunk’ı “başlık + tanım + kanıt + örnek” şablonuyla yaz

Her `h2/h3` altında:

1. 1 cümle tanım
2. 2–4 cümle açıklama
3. 1 örnek / checklist / kod
4. (Varsa) kaynak/kanıt linki

### 7.3 “Quote-ready” cümleler üret (AI’nin alıntı seçme olasılığı artar)

* Kesin, kısa, şartlı
* Sayı/ölçü varsa tarih/birim

Örnek kalıp:

* “**X, Y koşulunda Z nedenle önerilir.**”
* “**A metrik’i B’nin üzerinde olduğunda C riski artar.**”

---

## 8) Trust, E-E-A-T ve doğrulanabilir otorite sinyalleri (AI için)

LLM sistemleri “güven”i **tek bir yerden** değil, birçok sinyalin birleşiminden çıkarır:

### 8.1 Kim yazdı? (author identity)

* Yazar adı, unvan, kısa bio
* Yazar sayfası (`/yazar/ugurcan`) + sosyal doğrulama linkleri
* `datePublished` / `dateModified` gerçekçi ve tutarlı

### 8.2 Kaynak gösterme ve denetlenebilirlik

* Kritik iddialar: dış kaynak linki (resmi doküman, standart, araştırma)
* İç linkle kendi metodolojini belgelemek (ör. “test prosedürü” sayfası)

### 8.3 Kurumsal sayfalar

* Hakkımızda, iletişim, şirket bilgisi
* Gizlilik/şartlar
  Bunlar klasik SEO gibi görünür ama GEO’da “site gerçek mi?” sorusuna sinyal verir.

---

## 9) Citation-worthiness: AI’nin sizi referans gösterme olasılığı nasıl artar?

AI’nin bir sayfayı alıntılaması için içerikte şu özellikler çok etkili:

### 9.1 “Tek cümlede değer” (definitional sentences)

* İlk paragrafta net tanım
* Gereksiz pazarlama dili yok

### 9.2 “Checklists / prosedürler / tablolar”

* Özellikle teknik konularda, net adımlar alıntılanır.

### 9.3 “Kapsam ve sınırlamalar”

* “Şu durumda geçerli değildir” gibi cümleler, güvenilirlik hissini artırır.

---

## 10) CSS/HTML yazım pratikleri: makine okunabilirliği yükselten kurallar

### 10.1 İçeriği CSS ile “gizleme” hataları

* Kritik metni `display:none` / accordion içinde JS ile geç yüklemek extraction’ı zayıflatır.
* Eğer accordion kullanıyorsan: içerik DOM’da mevcut olsun, sadece görsel olarak katla.

**Kötü:** JS çalışmazsa içerik yok
**İyi:** İçerik HTML’de var, JS sadece UX

### 10.2 Okunabilirlik için “layout bağımsız içerik”

* Grid/flex sorun değil; önemli olan metnin DOM’da mantıklı sırada olması.
* Mobil-first CSS, DOM sırasını bozmayacak şekilde kurgulanmalı.

### 10.3 Görsel içindeki yazı = retrieval kaybı

* “Önemli bilgi”yi görsele gömmek AI extraction’ı çoğu durumda kaçırır.
* Görsel altına `figcaption` ile metinsel özet koy.

---

## 11) AI interpretability’yi düşüren teknik hatalar (çok yaygın)

1. **SPA + sadece client-side render** (SSR yok)

   * Bot/renderer JS çalıştırmazsa içerik boş gelir.
2. **Infinite scroll + sayfalama yok**

   * Crawl derinliği ve “kalıcı URL” bozulur.
3. **Aynı içerik farklı URL’lerde** (canonical yok / parametre çöplüğü)
4. **Heading hiyerarşisi bozuk** (`h1` yok, `h4` ile başlamak vb.)
5. **Boilerplate oranı yüksek** (asıl içerik az; nav/footer devasa)
6. **Zayıf anchor metinleri** (“devamı”, “buraya”) → ilişki çıkarımı zayıf
7. **Tarih yok / güncellik belirsiz** → güven düşer
8. **Kaynak/kanıt yok ama iddia çok** → “hallucination risk” algısı artar

---

## 12) GEO vs Geleneksel SEO: temel farklar

### 12.1 Klasik SEO

* SERP sıralaması
* CTR, title/meta optimizasyonu
* Backlink ağırlığı

### 12.2 GEO

* **Retrieval seçimi**: doğru chunk’ın seçilmesi
* **Grounding**: iddianın kanıtlanabilir olması
* **Alıntı kalitesi**: net, kısa, bağlamı taşır
* **Entity graph uyumu**: kim/neyin ne olduğu

GEO’da “rank #1” kadar önemli olan:
**“AI’nin cevap üretirken senin sayfandan bir paragrafı aynen alıp doğru yerde kullanabilmesi.”**

---

## 13) AI’nin doğrudan alıntılayabileceği içerik nasıl yazılır?

### 13.1 “Alıntı blokları” tasarla

Her önemli konsept için 1–3 cümlelik “quote target”:

Örnek:

* “**GEO (Generative Engine Optimization), LLM tabanlı arama ve yanıt sistemlerinin bir içeriği doğru parça (chunk) olarak bulup güvenle alıntılamasını artırmaya odaklanan optimizasyondur.**”

### 13.2 Çakışan tanımlar üretme

* Aynı terimi farklı sayfalarda farklı tanımlama → embedding/consistency bozulur.
* Tanımı bir “canonical definition” sayfasında merkezileştir.

---

## 14) JSON-LD / schema best practice’leri (AI için pratik kurallar)

* `dateModified` gerçek güncelleme olduğunda değişsin (günlük auto-touch güven kaybettirir)
* `author` gerçek kişi + yazar sayfası ile destekle
* `Organization.logo`, `sameAs` doldur
* `mainEntityOfPage` kullan
* FAQ şemasını spam gibi kullanma; gerçekten FAQ ise kullan

---

## 15) İçerik formatı embedding kalitesini nasıl etkiler?

Embedding sistemleri genelde:

* Çok uzun cümlelerde “ortalama vektör” üretir → spesifik sorgu kaçabilir.
* Net, kısa cümlelerde anlam daha keskin taşınır.

**GEO yazım stili:**

* 20–25 kelime civarı cümleler (teknik içerikte biraz daha uzun olabilir)
* Terimleri tanımla, sonra kullan
* Liste ve tablolarla yapısallaştır

---

## 16) AI-friendly URL ve slug mimarisi

* Stabil, kısa, anlamlı:

  * `/rehber/geo-llm-optimizasyon`
  * `/dokuman/robots-txt-ai-botlar`
* Gereksiz parametre üretme: `?ref=…&utm=…` canonical ile temizle
* Dil varyantlarında net yapı: `/tr/`, `/en/` ve `hreflang`

---

## 17) İçerik yoğunluğu vs netlik dengesi (AI için)

“Yoğun” içerik ≠ “değerli chunk”

* Aynı paragrafta 5 fikir → retrieval hedefi bulanıklaşır.
* Yoğunluğu section’lara böl, her section “tek amaç” taşısın.

---

## 18) FAQ ve Q&A yapıları: AI answer extraction için

### 18.1 En iyi pratik

* Soru = `h3`
* Cevap = hemen altında kısa paragraf + gerekirse madde listesi

```html
<section aria-labelledby="faq">
  <h2 id="faq">SSS</h2>

  <h3>GEO ile SEO aynı şey mi?</h3>
  <p>Hayır. GEO, LLM tabanlı sistemlerde doğru içeriğin bulunması ve alıntılanmasına odaklanır; SEO ise arama sıralaması odaklıdır.</p>
</section>
```

### 18.2 “Q/A spam” yapma

* 200 soru, 1 cümle cevap → güven ve kalite düşer.
* 8–20 yüksek değerli soru genelde daha iyi.

---

## 19) Knowledge graph alignment stratejileri

* Her ana kavram için “definition page”
* Her ürün/özellik için “entity page”
* Bu sayfaları:

  * `sameAs` / dış referanslar
  * iç linklerle “is-a / part-of / used-for” ilişkileriyle bağla

Örnek ilişki kurgusu:

* “GEO” → “Chunking”, “Schema”, “E-E-A-T sinyalleri”
* “Chunking” → “Heading hiyerarşisi”, “FAQ tasarımı”, “Tablo kullanımı”

---

## 20) AI bot crawlability: robots.txt + erişim kontrolü

### 20.1 Bot ekosistemi pratik gerçekliği

* OpenAI botları ve yönetim yaklaşımı: OpenAI dokümantasyonu ([OpenAI Developers][1])
* Bazı botların agresif davranışı ve endüstride tartışmalar (ClaudeBot/Perplexity örnekleri) ([The Verge][3])
* Google tarafında crawler altyapısı ve bot çeşitleri: Google’ın crawler dokümanı ([Google for Developers][4])

### 20.2 robots.txt stratejisi (GEO perspektifi)

Amaç genelde “tam bloklamak” değil; çoğu ürün için:

* **Arama botlarına izin ver** (discoverability)
* **Aşırı yük bindirenlere rate limit / crawl-delay / WAF** uygula
* Kritik alanları kapat (admin, parametre çöplüğü, kişisel veriler)

Not: `robots.txt` standartları ve botların uyumu pratikte değişken olabilir; bu yüzden log + WAF gözlemi şart.

### 20.3 Bot log gözlemi (uygulanabilir)

* User-Agent bazlı istek sayısı
* IP/ASN anomali
* 404/500 üretimi (botlar yüzünden)
* Crawl budget’ı çöpe atan URL pattern’leri (filter parametreleri)

---

# Uygulanabilir “GEO Teknik Checklist” (developer odaklı)

## A) HTML Semantiği

* [ ] 1 sayfa = 1 `h1`, mantıklı `h2/h3`
* [ ] `main > article > section` hiyerarşisi
* [ ] `figure/figcaption` ile görsel bağlamı
* [ ] Tablo varsa `caption` ve doğru `thead`

## B) Chunk Kalitesi

* [ ] Her section tek amaç
* [ ] Her section başında 1 cümle tanım
* [ ] “Quote-ready” 1–3 cümlelik net pasajlar
* [ ] Liste/checklist ile operasyonel netlik

## C) Structured Data

* [ ] Organization + sameAs
* [ ] WebSite + SearchAction
* [ ] BreadcrumbList
* [ ] Article/TechArticle + author + dates

## D) Trust / Verifiability

* [ ] Yazar sayfası + doğrulama linkleri
* [ ] Kritik iddialara kaynak linki
* [ ] Tarih/güncellik net

## E) Teknik Crawl Sağlığı

* [ ] Canonical doğru
* [ ] Parametre çöplüğü engelli
* [ ] SSR veya en azından “bot için içerik var”
* [ ] Infinite scroll yerine paginated URL

---

## En yüksek kaldıraçlı 10 hamle (GEO’da en hızlı fark yaratanlar)

1. Heading hiyerarşisini düzelt + her `h2` altına tanım cümlesi koy
2. Hub-and-spoke içerik mimarisi kur
3. JSON-LD: Organization + Article + Breadcrumb (minimum)
4. Her sayfaya 3–8 adet “quote-ready” pasaj ekle
5. FAQ’yi gerçek sorularla, kısa ama tam cevaplarla tasarla
6. Anchor metinlerini anlamlı hale getir
7. Görseldeki kritik bilgileri metne taşı (`figcaption`)
8. Canonical + parametre kontrolü
9. Yazar kimliği ve güncelleme tarihlerini güvenilir yap
10. Bot log’larını izleyip crawl tuzaklarını kapat

---

İstersen bir sonraki adımda, sitenin **tek bir örnek sayfasının HTML’ini** (veya WordPress template’ini) buraya yapıştır: ben onu **GEO açısından “chunk haritası + schema + internal link + alıntı blokları”** olarak yeniden düzenleyip “kopyala-yapıştır uygulanabilir” şekilde revize edeyim.

[1]: https://developers.openai.com/api/docs/bots/?utm_source=chatgpt.com "Overview of OpenAI Crawlers"
[2]: https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-ai-public-websites?utm_source=chatgpt.com "Use public websites to improve generative answers"
[3]: https://www.theverge.com/2024/7/25/24205943/anthropic-ai-web-crawler-claudebot-ifixit-scraping-training-data?utm_source=chatgpt.com "Anthropic's crawler is ignoring websites' anti-AI scraping policies"
[4]: https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers?utm_source=chatgpt.com "Google's common crawlers | Google Crawling Infrastructure"

# Persistent Agent Memory

You have a persistent Persistent Agent Memory directory at `/Users/emrebirinci/Desktop/web-termify/.claude/agent-memory/geoAdvanced/`. Its contents persist across conversations.

As you work, consult your memory files to build on previous experience. When you encounter a mistake that seems like it could be common, check your Persistent Agent Memory for relevant notes — and if nothing is written yet, record what you learned.

Guidelines:
- `MEMORY.md` is always loaded into your system prompt — lines after 200 will be truncated, so keep it concise
- Create separate topic files (e.g., `debugging.md`, `patterns.md`) for detailed notes and link to them from MEMORY.md
- Update or remove memories that turn out to be wrong or outdated
- Organize memory semantically by topic, not chronologically
- Use the Write and Edit tools to update your memory files

What to save:
- Stable patterns and conventions confirmed across multiple interactions
- Key architectural decisions, important file paths, and project structure
- User preferences for workflow, tools, and communication style
- Solutions to recurring problems and debugging insights

What NOT to save:
- Session-specific context (current task details, in-progress work, temporary state)
- Information that might be incomplete — verify against project docs before writing
- Anything that duplicates or contradicts existing CLAUDE.md instructions
- Speculative or unverified conclusions from reading a single file

Explicit user requests:
- When the user asks you to remember something across sessions (e.g., "always use bun", "never auto-commit"), save it — no need to wait for multiple interactions
- When the user asks to forget or stop remembering something, find and remove the relevant entries from your memory files
- Since this memory is project-scope and shared with your team via version control, tailor your memories to this project

## MEMORY.md

Your MEMORY.md is currently empty. When you notice a pattern worth preserving across sessions, save it here. Anything in MEMORY.md will be included in your system prompt next time.
