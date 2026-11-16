"""Reporte semanal unificado de GoatCounter (todos los sitios en un solo mail).

Uso:
  python3 -m src.weekly_report            # imprime el reporte (necesita GOATCOUNTER_TOKEN)
  python3 -m src.weekly_report --send     # además lo manda por mail (RESEND_API_KEY y REPORT_TO en el entorno)
"""
import html
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone

SITES = [
    ("Portafolio", "portafolio-proyectos"),
    ("Alera", "alera"),
    ("Estadísticas de Fútbol Amateur", "buitres"),
    ("Recomendador de Películas", "notas-peliculas"),
    ("Juegos de Mesa", "boardgames"),
    ("Recetas", "recetas"),
    ("Evaluación de Alternativas", "evaluador-alternativas"),
    ("Análisis de Reseñas", "reviews-analysis"),
]


def fetch_total(code, start, end, token):
    """Visitas (pageviews) entre start y end (inclusive), o None si falla."""
    q = f"start={start.isoformat()}T00:00:00Z&end={end.isoformat()}T23:59:59Z"
    req = urllib.request.Request(
        f"https://{code}.goatcounter.com/api/v0/stats/total?{q}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)["total"]
    except urllib.error.HTTPError as e:
        print(f"WARNING {code}: HTTP {e.code} {e.read().decode()[:300]}", file=sys.stderr)
        return None
    except (urllib.error.URLError, KeyError, ValueError) as e:
        print(f"WARNING {code}: {e}", file=sys.stderr)
        return None


def delta(cur, prev):
    if cur is None or prev is None:
        return "—"
    if prev == 0:
        return "nuevo" if cur else "="
    return f"{(cur - prev) / prev * 100:+.0f}%"


def plural(n):
    return f"{n} visita" if n == 1 else f"{n} visitas"


def build(today, token):
    end = today - timedelta(days=1)
    start = end - timedelta(days=6)
    pend = start - timedelta(days=1)
    pstart = pend - timedelta(days=6)
    rows = []
    for name, code in SITES:
        rows.append((name, code, fetch_total(code, start, end, token), fetch_total(code, pstart, pend, token)))
    rows.sort(key=lambda r: -(r[2] or 0))
    total = sum(r[2] or 0 for r in rows)
    ptotal = sum(r[3] or 0 for r in rows)
    subject = f"Tráfico semanal: {plural(total)}"
    period = f"{start:%d/%m} al {end:%d/%m}"
    failed = [r[0] for r in rows if r[2] is None]

    text = [f"Visitas del {period}, vs. la semana anterior", ""]
    for name, code, cur, prev in rows:
        c = "sin datos" if cur is None else plural(cur)
        text.append(f"- {name}: {c} (antes: {'sin datos' if prev is None else prev}, {delta(cur, prev)})")
    text += ["", f"Total: {plural(total)} (antes: {ptotal}, {delta(total, ptotal)})", ""]
    text += [f"{n}: https://{c}.goatcounter.com/" for n, c, _, _ in rows]
    if failed:
        text += ["", "No se pudo leer: " + ", ".join(failed)]

    def color(d):
        return "#1f6f50" if d.startswith("+") or d == "nuevo" else "#b42318" if d.startswith("-") else "#6e7278"

    tr = ""
    for name, code, cur, prev in rows:
        d = delta(cur, prev)
        tr += (
            f'<tr><td style="padding:10px 12px;border-bottom:1px solid #eee">'
            f'<a href="https://{code}.goatcounter.com/" style="color:#16181a;text-decoration:none">{html.escape(name)}</a></td>'
            f'<td style="padding:10px 12px;border-bottom:1px solid #eee;text-align:right;font-weight:700;font-size:16px">'
            f'{"—" if cur is None else cur}</td>'
            f'<td style="padding:10px 12px;border-bottom:1px solid #eee;text-align:right;color:#6e7278">'
            f'{"—" if prev is None else prev}</td>'
            f'<td style="padding:10px 12px;border-bottom:1px solid #eee;text-align:right;color:{color(d)}">{d}</td></tr>'
        )
    td = total and delta(total, ptotal) or "="
    body_html = f"""<div style="font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;max-width:560px;color:#16181a">
<h2 style="margin:0 0 4px;font-size:20px">Tráfico semanal</h2>
<p style="margin:0 0 18px;color:#6e7278">{period} · {plural(total)} en total ({delta(total, ptotal)} vs. semana anterior)</p>
<table style="border-collapse:collapse;width:100%;font-size:14px">
<tr style="background:#f5f5f4;color:#6e7278;font-size:12px;text-transform:uppercase">
<th style="padding:8px 12px;text-align:left">Proyecto</th><th style="padding:8px 12px;text-align:right">Esta semana</th>
<th style="padding:8px 12px;text-align:right">Anterior</th><th style="padding:8px 12px;text-align:right">Cambio</th></tr>
{tr}
<tr><td style="padding:10px 12px;font-weight:700">Total</td>
<td style="padding:10px 12px;text-align:right;font-weight:700;font-size:16px">{total}</td>
<td style="padding:10px 12px;text-align:right;color:#6e7278">{ptotal}</td>
<td style="padding:10px 12px;text-align:right;color:{color(td)}">{td}</td></tr>
</table>
{"<p style='margin-top:16px;color:#b42318;font-size:13px'>No se pudo leer: " + html.escape(", ".join(failed)) + "</p>" if failed else ""}
<p style="margin-top:18px;color:#6e7278;font-size:12px">Tocá el nombre de un proyecto para abrir su panel en GoatCounter.</p>
</div>"""
    return subject, "\n".join(text), body_html


def send(subject, text, body_html):
    """Manda el mail por la API de Resend (clave de solo envío, sin acceso a ninguna casilla)."""
    payload = {
        "from": os.environ.get("REPORT_FROM", "Reporte portfolio <onboarding@resend.dev>"),
        "to": [os.environ["REPORT_TO"]],
        "subject": subject,
        "text": text,
        "html": body_html,
    }
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {os.environ['RESEND_API_KEY']}",
            "Content-Type": "application/json",
            "User-Agent": "portfolio-weekly-report/1.0",
        },
    )
    try:
        urllib.request.urlopen(req, timeout=30).read()
    except urllib.error.HTTPError as e:
        sys.exit(f"Resend rechazó el envío ({e.code}): {e.read().decode()}")


if __name__ == "__main__":
    subject, text, body_html = build(datetime.now(timezone.utc).date(), os.environ["GOATCOUNTER_TOKEN"])
    print(subject + "\n\n" + text)
    if "--send" in sys.argv:
        send(subject, text, body_html)
