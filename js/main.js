(function () {
  "use strict";

  var header = document.querySelector(".header");
  if (header) {
    window.addEventListener(
      "scroll",
      function () {
        header.classList.toggle("scrolled", window.scrollY > 10);
      },
      { passive: true }
    );
  }

  var hamburgerSVG =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>';
  var closeSVG =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><line x1="6" y1="6" x2="18" y2="18"/><line x1="6" y1="18" x2="18" y2="6"/></svg>';

  window.toggleMobileMenu = function () {
    var menu = document.getElementById("mobile-menu");
    var overlay = document.getElementById("mobile-overlay");
    var btn = document.querySelector(".mobile-toggle");
    if (!menu || !overlay || !btn) {
      return;
    }

    var isOpen = menu.classList.toggle("open");
    overlay.classList.toggle("open", isOpen);
    btn.setAttribute("aria-expanded", String(isOpen));
    btn.innerHTML = isOpen ? closeSVG : hamburgerSVG;
    document.body.style.overflow = isOpen ? "hidden" : "";
  };

  window.closeMobileMenu = function () {
    var menu = document.getElementById("mobile-menu");
    var overlay = document.getElementById("mobile-overlay");
    var btn = document.querySelector(".mobile-toggle");
    if (!menu || !overlay || !btn) {
      return;
    }
    menu.classList.remove("open");
    overlay.classList.remove("open");
    btn.setAttribute("aria-expanded", "false");
    btn.innerHTML = hamburgerSVG;
    document.body.style.overflow = "";
  };

  function ensureLangSwitcher() {
    if (document.getElementById("termify-lang-switcher")) {
      return;
    }

    var localeOptions = [
      ["en", "en"],
      ["en-gb", "en-GB"],
      ["tr", "tr"],
      ["de", "de"],
      ["fr", "fr"],
      ["es", "es"],
      ["it", "it"],
      ["pt-br", "pt-BR"],
      ["pt-pt", "pt-PT"],
      ["ru", "ru"],
      ["ar", "ar"],
      ["hi", "hi"],
      ["ja", "ja"],
      ["ko", "ko"],
      ["zh-cn", "zh-CN"],
      ["zh-tw", "zh-TW"],
      ["id", "id"],
      ["nl", "nl"],
      ["pl", "pl"],
      ["sv", "sv"],
      ["th", "th"],
      ["vi", "vi"],
      ["ms", "ms"],
    ];
    var localePrefixes = localeOptions
      .map(function (item) {
        return item[0];
      })
      .filter(function (code) {
        return code !== "en";
      });

    var box = document.createElement("div");
    box.id = "termify-lang-switcher";
    box.className = "termify-lang-switcher";

    var label = document.createElement("label");
    label.setAttribute("for", "termify-lang-select");
    label.textContent = "Language";

    var select = document.createElement("select");
    select.id = "termify-lang-select";
    localeOptions.forEach(function (item) {
      var opt = document.createElement("option");
      opt.value = item[0];
      opt.textContent = item[1];
      select.appendChild(opt);
    });

    box.appendChild(label);
    box.appendChild(select);
    document.body.appendChild(box);

    if (!document.getElementById("termify-lang-switcher-style")) {
      var style = document.createElement("style");
      style.id = "termify-lang-switcher-style";
      style.textContent =
        ".termify-lang-switcher{position:fixed;right:1rem;bottom:1rem;z-index:9999;display:flex;align-items:center;gap:.5rem;padding:.55rem .7rem;border:1px solid rgba(255,255,255,.22);border-radius:9999px;background:rgba(8,8,10,.92);color:#fafafa;font-size:12px;backdrop-filter:blur(8px)}" +
        ".termify-lang-switcher label{font-weight:600;opacity:.92}" +
        ".termify-lang-switcher select{border:1px solid rgba(255,255,255,.2);border-radius:9999px;background:#121216;color:#fafafa;padding:.2rem .5rem;font-size:12px}" +
        "@media (max-width:640px){.termify-lang-switcher{left:.75rem;right:.75rem;bottom:.75rem;justify-content:space-between}}";
      document.head.appendChild(style);
    }

    var path = window.location.pathname || "/";
    var current = "en";
    for (var i = 0; i < localePrefixes.length; i++) {
      var code = localePrefixes[i];
      if (path === "/" + code || path.indexOf("/" + code + "/") === 0) {
        current = code;
        break;
      }
    }

    var basePath = path;
    if (current !== "en") {
      var prefix = "/" + current;
      if (basePath === prefix) {
        basePath = "/";
      } else if (basePath.indexOf(prefix + "/") === 0) {
        basePath = basePath.slice(prefix.length) || "/";
      }
    }

    select.value = current;
    if (current === "tr") {
      label.textContent = "Dil";
    }
    select.addEventListener("change", function () {
      var target = select.value || "en";
      var nextPath =
        target === "en"
          ? basePath
          : "/" + target + (basePath === "/" ? "" : basePath);
      window.location.href =
        nextPath + (window.location.search || "") + (window.location.hash || "");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureLangSwitcher);
  } else {
    ensureLangSwitcher();
  }
})();
