"""Valida data/posts.json contra el contrato y contra los HTML del sitio.

Dos niveles (playbook §4): ERROR corta (exit 1), WARNING se lista y sigue.
Uso: python -m src.validate_site
"""
import json
import re
import sys
from datetime import date

from . import config, schema


def validate(data, blog_slugs, project_ids, html_slugs=None):
    """Devuelve (errors, warnings). Puro: no toca el disco."""
    errors, warnings = [], []

    extra = set(data) - schema.TOP_LEVEL
    if extra:
        errors.append(f"campos no permitidos en la raíz: {sorted(extra)}")
    if data.get("schema_version") != schema.SCHEMA_VERSION:
        errors.append(f"schema_version debe ser {schema.SCHEMA_VERSION}, es {data.get('schema_version')!r}")

    projects = data.get("projects", {})
    for pid, names in projects.items():
        if set(names) != schema.PROJECT_FIELDS or not all(isinstance(v, str) and v for v in names.values()):
            errors.append(f"proyecto '{pid}': necesita exactamente {sorted(schema.PROJECT_FIELDS)} con texto")
        if pid not in project_ids:
            errors.append(f"proyecto '{pid}' no tiene <article id=\"{pid}\"> en proyectos.html")

    seen = set()
    for i, p in enumerate(data.get("posts", [])):
        slug = p.get("slug", f"#{i}")
        where = f"post '{slug}'"
        missing = schema.POST_REQUIRED - set(p)
        extra = set(p) - schema.POST_FIELDS
        if missing:
            errors.append(f"{where}: faltan campos {sorted(missing)}")
        if extra:
            errors.append(f"{where}: campos no permitidos {sorted(extra)}")
        if slug in seen:
            errors.append(f"{where}: slug duplicado")
        seen.add(slug)
        try:
            date.fromisoformat(p.get("date", ""))
        except (TypeError, ValueError):
            errors.append(f"{where}: date debe ser YYYY-MM-DD")
        m = p.get("minutes")
        if not isinstance(m, int) or isinstance(m, bool) or m < 1:
            errors.append(f"{where}: minutes debe ser entero >= 1")
        if p.get("project") is not None and p["project"] not in projects:
            errors.append(f"{where}: project '{p['project']}' no existe en projects")
        if slug not in blog_slugs:
            errors.append(f"{where}: no existe blog/{slug}.html")
        elif html_slugs is not None and html_slugs.get(slug) != slug:
            warnings.append(f"{where}: data-post-slug de su HTML es {html_slugs.get(slug)!r}")
        if len(p.get("summary", "")) > schema.SUMMARY_MAX:
            warnings.append(f"{where}: summary de {len(p['summary'])} caracteres (> {schema.SUMMARY_MAX})")

    for s in sorted(blog_slugs - seen):
        warnings.append(f"blog/{s}.html no está en posts.json (no aparece en el listado)")
    return errors, warnings


def _scan_disk():
    blog_slugs = {p.stem for p in config.BLOG_DIR.glob("*.html")}
    html_slugs = {}
    for s in blog_slugs:
        m = re.search(r'data-post-slug="([^"]*)"', (config.BLOG_DIR / f"{s}.html").read_text(encoding="utf-8"))
        html_slugs[s] = m.group(1) if m else None
    ids = set(re.findall(r'<article[^>]*\bid="([^"]+)"', config.PROYECTOS_HTML.read_text(encoding="utf-8")))
    return blog_slugs, ids, html_slugs


def main():
    data = json.loads(config.POSTS_JSON.read_text(encoding="utf-8"))
    errors, warnings = validate(data, *_scan_disk())
    for w in warnings:
        print("WARNING:", w)
    for e in errors:
        print("ERROR:  ", e)
    print(f"{len(errors)} errores, {len(warnings)} avisos")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
