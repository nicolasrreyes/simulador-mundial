import os
import pytest


pytestmark = pytest.mark.frontend

APP_URL = os.getenv("APP_URL", "http://127.0.0.1:8000")


def test_frontend_page_loads(page):
    page.goto(APP_URL)
    page.wait_for_load_state("networkidle")

    button = page.locator("#btnSimular")
    assert button.is_visible()
    assert button.is_enabled()

    errors = page.evaluate("window.__collectedErrors || []")
    assert len(errors) == 0, f"Console errors found: {errors}"


def test_frontend_simulation_triggers(page):
    page.goto(APP_URL)
    page.wait_for_load_state("networkidle")

    with page.expect_response(
        lambda response: "/simulator/run" in response.url
        and response.request.method == "POST",
        timeout=30000,
    ) as simulation_response:
        page.locator("#btnSimular").click()

    response = simulation_response.value
    assert response.ok


def test_frontend_results_rendered(page):
    page.goto(APP_URL)
    page.wait_for_load_state("networkidle")

    page.locator("#btnSimular").click()
    page.wait_for_selector("#resultsSection", state="visible", timeout=30000)
    page.wait_for_function(
        "document.getElementById('championResult').innerText.trim().length > 0",
        timeout=30000,
    )
    page.wait_for_function(
        "document.getElementById('dashboardResult').innerText.trim().length > 10",
        timeout=30000,
    )
    page.wait_for_function(
        "document.getElementById('bracketResult').innerText.trim().length > 10",
        timeout=30000,
    )

    assert page.locator("#championResult").is_visible()
    assert page.locator("#dashboardResult").is_visible()
    assert page.locator("#bracketResult").is_visible()


def test_frontend_mobile_no_scroll(page):
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(APP_URL)
    page.wait_for_load_state("networkidle")

    page.locator("#btnSimular").click()
    page.wait_for_selector("#resultsSection", state="visible", timeout=30000)

    page.wait_for_timeout(500)
    scroll_width = page.evaluate("document.body.scrollWidth")
    viewport_width = page.evaluate("window.innerWidth")
    assert scroll_width <= viewport_width
