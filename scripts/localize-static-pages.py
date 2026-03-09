#!/usr/bin/env python3
"""
Generate localized copies of static site pages under /<locale>/...

This script:
- clones core static HTML pages for all locales
- updates canonical + og:url to locale URLs
- injects hreflang tags for all locales
- rewrites internal links to locale-prefixed paths
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parents[1]
SITE_URL = "https://protermify.com"

LOCALES = [
    {"code": "en", "hreflang": "en", "is_default": True},
    {"code": "en-gb", "hreflang": "en-GB", "is_default": False},
    {"code": "tr", "hreflang": "tr", "is_default": False},
    {"code": "de", "hreflang": "de", "is_default": False},
    {"code": "fr", "hreflang": "fr", "is_default": False},
    {"code": "es", "hreflang": "es", "is_default": False},
    {"code": "it", "hreflang": "it", "is_default": False},
    {"code": "pt-br", "hreflang": "pt-BR", "is_default": False},
    {"code": "pt-pt", "hreflang": "pt-PT", "is_default": False},
    {"code": "ru", "hreflang": "ru", "is_default": False},
    {"code": "ar", "hreflang": "ar", "is_default": False},
    {"code": "hi", "hreflang": "hi", "is_default": False},
    {"code": "ja", "hreflang": "ja", "is_default": False},
    {"code": "ko", "hreflang": "ko", "is_default": False},
    {"code": "zh-cn", "hreflang": "zh-CN", "is_default": False},
    {"code": "zh-tw", "hreflang": "zh-TW", "is_default": False},
    {"code": "id", "hreflang": "id", "is_default": False},
    {"code": "nl", "hreflang": "nl", "is_default": False},
    {"code": "pl", "hreflang": "pl", "is_default": False},
    {"code": "sv", "hreflang": "sv", "is_default": False},
    {"code": "th", "hreflang": "th", "is_default": False},
    {"code": "vi", "hreflang": "vi", "is_default": False},
    {"code": "ms", "hreflang": "ms", "is_default": False},
]

SOURCE_FILES = [
    "index.html",
    "pages/aviation-english.html",
    "pages/maritime-english.html",
    "pages/logistics-english.html",
    "pages/finance-english.html",
    "pages/cybersecurity-english.html",
    "pages/it-devops-english.html",
    "pages/compare.html",
    "pages/legal/index.html",
    "pages/legal/privacy.html",
    "pages/legal/terms.html",
]

SKIP_PREFIXES = (
    "/images/",
    "/css/",
    "/js/",
    "/api/",
    "/.well-known/",
    "/manifest.json",
    "/robots.txt",
    "/sitemap",
    "/llms",
    "/worker.js",
    "/wrangler.jsonc",
    "/_headers",
)

TRANSLATION_ROOTS = [
    Path("/Users/emrebirinci/Desktop/Desktop/main/termify/kelime/Core/Localization"),
    Path("/Users/emrebirinci/Desktop/Desktop/TermifyProje_EnSon/kelime 2/kelime/Core/Localization"),
    Path("/Users/emrebirinci/Desktop/Desktop/kelime 2/kelime/Core/Localization"),
    # Fallback source to improve KO/NL/SV UI coverage when Termify locale files are missing.
    Path("/Users/emrebirinci/Desktop/Desktop/kelime 3/kelime/Core/Localization"),
]

LOCALE_SOURCE_PRIORITY = {
    "en": ["en"],
    "en-gb": ["en-gb", "en"],
    "tr": ["tr"],
    "de": ["de"],
    "fr": ["fr"],
    "es": ["es", "es-us", "es-419"],
    "it": ["it"],
    "pt-br": ["pt-br", "pt"],
    "pt-pt": ["pt-pt", "pt-br", "pt"],
    "ru": ["ru"],
    "ar": ["ar"],
    "hi": ["hi"],
    "ja": ["ja"],
    "ko": ["ko"],
    "zh-cn": ["zh-hans", "zh", "zh-cn"],
    "zh-tw": ["zh-hant", "zh-hans", "zh", "zh-tw"],
    "id": ["id"],
    "nl": ["nl"],
    "pl": ["pl"],
    "sv": ["sv"],
    "th": ["th"],
    "vi": ["vi"],
    "ms": ["ms"],
}

# Keep automatic replacement conservative to avoid corrupting URLs/JS/CSS.
SAFE_SINGLE_TOKEN_REPLACEMENTS = {
    "Home",
    "Language",
    "FAQ",
}

STRINGS_LINE_PATTERN = re.compile(
    r'^\s*"((?:\\.|[^"\\])*)"\s*=\s*"((?:\\.|[^"\\])*)"\s*;\s*$'
)

LOCALE_TEXT_REPLACEMENTS: dict[str, list[tuple[str, str]]] = {}

MANUAL_UI_TRANSLATIONS: dict[str, dict[str, str]] = {
    "tr": {
        "Skip to main content": "Ana icerige gec",
        "Main navigation": "Ana gezinme",
        "Mobile navigation": "Mobil gezinme",
        "Toggle menu": "Menuyu ac/kapat",
        "Industries": "Sektorler",
        "Glossary": "Sozluk",
        "Features": "Ozellikler",
        "Exam Prep": "Sinav Hazirligi",
        "Compare": "Karsilastir",
        "Download Free": "Ucretsiz Indir",
        "Download Free for iOS": "iOS icin Ucretsiz Indir",
        "Explore 6 Industries": "6 Sektoru Kesfet",
        "No Sign Up Required": "Kayit Gerekmez",
        "Privacy Policy": "Gizlilik Politikasi",
        "Terms of Use": "Kullanim Kosullari",
        "Back to Home": "Ana Sayfaya Don",
        "Language": "Dil",
    },
    "de": {
        "Skip to main content": "Zum Hauptinhalt springen",
        "Main navigation": "Hauptnavigation",
        "Mobile navigation": "Mobile Navigation",
        "Toggle menu": "Menue umschalten",
        "Industries": "Branchen",
        "Glossary": "Glossar",
        "Features": "Funktionen",
        "Exam Prep": "Pruefungsvorbereitung",
        "Compare": "Vergleichen",
        "Download Free": "Kostenlos herunterladen",
        "Download Free for iOS": "Fuer iOS kostenlos herunterladen",
        "Explore 6 Industries": "6 Branchen entdecken",
        "No Sign Up Required": "Keine Anmeldung erforderlich",
        "Privacy Policy": "Datenschutzrichtlinie",
        "Terms of Use": "Nutzungsbedingungen",
        "Back to Home": "Zur Startseite",
        "Language": "Sprache",
    },
    "fr": {
        "Skip to main content": "Aller au contenu principal",
        "Main navigation": "Navigation principale",
        "Mobile navigation": "Navigation mobile",
        "Toggle menu": "Basculer le menu",
        "Industries": "Secteurs",
        "Glossary": "Glossaire",
        "Features": "Fonctionnalites",
        "Exam Prep": "Preparation aux examens",
        "Compare": "Comparer",
        "Download Free": "Telecharger gratuitement",
        "Download Free for iOS": "Telecharger gratuitement pour iOS",
        "Explore 6 Industries": "Explorer 6 secteurs",
        "No Sign Up Required": "Sans inscription requise",
        "Privacy Policy": "Politique de confidentialite",
        "Terms of Use": "Conditions d'utilisation",
        "Back to Home": "Retour a l'accueil",
        "Language": "Langue",
    },
    "es": {
        "Skip to main content": "Saltar al contenido principal",
        "Main navigation": "Navegacion principal",
        "Mobile navigation": "Navegacion movil",
        "Toggle menu": "Alternar menu",
        "Industries": "Industrias",
        "Glossary": "Glosario",
        "Features": "Funciones",
        "Exam Prep": "Preparacion para examenes",
        "Compare": "Comparar",
        "Download Free": "Descargar gratis",
        "Download Free for iOS": "Descargar gratis para iOS",
        "Explore 6 Industries": "Explorar 6 industrias",
        "No Sign Up Required": "No se requiere registro",
        "Privacy Policy": "Politica de privacidad",
        "Terms of Use": "Terminos de uso",
        "Back to Home": "Volver al inicio",
        "Language": "Idioma",
    },
    "it": {
        "Skip to main content": "Vai al contenuto principale",
        "Main navigation": "Navigazione principale",
        "Mobile navigation": "Navigazione mobile",
        "Toggle menu": "Apri/chiudi menu",
        "Industries": "Settori",
        "Glossary": "Glossario",
        "Features": "Funzionalita",
        "Exam Prep": "Preparazione esami",
        "Compare": "Confronta",
        "Download Free": "Scarica gratis",
        "Download Free for iOS": "Scarica gratis per iOS",
        "Explore 6 Industries": "Esplora 6 settori",
        "No Sign Up Required": "Nessuna registrazione richiesta",
        "Privacy Policy": "Informativa sulla privacy",
        "Terms of Use": "Termini di utilizzo",
        "Back to Home": "Torna alla home",
        "Language": "Lingua",
    },
    "pt-br": {
        "Skip to main content": "Ir para o conteudo principal",
        "Main navigation": "Navegacao principal",
        "Mobile navigation": "Navegacao mobile",
        "Toggle menu": "Alternar menu",
        "Industries": "Setores",
        "Glossary": "Glossario",
        "Features": "Recursos",
        "Exam Prep": "Preparacao para exames",
        "Compare": "Comparar",
        "Download Free": "Baixar gratis",
        "Download Free for iOS": "Baixar gratis para iOS",
        "Explore 6 Industries": "Explorar 6 setores",
        "No Sign Up Required": "Sem cadastro obrigatorio",
        "Privacy Policy": "Politica de privacidade",
        "Terms of Use": "Termos de uso",
        "Back to Home": "Voltar ao inicio",
        "Language": "Idioma",
    },
    "pt-pt": {
        "Skip to main content": "Ir para o conteudo principal",
        "Main navigation": "Navegacao principal",
        "Mobile navigation": "Navegacao movel",
        "Toggle menu": "Alternar menu",
        "Industries": "Setores",
        "Glossary": "Glossario",
        "Features": "Funcionalidades",
        "Exam Prep": "Preparacao para exames",
        "Compare": "Comparar",
        "Download Free": "Descarregar gratis",
        "Download Free for iOS": "Descarregar gratis para iOS",
        "Explore 6 Industries": "Explorar 6 setores",
        "No Sign Up Required": "Sem registo obrigatorio",
        "Privacy Policy": "Politica de privacidade",
        "Terms of Use": "Termos de utilizacao",
        "Back to Home": "Voltar ao inicio",
        "Language": "Idioma",
    },
    "ru": {
        "Skip to main content": "Перейти к основному содержанию",
        "Main navigation": "Основная навигация",
        "Mobile navigation": "Мобильная навигация",
        "Toggle menu": "Переключить меню",
        "Industries": "Отрасли",
        "Glossary": "Глоссарий",
        "Features": "Функции",
        "Exam Prep": "Подготовка к экзаменам",
        "Compare": "Сравнить",
        "Download Free": "Скачать бесплатно",
        "Download Free for iOS": "Скачать бесплатно для iOS",
        "Explore 6 Industries": "Изучить 6 отраслей",
        "No Sign Up Required": "Регистрация не требуется",
        "Privacy Policy": "Политика конфиденциальности",
        "Terms of Use": "Условия использования",
        "Back to Home": "Назад на главную",
        "Language": "Язык",
    },
    "ar": {
        "Skip to main content": "انتقل إلى المحتوى الرئيسي",
        "Main navigation": "التنقل الرئيسي",
        "Mobile navigation": "التنقل على الهاتف",
        "Toggle menu": "تبديل القائمة",
        "Industries": "القطاعات",
        "Glossary": "مسرد",
        "Features": "الميزات",
        "Exam Prep": "التحضير للاختبار",
        "Compare": "مقارنة",
        "Download Free": "تنزيل مجاني",
        "Download Free for iOS": "تنزيل مجاني لـ iOS",
        "Explore 6 Industries": "استكشف 6 قطاعات",
        "No Sign Up Required": "بدون تسجيل",
        "Privacy Policy": "سياسة الخصوصية",
        "Terms of Use": "شروط الاستخدام",
        "Back to Home": "العودة إلى الرئيسية",
        "Language": "اللغة",
    },
    "hi": {
        "Skip to main content": "मुख्य सामग्री पर जाएं",
        "Main navigation": "मुख्य नेविगेशन",
        "Mobile navigation": "मोबाइल नेविगेशन",
        "Toggle menu": "मेनू बदलें",
        "Industries": "उद्योग",
        "Glossary": "शब्दकोश",
        "Features": "विशेषताएं",
        "Exam Prep": "परीक्षा तैयारी",
        "Compare": "तुलना",
        "Download Free": "मुफ्त डाउनलोड",
        "Download Free for iOS": "iOS के लिए मुफ्त डाउनलोड",
        "Explore 6 Industries": "6 उद्योग देखें",
        "No Sign Up Required": "साइन अप की आवश्यकता नहीं",
        "Privacy Policy": "गोपनीयता नीति",
        "Terms of Use": "उपयोग की शर्तें",
        "Back to Home": "होम पर वापस जाएं",
        "Language": "भाषा",
    },
    "ja": {
        "Skip to main content": "メインコンテンツへ移動",
        "Main navigation": "メインナビゲーション",
        "Mobile navigation": "モバイルナビゲーション",
        "Toggle menu": "メニューを切り替え",
        "Industries": "産業",
        "Glossary": "用語集",
        "Features": "機能",
        "Exam Prep": "試験対策",
        "Compare": "比較",
        "Download Free": "無料でダウンロード",
        "Download Free for iOS": "iOSで無料ダウンロード",
        "Explore 6 Industries": "6つの産業を見る",
        "No Sign Up Required": "登録不要",
        "Privacy Policy": "プライバシーポリシー",
        "Terms of Use": "利用規約",
        "Back to Home": "ホームに戻る",
        "Language": "言語",
    },
    "ko": {
        "Skip to main content": "본문으로 건너뛰기",
        "Main navigation": "메인 내비게이션",
        "Mobile navigation": "모바일 내비게이션",
        "Toggle menu": "메뉴 전환",
        "Industries": "산업",
        "Glossary": "용어집",
        "Features": "기능",
        "Exam Prep": "시험 준비",
        "Compare": "비교",
        "Download Free": "무료 다운로드",
        "Download Free for iOS": "iOS 무료 다운로드",
        "Explore 6 Industries": "6개 산업 보기",
        "No Sign Up Required": "가입 필요 없음",
        "Privacy Policy": "개인정보 처리방침",
        "Terms of Use": "이용 약관",
        "Back to Home": "홈으로 돌아가기",
        "Language": "언어",
    },
    "zh-cn": {
        "Skip to main content": "跳转到主要内容",
        "Main navigation": "主导航",
        "Mobile navigation": "移动导航",
        "Toggle menu": "切换菜单",
        "Industries": "行业",
        "Glossary": "术语表",
        "Features": "功能",
        "Exam Prep": "考试准备",
        "Compare": "对比",
        "Download Free": "免费下载",
        "Download Free for iOS": "在 iOS 上免费下载",
        "Explore 6 Industries": "探索 6 个行业",
        "No Sign Up Required": "无需注册",
        "Privacy Policy": "隐私政策",
        "Terms of Use": "使用条款",
        "Back to Home": "返回首页",
        "Language": "语言",
    },
    "zh-tw": {
        "Skip to main content": "跳到主要內容",
        "Main navigation": "主導覽",
        "Mobile navigation": "行動導覽",
        "Toggle menu": "切換選單",
        "Industries": "行業",
        "Glossary": "術語表",
        "Features": "功能",
        "Exam Prep": "考試準備",
        "Compare": "比較",
        "Download Free": "免費下載",
        "Download Free for iOS": "在 iOS 上免費下載",
        "Explore 6 Industries": "探索 6 個行業",
        "No Sign Up Required": "無需註冊",
        "Privacy Policy": "隱私政策",
        "Terms of Use": "使用條款",
        "Back to Home": "返回首頁",
        "Language": "語言",
    },
    "id": {
        "Skip to main content": "Lewati ke konten utama",
        "Main navigation": "Navigasi utama",
        "Mobile navigation": "Navigasi seluler",
        "Toggle menu": "Ubah menu",
        "Industries": "Industri",
        "Glossary": "Glosarium",
        "Features": "Fitur",
        "Exam Prep": "Persiapan Ujian",
        "Compare": "Bandingkan",
        "Download Free": "Unduh Gratis",
        "Download Free for iOS": "Unduh Gratis untuk iOS",
        "Explore 6 Industries": "Jelajahi 6 Industri",
        "No Sign Up Required": "Tanpa perlu daftar",
        "Privacy Policy": "Kebijakan Privasi",
        "Terms of Use": "Syarat Penggunaan",
        "Back to Home": "Kembali ke Beranda",
        "Language": "Bahasa",
    },
    "nl": {
        "Skip to main content": "Ga naar hoofdinhoud",
        "Main navigation": "Hoofdnavigatie",
        "Mobile navigation": "Mobiele navigatie",
        "Toggle menu": "Menu wisselen",
        "Industries": "Sectoren",
        "Glossary": "Woordenlijst",
        "Features": "Functies",
        "Exam Prep": "Examenvoorbereiding",
        "Compare": "Vergelijken",
        "Download Free": "Gratis downloaden",
        "Download Free for iOS": "Gratis downloaden voor iOS",
        "Explore 6 Industries": "Verken 6 sectoren",
        "No Sign Up Required": "Geen registratie vereist",
        "Privacy Policy": "Privacybeleid",
        "Terms of Use": "Gebruiksvoorwaarden",
        "Back to Home": "Terug naar home",
        "Language": "Taal",
    },
    "pl": {
        "Skip to main content": "Przejdz do glownej tresci",
        "Main navigation": "Nawigacja glowna",
        "Mobile navigation": "Nawigacja mobilna",
        "Toggle menu": "Przelacz menu",
        "Industries": "Branze",
        "Glossary": "Slownik",
        "Features": "Funkcje",
        "Exam Prep": "Przygotowanie do egzaminu",
        "Compare": "Porownaj",
        "Download Free": "Pobierz za darmo",
        "Download Free for iOS": "Pobierz za darmo na iOS",
        "Explore 6 Industries": "Odkryj 6 branz",
        "No Sign Up Required": "Brak wymogu rejestracji",
        "Privacy Policy": "Polityka prywatnosci",
        "Terms of Use": "Warunki uzytkowania",
        "Back to Home": "Wroc do strony glownej",
        "Language": "Jezyk",
    },
    "sv": {
        "Skip to main content": "Hoppa till huvudinnehall",
        "Main navigation": "Huvudnavigering",
        "Mobile navigation": "Mobil navigering",
        "Toggle menu": "Vaxla meny",
        "Industries": "Branscher",
        "Glossary": "Ordlista",
        "Features": "Funktioner",
        "Exam Prep": "Examensforberedelse",
        "Compare": "Jamfor",
        "Download Free": "Ladda ner gratis",
        "Download Free for iOS": "Ladda ner gratis for iOS",
        "Explore 6 Industries": "Utforska 6 branscher",
        "No Sign Up Required": "Ingen registrering kravs",
        "Privacy Policy": "Integritetspolicy",
        "Terms of Use": "Anvandarvillkor",
        "Back to Home": "Tillbaka till startsidan",
        "Language": "Sprak",
    },
    "th": {
        "Skip to main content": "ข้ามไปยังเนื้อหาหลัก",
        "Main navigation": "การนำทางหลัก",
        "Mobile navigation": "การนำทางมือถือ",
        "Toggle menu": "สลับเมนู",
        "Industries": "อุตสาหกรรม",
        "Glossary": "คำศัพท์",
        "Features": "ฟีเจอร์",
        "Exam Prep": "เตรียมสอบ",
        "Compare": "เปรียบเทียบ",
        "Download Free": "ดาวน์โหลดฟรี",
        "Download Free for iOS": "ดาวน์โหลดฟรีสำหรับ iOS",
        "Explore 6 Industries": "สำรวจ 6 อุตสาหกรรม",
        "No Sign Up Required": "ไม่ต้องสมัคร",
        "Privacy Policy": "นโยบายความเป็นส่วนตัว",
        "Terms of Use": "ข้อกำหนดการใช้งาน",
        "Back to Home": "กลับหน้าแรก",
        "Language": "ภาษา",
    },
    "vi": {
        "Skip to main content": "Bo qua den noi dung chinh",
        "Main navigation": "Dieu huong chinh",
        "Mobile navigation": "Dieu huong di dong",
        "Toggle menu": "Chuyen menu",
        "Industries": "Nganh",
        "Glossary": "Thuat ngu",
        "Features": "Tinh nang",
        "Exam Prep": "Luyen thi",
        "Compare": "So sanh",
        "Download Free": "Tai mien phi",
        "Download Free for iOS": "Tai mien phi cho iOS",
        "Explore 6 Industries": "Kham pha 6 nganh",
        "No Sign Up Required": "Khong can dang ky",
        "Privacy Policy": "Chinh sach bao mat",
        "Terms of Use": "Dieu khoan su dung",
        "Back to Home": "Quay lai trang chu",
        "Language": "Ngon ngu",
    },
    "ms": {
        "Skip to main content": "Langkau ke kandungan utama",
        "Main navigation": "Navigasi utama",
        "Mobile navigation": "Navigasi mudah alih",
        "Toggle menu": "Tukar menu",
        "Industries": "Industri",
        "Glossary": "Glosari",
        "Features": "Ciri",
        "Exam Prep": "Persediaan Peperiksaan",
        "Compare": "Bandingkan",
        "Download Free": "Muat Turun Percuma",
        "Download Free for iOS": "Muat Turun Percuma untuk iOS",
        "Explore 6 Industries": "Terokai 6 Industri",
        "No Sign Up Required": "Tiada pendaftaran diperlukan",
        "Privacy Policy": "Dasar Privasi",
        "Terms of Use": "Terma Penggunaan",
        "Back to Home": "Kembali ke Laman Utama",
        "Language": "Bahasa",
    },
}

TR_REPLACEMENTS = [
    ("Skip to main content", "Ana icerige gec"),
    ("Termify Home", "Termify Ana Sayfa"),
    ("Toggle menu", "Menuyu ac/kapat"),
    ("Main navigation", "Ana gezinme"),
    ("Mobile navigation", "Mobil gezinme"),
    ("Privacy Policy", "Gizlilik Politikasi"),
    ("Terms of Use", "Kullanim Kosullari"),
    ("Legal Center", "Yasal Bilgilendirme Merkezi"),
    ("Contact Us", "Iletisim"),
    ("Last updated:", "Son guncelleme:"),
    ("Back to Home", "Ana Sayfaya Don"),
    ("Download Free for iOS", "iOS icin Ucretsiz Indir"),
    ("Download Free", "Ucretsiz Indir"),
    ("No Sign Up Required", "Kayit Gerekmez"),
    ("Download Free on the", "Ucretsiz Indir"),
    ("Industries", "Sektorler"),
    ("Glossary", "Sozluk"),
    ("Features", "Ozellikler"),
    ("Compare", "Karsilastir"),
    ("Exam Prep", "Sinav Hazirligi"),
    ("Language", "Dil"),
    ("Home", "Ana Sayfa"),
    ("Havacilik Ingilizcesi Exams", "Havacilik Ingilizcesi Sinavlari"),
    ("Denizcilik Ingilizcesi Exams", "Denizcilik Ingilizcesi Sinavlari"),
    ("BT/DevOps Ingilizcesi Exams", "BT/DevOps Ingilizcesi Sinavlari"),
    ("for Aviation, Maritime, Logistics, Finance, Cybersecurity and IT/DevOps", "Havacilik, Denizcilik, Lojistik, Finans, Siber Guvenlik ve BT/DevOps icin"),
    ("for Aviation, Maritime, Finance, Cybersecurity & IT", "Havacilik, Denizcilik, Finans, Siber Guvenlik ve BT icin"),
    ("Aviation English", "Havacilik Ingilizcesi"),
    ("Maritime English", "Denizcilik Ingilizcesi"),
    ("Logistics English", "Lojistik Ingilizcesi"),
    ("Finance English", "Finans Ingilizcesi"),
    ("Cybersecurity English", "Siber Guvenlik Ingilizcesi"),
    ("IT/DevOps English", "BT/DevOps Ingilizcesi"),
    ("IT & DevOps English", "BT ve DevOps Ingilizcesi"),
    ("Product", "Urun"),
    ("Key Features", "Temel Ozellikler"),
    ("Exam Preparation", "Sinav Hazirligi"),
    ("App Comparison", "Uygulama Karsilastirmasi"),
    ("Why Free", "Neden Ucretsiz"),
    ("Helpful Links", "Yardimci Baglantilar"),
    ("Aviation Glossary", "Havacilik Sozlugu"),
    ("Termify vs PeakTalk", "Termify ve PeakTalk"),
    ("Termify vs Duolingo", "Termify ve Duolingo"),
    ("Termify vs Babbel", "Termify ve Babbel"),
    ("Privacy", "Gizlilik"),
    ("Terms", "Kosullar"),
    ("Sitemap", "Site Haritasi"),
    ("Professional Terms", "Profesyonel Terimler"),
    ("Industry Modules", "Sektor Modulleri"),
    ("Languages", "Diller"),
    ("Professionals", "Profesyoneller"),
    ("Forever Free Plan", "Her Zaman Ucretsiz Plan"),
    (">Industries<", ">Sektorler<"),
    (">Features<", ">Ozellikler<"),
    (">Compare<", ">Karsilastir<"),
    (">Glossary<", ">Sozluk<"),
    (">Home<", ">Ana Sayfa<"),
    (">Exam Prep<", ">Sinav Hazirligi<"),
    (">Language<", ">Dil<"),
    (
        "The <strong>100% free</strong> professional English app. Learn 4,230+ industry terms for Aviation, Maritime, Logistics, Finance, Cybersecurity and IT/DevOps. Sourced from official <abbr title=\"International Civil Aviation Organization\">ICAO</abbr>, <abbr title=\"International Maritime Organization\">IMO</abbr>, <abbr title=\"International Organization for Standardization\">ISO</abbr> 27001 and <abbr title=\"National Institute of Standards and Technology\">NIST</abbr> standards.",
        "<strong>%100 ucretsiz</strong> profesyonel Ingilizce uygulamasi. Havacilik, denizcilik, lojistik, finans, siber guvenlik ve BT/DevOps alanlarinda 4,230+ terim ogrenin. Icerikler resmi <abbr title=\"International Civil Aviation Organization\">ICAO</abbr>, <abbr title=\"International Maritime Organization\">IMO</abbr>, <abbr title=\"International Organization for Standardization\">ISO</abbr> 27001 ve <abbr title=\"National Institute of Standards and Technology\">NIST</abbr> standartlarina dayanir.",
    ),
    (
        "The <strong>100% free</strong> professional English app. Learn 4,230+ industry terms Havacilik, Denizcilik, Lojistik, Finans, Siber Guvenlik ve BT/DevOps icin. Sourced from official <abbr title=\"International Civil Aviation Organization\">ICAO</abbr>, <abbr title=\"International Maritime Organization\">IMO</abbr>, <abbr title=\"International Organization for Standardization\">ISO</abbr> 27001 and <abbr title=\"National Institute of Standards and Technology\">NIST</abbr> standards.",
        "<strong>%100 ucretsiz</strong> profesyonel Ingilizce uygulamasi. Havacilik, denizcilik, lojistik, finans, siber guvenlik ve BT/DevOps alanlarinda 4,230+ terim ogrenin. Icerikler resmi <abbr title=\"International Civil Aviation Organization\">ICAO</abbr>, <abbr title=\"International Maritime Organization\">IMO</abbr>, <abbr title=\"International Organization for Standardization\">ISO</abbr> 27001 ve <abbr title=\"National Institute of Standards and Technology\">NIST</abbr> standartlarina dayanir.",
    ),
]

TR_PAGE_REPLACEMENTS = {
    "index.html": [
        (
            "100% Free Professional English App for Aviation, Maritime, Finance, Cybersecurity & IT",
            "Havacilik, Denizcilik, Finans, Siber Guvenlik ve BT icin %100 Ucretsiz Profesyonel Ingilizce Uygulamasi",
        ),
        (
            "100% Free Professional English App for 6 Industries",
            "6 Sektor icin %100 Ucretsiz Profesyonel Ingilizce Uygulamasi",
        ),
        (
            "100% Free Professional English App",
            "%100 Ucretsiz Profesyonel Ingilizce Uygulamasi",
        ),
        (
            "Free Professional English App Logo",
            "Ucretsiz Profesyonel Ingilizce Uygulamasi Logosu",
        ),
        (
            "Termify \u2014 100% Free Professional English Learning App",
            "Termify \u2014 %100 Ucretsiz Profesyonel Ingilizce Ogrenme Uygulamasi",
        ),
        (
            "Termify - 100% Free Professional English App for Aviation, Maritime, Finance, Cybersecurity & IT",
            "Termify - Havacilik, Denizcilik, Finans, Siber Guvenlik ve BT icin %100 Ucretsiz Profesyonel Ingilizce Uygulamasi",
        ),
        (
            "Termify is a 100% free professional English app. Learn 4,230+ industry terms for Aviation, Maritime, Logistics, Finance, Cybersecurity and IT/DevOps. Free download, free terms, free quizzes. Sourced from ICAO, IMO, ISO 27001 & NIST with native pronunciation.",
            "Termify, %100 ucretsiz profesyonel Ingilizce uygulamasidir. Havacilik, denizcilik, lojistik, finans, siber guvenlik ve BT/DevOps alanlari icin 4,230+ sektor terimi ogrenin. Ucretsiz indirme, ucretsiz terimler, ucretsiz quizler. ICAO, IMO, ISO 27001 ve NIST kaynakli icerikler ana dil telaffuzuyla sunulur.",
        ),
        (
            "Termify is a 100% free professional English app. Learn 4,230+ industry terms Havacilik, Denizcilik, Lojistik, Finans, Siber Guvenlik ve BT/DevOps icin. Free download, free terms, free quizzes. Sourced from ICAO, IMO, ISO 27001 & NIST with native pronunciation.",
            "Termify, %100 ucretsiz profesyonel Ingilizce uygulamasidir. Havacilik, denizcilik, lojistik, finans, siber guvenlik ve BT/DevOps alanlari icin 4,230+ sektor terimi ogrenin. Ucretsiz indirme, ucretsiz terimler, ucretsiz quizler. ICAO, IMO, ISO 27001 ve NIST kaynakli icerikler ana dil telaffuzuyla sunulur.",
        ),
        ("Explore 6 Industries", "6 Sektoru Kesfet"),
        (
            "<strong>100% free</strong> to download and use. Join 50,000+ professionals from airlines, shipping lines, banks, SOC teams and tech companies in over 120 countries. No credit card required, no trial period &mdash; just free professional English learning.",
            "<strong>%100 ucretsiz</strong> indirip hemen kullanabilirsiniz. 120+ ulkede havayollarindan denizcilik sirketlerine, bankalardan SOC ekiplerine ve teknoloji sirketlerine kadar 50,000+ profesyonele katilin. Kredi karti gerekmez, deneme suresi yoktur &mdash; sadece ucretsiz profesyonel Ingilizce ogrenimi.",
        ),
        (
            "Termify - 100% Free Professional English App for 6 Industries",
            "Termify - 6 Sektor icin %100 Ucretsiz Profesyonel Ingilizce Uygulamasi",
        ),
        (
            "Termify - 100% Free Professional English App",
            "Termify - %100 Ucretsiz Profesyonel Ingilizce Uygulamasi",
        ),
        ("Termify - Free Professional English App Logo", "Termify - Ucretsiz Profesyonel Ingilizce Uygulamasi Logosu"),
        ("100% Free &mdash; No credit card required", "%100 Ucretsiz &mdash; Kredi karti gerekmez"),
        ("Learn <span class=\"gradient-text\">Professional English</span> for Free", "<span class=\"gradient-text\">Profesyonel Ingilizce</span>yi Ucretsiz Ogrenin"),
        (
            "<strong>Termify</strong> is a <strong>100% free</strong> app that teaches mission-critical English terminology for Aviation, Maritime, Logistics, Finance, Cybersecurity and IT/DevOps. 4,230+ terms with native pronunciation, IPA transcriptions and career quizzes &mdash; all at no cost.",
            "<strong>Termify</strong>, Havacilik, Denizcilik, Lojistik, Finans, Siber Guvenlik ve BT/DevOps icin kritik Ingilizce terminolojiyi ogreten <strong>%100 ucretsiz</strong> bir uygulamadir. 4,230+ terim; ana dil telaffuzu, IPA transkripsiyonlari ve kariyer quizleriyle tamamen ucretsiz sunulur.",
        ),
        ("Built on <span>official industry standards</span>", "<span>Resmi sektor standartlari</span> ile hazirlandi"),
        ("Professional English for Every Industry", "Her Sektor icin Profesyonel Ingilizce"),
        (
            "<strong>Termify</strong> covers 6 high-demand professional fields. Every term is sourced from official industry manuals and paired with native pronunciation, IPA transcriptions, real-world dialogues and contextual usage notes.",
            "<strong>Termify</strong>, yuksek talep goren 6 profesyonel alani kapsar. Her terim resmi sektor kaynaklarindan alinmis; ana dil telaffuzu, IPA transkripsiyonu, gercek hayattan diyaloglar ve baglamsal kullanim notlariyla sunulmustur.",
        ),
        ("Core Features", "Temel Ozellikler"),
        ("Everything You Need to Master Professional English", "Profesyonel Ingilizceyi Ust Duzey Ogrenmek Icin Ihtiyaciniz Olan Her Sey"),
        (
            "Termify combines proven learning methods with industry-specific content to help you learn faster and retain terminology longer.",
            "Termify, kanitlanmis ogrenme yontemlerini sektor odakli iceriklerle birlestirerek daha hizli ogrenmenizi ve terimleri daha uzun sure hatirlamanizi saglar.",
        ),
        ("Professional Exam Preparation", "Profesyonel Sinav Hazirligi"),
        ("Prepare for International Professional English Exams", "Uluslararasi Profesyonel Ingilizce Sinavlarina Hazirlanin"),
        ("Completely Free &mdash; Everything Included", "Tamamen Ucretsiz &mdash; Her Sey Dahil"),
        ("How Does Termify Compare to Other Professional English Apps?", "Termify, Diger Profesyonel Ingilizce Uygulamalariyla Nasil Karsilasiyor?"),
        ("Available in 23 Languages &mdash; Completely Free", "23 Dilde Kullanilabilir &mdash; Tamamen Ucretsiz"),
        ("Frequently Asked Questions About Termify", "Termify Hakkinda Sik Sorulan Sorular"),
        ("Who Uses Termify?", "Termify'yi Kimler Kullaniyor?"),
        ("Download Termify Free &mdash; Start Learning Today", "Termify'yi Ucretsiz Indirin &mdash; Bugun Ogrenmeye Baslayin"),
        ("All rights reserved.", "Tum haklari saklidir."),
        ("100% Free Professional English for Aviation, Maritime, Logistics, Finance, Cybersecurity &amp; IT/DevOps", "Havacilik, Denizcilik, Lojistik, Finans, Siber Guvenlik ve BT/DevOps icin %100 Ucretsiz Profesyonel Ingilizce"),
    ]
}

TR_INDEX_MAIN_CONTENT = """
    <main role="main" id="content">
        <section class="hero" id="hero" aria-labelledby="main-heading">
            <div class="vlines" aria-hidden="true"></div>
            <div class="container">
                <div class="hero-content">
                    <a href="#download" class="hero-badge">
                        <span class="badge-dot" aria-hidden="true"></span>
                        <span>%100 Ucretsiz - Kredi karti gerekmez</span>
                        <span class="badge-divider" aria-hidden="true"></span>
                    </a>

                    <h1 id="main-heading">
                        <span class="gradient-text">Profesyonel Ingilizce</span>yi Ucretsiz Ogrenin
                    </h1>

                    <p class="hero-description">
                        Termify, Havacilik, Denizcilik, Lojistik, Finans, Siber Guvenlik ve BT/DevOps alanlari icin
                        4,230+ terim sunan %100 ucretsiz profesyonel Ingilizce uygulamasidir.
                        Ana dil telaffuzu, IPA transkripsiyonlari ve kariyer quizleri dahildir.
                    </p>

                    <div class="btn-group">
                        <a href="https://apps.apple.com/app/professional-english-termify/id6744872522" class="btn btn-primary btn-lg" aria-label="Termify uygulamasini App Store'dan ucretsiz indir">
                            iOS icin Ucretsiz Indir
                        </a>
                        <a href="#industries" class="btn btn-secondary btn-lg">
                            6 Sektoru Kesfet
                        </a>
                    </div>

                    <div class="hero-stats">
                        <div class="hero-stat">
                            <div class="stat-value free-highlight">FREE</div>
                            <div class="stat-label">Her Zaman Ucretsiz</div>
                        </div>
                        <div class="hero-stat">
                            <div class="stat-value">4,230+</div>
                            <div class="stat-label">Profesyonel Terim</div>
                        </div>
                        <div class="hero-stat">
                            <div class="stat-value">6</div>
                            <div class="stat-label">Sektor Modulu</div>
                        </div>
                        <div class="hero-stat">
                            <div class="stat-value">23</div>
                            <div class="stat-label">Dil</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section class="section" id="industries" aria-labelledby="industries-heading">
            <div class="container">
                <div class="section-header animate-on-scroll">
                    <span class="section-label">6 Sektor Modulu</span>
                    <h2 id="industries-heading">Her Sektor icin Profesyonel Ingilizce</h2>
                    <p>
                        Tum icerikler resmi standartlara dayali ve gercek is akisina uygun olarak hazirlandi.
                    </p>
                </div>

                <div class="industries-grid">
                    <article class="industry-card animate-on-scroll" data-field="aviation">
                        <div class="card-icon" aria-hidden="true">&#9992;</div>
                        <h3>Havacilik Ingilizcesi</h3>
                        <p>ICAO ve FAA terminolojisi, pilot-ATC iletisimi ve operasyonel ifade kaliplari.</p>
                        <div class="card-tags">
                            <span class="card-tag">ICAO Doc 9432</span>
                            <span class="card-tag">FAA PCG</span>
                        </div>
                    </article>

                    <article class="industry-card animate-on-scroll" data-field="maritime">
                        <div class="card-icon" aria-hidden="true">&#9875;</div>
                        <h3>Denizcilik Ingilizcesi</h3>
                        <p>IMO SMCP, kopruustu iletisimi, emniyet komutlari ve deniz operasyonu sozlugu.</p>
                        <div class="card-tags">
                            <span class="card-tag">IMO SMCP</span>
                            <span class="card-tag">STCW</span>
                        </div>
                    </article>

                    <article class="industry-card animate-on-scroll" data-field="logistics">
                        <div class="card-icon" aria-hidden="true">&#128230;</div>
                        <h3>Lojistik Ingilizcesi</h3>
                        <p>Incoterms 2020, tedarik zinciri KPI'lari, gumruk ve dis ticaret dokumani terimleri.</p>
                        <div class="card-tags">
                            <span class="card-tag">Incoterms 2020</span>
                            <span class="card-tag">FIATA</span>
                        </div>
                    </article>

                    <article class="industry-card animate-on-scroll" data-field="finance">
                        <div class="card-icon" aria-hidden="true">&#128176;</div>
                        <h3>Finans Ingilizcesi</h3>
                        <p>Trading, bankacilik, raporlama ve fintech terminolojisi; sinav odakli kelime kapsami.</p>
                        <div class="card-tags">
                            <span class="card-tag">CFA</span>
                            <span class="card-tag">ACCA</span>
                        </div>
                    </article>

                    <article class="industry-card animate-on-scroll" data-field="cybersecurity">
                        <div class="card-icon" aria-hidden="true">&#128274;</div>
                        <h3>Siber Guvenlik Ingilizcesi</h3>
                        <p>ISO 27001 ve NIST uyumlu tehdit, risk, SOC ve olay mudahale terminolojisi.</p>
                        <div class="card-tags">
                            <span class="card-tag">ISO 27001</span>
                            <span class="card-tag">NIST</span>
                        </div>
                    </article>

                    <article class="industry-card animate-on-scroll" data-field="devops">
                        <div class="card-icon" aria-hidden="true">&#128187;</div>
                        <h3>BT/DevOps Ingilizcesi</h3>
                        <p>Cloud mimarisi, CI/CD, incident response ve ITIL v4 tabanli teknik iletisim dili.</p>
                        <div class="card-tags">
                            <span class="card-tag">CI/CD</span>
                            <span class="card-tag">ITIL v4</span>
                        </div>
                    </article>
                </div>
            </div>
        </section>

        <section class="section" id="features" aria-labelledby="features-heading">
            <div class="container">
                <div class="section-header animate-on-scroll">
                    <span class="section-label">Temel Ozellikler</span>
                    <h2 id="features-heading">Hizli Ogrenme, Kalici Hatirlama</h2>
                    <p>Uygulama, profesyonel ortamlarda kullanilan terminolojiyi pratik odakli yontemlerle ogretir.</p>
                </div>

                <div class="features-list">
                    <article class="feature-item animate-on-scroll">
                        <div class="feature-icon" aria-hidden="true">&#127911;</div>
                        <div>
                            <h3>Ana Dil Telaffuzu + IPA</h3>
                            <p>Her terim icin seslendirme ve IPA transkripsiyonu ile dogru telaffuz.</p>
                        </div>
                    </article>
                    <article class="feature-item animate-on-scroll">
                        <div class="feature-icon" aria-hidden="true">&#128257;</div>
                        <div>
                            <h3>Uyarlamali Tekrar Sistemi</h3>
                            <p>Zorlandigin terimleri daha sik gosterir, ogrendiklerini uzun vadede kalici yapar.</p>
                        </div>
                    </article>
                    <article class="feature-item animate-on-scroll">
                        <div class="feature-icon" aria-hidden="true">&#128172;</div>
                        <div>
                            <h3>Gercek Senaryo Diyaloglari</h3>
                            <p>Pilot-ATC, kaptan-ekip, SOC ekipleri gibi mesleki iletisim senaryolari.</p>
                        </div>
                    </article>
                    <article class="feature-item animate-on-scroll">
                        <div class="feature-icon" aria-hidden="true">&#127942;</div>
                        <div>
                            <h3>Kariyer Quizleri ve Sertifika</h3>
                            <p>Sinav mantigina uygun quizler ve paylasilabilir PDF sertifika ciktilari.</p>
                        </div>
                    </article>
                    <article class="feature-item animate-on-scroll">
                        <div class="feature-icon" aria-hidden="true">&#129302;</div>
                        <div>
                            <h3>AI Destekli Ogrenme</h3>
                            <p>Guclu/zayif alanlara gore calisma yolunu duzenleyen uyarlamali ogrenme yapisi.</p>
                        </div>
                    </article>
                    <article class="feature-item animate-on-scroll">
                        <div class="feature-icon" aria-hidden="true">&#128268;</div>
                        <div>
                            <h3>Offline Kullanim</h3>
                            <p>Ilk indirmeden sonra internet olmadan da terim calisma, dinleme ve quiz cozme.</p>
                        </div>
                    </article>
                </div>
            </div>
        </section>

        <section class="section" id="how-it-works" aria-labelledby="exam-heading" style="border-top: 1px solid var(--color-border);">
            <div class="container">
                <div class="section-header animate-on-scroll">
                    <span class="section-label">Sinav Hazirligi</span>
                    <h2 id="exam-heading">Uluslararasi Mesleki Sinavlara Hazirlanin</h2>
                    <p>Icerikler; ICAO, IMO, FIATA, CFA, CISSP, AWS, ITIL gibi global standart ve sertifikalara gore duzenlenmistir.</p>
                </div>
                <div class="exam-grid">
                    <article class="exam-card animate-on-scroll" data-field="aviation">
                        <h3>Havacilik</h3>
                        <p>ICAO Level 4/5/6 ve EASA FCL.055 odakli terminoloji ve iletisim kaliplari.</p>
                    </article>
                    <article class="exam-card animate-on-scroll" data-field="maritime">
                        <h3>Denizcilik</h3>
                        <p>IMO SMCP, STCW ve gemi operasyonlarinda kullanilan kritik komut ve ifadeler.</p>
                    </article>
                    <article class="exam-card animate-on-scroll" data-field="tech">
                        <h3>Teknoloji ve Guvenlik</h3>
                        <p>ISO 27001, NIST, AWS/Azure, ITIL ve modern operasyon terminolojisi.</p>
                    </article>
                </div>
            </div>
        </section>

        <section class="section" id="comparison" aria-labelledby="comparison-heading" style="border-top: 1px solid var(--color-border);">
            <div class="container">
                <div class="section-header animate-on-scroll">
                    <span class="section-label">Karsilastirma</span>
                    <h2 id="comparison-heading">Termify Neden Farkli?</h2>
                    <p>Termify; profesyonel terminoloji, resmi kaynak uyumu ve %100 ucretsiz modeli birlikte sunar.</p>
                </div>
                <div class="comparison-cards">
                    <article class="comparison-card animate-on-scroll">
                        <h3>%100 Ucretsiz</h3>
                        <p>Abonelik yok, gizli ucret yok, tum moduller acik.</p>
                    </article>
                    <article class="comparison-card animate-on-scroll">
                        <h3>Resmi Kaynak Uyumlu</h3>
                        <p>ICAO, IMO, ISO 27001, NIST gibi standartlara dayali icerik.</p>
                    </article>
                    <article class="comparison-card animate-on-scroll">
                        <h3>Meslek Odakli</h3>
                        <p>Genel Ingilizce degil; gercek is ortami dili ve terminolojisi.</p>
                    </article>
                </div>
            </div>
        </section>

        <section class="section" id="faq" aria-labelledby="faq-heading">
            <div class="container">
                <div class="section-header animate-on-scroll">
                    <span class="section-label">FAQ</span>
                    <h2 id="faq-heading">Sik Sorulan Sorular</h2>
                </div>
                <div class="faq-grid">
                    <details class="faq-item animate-on-scroll">
                        <summary><strong>Termify nedir?</strong></summary>
                        <div class="faq-answer">
                            <p>Termify, 6 farkli sektorde profesyonel Ingilizce terminoloji ogreten %100 ucretsiz bir ogrenme uygulamasidir.</p>
                        </div>
                    </details>
                    <details class="faq-item animate-on-scroll">
                        <summary><strong>Gercekten tamamen ucretsiz mi?</strong></summary>
                        <div class="faq-answer">
                            <p>Evet. Tum moduller, terimler, quizler ve dil secenekleri ucretsizdir.</p>
                        </div>
                    </details>
                    <details class="faq-item animate-on-scroll">
                        <summary><strong>Hangi platformlarda calisiyor?</strong></summary>
                        <div class="faq-answer">
                            <p>Uygulama iOS platformunda (iPhone/iPad) kullanilabilir.</p>
                        </div>
                    </details>
                    <details class="faq-item animate-on-scroll">
                        <summary><strong>Offline kullanim var mi?</strong></summary>
                        <div class="faq-answer">
                            <p>Evet. Ilk indirme sonrasinda bircok icerik offline olarak kullanilabilir.</p>
                        </div>
                    </details>
                </div>
            </div>
        </section>

        <section class="section cta-section" id="download" aria-labelledby="download-heading" style="border-top: 1px solid var(--color-border);">
            <div class="container">
                <div class="cta-content animate-on-scroll">
                    <h2 id="download-heading">Termify'yi Ucretsiz Indirin - Bugun Baslayin</h2>
                    <p>%100 ucretsiz profesyonel Ingilizce ogrenimi icin hemen App Store'dan indirin.</p>
                    <div class="store-badges">
                        <a href="https://apps.apple.com/app/professional-english-termify/id6744872522" class="store-badge" aria-label="Termify uygulamasini App Store'dan ucretsiz indir">
                            <span class="store-text">
                                <span class="store-label">Ucretsiz Indir</span>
                                <span class="store-name">App Store</span>
                            </span>
                        </a>
                    </div>
                </div>
            </div>
        </section>
    </main>
