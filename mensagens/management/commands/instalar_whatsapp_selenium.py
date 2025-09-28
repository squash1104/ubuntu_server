from django.core.management.base import BaseCommand
import subprocess
import sys


class Command(BaseCommand):
    help = 'Instala dependências para WhatsApp via Selenium'

    def handle(self, *args, **options):
        self.stdout.write("🔧 Instalando dependências para WhatsApp Selenium...")
        
        try:
            # Instalar selenium
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'selenium'])
            self.stdout.write(self.style.SUCCESS("✅ Selenium instalado"))
            
            # Instalar webdriver-manager
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'webdriver-manager'])
            self.stdout.write(self.style.SUCCESS("✅ WebDriver Manager instalado"))
            
            self.stdout.write("\n📱 WhatsApp Selenium configurado!")
            self.stdout.write("   - Funciona com WhatsApp Web")
            self.stdout.write("   - 100% gratuito")
            self.stdout.write("   - Requer login manual uma vez")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {str(e)}"))
