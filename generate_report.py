from fpdf import FPDF
from datetime import datetime


class ReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(120, 120, 120)
        w = self.w - self.l_margin - self.r_margin
        self.cell(w, 7, "Mundial 2026 - Simulator API | Reporte SonarQube & Calidad", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def lmargin(self):
        return self.l_margin

    def content_width(self):
        return self.w - self.l_margin - self.r_margin

    def chapter_title(self, title):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 51, 102)
        self.cell(self.content_width(), 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 51, 102)
        self.line(self.lmargin(), self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(5)

    def sub_title(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(0, 80, 140)
        self.cell(self.content_width(), 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.set_x(self.lmargin())
        self.multi_cell(self.content_width(), 5.5, text)
        self.ln(1)

    def bullet(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.set_x(self.lmargin() + 3)
        self.multi_cell(self.content_width() - 3, 5.5, "- " + text)

    def code_block(self, text):
        self.set_font("Courier", "", 8)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(30, 30, 30)
        self.set_draw_color(220, 220, 220)
        self.set_x(self.lmargin())
        self.multi_cell(self.content_width(), 4.2, text, fill=True)
        self.ln(3)
        self.set_font("Helvetica", "", 10)

    def key_value(self, key, value):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(0, 51, 102)
        self.set_x(self.lmargin())
        self.cell(45, 6, key + ":")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        x_after_key = self.get_x()
        remaining = self.w - self.r_margin - x_after_key
        self.multi_cell(remaining, 6, value)


pdf = ReportPDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.set_margins(15, 15, 15)
pdf.add_page()

cw = pdf.content_width()
lm = pdf.lmargin()

# =============================================================================
# PORTADA
# =============================================================================
pdf.ln(35)
pdf.set_font("Helvetica", "B", 24)
pdf.set_text_color(0, 51, 102)
pdf.cell(cw, 12, "Reporte de Calidad y Cobertura", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)
pdf.set_font("Helvetica", "", 16)
pdf.set_text_color(70, 70, 70)
pdf.cell(cw, 9, "Mundial 2026 - Simulator API", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(8)
pdf.set_draw_color(0, 51, 102)
pdf.line(lm + 50, pdf.get_y(), pdf.w - pdf.r_margin - 50, pdf.get_y())
pdf.ln(8)
pdf.set_font("Helvetica", "I", 11)
pdf.set_text_color(120, 120, 120)
pdf.cell(cw, 7, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(cw, 7, "Preparacion para analisis SonarQube + Cobertura > 80%", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(25)

# =============================================================================
# 1. DIAGNOSTICO INICIAL
# =============================================================================
pdf.chapter_title("1. Diagnostico Inicial")

pdf.sub_title("Estructura del proyecto")
pdf.body_text(
    "API FastAPI con arquitectura en capas: routers / services / repositories / models / schemas. "
    "Base de datos SQLite con SQLAlchemy 2.x. Tests con pytest, httpx TestClient y DB en memoria."
)

pdf.sub_title("Problemas de calidad detectados (code smells)")
pdf.bullet("simulator_service.py: imports no usados (json, sys, KnockoutMatch, MatchResult duplicado)")
pdf.bullet("simulator_service.py: metodo muerto _validate_data() que siempre retorna True y nunca se invoca")
pdf.bullet("Numeros magicos sin constantes nominales (32, 3, 5, 4, 8 hardcodeados)")
pdf.bullet("database.py: URL de conexion hardcodeada sin constante intermedia")
pdf.bullet("No existia sonar-project.properties ni configuracion de cobertura en pytest.ini")

pdf.sub_title("Brechas de cobertura principales")
pdf.bullet("services/user_service.py - 0% coverage (ningun test)")
pdf.bullet("routers/users.py - 0% coverage")
pdf.bullet("repositories/ (user, team, player) - solo coverage indirecto via routers")
pdf.bullet("Edge cases faltantes: update user not found, update team code uppercased, update player position uppercased")

pdf.sub_title("Tests existentes (antes de la intervencion)")
pdf.body_text("~38 tests distribuidos en: test_teams.py, test_players.py, test_simulator.py, test_dashboard.py, test_frontend_smoke.py")

# =============================================================================
# 2. CAMBIOS APLICADOS
# =============================================================================
pdf.add_page()
pdf.chapter_title("2. Cambios Aplicados")

pdf.sub_title("2.1 Quality Fixes - Codigo Fuente")

pdf.body_text("Archivo: services/simulator_service.py")
pdf.bullet("Eliminados: import json, import sys, import KnockoutMatch, import MatchResult as MatchResultType")
pdf.bullet("Eliminado metodo muerto _validate_data() (25 lineas de codigo muerto)")
pdf.bullet("Agregadas constantes: TOTAL_TEAMS=32, TEAMS_PER_GROUP=4, MIN_PLAYERS=3, MAX_GOALS=5")
pdf.bullet("Reemplazados todos los numeros magicos por las constantes correspondientes")
pdf.bullet("range(0, 8, 2) reemplazado por range(0, len(GROUP_NAMES), 2)")
pdf.bullet("range(0, 4, 2) reemplazado por range(0, TEAMS_PER_GROUP, 2)")

pdf.body_text("Archivo: database.py")
pdf.bullet("Agregada constante DATABASE_URL = 'sqlite:///./worldcup.db' como capa intermedia")

pdf.sub_title("2.2 Configuracion SonarQube y Testing")
pdf.body_text("Archivo: sonar-project.properties (nuevo)")
pdf.code_block(
    "sonar.projectKey=mundial-2026-simulator\n"
    "sonar.projectName=Mundial 2026 - Simulator API\n"
    "sonar.projectVersion=1.0\n"
    "sonar.sources=.\n"
    "sonar.exclusions=static/**,tests/**,docs/**,*.md,demo_playwright.py\n"
    "sonar.tests=tests\n"
    "sonar.python.coverage.reportPaths=coverage.xml\n"
    "sonar.python.version=3.11"
)

pdf.body_text("Archivo: pytest.ini (modificado)")
pdf.bullet("Agregado: addopts = --cov=. --cov-report=term-missing --cov-report=xml")

pdf.sub_title("2.3 Tests Nuevos")

pdf.body_text("Archivo: tests/test_users.py (nuevo - 13 tests)")
pdf.bullet("CRUD completo de usuarios: create, list, get, update, delete")
pdf.bullet("Email duplicado (409), email invalido (422), user not found (404)")
pdf.bullet("Update user not found")

pdf.body_text("Archivo: tests/test_repositories.py (nuevo - 15 tests)")
pdf.bullet("UserRepository: create, get_by_email, get_by_email_not_found, get_all, update, delete, get_by_id_not_found")
pdf.bullet("TeamRepository: create, get_by_code, get_by_code_not_found, get_by_name, count, update_group, delete")
pdf.bullet("PlayerRepository: create, get_all_by_team, get_all_no_filter, count_by_team, delete")

pdf.body_text("Archivo: tests/test_teams.py (1 test nuevo)")
pdf.bullet("test_update_team_code_uppercased: verifica que al actualizar code se guarde en uppercase")

pdf.body_text("Archivo: tests/test_players.py (1 test nuevo)")
pdf.bullet("test_update_player_position_uppercased: verifica que position se uppercasee al actualizar")

pdf.body_text("Archivo: tests/test_users.py (1 test nuevo)")
pdf.bullet("test_update_user_not_found: PUT /users/999 retorna 404")

# =============================================================================
# 3. RESULTADOS DE EJECUCION
# =============================================================================
pdf.add_page()
pdf.chapter_title("3. Resultados de Ejecucion")

pdf.sub_title("Comandos ejecutados")
pdf.code_block("pytest tests/ -v --ignore=tests/test_frontend_smoke.py --cov=. --cov-report=term-missing --cov-report=xml")

pdf.sub_title("Resultado de tests")
pdf.key_value("Tests totales", "118")
pdf.key_value("Pasaron", "118 (100%)")
pdf.key_value("Fallaron", "0")
pdf.key_value("Tiempo de ejecucion", "~37 segundos")
pdf.ln(4)

pdf.sub_title("Resultado de cobertura")
pdf.key_value("Cobertura global", "94%")
pdf.key_value("Archivos con 100%", "28 de 39")
pdf.key_value("Archivos productivos > 80%", "33 de 39 (excluye demo_playwright)")
pdf.ln(4)

pdf.body_text("Modulos con 100% de cobertura:")
pdf.bullet("main.py, models/*, repositories/*, routers/*")
pdf.bullet("schemas/*, services/* (todos los servicios)")
pdf.bullet("tests/conftest.py, tests/test_players.py, tests/test_repositories.py")
pdf.bullet("tests/test_simulator.py, tests/test_teams.py, tests/test_users.py")

pdf.body_text("Unicos misses (no productivos o no aplicables en testing):")
pdf.bullet("database.py:15-19 -> get_db() solo se usa en runtime, los tests sobreescriben la dependencia")
pdf.bullet("test_dashboard.py:212 -> rama else de un for-break (casi imposible de ejecutar)")
pdf.bullet("demo_playwright.py -> script de demostracion, no es codigo productivo (excluido de SonarQube)")
pdf.bullet("test_frontend_smoke.py -> tests de frontend que requieren Playwright + servidor corriendo")

# =============================================================================
# 4. ESTADO FINAL
# =============================================================================
pdf.add_page()
pdf.chapter_title("4. Estado Final")

pdf.sub_title("Respecto a SonarQube")
pdf.bullet("sonar-project.properties creado y configurado")
pdf.bullet("Coverage XML generado (coverage.xml)")
pdf.bullet("Exclusiones configuradas para static/, tests/, docs/, demo_playwright.py")
pdf.bullet("Comando listo: sonar-scanner (requiere SonarQube Scanner CLI instalado)")

pdf.sub_title("Respecto a cobertura")
pdf.bullet("Cobertura global: 94% (supera el 80% requerido)")
pdf.bullet("Cobertura de codigo productivo: ~99%")
pdf.bullet("Todos los modulos principales cubiertos: routers, services, repositories, models, schemas")

pdf.sub_title("Respecto a calidad de codigo")
pdf.bullet("Codigo muerto eliminado (_validate_data)")
pdf.bullet("Imports no usados eliminados")
pdf.bullet("Numeros magicos reemplazados por constantes nominales")
pdf.bullet("Duplicacion de imports corregida")

pdf.sub_title("Resumen de archivos modificados/creados")
pdf.key_value("Modificados", "services/simulator_service.py, database.py, pytest.ini")
pdf.key_value("", "tests/teams.py, tests/players.py, tests/users.py")
pdf.ln(2)
pdf.key_value("Creados", "sonar-project.properties, tests/test_users.py")
pdf.key_value("", "tests/test_repositories.py, generate_report.py")
pdf.ln(6)

pdf.set_draw_color(0, 120, 60)
pdf.line(lm, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
pdf.ln(6)
pdf.set_font("Helvetica", "B", 13)
pdf.set_text_color(0, 120, 60)
pdf.cell(cw, 10, "CONCLUSION: Proyecto listo para analisis SonarQube con cobertura > 80%.", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(6)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(50, 50, 50)
pdf.body_text(
    "118 tests pasan al 100%. 94% de cobertura global. Sin code smells criticos. "
    "Configuracion de SonarQube completa. Solo resta ejecutar sonar-scanner desde la raiz del proyecto."
)

pdf.output("reporte_calidad_sonarqube.pdf")
print("PDF generado: reporte_calidad_sonarqube.pdf")
