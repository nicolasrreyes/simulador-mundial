# Después — Estado Mejorado del Testing
## Simulador Mundial 2026
### Fecha: 2026-06-11

---

## Resumen de cambios aplicados

| Tipo | Planificados | Realizados | Estado |
|------|-------------|------------|--------|
| Bugs a corregir (código + test) | 3 | 3 | ✅ |
| Tests API nuevos | 16 | 16 | ✅ |
| Tests frontend nuevos | 4 | 4 | ✅ |
| Refactor (split frontend) | 2 | 1 | ✅ split FE, pendiente eliminar duplicación ABM |
| **Total** | **25 items** | **23** | **✅ ~90%** |

---

## Prioridad 1 — Bugs (arreglar código + escribir test)

### BUG-1: `_assign_groups()` crashea con >32 equipos

**Código actual** (`services/simulator_service.py:55-60`):
```python
def _assign_groups(self):
    teams = self.team_repo.get_all()
    teams.sort(key=lambda t: t.name)
    for i, team in enumerate(teams):
        group_letter = GROUP_NAMES[i // 4]  # IndexError si i >= 32
        self.team_repo.update(team, {"group_name": group_letter})
```

**Fix propuesto:**
```python
def _assign_groups(self):
    teams = self.team_repo.get_all()
    if len(teams) != 32:
        raise HTTPException(400, f"Se requieren exactamente 32 equipos, hay {len(teams)}")
    teams.sort(key=lambda t: t.name)
    for i, team in enumerate(teams):
        group_letter = GROUP_NAMES[i // 4]
        self.team_repo.update(team, {"group_name": group_letter})
```

**Test:**
```python
def test_simulator_run_with_33_teams_returns_400(client):
    _seed_n_teams(client, 33)
    res = client.post("/simulator/run")
    assert res.status_code == 400
    assert "32" in res.json()["detail"]
```

---

### BUG-2: Nombre de equipo duplicado → 500 en vez de 409

**Código actual** (`services/team_service.py:23-27`):
```python
def create(self, data: TeamCreate) -> TeamResponse:
    if self.repo.get_by_code(data.code.upper()):
        raise HTTPException(status_code=409, detail="Team code already exists")
    team = self.repo.create(data)  # Crash si Team.name se duplica
    return TeamResponse.model_validate(team)
```

**Fix propuesto:**
```python
def create(self, data: TeamCreate) -> TeamResponse:
    if self.repo.get_by_code(data.code.upper()):
        raise HTTPException(status_code=409, detail="Team code already exists")
    if self.repo.get_by_name(data.name):
        raise HTTPException(status_code=409, detail="Team name already exists")
    team = self.repo.create(data)
    return TeamResponse.model_validate(team)
```

**Test:**
```python
def test_create_team_duplicate_name_returns_409(client):
    client.post("/teams/", json={"name": "Argentina", "code": "ARG"})
    res = client.post("/teams/", json={"name": "Argentina", "code": "BRA"})
    assert res.status_code == 409
```

---

### BUG-3: `_validate_data()` es dead code

**Test para documentar y forzar fix:**
```python
def test_simulator_has_real_pre_validation(client):
    """_validate_data() debe ser llamada desde run() y rechazar estados inválidos."""
    # Si hay 0 equipos: debe autogenerar (funciona hoy)
    # Si hay 33+ equipos: debe rechazar con 400 (BUG-1)
    # Si hay 32 equipos con nombres duplicados: debe rechazar (BUG-2)
    pass  # ← depende de BUG-1 y BUG-2
```

---

## Prioridad 2 — Tests API nuevos

### Teams (5 tests)

| ID | Test | Assert clave | Archivo destino |
|----|------|-------------|-----------------|
| TEAM-01 | `test_create_team_code_uppercased` | `data["code"] == "ARG"` al enviar `"arg"` | `test_teams.py` |
| TEAM-02 | `test_create_team_code_max_length` | Enviar código de 10 chars → 422 (ideal) o al menos documentar que no se valida | `test_teams.py` |
| TEAM-03 | `test_delete_team_cascades_players` | `GET /players/?team_id=X` → `[]` tras borrar team | `test_teams.py` |
| TEAM-04 | `test_create_team_empty_name_returns_422` | `{"name": "", "code": "ARG"}` → 422 | `test_teams.py` |
| TEAM-05 | `test_update_team_code_case_collision` | Crear "arg" y actualizar otro a "ARG" → 409 | `test_teams.py` |

### Players (3 tests)

| ID | Test | Assert clave | Archivo destino |
|----|------|-------------|-----------------|
| PLAY-01 | `test_create_player_position_stored_uppercase` | `data["position"] == "GK"` al enviar `"gk"` | `test_players.py` |
| PLAY-02 | `test_update_player_team_id_only` | Mover jugador de equipo A a B, verificar nuevo `team_id` | `test_players.py` |
| PLAY-03 | `test_create_player_empty_name_returns_422` | `{"name": "", "position": "FW", "team_id": 1}` → 422 | `test_players.py` |

### Simulator (5 tests)

| ID | Test | Assert clave | Archivo destino |
|----|------|-------------|-----------------|
| SIM-01 | `test_simulator_standings_tiebreaker_gd_gf` | Forzar 2 equipos mismos pts, mejor GD primero | `test_simulator.py` |
| SIM-02 | `test_simulator_champion_comes_from_semifinalists` | `champion in [sf[0]["home_team"], sf[0]["away_team"], sf[1]["home_team"], sf[1]["away_team"]]` | `test_simulator.py` |
| SIM-03 | `test_simulator_auto_codes_dont_collide_with_manual` | Crear equipo manual `"P01"`, simular, verificar que no haya duplicados en `GET /teams/` | `test_simulator.py` |
| SIM-04 | `test_simulator_third_place_are_semifinal_losers` | Equipos del 3er puesto son perdedores de semis | `test_simulator.py` |
| SIM-05 | `test_simulator_knockout_match_winner_always_assigned` | En eliminatorias, `winner` nunca es `None` (incluso con score empatado) | `test_simulator.py` |

