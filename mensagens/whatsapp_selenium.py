import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class WhatsAppSelenium:
    """Serviço para envio de mensagens via WhatsApp Web usando Selenium"""

    def __init__(self):
        self.driver = None
        self.wait = None
        self.is_logged_in = False

    def _setup_driver(self):
        """Configura o driver do Chrome"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Para rodar em servidor (headless)
        # chrome_options.add_argument("--headless")

        # Manter sessão ativa
        chrome_options.add_argument("--user-data-dir=/tmp/whatsapp-session")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def login(self):
        """Faz login no WhatsApp Web"""
        if self.is_logged_in:
            return True

        try:
            if not self.driver:
                self._setup_driver()

            # Acessar WhatsApp Web
            self.driver.get("https://web.whatsapp.com")

            # Aguardar QR Code aparecer
            print("📱 Abra o WhatsApp no seu celular e escaneie o QR Code")
            print("   Aguardando login...")

            # Aguardar login (QR Code ser escaneado)
            try:
                # Aguardar o chat aparecer (indica que fez login)
                self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '[data-testid="chat-list"]')
                    )
                )
                self.is_logged_in = True
                print("✅ Login realizado com sucesso!")
                return True
            except TimeoutException:
                print("❌ Timeout - Login não realizado")
                return False

        except Exception as e:
            print(f"❌ Erro no login: {e!s}")
            return False

    def enviar_mensagem(self, telefone, mensagem):
        """Envia uma mensagem para um número"""
        if not self.is_logged_in:
            if not self.login():
                return False

        try:
            # Formatar telefone (remover caracteres especiais)
            telefone_limpo = "".join(filter(str.isdigit, telefone))
            if not telefone_limpo.startswith("55"):
                telefone_limpo = "55" + telefone_limpo

            # URL do WhatsApp com o número
            url = f"https://web.whatsapp.com/send?phone={telefone_limpo}"
            self.driver.get(url)

            # Aguardar a página carregar
            time.sleep(3)

            # Aguardar o campo de mensagem aparecer
            try:
                message_box = self.wait.until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            '[data-testid="conversation-compose-box-input"]',
                        )
                    )
                )
            except TimeoutException:
                print(
                    f"❌ Não foi possível encontrar o campo de mensagem para {telefone}"
                )
                return False

            # Digitar a mensagem
            message_box.clear()
            message_box.send_keys(mensagem)

            # Aguardar um pouco
            time.sleep(1)

            # Enviar mensagem (Enter)
            message_box.send_keys("\n")

            # Aguardar envio
            time.sleep(2)

            print(f"✅ Mensagem enviada para {telefone}")
            return True

        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e!s}")
            return False

    def enviar_multiplas_mensagens(self, destinatarios):
        """Envia mensagens para múltiplos destinatários"""
        resultados = []

        for destinatario in destinatarios:
            telefone = destinatario.get("telefone", "")
            nome = destinatario.get("nome", "")
            mensagem = destinatario.get("mensagem", "")

            print(f"📤 Enviando para {nome} ({telefone})...")

            sucesso = self.enviar_mensagem(telefone, mensagem)
            resultados.append({"nome": nome, "telefone": telefone, "sucesso": sucesso})

            # Aguardar entre mensagens para evitar spam
            time.sleep(2)

        return resultados

    def fechar(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.is_logged_in = False
