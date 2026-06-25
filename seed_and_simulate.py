import json
import os
import pathlib

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi.testclient import TestClient
from main import app

DIST = pathlib.Path("dist")
DIST_DATA = DIST / "data"


def main():
    DIST.mkdir(parents=True, exist_ok=True)
    DIST_DATA.mkdir(parents=True, exist_ok=True)

    client = TestClient(app)

    print("Ejecutando simulación...")
    sim_res = client.post("/simulator/run")
    sim_res.raise_for_status()
    sim_data = sim_res.json()

    (DIST_DATA / "simulation.json").write_text(
        json.dumps(sim_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    champion = sim_data["champion"]
    print(f"Campeón: {champion}")

    print("Obteniendo dashboard...")
    dash_res = client.get("/metrics/dashboard")
    dash_data = dash_res.json() if dash_res.status_code < 400 else {}
    (DIST_DATA / "dashboard.json").write_text(
        json.dumps(dash_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("Obteniendo equipos...")
    teams_res = client.get("/teams/")
    teams_data = teams_res.json() if teams_res.status_code < 400 else []
    (DIST_DATA / "teams.json").write_text(
        json.dumps(teams_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    _generate_index_html(sim_data, dash_data, teams_data)
    print(f"Sitio estático generado en {DIST.resolve()}")
    assert DIST_DATA.joinpath("simulation.json").exists()
    assert DIST.joinpath("index.html").exists()
    print("Validación exitosa — pipeline listo para deploy")


def _generate_index_html(sim_data, dash_data, teams_data):
    html = _build_html(sim_data, dash_data, teams_data)
    (DIST / "index.html").write_text(html, encoding="utf-8")


def _build_html(sim_data, dash_data, teams_data):
    groups_html = _render_groups(sim_data.get("groups", []))
    bracket_html = _render_bracket(sim_data)
    champion = sim_data.get("champion", "")
    champion_html = f"""<div class="champion-banner"><span class="trophy-icon">🏆</span><div class="champion-name">{_h(champion)}</div><div class="champion-sub">Campeón del Mundo 2026</div></div>"""
    stats_html = _render_stats(sim_data)
    dash_html = _render_dashboard(dash_data)
    teams_grid = _render_teams_before(teams_data)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Mundial 2026 — Resultados</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@500;600;700&display=swap" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
:root{{--cda-primary:#0056a7;--cda-primary-dark:#003d7a;--cda-secondary:#0096d6;--cda-accent:#00a8e0;--cda-dark:#002b54;--cda-white:#fff;--cda-light-bg:#f0f4f8;--cda-card-bg:#fff;--cda-text:#1a2332;--cda-text-light:#5e6f8d;--cda-border:#d0d8e3;--cda-border-light:#e8ecf2;--cda-success:#16a34a;--cda-danger:#dc2626;--cda-shadow-sm:0 1px 3px rgba(0,30,60,.08);--cda-shadow:0 4px 16px rgba(0,30,60,.1);--cda-shadow-lg:0 8px 32px rgba(0,30,60,.12);--cda-radius-sm:4px;--cda-radius:8px;--cda-radius-lg:12px}}
*{{box-sizing:border-box}}
body{{background:var(--cda-light-bg);color:var(--cda-text);font-family:"Inter","Poppins",system-ui,sans-serif;margin:0;min-height:100vh}}
.hero{{background:linear-gradient(135deg,var(--cda-primary),var(--cda-dark));padding:3rem 0;text-align:center}}
.hero h1{{font-family:"Poppins",sans-serif;font-weight:700;font-size:2rem;color:var(--cda-white);margin:0}}
.hero h1 .highlight{{color:var(--cda-accent)}}
.hero p{{color:rgba(255,255,255,.7);margin:.25rem 0 0}}
.section-title{{font-family:"Poppins",sans-serif;font-weight:600;font-size:1.2rem;text-align:center;margin:1.5rem 0 1rem}}
.section-title::after{{content:"";display:block;width:40px;height:3px;background:var(--cda-primary);margin:.4rem auto 0;border-radius:2px}}
.group-card{{background:var(--cda-card-bg);border:1px solid var(--cda-border-light);border-radius:var(--cda-radius);overflow:hidden;box-shadow:var(--cda-shadow-sm)}}
.group-header{{background:var(--cda-primary);padding:.5rem 1rem;font-weight:700;font-size:.8rem;color:var(--cda-white);text-transform:uppercase;letter-spacing:1.5px}}
.group-table{{margin:0;width:100%;border-collapse:collapse}}
.group-table th{{border:none;color:var(--cda-text-light);font-weight:600;font-size:.65rem;text-transform:uppercase;letter-spacing:1px;padding:.4rem .6rem;border-bottom:1px solid var(--cda-border-light);background:var(--cda-light-bg)}}
.group-table td{{border:none;padding:.4rem .6rem;font-size:.8rem;border-bottom:1px solid var(--cda-border-light)}}
.group-table tr:last-child td{{border-bottom:none}}
.group-table .qualified{{color:var(--cda-text)}}
.group-table .eliminated{{opacity:.35}}
.knockout-section{{margin-top:1rem}}
.round-header{{text-align:center;font-weight:700;font-size:.75rem;text-transform:uppercase;letter-spacing:2px;padding:.4rem 0;margin-bottom:.5rem;border-radius:var(--cda-radius-sm);color:var(--cda-white)}}
.match-card{{background:var(--cda-card-bg);border:1px solid var(--cda-border-light);border-radius:var(--cda-radius);padding:.4rem .75rem;margin-bottom:.4rem;box-shadow:var(--cda-shadow-sm)}}
.match-teams .team{{display:flex;justify-content:space-between;align-items:center;padding:.1rem 0;font-size:.8rem}}
.match-teams .team .team-label{{font-weight:500;color:var(--cda-text)}}
.match-teams .team.winner .team-label{{font-weight:700;color:var(--cda-primary)}}
.match-score{{font-family:"Poppins",sans-serif;font-weight:600;font-size:.9rem;min-width:30px;text-align:center;background:var(--cda-light-bg);padding:.05rem .25rem;border-radius:var(--cda-radius-sm)}}
.champion-banner{{background:linear-gradient(135deg,var(--cda-primary),var(--cda-dark));border-radius:var(--cda-radius-lg);padding:1.5rem;text-align:center;margin:1.5rem 0}}
.champion-banner .trophy-icon{{font-size:2.2rem;display:block}}
.champion-banner .champion-name{{font-family:"Poppins",sans-serif;font-weight:700;font-size:1.6rem;color:var(--cda-white)}}
.champion-banner .champion-sub{{font-size:.8rem;color:rgba(255,255,255,.7)}}
.stats-bar{{display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;margin:1rem 0}}
.stat-item{{text-align:center}}
.stat-item .stat-value{{font-family:"Poppins",sans-serif;font-weight:700;font-size:1.2rem;color:var(--cda-primary)}}
.stat-item .stat-label{{font-size:.65rem;color:var(--cda-text-light);text-transform:uppercase;letter-spacing:1px}}
.dashboard-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem;margin:1rem 0}}
.kpi-card{{background:var(--cda-card-bg);border:1px solid var(--cda-border-light);border-radius:var(--cda-radius);padding:1rem;text-align:center;box-shadow:var(--cda-shadow-sm)}}
.kpi-card .kpi-icon{{font-size:1.4rem}}
.kpi-card .kpi-value{{font-family:"Poppins",sans-serif;font-weight:700;font-size:1.1rem;color:var(--cda-primary)}}
.kpi-card .kpi-label{{font-size:.65rem;color:var(--cda-text-light);text-transform:uppercase;letter-spacing:.8px}}
.kpi-card .kpi-sub{{font-size:.7rem;color:var(--cda-text-light)}}
.footer{{background:var(--cda-dark);padding:1rem 0;margin-top:2rem;text-align:center;color:rgba(255,255,255,.4);font-size:.7rem}}
.team-card{{background:var(--cda-card-bg);border:1px solid var(--cda-border-light);border-radius:var(--cda-radius);padding:.6rem 1rem;margin-bottom:.5rem;box-shadow:var(--cda-shadow-sm)}}
.team-card .name{{font-weight:600;font-size:.85rem}}
.team-card .code{{font-size:.7rem;color:var(--cda-text-light)}}
</style>
</head>
<body>
<div class="hero">
<div class="container">
<h1>Mundial <span class="highlight">2026</span></h1>
<p>Resultados generados automáticamente por CDA CI/CD</p>
</div>
</div>
<div class="container py-4">
<h2 class="section-title">Equipos Participantes</h2>
<div class="row g-2">{teams_grid}</div>
<hr>
<h2 class="section-title">Estadísticas</h2>
<div class="stats-bar">{stats_html}</div>
<hr>
<h2 class="section-title">Fase de Grupos</h2>
<div class="row g-3">{groups_html}</div>
<hr>
<h2 class="section-title">Eliminatorias</h2>
{bracket_html}
{champion_html}
{dash_html}
</div>
<div class="footer"><div class="container">CDA Informática — Simulador Mundial 2026</div></div>
</body>
</html>"""


def _render_groups(groups):
    if not groups:
        return "<p>No hay datos de grupos</p>"
    cols = []
    for gr in groups:
        standings_rows = "".join(
            f"""<tr class="{'qualified' if s.get('position', 99) <= 2 else 'eliminated'}">
<td>{s.get('position', '')}</td><td>{_h(s.get('team', ''))}</td>
<td>{s.get('pts', 0)}</td><td>{s.get('gf', 0)}</td><td>{s.get('ga', 0)}</td>
<td>{s.get('gd', 0):+d}</td></tr>"""
            for s in gr.get("standings", [])
        )
        cols.append(f"""<div class="col-md-3 col-sm-6"><div class="group-card">
<div class="group-header">Grupo {_h(gr.get('group', ''))}</div>
<table class="group-table"><thead><tr><th>#</th><th>Equipo</th><th>Pts</th><th>GF</th><th>GA</th><th>DG</th></tr></thead>
<tbody>{standings_rows}</tbody></table></div></div>""")
    return "".join(cols)


def _render_bracket(data):
    rounds = [
        ("round_of_16", "Octavos de Final"),
        ("quarterfinals", "Cuartos de Final"),
        ("semifinals", "Semifinales"),
    ]
    parts = []
    for key, label in rounds:
        matches = data.get(key, [])
        if not matches:
            continue
        items = "".join(
            f"""<div class="col-12 mb-2"><div class="match-card"><div class="match-teams">
<div class="team{' winner' if m.get('winner') == m.get('home_team') else ''}">
<span class="team-label">{_h(m.get('home_team', ''))}</span>
<span class="match-score">{m.get('home_goals', 0)}</span></div>
<div class="team{' winner' if m.get('winner') == m.get('away_team') else ''}">
<span class="team-label">{_h(m.get('away_team', ''))}</span>
<span class="match-score">{m.get('away_goals', 0)}</span></div>
</div></div></div>"""
            for m in matches
        )
        parts.append(f"""<div class="knockout-section"><div class="round-header">{label}</div><div class="row">{items}</div></div>""")

    tp = data.get("third_place")
    if tp:
        parts.append(f"""<div class="knockout-section" style="opacity:.65"><div class="round-header">Tercer Puesto</div>
<div class="row justify-content-center"><div class="col-md-4"><div class="match-card"><div class="match-teams">
<div class="team{' winner' if tp.get('winner') == tp.get('home_team') else ''}">
<span class="team-label">{_h(tp.get('home_team', ''))}</span>
<span class="match-score">{tp.get('home_goals', 0)}</span></div>
<div class="team{' winner' if tp.get('winner') == tp.get('away_team') else ''}">
<span class="team-label">{_h(tp.get('away_team', ''))}</span>
<span class="match-score">{tp.get('away_goals', 0)}</span></div>
</div></div></div></div></div>""")

    final = data.get("final", {})
    parts.append(f"""<div class="knockout-section"><div class="round-header">Final</div>
<div class="row justify-content-center"><div class="col-md-5"><div class="match-card" style="border-color:var(--cda-border);border-width:2px"><div class="match-teams">
<div class="team{' winner' if final.get('winner') == final.get('home_team') else ''}">
<span class="team-label">{_h(final.get('home_team', ''))}</span>
<span class="match-score">{final.get('home_goals', 0)}</span></div>
<div class="team{' winner' if final.get('winner') == final.get('away_team') else ''}">
<span class="team-label">{_h(final.get('away_team', ''))}</span>
<span class="match-score">{final.get('away_goals', 0)}</span></div>
</div></div></div></div></div>""")

    return "".join(parts)


def _render_stats(data):
    groups = data.get("groups", [])
    total_goals = sum(
        m.get("home_goals", 0) + m.get("away_goals", 0)
        for gr in groups
        for m in gr.get("matches", [])
    )
    champion = data.get("champion", "")
    return f"""<div class="stat-item"><div class="stat-value">{len(groups) * 4}</div><div class="stat-label">Equipos</div></div>
<div class="stat-item"><div class="stat-value">{total_goals}</div><div class="stat-label">Goles</div></div>
<div class="stat-item"><div class="stat-value">{_h(champion)}</div><div class="stat-label">Campeón</div></div>"""


def _render_dashboard(dash):
    if not dash or "champion" not in dash:
        return ""
    ts = dash.get("top_scorer", {})
    return f"""<h2 class="section-title">Dashboard Ejecutivo</h2>
<div class="dashboard-grid">
<div class="kpi-card"><div class="kpi-icon">🏆</div><div class="kpi-value">{_h(dash.get('champion', ''))}</div><div class="kpi-label">Campeón</div></div>
<div class="kpi-card"><div class="kpi-icon">⚽</div><div class="kpi-value">{_h(ts.get('player_name', ''))}</div><div class="kpi-label">Botín de Oro</div><div class="kpi-sub">{_h(ts.get('team_name', ''))} · {ts.get('goals', 0)} goles</div></div>
<div class="kpi-card"><div class="kpi-icon">📊</div><div class="kpi-value">{dash.get('avg_goals_per_match', 0)}</div><div class="kpi-label">Prom. Goles</div></div>
<div class="kpi-card"><div class="kpi-icon">🥅</div><div class="kpi-value">{dash.get('total_goals', 0)}</div><div class="kpi-label">Goles Totales</div><div class="kpi-sub">en {dash.get('total_matches', 0)} partidos</div></div>
</div>"""


def _render_teams_before(teams):
    if not teams:
        return "<p>No hay equipos registrados</p>"
    return "".join(
        f"""<div class="col-md-3 col-sm-6"><div class="team-card">
<div class="name">{_h(t.get('name', ''))}</div>
<div class="code">{_h(t.get('code', ''))}</div></div></div>"""
        for t in teams
    )


def _h(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


if __name__ == "__main__":
    main()
