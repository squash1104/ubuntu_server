"""
Captura screenshots das páginas do sistema SisAps para o PDF de apresentação.
Usa Playwright (Chromium headless).
"""

import contextlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_fidelizacao.settings")

from django.conf import settings as django_settings
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8000"
CHROMIUM_PATH = str(
    Path.home() / ".cache/ms-playwright/chromium-1223/chrome-linux64/chrome"
)
USERNAME = "lucianosouza"
PASSWORD = "admin123"
OUTPUT_DIR = Path(django_settings.BASE_DIR) / "static" / "img" / "apresentacao"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SCREENSHOTS = [
    # (filename, url, description, full_page, selector_to_wait)
    ("01_login.png", "/login/", "Tela de Login", False, None),
    ("02_home.png", "/home/", "Página Inicial", True, None),
    ("03_dashboard_top.png", "/dashboard/", "Dashboard - Topo", False, "#map"),
    (
        "04_dashboard_charts.png",
        "/dashboard/",
        "Dashboard - Gráficos",
        False,
        "#convidadosRegiaoChart",
    ),
    ("05_dashboard_full.png", "/dashboard/", "Dashboard - Completo", True, None),
    (
        "06_mapa_apoiadores.png",
        "/mapa-apoiadores/",
        "Mapa de Apoiadores",
        False,
        "#map",
    ),
    (
        "07_colaboradores_lista.png",
        "/colaboradores/",
        "Lista de Apoiadores",
        True,
        None,
    ),
    (
        "08_colaboradores_form.png",
        "/colaboradores/adicionar/",
        "Cadastro de Apoiador",
        True,
        None,
    ),
    (
        "09_tipos_colaborador.png",
        "/colaboradores/tipos/",
        "Tipos de Colaborador",
        True,
        None,
    ),
    ("10_convidados_lista.png", "/convidados/", "Lista de Convidados", True, None),
    (
        "11_convidados_form.png",
        "/convidados/cadastrar/",
        "Cadastro de Convidado",
        True,
        None,
    ),
    ("12_recepcao_home.png", "/recepcao/", "Recepção - Home", True, None),
    (
        "13_recepcao_dashboard.png",
        "/recepcao/dashboard/",
        "Recepção - Dashboard",
        True,
        None,
    ),
    (
        "14_recepcao_visitantes.png",
        "/recepcao/visitantes/",
        "Recepção - Visitantes",
        True,
        None,
    ),
    ("15_mensagens_painel.png", "/mensagens/", "Painel de Mensagens", True, None),
    ("16_mensagens_enviar.png", "/mensagens/enviar/", "Envio de Mensagens", True, None),
    (
        "17_mensagens_historico.png",
        "/mensagens/historico/",
        "Histórico de Mensagens",
        True,
        None,
    ),
    ("18_mensagens_campanhas.png", "/mensagens/campanhas/", "Campanhas", True, None),
    ("19_historico.png", "/historico/", "Histórico do Sistema", True, None),
    ("20_aniversariantes.png", "/aniversariantes/", "Aniversariantes", True, None),
    ("21_sobre.png", "/sobre/", "Sobre o Sistema", True, None),
    (
        "22_relatorio_colaboradores.png",
        "/colaboradores/relatorios/colaboradores/",
        "Relatório de Apoiadores",
        True,
        None,
    ),
    (
        "23_relatorio_convidados.png",
        "/convidados/relatorios/convidados/",
        "Relatório de Convidados",
        True,
        None,
    ),
    (
        "24_user_settings.png",
        "/user-profiles/settings/",
        "Configurações do Usuário",
        True,
        None,
    ),
    ("25_admin.png", "/admin/", "Administração Django", True, None),
]


def capture():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROMIUM_PATH,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="pt-BR",
        )
        page = context.new_page()

        # Login first
        print("Fazendo login...")
        page.goto(f"{BASE_URL}/login/", wait_until="networkidle")
        page.fill('input[name="username"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        print(f"  URL após login: {page.url}")
        assert "login" not in page.url.lower(), "Falha no login!"

        for filename, url_path, desc, full_page, wait_selector in SCREENSHOTS:
            filepath = OUTPUT_DIR / filename
            print(f"{filename}: {desc} ({url_path})...", end=" ", flush=True)

            try:
                page.goto(f"{BASE_URL}{url_path}", wait_until="networkidle")

                # Handle redirects to login
                if "login" in page.url.lower():
                    print("Redirecionado para login - refazendo login...")
                    page.fill('input[name="username"]', USERNAME)
                    page.fill('input[name="password"]', PASSWORD)
                    page.click('button[type="submit"]')
                    page.wait_for_load_state("networkidle")
                    page.goto(f"{BASE_URL}{url_path}", wait_until="networkidle")

                # Wait for specific element if needed
                if wait_selector:
                    with contextlib.suppress(Exception):
                        page.wait_for_selector(wait_selector, timeout=5000)

                # Extra wait for charts/maps to render
                if url_path in ("/dashboard/", "/mapa-apoiadores/"):
                    page.wait_for_timeout(3000)

                page.wait_for_timeout(500)

                if full_page:
                    page.screenshot(path=str(filepath), full_page=True)
                else:
                    page.screenshot(path=str(filepath))

                print("OK")
            except Exception as e:
                print(f"ERRO: {e}")
                with contextlib.suppress(Exception):
                    page.screenshot(path=str(OUTPUT_DIR / f"ERROR_{filename}"))

        browser.close()
        print(f"\nScreenshots salvos em: {OUTPUT_DIR}")


if __name__ == "__main__":
    capture()
