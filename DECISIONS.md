# Decisiones

Seguimos `utils/DATA_FLOW_PLAYBOOK_unificado.md` en modo simple (sin datos sensibles).

- **No hay export ni script de build.** `data/posts.json` lo edita un humano y no se puede recalcular de otro lado: es a la vez fuente (cat. 1) y artefacto publicado (cat. 3), versionado. Un export intermedio sería ceremonia sin valor. El playbook §3.2 ya contempla que una fuente chica que cambia poco vive como JSON editado directo.
- **Sí hay validación (§4).** Es la parte que sí paga: ERROR corta (campo fuera de allowlist, slug sin HTML, proyecto inexistente, fecha inválida), WARNING lista (HTML huérfano, summary largo).
- **Contrato con `schema_version`** y allowlist de campos en `src/schema.py`.
- **Frontend (§10):** `preload` + `fetch` en las páginas que usan el JSON; si el fetch de la lista falla se muestra un mensaje legible. En proyectos y posts los links al blog son un extra: si falla, la página queda completa.
- **Todo lo servido en `site/`, con `css/`, `js/`, `img/` y `data/` adentro.** Lo que no se sirve (`src/`, `tests/`, `marketing/`, docs) queda afuera: se ve de un vistazo qué es público. Pages por rama solo acepta `/` o `/docs`, así que se publica con Actions (`upload-pages-artifact` + `deploy-pages`), que además corre `make test` antes. Ver `utils/REPO_STRUCTURE_PLAYBOOK.md`.
- **Sin `.env`, `cache/` ni `models/`:** no hay APIs ni ML. `.env` queda en `.gitignore` por si aparece.