"""


def language_switcher_snippet() -> str:
    locale_names = {
        "en": "English (US)",
        "en-gb": "English (UK)",
        "tr": "Turkce",
        "de": "Deutsch",
        "fr": "Francais",
        "es": "Espanol",
        "it": "Italiano",
        "pt-br": "Portugues (BR)",
        "pt-pt": "Portugues (PT)",
        "ru": "Russkiy",
        "ar": "al arabiyya",
        "hi": "Hindi",
        "ja": "Nihongo",
        "ko": "Hangugeo",
        "zh-cn": "Chinese (Simplified)",
        "zh-tw": "Chinese (Traditional)",
        "id": "Bahasa Indonesia",
        "nl": "Nederlands",
        "pl": "Polski",
        "sv": "Svenska",
        "th": "Thai",
        "vi": "Tieng Viet",
        "ms": "Bahasa Melayu",
    }
    label_by_locale = {
        "en": "Language",
        "en-gb": "Language",
        "tr": "Dil",
        "de": "Sprache",
        "fr": "Langue",
        "es": "Idioma",
        "it": "Lingua",
        "pt-br": "Idioma",
        "pt-pt": "Idioma",
        "ru": "Yazyk",
        "ar": "al-lugha",
        "hi": "Bhasha",
        "ja": "Gengo",
        "ko": "Eoneo",
        "zh-cn": "Yuyan",
        "zh-tw": "Yuyan",
        "id": "Bahasa",
        "nl": "Taal",
        "pl": "Jezyk",
        "sv": "Sprak",
        "th": "Phasa",
        "vi": "Ngon ngu",
        "ms": "Bahasa",
    }

    locale_options = "\n".join(
        f'      <option value="{loc["code"]}">{locale_names.get(loc["code"], loc["hreflang"])}</option>'
        for loc in LOCALES
    )
    locale_codes = [loc["code"] for loc in LOCALES if not loc["is_default"]]
    label_json = json.dumps(label_by_locale, ensure_ascii=True)
    locale_codes_json = json.dumps(locale_codes)
    return f"""
