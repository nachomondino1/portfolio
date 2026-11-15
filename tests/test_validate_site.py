import copy
import json
import unittest

from src import config
from src.validate_site import validate, _scan_disk

OK = {
    "schema_version": 1,
    "projects": {"x": {"es": "X", "en": "X"}},
    "posts": [{"slug": "a", "date": "2026-01-02", "tag": "T", "minutes": 2,
               "title": "t", "short": "s", "summary": "ok", "project": "x"}],
}


def run(data, slugs=("a",), ids=("x",)):
    return validate(data, set(slugs), set(ids))


class Validate(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(run(OK), ([], []))

    def test_campo_fuera_de_allowlist(self):
        d = copy.deepcopy(OK); d["posts"][0]["secreto"] = 1
        self.assertTrue(any("no permitidos" in e for e in run(d)[0]))

    def test_slug_sin_html(self):
        self.assertTrue(any("blog/a.html" in e for e in run(OK, slugs=())[0]))

    def test_proyecto_inexistente(self):
        d = copy.deepcopy(OK); d["posts"][0]["project"] = "nope"
        self.assertTrue(any("nope" in e for e in run(d)[0]))

    def test_fecha_invalida(self):
        d = copy.deepcopy(OK); d["posts"][0]["date"] = "2026-13-40"
        self.assertTrue(any("date" in e for e in run(d)[0]))

    def test_html_huerfano_es_warning(self):
        errs, warns = run(OK, slugs=("a", "b"))
        self.assertEqual(errs, [])
        self.assertTrue(any("blog/b.html" in w for w in warns))


class RepoReal(unittest.TestCase):
    def test_posts_json_real_sin_errores(self):
        data = json.loads(config.POSTS_JSON.read_text(encoding="utf-8"))
        errors, _ = validate(data, *_scan_disk())
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
