# Portfolio

Sitio estático en GitHub Pages, publicado desde `site/` por GitHub Actions. Sin build step.

> Primer deploy: en el repo, Settings → Pages → Source = **GitHub Actions** (antes estaba en "Deploy from a branch").

```
├── site/                       # TODO lo que se sirve (y nada más)
│   ├── index.html · proyectos.html · blog.html
│   ├── blog/                   # un HTML por post
│   ├── css/styles.css
│   ├── js/site.js
│   ├── img/                    # fotos, og-image
│   ├── data/posts.json         # FUENTE DE VERDAD + artefacto publicado (versionado, editado a mano)
│   └── favicon.svg
├── src/                        # config.py (paths) · schema.py (contrato) · validate_site.py (ERROR/WARNING)
├── tests/                      # contrato, reglas y chequeo contra el repo real
├── marketing/                  # borradores de posts para LinkedIn (no se sirve)
├── Makefile                    # help · check · test · serve
└── .github/workflows/deploy.yml  # make test → publica site/ en GitHub Pages
```

Flujo: editar `data/posts.json` (o un HTML) → `make test` → commit y push.
Para un post nuevo: crear `blog/<slug>.html` con `data-post-slug="<slug>"` en el `<main>` y agregar su entrada en `posts.json`; el validador avisa si falta una de las dos mitades.
Decisiones y por qué: [DECISIONS.md](DECISIONS.md).
