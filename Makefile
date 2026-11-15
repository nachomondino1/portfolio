.PHONY: help test check serve

help:  ## qué hace cada comando
	@echo "Flujo habitual: editar data/posts.json (o un HTML) -> make test -> commit/push"
	@echo "  make test   validación + tests (lo mismo que corre el CI)"
	@echo "  make check  solo valida posts.json contra los HTML"
	@echo "  make serve  sitio local en http://localhost:8000"

check:
	python3 -m src.validate_site

test: check
	python3 -m unittest discover -s tests -t .

serve:
	python3 -m http.server 8000 --directory site
