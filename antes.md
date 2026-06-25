# Antes — Estado Actual del Testing
## Simulador Mundial 2026
### Fecha: 2026-06-11

---

## Resumen de cobertura actual

| Archivo | Tests | Happy Path | Reglas Negocio | Edge Cases | Líneas |
|---------|-------|------------|----------------|------------|--------|
| `test_teams.py` | 8 | 5 | 1 (duplicado) | 2 (not found) | 53 |
| `test_players.py` | 8 | 5 | 1 (posición inv.) | 2 (not found) | 78 |
| `test_simulator.py` | 22 | 6 | 8 | 8 (incluye ABM duplicados) | 442 |
| `test_dashboard.py` | 13 | 9 | 4 | 0 | 181 |
| `test_frontend_smoke.py` | 1 | 1 | 0 | 0 | 52 |
| **Total** | **52** | **26** | **14** | **12** | **806** |

---

## Bugs encontrados en el código (0 tests)

### BUG-1: `_assign_groups()` crashea con >32 equipos
**Archivo:** `services/simulator_service.py:58-60`
**Problema:** Si hay 33+ equipos, `i // 4` da índice 8+ sobre `GROUP_NAMES = ["A"..."H"]` (8 elementos) → **IndexError**.
**Sin test que lo cubra.**

### BUG-2: Nombre de equipo duplicado → 500 en vez de 409
**Archivo:** `services/team_service.py:23-27`
**Problema:** `Team.name` es `unique=True` en DB, pero el service nunca verifica. Si creás dos equipos con el mismo nombre, SQLite lanza `IntegrityError` → **500 Internal Server Error**.
**Sin test que lo cubra.**

### BUG-3: `_validate_data()` es dead code
**Archivo:** `services/simulator_service.py:138-144`
**Problema:** El método solo hace `if x == 32: pass` y siempre retorna `True`. Nunca se invoca desde `run()`.
**Sin test. No hay validación real de integridad pre-simulación.**

---

## Mapa de cobertura vs. endpoints

### `POST /teams/`
| Escenario | Status |
|-----------|--------|
| Creación exitosa | ✅ `test_create_team` |
| Código duplicado → 409 | ✅ `test_create_team_duplicate_code` |
| Nombre duplicado → 409? | ❌ No testea → **BUG-2** (da 500) |
| Código en minúscula → upper automático | ❌ No testea |
| Código > 3 caracteres | ❌ No testea |
| Campos vacíos → 422 | ❌ No testea |

### `GET /teams/`
| Escenario | Status |
|-----------|--------|
| Lista vacía | ✅ `test_team_abm_empty_list` (en simulator) |
| Lista con datos | ✅ `test_list_teams` |
| Con `group_name` post-simulación | ❌ No testea |

### `GET /teams/{id}`
| Escenario | Status |
|-----------|--------|
| Equipo existe con players | ✅ `test_get_team` + `test_team_abm_get_with_players` |
| Equipo no existe → 404 | ✅ `test_get_team_not_found` |

### `PUT /teams/{id}`
| Escenario | Status |
|-----------|--------|
| Actualización exitosa | ✅ `test_update_team` |
| No existe → 404 | ✅ `test_team_abm_update_nonexistent` |
| Código duplicado → 409 | ✅ `test_team_abm_update_duplicate_code` |
| Actualizar a código existente con distinto case | ❌ No testea |

### `DELETE /teams/{id}`
| Escenario | Status |
|-----------|--------|
| Eliminación exitosa | ✅ `test_delete_team` |
| No existe → 404 | ✅ `test_team_abm_delete_nonexistent` |
| Cascade a jugadores | ❌ No testea |

### `POST /players/`
| Escenario | Status |
|-----------|--------|
| Creación exitosa | ✅ `test_create_player` |
| Posición inválida → 400 | ✅ `test_create_player_invalid_position` |
| Equipo no existe → 404 | ✅ `test_create_player_team_not_found` |
| Posición en minúscula → upper | ❌ No testea |
| Nombre vacío → 422 | ❌ No testea |

### `GET /players/`
| Escenario | Status |
|-----------|--------|
| Lista completa | ✅ `test_list_players` |
| Filtro por team_id | ✅ `test_list_players_by_team` |
| Filtro por team_id inexistente | ✅ `test_player_abm_list_by_nonexistent_team` |

### `GET /players/{id}`
| Escenario | Status |
|-----------|--------|
| Existe | ✅ `test_get_player` |
| No existe → 404 | ✅ `test_get_player_not_found` |

### `PUT /players/{id}`
| Escenario | Status |
|-----------|--------|
| Actualización exitosa | ✅ `test_update_player` |
| Posición inválida en update → 400 | ✅ `test_player_abm_update_invalid_position` |
| Team_id inexistente en update → 404 | ✅ `test_player_abm_update_invalid_team` |
| No existe → 404 | ✅ `test_player_abm_update_nonexistent` |
| Actualizar solo posición (válida) | ❌ No testea |
| Actualizar solo team_id (válido) | ❌ No testea |

### `DELETE /players/{id}`
| Escenario | Status |
|-----------|--------|
| Eliminación exitosa | ✅ `test_delete_player` |
| No existe → 404 | ✅ `test_player_abm_delete_nonexistent` |