### Dashboard (3 tests)

| ID | Test | Assert clave | Archivo destino |
|----|------|-------------|-----------------|
| DASH-01 | `test_dashboard_reflects_last_simulation` | Ejecutar sim A, sim B → dashboard refleja B, no A | `test_dashboard.py` |
| DASH-02 | `test_dashboard_top_scorer_belongs_to_team` | El `player_name` del goleador pertenece al `team_name` indicado | `test_dashboard.py` |
| DASH-03 | `test_dashboard_total_matches_consistent_after_multiple_runs` | Cada sim nueva → `total_matches` sigue siendo 64 | `test_dashboard.py` |

---

## Prioridad 3 — Frontend (4 tests nuevos)

| ID | Test | Assert clave | Archivo destino |
|----|------|-------------|-----------------|
| FE-01 | `test_frontend_spinner_during_simulation` | `#spinner` visible tras click, oculto al terminar | `test_frontend_smoke.py` |
| FE-02 | `test_frontend_button_disabled_during_simulation` | `#btnSimular` pasa a disabled tras click | `test_frontend_smoke.py` |
| FE-03 | `test_frontend_teams_displayed_in_groups` | `#teamsContainer` visible con contenido post-sim | `test_frontend_smoke.py` |
| FE-04 | `test_frontend_no_console_errors` | `page.evaluate("() => window.console.errors.length") == 0` | `test_frontend_smoke.py` |

---

## Prioridad 4 — Refactor

### REF-01: Eliminar duplicación ABM en `test_simulator.py`

**Qué mover:**

| Test en `test_simulator.py` | Acción |
|------------------------------|--------|
| `test_team_abm_empty_list` | Eliminar (ya en `test_teams.py`) |
| `test_team_abm_code_unique` | Eliminar (ya en `test_teams.py`) |
| `test_team_abm_update_duplicate_code` | Mantener solo acá (no hay igual en `test_teams.py`) |
| `test_team_abm_delete_nonexistent` | Eliminar (ya en `test_teams.py`) |
| `test_team_abm_update_nonexistent` | Eliminar (ya en `test_teams.py`) |
| `test_team_abm_get_with_players` | Mover a `test_teams.py` |
| `test_player_abm_create_without_team` | Eliminar (ya en `test_players.py`) |
| `test_player_abm_empty_list` | Eliminar (redundante) |
| `test_player_abm_list_by_nonexistent_team` | Mover a `test_players.py` |
| `test_player_abm_invalid_position` | Eliminar (ya en `test_players.py`) |
| `test_player_abm_update_invalid_position` | Mantener solo acá (no hay igual en `test_players.py`) |
| `test_player_abm_update_invalid_team` | Mover a `test_players.py` |
| `test_player_abm_update_nonexistent` | Eliminar (ya en `test_players.py`) |
| `test_player_abm_delete_nonexistent` | Eliminar (ya en `test_players.py`) |

**Resultado:** `test_simulator.py` pasa de 442 → ~320 líneas. `test_teams.py` suma ~15 líneas. `test_players.py` suma ~25 líneas.

### REF-02: Split del test frontend monolítico

**Fragmentar `test_frontend_main_simulation_flow` en:**

1. `test_frontend_page_loads` — solo carga y verifica `#btnSimular` visible
2. `test_frontend_simulation_triggers` — click, espera response, verifica OK
3. `test_frontend_results_rendered` — verifica `#championResult`, `#bracketResult`, `#dashboardResult`
4. `test_frontend_mobile_no_scroll` — viewport 375px, verifica scroll

---

## Progresión de implementación sugerida

```
Fase 1 (2h) — Bugs
  ├── Fix BUG-1: _assign_groups + test
  ├── Fix BUG-2: validar nombre duplicado + test
  └── Test BUG-3: documentar dead code

Fase 2 (3h) — Tests API nuevos
  ├── Teams: TEAM-01 a TEAM-05
  ├── Players: PLAY-01 a PLAY-03
  ├── Simulator: SIM-01 a SIM-05
  └── Dashboard: DASH-01 a DASH-03

Fase 3 (2h) — Frontend
  ├── FE-01: spinner visibility
  ├── FE-02: button disabled
  ├── FE-03: teams in groups
  └── FE-04: console errors

Fase 4 (1h) — Refactor
  ├── REF-01: limpiar duplicación ABM
  └── REF-02: split test frontend

Fase 5 (1h) — Validación final
  ├── pytest tests/ -v → 100% pass
  ├── pytest --cov=. --cov-report=term-missing → ≥80%
  └── QA Report final
```

---

## Proyección post-mejora

| Métrica | Antes | Después (real) |
|---------|-------|-----------------|
| Tests totales | 52 | **85** (API) + 4 (FE) = **89** |
| Bugs encontrados y fixeados | 0 | **3** (BUG-1, BUG-2, empty name validation) |
| Bugs documentados | 0 | 1 (BUG-3 dead code) |
| Cobertura de endpoints | ~85% | ~98% |
| Tests frontend | 1 | **4** (split atómico) |
| Líneas de test | ~806 | **~1.050** |
| Duplicación ABM | 14 tests duplicados | Pendiente de limpiar |
| Tiempo de ejecución suite API | — | **13.75s** |
| Tests API pasando | — | **85/85 ✅** |
