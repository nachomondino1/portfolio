(function () {
  function applyLang(lang) {
    document.querySelectorAll("[data-lang]").forEach(function (el) {
      el.hidden = el.getAttribute("data-lang") !== lang;
    });
    document.documentElement.setAttribute("lang", lang);
    document.querySelectorAll("[data-lang-btn]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", String(btn.dataset.langBtn === lang));
    });
  }

  var saved = "es";
  try {
    saved = localStorage.getItem("ficheroLang") || "es";
  } catch (e) {}

  applyLang(saved);

  document.querySelectorAll("[data-lang-btn]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var lang = btn.dataset.langBtn;
      applyLang(lang);
      try {
        localStorage.setItem("ficheroLang", lang);
      } catch (e) {}
    });
  });
})();

(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll("[data-toc]"));
  var entries = links.map(function (link) {
    return document.getElementById(link.dataset.toc);
  });

  if (!("IntersectionObserver" in window) || !entries.length) return;

  function setActive(id) {
    links.forEach(function (link) {
      link.classList.toggle("active", link.dataset.toc === id);
    });
  }

  var observer = new IntersectionObserver(function (observed) {
    observed.forEach(function (item) {
      if (item.isIntersecting) setActive(item.target.id);
    });
  }, { rootMargin: "-20% 0px -70% 0px", threshold: 0 });

  entries.forEach(function (entry) {
    if (entry) observer.observe(entry);
  });
})();
