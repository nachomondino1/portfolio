// Analytics: GoatCounter (sin cookies). No cuenta visitas en localhost.
(function () {
  var h = location.hostname;
  if (h === "localhost" || h === "127.0.0.1" || h === "") return;
  var s = document.createElement("script");
  s.async = true;
  s.src = "//gc.zgo.at/count.js";
  s.setAttribute("data-goatcounter", "https://portafolio-proyectos.goatcounter.com/count");
  document.head.appendChild(s);
})();

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

(function () {
  var root = document.body.getAttribute("data-root") || "";
  var cur = function () { return document.documentElement.getAttribute("lang") === "en" ? "en" : "es"; };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  // texto bilingüe: ambos spans, uno oculto según el idioma activo
  function bi(es, en) {
    var l = cur();
    return '<span data-lang="es"' + (l === "es" ? "" : " hidden") + ">" + es + '</span><span data-lang="en"' + (l === "en" ? "" : " hidden") + ">" + en + "</span>";
  }
  function fmtDate(iso, lang) {
    var d = new Date(iso + "T12:00:00");
    return d.toLocaleDateString(lang === "en" ? "en-GB" : "es-AR", { day: "numeric", month: "short", year: "numeric" }).replace(/\./g, "");
  }

  var listEl = document.querySelector("[data-posts-list]");
  var postEl = document.querySelector("[data-post-slug]");
  var projEls = document.querySelectorAll("article.entry[id]");
  if (!listEl && !postEl && !projEls.length) return;

  fetch(root + "data/posts.json")
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (data) {
      var posts = data.posts.slice().sort(function (a, b) { return a.date < b.date ? 1 : -1; });
      var projects = data.projects;

      function chip(post, href) {
        var pr = post.project && projects[post.project];
        if (!pr) return "";
        return '<a class="project-chip" href="' + href + "#" + post.project + '">' + bi("Proyecto: " + esc(pr.es), "Project: " + esc(pr.en)) + "</a>";
      }

      if (listEl) {
        listEl.innerHTML = posts.map(function (p) {
          return '<div class="card-wrap' + (p.project ? " has-chip" : "") + '"><a class="card" href="blog/' + p.slug + '.html">' +
            '<div class="meta-row"><span class="tag">' + esc(p.tag) + "</span><time datetime=\"" + p.date + "\">" + bi(fmtDate(p.date, "es"), fmtDate(p.date, "en")) + "</time><span>" + p.minutes + " min</span></div>" +
            "<h2>" + esc(p.title) + "</h2><p>" + esc(p.summary) + "</p>" +
            '<span class="card-cta">' + bi("Leer →", "Read →") + "</span></a>" + chip(p, "proyectos.html") + "</div>";
        }).join("");
      }

      if (postEl) {
        var post = posts.filter(function (p) { return p.slug === postEl.getAttribute("data-post-slug"); })[0];
        var h1 = postEl.querySelector("h1");
        if (post && h1) h1.insertAdjacentHTML("beforebegin", chip(post, "../proyectos.html").replace("</a>", " →</a>"));
      }

      projEls.forEach(function (art) {
        var rel = posts.filter(function (p) { return p.project === art.id; });
        var links = art.querySelector(".links");
        if (!rel.length || !links) return;
        rel.forEach(function (p) {
          links.insertAdjacentHTML("beforeend", '<a href="blog/' + p.slug + '.html">' + bi("Blog: " + esc(p.short) + " →", "Blog: " + esc(p.short) + " →") + "</a>");
        });
      });
    })
    .catch(function () {
      // la lista es contenido principal: error legible, nunca página en blanco.
      // En proyectos y posts los links al blog son un extra; sin ellos la página sigue entera.
      if (listEl) listEl.innerHTML = '<p class="load-error">' + bi("No se pudo cargar la lista de posts. Probá recargar la página.", "Couldn't load the post list. Try reloading the page.") + "</p>";
    });
})();