### `POST /simulator/run`
| Escenario | Status |
|-----------|--------|
| Responde 200 | ✅ `test_simulator_run_returns_200` |
| Estructura de respuesta | ✅ `test_simulator_run_response_structure` |
| 64 partidos totales | ✅ `test_simulator_run_exact_match_counts` |
| 8 grupos, 4 equipos c/u | ✅ `test_simulator_run_group_stage_structure` |
| 48 partidos grupo + 16 eliminatoria | ✅ `test_simulator_run_exact_match_counts` |
| Campeón = ganador final | ✅ `test_simulator_run_champion_is_final_winner` |
| Sin empates en eliminatoria | ✅ `test_simulator_run_knockout_no_draws` |
| Goles 0-5 por equipo | ✅ `test_simulator_run_match_scores_in_range` |
| Puntos consistentes | ✅ `test_simulator_run_standings_points_valid` |
| Diferencia de gol correcta | ✅ `test_simulator_run_standings_goal_diffs_correct` |
| 16 clasificados únicos | ✅ `test_simulator_run_qualified_teams_unique` |
| Posiciones 1-4 únicas por grupo | ✅ `test_simulator_run_group_positions_unique` |
| Standings ordenados por puntos | ✅ `test_simulator_run_standings_ordered_by_pts` |
| Equipos autogenerados si DB vacía | ✅ `test_simulator_run_empty_db_autogenerates` |
| 32 equipos preexistentes reusados | ✅ `test_simulator_run_reuses_existing_32_teams` |
| Equipos parciales completados | ✅ `test_simulator_run_partial_teams_generates_rest` |
| Players autogenerados si faltan | ✅ `test_simulator_run_exact_32_teams_no_players` |
| 33+ equipos → crash | ❌ No testea → **BUG-1** |
| Tiebreaker (pts → GD → GF) | ❌ No testea |
| Campeón siempre de semifinalistas | ❌ No testea |
| Códigos autogenerados únicos vs manuales | ❌ No testea |
| 3er puesto = perdedores de semis | ❌ No testea |

### `GET /metrics/dashboard`
| Escenario | Status |
|-----------|--------|
| Sin simulación → 404 | ✅ `test_dashboard_no_simulation_returns_404` |
| Post-simulación → 200 | ✅ `test_dashboard_after_simulation_returns_200` |
| Estructura de respuesta | ✅ `test_dashboard_response_structure` |
| Campeón = simulación | ✅ `test_dashboard_champion_consistency` |
| Campeón = final.winner | ✅ `test_dashboard_champion_is_final_winner` |
| Goleador > 0 goles | ✅ `test_dashboard_top_scorer_positive_goals` |
| Goleador existe en DB | ✅ `test_dashboard_top_scorer_exists_in_db` |
| Promedio = total / partidos | ✅ `test_dashboard_avg_goals_formula` |
| 64 partidos totales | ✅ `test_dashboard_total_matches_is_64` |
| Refleja última simulación | ❌ No testea correctamente (solo checkea `is not None`) |

### Frontend (Playwright)
| Escenario | Status |
|-----------|--------|
| Flujo completo: carga → simular → resultados | ✅ `test_frontend_main_simulation_flow` |
| Spinner aparece/desaparece | ❌ No testea |
| Botón disabled durante simulación | ❌ No testea |
| Equipos agrupados en UI | ❌ No testea |
| Sin errores de consola | ❌ No testea |

---

## Duplicación detectada

Los siguientes tests en `test_simulator.py` duplican cobertura de `test_teams.py` y `test_players.py`:

| Test duplicado | Original en |
|----------------|-------------|
| `test_team_abm_empty_list` | `test_teams.py:test_list_teams` |
| `test_team_abm_code_unique` | `test_teams.py:test_create_team_duplicate_code` |
| `test_team_abm_update_duplicate_code` | Parcialmente en `test_teams.py` |
| `test_team_abm_delete_nonexistent` | Parcialmente en `test_teams.py` |
| `test_team_abm_update_nonexistent` | Parcialmente en `test_teams.py` |
| `test_team_abm_get_with_players` | Parcialmente en `test_teams.py` |
| `test_player_abm_create_without_team` | `test_players.py:test_create_player_team_not_found` |
| `test_player_abm_empty_list` | Parcialmente en `test_players.py` |
| `test_player_abm_list_by_nonexistent_team` | ❌ No duplicado (solo acá) |
| `test_player_abm_invalid_position` | `test_players.py:test_create_player_invalid_position` |
| `test_player_abm_update_invalid_position` | ❌ No duplicado (solo acá) |
| `test_player_abm_update_invalid_team` | ❌ No duplicado (solo acá) |
| `test_player_abm_update_nonexistent` | Parcialmente en `test_players.py` |
| `test_player_abm_delete_nonexistent` | Parcialmente en `test_players.py` |

---

## Riesgos no cubiertos (resumen)

1. **BUG-1**: Simular con 33+ equipos crashea la app (IndexError)
2. **BUG-2**: Nombre duplicado da 500 en vez de 409
3. **BUG-3**: `_validate_data()` es código muerto — no hay validación real
4. **Sin test de tiebreakers**: Si dos equipos empatan en puntos, el orden por GD y GF no está testeado
5. **Sin test de unicidad de códigos autogenerados**: Si el usuario crea equipos manuales con códigos como `P01`, colisionan con autogeneración
6. **Frontend monolítico**: 1 solo test que mezcla carga, simulación, render y mobile. Difícil de diagnosticar si falla
7. **Spinner y botón disabled**: Comportamiento UI crítico no testeado