<div class="termify-lang-switcher" id="termify-lang-switcher">
  <label for="termify-lang-select">Language</label>
  <select id="termify-lang-select">
    {locale_options}
  </select>
</div>
<style>
.termify-lang-switcher {{
  position: fixed;
  right: 1rem;
  bottom: 1rem;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.7rem;
  border: 1px solid rgba(255,255,255,0.22);
  border-radius: 9999px;
  background: rgba(8,8,10,0.92);
  color: #fafafa;
  font-size: 12px;
  backdrop-filter: blur(8px);
}}
.termify-lang-switcher label {{
  font-weight: 600;
  opacity: 0.92;
}}
.termify-lang-switcher select {{
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 9999px;
  background: #121216;
  color: #fafafa;
  padding: 0.2rem 0.5rem;
  font-size: 12px;
}}
@media (max-width: 640px) {{
  .termify-lang-switcher {{
    left: 0.75rem;
    right: 0.75rem;
    bottom: 0.75rem;
    justify-content: space-between;
  }}
}}
</style>
<script>
(function() {{
  var localePrefixes = {locale_codes_json};
  var labelByLocale = {label_json};
  var label = document.querySelector('label[for="termify-lang-select"]');
  var select = document.getElementById('termify-lang-select');
  if (!select) return;

  var path = window.location.pathname || '/';
  var current = 'en';
  for (var i = 0; i < localePrefixes.length; i++) {{
    var code = localePrefixes[i];
    if (path === '/' + code || path.indexOf('/' + code + '/') === 0) {{
      current = code;
      break;
    }}
  }}

  var basePath = path;
  if (current !== 'en') {{
    var prefix = '/' + current;
    if (basePath === prefix) {{
      basePath = '/';
    }} else if (basePath.indexOf(prefix + '/') === 0) {{
      basePath = basePath.slice(prefix.length) || '/';
    }}
  }}
  select.value = current;
  if (label && labelByLocale[current]) {{
    label.textContent = labelByLocale[current];
  }}
  select.addEventListener('change', function() {{
    var target = this.value || 'en';
    var nextPath = target === 'en' ? basePath : ('/' + target + (basePath === '/' ? '/' : basePath));
    var query = window.location.search || '';
    var hash = window.location.hash || '';
    window.location.href = nextPath + query + hash;
  }});
}})();
</script>
"""


def normalize_locale_code(code: str) -> str:
    return code.strip().lower().replace("_", "-")


def decode_apple_escaped(value: str) -> str:
    def replacer(match: re.Match) -> str:
        token = match.group(1)
        if token == "n":
            return "\n"
        if token == "r":
            return "\r"
        if token == "t":
            return "\t"
        if token == '"':
            return '"'
        if token == "\\":
            return "\\"
        if token.startswith("u") and len(token) == 5:
            return chr(int(token[1:], 16))
        if token.startswith("U") and len(token) == 9:
            return chr(int(token[1:], 16))
        return token

    return re.sub(r'\\(u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8}|["\\nrt])', replacer, value)


def parse_strings_file(path: Path) -> dict[str, str]:
    content = path.read_text(encoding="utf-8")
    result: dict[str, str] = {}
    for line in content.splitlines():
        match = STRINGS_LINE_PATTERN.match(line)
        if not match:
            continue
        key = decode_apple_escaped(match.group(1))
        value = decode_apple_escaped(match.group(2))
        result[key] = value
    return result


def load_localizable_bundles(root: Path) -> dict[str, dict[str, str]]:
    bundles: dict[str, dict[str, str]] = {}
    if not root.exists():
        return bundles

    for locale_dir in root.glob("*.lproj"):
        if not locale_dir.is_dir():
            continue
        code = normalize_locale_code(locale_dir.name[:-6])
        merged: dict[str, str] = {}
        for strings_file in sorted(locale_dir.glob("Localizable*.strings")):
            try:
                merged.update(parse_strings_file(strings_file))
            except OSError:
                continue
        if merged:
            bundles[code] = merged
    return bundles


def should_auto_replace_phrase(source: str) -> bool:
    phrase = source.strip()
    if not phrase:
        return False
    if phrase.startswith("http://") or phrase.startswith("https://"):
        return False
    if "@" in phrase and " " not in phrase:
        return False
    if phrase in SAFE_SINGLE_TOKEN_REPLACEMENTS:
        return True
    return " " in phrase


def bundle_for_locale(bundles: dict[str, dict[str, str]], locale_code: str) -> Optional[dict[str, str]]:
    normalized = normalize_locale_code(locale_code)
    candidates = [normalized]
    base = normalized.split("-")[0]
    if base != normalized:
        candidates.append(base)
    if normalized == "zh":
        candidates.extend(["zh-hans", "zh-cn", "zh-hant", "zh-tw"])
    if normalized == "es":
        candidates.extend(["es-us", "es-419"])
    if normalized == "pt":
        candidates.extend(["pt-br", "pt-pt"])
    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate in bundles:
            return bundles[candidate]
    return None


def build_locale_text_replacements() -> dict[str, list[tuple[str, str]]]:
    replacements: dict[str, dict[str, str]] = {
        locale["code"]: {} for locale in LOCALES if not locale["is_default"]
    }

    for root in TRANSLATION_ROOTS:
        bundles = load_localizable_bundles(root)
        en_bundle = bundle_for_locale(bundles, "en")
        if not en_bundle:
            continue

        for locale in LOCALES:
            code = locale["code"]
            if locale["is_default"]:
                continue

            source_priority = LOCALE_SOURCE_PRIORITY.get(code, [code])
            target_bundle = None
            for source_code in source_priority:
                target_bundle = bundle_for_locale(bundles, source_code)
                if target_bundle:
                    break
            if not target_bundle:
                continue

            locale_replacements = replacements[code]
            for key, english_value in en_bundle.items():
                if key not in target_bundle:
                    continue
                localized_value = target_bundle[key]
                if not localized_value or localized_value == english_value:
                    continue
                if not should_auto_replace_phrase(english_value):
                    continue
                locale_replacements.setdefault(english_value, localized_value)

    for locale_code, phrase_map in MANUAL_UI_TRANSLATIONS.items():
        locale_replacements = replacements.get(locale_code)
        if locale_replacements is None:
            continue
        for source, target in phrase_map.items():
            locale_replacements[source] = target
        exam_prep = phrase_map.get("Exam Prep")
        if exam_prep:
            locale_replacements.setdefault("Exam Preparation", exam_prep)
            locale_replacements.setdefault("Professional Exam Preparation", exam_prep)
        download_free = phrase_map.get("Download Free")
        if download_free:
            locale_replacements.setdefault("Download Free on the", download_free)

    # Keep existing high-coverage TR overrides as the source of truth.
    tr_map = replacements.get("tr", {})
    for source, target in TR_REPLACEMENTS:
        tr_map[source] = target
    for page_items in TR_PAGE_REPLACEMENTS.values():
        for source, target in page_items:
            tr_map[source] = target
    replacements["tr"] = tr_map

    finalized: dict[str, list[tuple[str, str]]] = {}
    for locale_code, mapping in replacements.items():
        finalized[locale_code] = sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True)
    return finalized


def ensure_locale_replacements_loaded() -> None:
    global LOCALE_TEXT_REPLACEMENTS
    if LOCALE_TEXT_REPLACEMENTS:
        return
    LOCALE_TEXT_REPLACEMENTS = build_locale_text_replacements()


def locale_prefix(locale: dict) -> str:
    return "" if locale["is_default"] else f"/{locale['code']}"


def html_dir(locale: dict) -> str:
    return "rtl" if locale["code"] == "ar" else "ltr"


def og_locale_tag(locale: dict) -> str:
    mapping = {
        "en": "en_US",
        "en-gb": "en_GB",
        "tr": "tr_TR",
        "de": "de_DE",
        "fr": "fr_FR",
        "es": "es_ES",
        "it": "it_IT",
        "pt-br": "pt_BR",
        "pt-pt": "pt_PT",
        "ru": "ru_RU",
        "ar": "ar_AR",
        "hi": "hi_IN",
        "ja": "ja_JP",
        "ko": "ko_KR",
        "zh-cn": "zh_CN",
        "zh-tw": "zh_TW",
        "id": "id_ID",
        "nl": "nl_NL",
        "pl": "pl_PL",
        "sv": "sv_SE",
        "th": "th_TH",
        "vi": "vi_VN",
        "ms": "ms_MY",
    }
    return mapping.get(locale["code"], "en_US")


def source_path_for_file(rel_file: str) -> str:
    return "/" if rel_file == "index.html" else f"/{rel_file}"


def localized_path(rel_file: str, locale: dict) -> str:
    src_path = source_path_for_file(rel_file)
    p = locale_prefix(locale)
    if src_path == "/":
        return f"{p}/" if p else "/"
    return f"{p}{src_path}"


def should_localize_path(path: str) -> bool:
    if not path.startswith("/"):
        return False
    for prefix in SKIP_PREFIXES:
        if path.startswith(prefix):
            return False
    return True


def has_known_locale_prefix(path: str) -> bool:
    for loc in LOCALES:
        code = loc["code"]
        if path == f"/{code}" or path.startswith(f"/{code}/"):
            return True
    return False


def localize_href(value: str, locale: dict) -> str:
    p = locale_prefix(locale)
    if locale["is_default"]:
        return value

    if value.startswith(("mailto:", "tel:", "javascript:", "#")):
        return value

    if value.startswith("https://apps.apple.com"):
        return value

    if value.startswith("https://protermify.com"):
        path = value[len("https://protermify.com") :]
        if has_known_locale_prefix(path):
            return value
        if should_localize_path(path):
            return f"https://protermify.com{p}{path}"
        return value

    if has_known_locale_prefix(value):
        return value

    if should_localize_path(value):
        return f"{p}{value}"

    return value


def build_hreflang_block(rel_file: str) -> str:
    lines = ["    <!-- Hreflang Tags -->"]
    for loc in LOCALES:
        href = f"{SITE_URL}{localized_path(rel_file, loc)}"
        lines.append(f'    <link rel="alternate" hreflang="{loc["hreflang"]}" href="{href}">')
    default_href = f"{SITE_URL}{localized_path(rel_file, LOCALES[0])}"
    lines.append(f'    <link rel="alternate" hreflang="x-default" href="{default_href}">')
    return "\n".join(lines)


def replace_hreflang_block(content: str, rel_file: str) -> str:
    new_block = build_hreflang_block(rel_file)
    pattern = re.compile(
        r"<!-- Hreflang Tags -->\n(?:\s*<link rel=\"alternate\" hreflang=\"[^\"]+\" href=\"[^\"]+\">\n?)+",
        re.MULTILINE,
    )
    if pattern.search(content):
        return pattern.sub(new_block + "\n", content, count=1)
    return content


def replace_in_text_nodes(content: str, replacements: list[tuple[str, str]]) -> str:
    parts = re.split(r"(<[^>]+>)", content)
    output: list[str] = []
    in_script = False
    in_style = False

    for part in parts:
        if not part:
            continue
        if part.startswith("<"):
            lower = part.lower()
            if lower.startswith("<script"):
                in_script = True
            elif lower.startswith("</script"):
                in_script = False
            elif lower.startswith("<style"):
                in_style = True
            elif lower.startswith("</style"):
                in_style = False
            output.append(part)
            continue

        if in_script or in_style:
            output.append(part)
            continue

        text = part
        for source, target in replacements:
            text = text.replace(source, target)
        output.append(text)

    return "".join(output)


def apply_text_overrides(content: str, locale: dict, rel_file: str) -> str:
    if locale["is_default"]:
        return content

    ensure_locale_replacements_loaded()
    replacements = LOCALE_TEXT_REPLACEMENTS.get(locale["code"], [])
    return replace_in_text_nodes(content, replacements)


def localize_file(rel_file: str, locale: dict) -> tuple[Path, str]:
    src = BASE_DIR / rel_file
    content = src.read_text(encoding="utf-8")

    locale_lang = locale["hreflang"].lower()
    page_path = localized_path(rel_file, locale)
    page_url = f"{SITE_URL}{page_path}"

    content = re.sub(
        r'<html lang="[^"]+"(?:\s+dir="[^"]+")?',
        f'<html lang="{locale_lang}" dir="{html_dir(locale)}"',
        content,
        count=1,
    )

    def href_replacer(match: re.Match) -> str:
        value = match.group(1)
        localized = localize_href(value, locale)
        return f'href="{localized}"'

    content = re.sub(r'href="([^"]+)"', href_replacer, content)

    # Ensure asset links remain absolute in locale-prefixed copies.
    content = re.sub(r'href="(?:\.\./)+css/style\.css"', 'href="/css/style.css"', content)
    content = re.sub(r'src="(?:\.\./)+js/main\.js"', 'src="/js/main.js"', content)

    content = re.sub(
        r'(<link rel="canonical" href=")[^"]+(">)',
        rf"\1{page_url}\2",
        content,
        count=1,
    )
    content = re.sub(
        r'(<meta property="og:url" content=")[^"]+(">)',
        rf"\1{page_url}\2",
        content,
        count=1,
    )
    content = re.sub(
        r'(<meta property="og:locale" content=")[^"]+(">)',
        rf"\1{og_locale_tag(locale)}\2",
        content,
        count=1,
    )

    content = replace_hreflang_block(content, rel_file)
    content = apply_text_overrides(content, locale, rel_file)

    if "</body>" in content and "termify-lang-switcher" not in content:
        content = content.replace("</body>", language_switcher_snippet() + "\n</body>", 1)

    if locale["is_default"]:
        out_path = src
    else:
        out_path = BASE_DIR / locale["code"] / rel_file
        out_path.parent.mkdir(parents=True, exist_ok=True)
    return out_path, content


def cleanup_locale_dirs() -> None:
    for loc in LOCALES:
        if loc["is_default"]:
            continue
        locale_root = BASE_DIR / loc["code"]
        if locale_root.exists() and locale_root.is_dir():
            # Keep only glossary folder generated elsewhere; refresh static pages cleanly.
            for child in locale_root.iterdir():
                if child.is_dir() and child.name == "glossary":
                    continue
                if child.is_dir():
                    for root, dirs, files in os.walk(child, topdown=False):
                        for name in files:
                            Path(root, name).unlink(missing_ok=True)
                        for name in dirs:
                            Path(root, name).rmdir()
                    child.rmdir()
                else:
                    child.unlink(missing_ok=True)


def main() -> None:
    cleanup_locale_dirs()

    written = 0
    for locale in LOCALES:
        for rel_file in SOURCE_FILES:
            out_path, content = localize_file(rel_file, locale)
            out_path.write_text(content, encoding="utf-8")
            written += 1

    print(f"Localized static pages generated: {written}")


if __name__ == "__main__":
    main()
