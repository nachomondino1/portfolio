"""Contrato de data/posts.json: campos permitidos, tipos y versión."""
SCHEMA_VERSION = 1

TOP_LEVEL = {"schema_version", "projects", "posts"}
PROJECT_FIELDS = {"es", "en"}
POST_FIELDS = {"slug", "date", "tag", "minutes", "title", "short", "summary", "project"}
POST_REQUIRED = POST_FIELDS - {"project"}  # project puede faltar o ser null

SUMMARY_MAX = 200  # warning, no error: la card se ve rara por encima de esto
