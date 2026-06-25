# PROMPT_SONAR_DEVOPS.md


## Prompt listo para usar


[ROL]
Actua como un DevOps Senior y experto en SonarQube, calidad de codigo, testing automatizado y pipelines CI/CD para proyectos Python con FastAPI.

Necesito que trabajes sobre un proyecto real con este stack:
- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- Pydantic v2
- SQLite
- pytest
- pytest-cov
- Playwright / pytest-playwright
- Allure

[OBJETIVO]
Quiero que analices el codigo, revises la suite de tests existente, detectes brechas de cobertura y de calidad, y dejes el proyecto en condiciones de pasar un analisis de SonarQube con cobertura mayor al 80%.

No quiero una respuesta generica. Quiero un analisis tecnico, accionable y ejecutable sobre el repo.

[CONTEXTO DEL PROYECTO]
La app es una API FastAPI llamada "Mundial 2026 - Simulator API".

Estructura relevante:
- `main.py`
- `database.py`
- `routers/`
- `services/`
- `repositories/`
- `models/`
- `schemas/`
- `tests/`
- `static/index.html`
- `requirements.txt`
- `pytest.ini`
- `QA.md`

Dependencias actuales relevantes:
- fastapi
- uvicorn
- sqlalchemy
- pydantic[email]
- httpx
- pytest
- pytest-cov
- playwright
- pytest-playwright
- allure-pytest

Configuracion de tests conocida:
- Se usa `pytest`
- Existe `pytest.ini`
- Hay fixture con DB en memoria SQLite en `tests/conftest.py`
- Hay tests backend y smoke/frontend

Tests existentes detectados:
- `tests/test_teams.py`
- `tests/test_players.py`
- `tests/test_simulator.py`
- `tests/test_dashboard.py`
- `tests/test_frontend_smoke.py`

Reglas funcionales importantes ya conocidas:
- La simulacion debe manejar 32 equipos
- Cada grupo debe tener exactamente 4 equipos
- El campeon debe coincidir con el ganador de la final
- El dashboard depende de una simulacion previa
- Las posiciones validas de jugadores son `GK`, `DF`, `MF`, `FW`
- Debe respetarse unicidad de codigo de equipo

[FORMA DE TRABAJO OBLIGATORIA]
Trabaja en este orden y no te saltees pasos:

1. Inspecciona el codigo fuente y la estructura del repo.
2. Revisa los tests existentes antes de proponer nuevos.
3. Detecta problemas de calidad que probablemente impacten en SonarQube:
   - code smells
   - complejidad
   - duplicacion
   - validaciones faltantes
   - ramas no cubiertas
   - manejo deficiente de errores
   - deuda tecnica visible
4. Detecta exactamente que partes del codigo tienen mayor riesgo de quedar por debajo del 80% de cobertura.
5. Propone un plan concreto para:
   - corregir problemas de calidad
   - agregar o ajustar tests
   - mejorar cobertura real
   - dejar configurado SonarQube si falta configuracion
6. Ejecuta los cambios necesarios.
7. Corre los tests y la cobertura.
8. Si hace falta, agrega o ajusta configuracion para SonarQube.
9. Entrega un resumen final con evidencia.

[RESTRICCIONES]
- No borres tests utiles solo para inflar metricas.
- No hagas cambios cosmeticos sin impacto real.
- No ocultes problemas reales excluyendo modulos arbitrariamente del analisis.
- No inventes resultados: si algo no puede ejecutarse, dilo explicitamente.
- Minimiza cambios innecesarios en logica productiva.
- Prioriza mejoras seguras, mantenibles y alineadas al comportamiento actual del sistema.

[CRITERIOS TECNICOS]
Quiero que revises y, si aplica, mejores estos puntos:

1. Cobertura
- Identifica modulos, funciones y ramas con cobertura insuficiente.
- Agrega tests unitarios/integracion donde mas valor aporten.
- Busca superar 80% de cobertura total o al menos dejarla claramente encaminada con evidencia.

2. Calidad SonarQube
- Identifica hotspots tipicos de SonarQube en Python:
  - funciones largas
  - duplicacion
  - condicionales complejos
  - valores magic numbers evitables
  - nombres poco claros
  - falta de validaciones
  - manejo de excepciones pobre
  - codigo muerto
- Corrige lo que tenga sentido sin sobredisenar.

3. Testing
- Reutiliza el patron existente del repo.
- Usa la fixture de DB en memoria si corresponde.
- Evita tests duplicados respecto a los ya presentes.
- Prioriza casos de negocio, errores, bordes y ramas no cubiertas.
- Si detectas tests fragiles o redundantes, explicalo.

4. SonarQube / Config
- Verifica si falta `sonar-project.properties` u otra configuracion necesaria.
- Si no existe, proponla o creala con valores razonables para este proyecto.
- Incluye configuracion de coverage report para Python si corresponde.
- Asegura que el analisis apunte al codigo fuente y a los tests correctamente.

[COMANDOS ESPERADOS]
Usa o adapta estos comandos segun el proyecto:

```bash
pip install -r requirements.txt
pytest tests/ -v
pytest tests/ --cov=. --cov-report=term-missing --cov-report=xml
```

Si configuras SonarQube para Python, considera tambien el uso de:

```bash
sonar-scanner
```

[ENTREGABLES OBLIGATORIOS]
Quiero que tu respuesta final quede organizada asi:

1. Diagnostico inicial
- Que encontraste en el codigo
- Que encontraste en los tests
- Riesgos principales para SonarQube

2. Plan de accion
- Lista concreta de cambios a realizar
- Archivos a modificar o crear
- Justificacion breve de cada cambio

3. Cambios aplicados
- Resumen de refactors
- Resumen de tests agregados o ajustados
- Configuracion SonarQube agregada o modificada

4. Evidencia de ejecucion
- Comandos ejecutados
- Resultado de tests
- Resultado de cobertura
- Si hay fallas, explicar causa exacta

5. Resultado final
- Indica si el proyecto queda:
  - listo para analisis SonarQube
  - listo para pasar cobertura > 80%
  - o que bloqueantes faltan

[SI NECESITAS TOMAR DECISIONES]
Aplica este criterio:
- Primero corrige lo que impacta calidad y cobertura de forma medible.
- Luego mejora la configuracion de SonarQube.
- Finalmente deja recomendaciones opcionales separadas del trabajo obligatorio.

[INSTRUCCION FINAL]
No te limites a aconsejar: inspecciona, modifica, ejecuta, verifica y deja evidencia.
Si detectas que algo ya esta bien cubierto, no lo dupliques.
Si encuentras oportunidades claras para superar 80% de cobertura con pocos cambios de alto impacto, priorizalas.
```

---

## Uso sugerido en este repo

Antes de pasarle el prompt a la otra IA, conviene adjuntarle tambien estos archivos como contexto:

- `QA.md`
- `requirements.txt`
- `pytest.ini`
- `tests/conftest.py`
- `main.py`
- `database.py`

Si quieres darle mas precision todavia, puedes agregarle este mensaje debajo del prompt:

```text
Importante: revisa primero `tests/test_simulator.py`, porque ya existe bastante cobertura funcional y no quiero duplicaciones innecesarias. Prioriza cubrir huecos reales en `services/`, `repositories/`, `routers/` y validaciones no testeadas.
```

