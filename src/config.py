"""Todos los paths del repo. Nadie hardcodea un path en otro módulo."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"
DATA_DIR = SITE_DIR / "data"
POSTS_JSON = DATA_DIR / "posts.json"
BLOG_DIR = SITE_DIR / "blog"
PROYECTOS_HTML = SITE_DIR / "proyectos.html"
