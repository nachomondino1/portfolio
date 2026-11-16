"""Reporte semanal unificado de GoatCounter (todos los sitios en un solo mail).

Uso:
  python3 -m src.weekly_report            # imprime el reporte (necesita GOATCOUNTER_TOKEN)
  python3 -m src.weekly_report --send     # además lo manda por mail (RESEND_API_KEY y REPORT_TO en el entorno)
"""
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
    except (urllib.error.URLError, KeyError, ValueError) as e:
        print(f"WARNING {code}: {e}", file=sys.stderr)
        return None


def delta(cur, prev):
    if cur is None or prev is None:
        return "—"
    if prev == 0:
        return "nuevo" if cur else "="
    return f"{(cur - prev) / prev * 100:+.0f}%"


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
    lines = [f"Visitas del {start:%d/%m} al {end:%d/%m} (vs. semana anterior)", ""]
    w = max(len(r[0]) for r in rows)
    for name, code, cur, prev in rows:
        c = "s/d" if cur is None else cur
        p = "s/d" if prev is None else prev
        lines.append(f"{name:<{w}}  {c:>6}  (antes {p:>5}, {delta(cur, prev)})")
    lines += ["", f"{'Total':<{w}}  {total:>6}  (antes {ptotal:>5}, {delta(total, ptotal)})", ""]
    lines += [f"{n}: https://{c}.goatcounter.com/" for n, c, _, _ in rows]
    return f"Reporte semanal de tráfico: {total} visitas", "\n".join(lines)


def send(subject, body):
    """Manda el mail por la API de Resend (clave de solo envío, sin acceso a ninguna casilla)."""
    payload = {
        "from": os.environ.get("REPORT_FROM", "Reporte portfolio <onboarding@resend.dev>"),
        "to": [os.environ["REPORT_TO"]],
        "subject": subject,
        "text": body,
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
    subject, body = build(datetime.now(timezone.utc).date(), os.environ["GOATCOUNTER_TOKEN"])
    print(subject + "\n\n" + body)
    if "--send" in sys.argv:
        send(subject, body)
