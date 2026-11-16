# Portfolio

## Comandos

```bash
make serve   # sitio en http://localhost:8000
```

```bash
make test    # valida site/data/posts.json contra los HTML + tests (lo mismo que corre el CI)
```

```bash
make check   # solo la validación (ERROR/WARNING)
```

```bash
make help    # lista de comandos y flujo habitual
```

Desplegar: `git push` a `main`. El workflow corre `make test` y publica `site/` en GitHub Pages.
Primer deploy: Settings → Pages → Source = **GitHub Actions**.

## Analytics

Tráfico medido con [GoatCounter](https://portafolio-proyectos.goatcounter.com/) (sin cookies). El snippet vive en `site/js/site.js` y no corre en localhost.

## Qué es

Sitio estático en GitHub Pages, publicado desde `site/` por GitHub Actions. Sin build step.

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

Flujo: editar `site/data/posts.json` (o un HTML) → `make test` → commit y push.
Para un post nuevo: crear `site/blog/<slug>.html` con `data-post-slug="<slug>"` en el `<main>` y agregar su entrada en `posts.json`; el validador avisa si falta una de las dos mitades.
Decisiones y por qué: [DECISIONS.md](DECISIONS.md).
