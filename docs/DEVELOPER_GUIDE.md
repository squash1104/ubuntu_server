# Guia do Desenvolvedor - SisAps

## 🚀 Ambiente de Desenvolvimento

### Configuração Inicial
```bash
# Clone o repositório
git clone <repository-url>
cd sisvot

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configure o pre-commit
pre-commit install
```

### Estrutura de Desenvolvimento
```
sisvot/
├── .venv/                  # Ambiente virtual Python
├── .git/                   # Repositório Git
├── .ruff_cache/           # Cache do Ruff
├── .idea/                  # Configurações IntelliJ/PyCharm
├── .vscode/               # Configurações VS Code
├── sistema_fidelizacao/   # Projeto principal
├── colaboradores/         # App colaboradores
├── convidados/           # App convidados
├── geografia/            # App geografia
├── chat/                 # App chat
├── templates/            # Templates HTML
├── static/               # Arquivos estáticos
├── staticfiles/          # Arquivos coletados
├── docs/                 # Documentação
└── requirements.txt      # Dependências
```

## 🐍 Python e Django

### Versões Suportadas
- **Python**: 3.12+
- **Django**: 5.2.4
- **Django Channels**: 4.2.2

### Configurações de Desenvolvimento
```python
# settings.py - Configurações de desenvolvimento
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

# Banco de dados de desenvolvimento
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sisvot_dev',
        'USER': 'postgres',
        'PASSWORD': 'senha_dev',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Email de desenvolvimento
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

## 🗄️ Banco de Dados

### Modelos e Relacionamentos
```python
# Estrutura de relacionamentos
Colaborador -> Cidade (ForeignKey)
Colaborador -> Bairro (ForeignKey)
Colaborador -> User (ForeignKey)  # cadastrado_por

Convidado -> Cidade (ForeignKey)
Convidado -> Bairro (ForeignKey)
Convidado -> Colaborador (ForeignKey)

Bairro -> Cidade (ForeignKey)

Message -> User (ForeignKey)  # sender e recipient
Profile -> User (OneToOneField)
```

### Migrações
```bash
# Criar migração
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Verificar status das migrações
python manage.py showmigrations

# Reverter migração específica
python manage.py migrate app_name 0001
```

### Dados de Teste
```bash
# Criar superusuário
python manage.py createsuperuser

# Shell do Django
python manage.py shell

# Exemplo de criação de dados
from geografia.models import Cidade, Bairro
from colaboradores.models import Colaborador

# Criar cidade
cidade = Cidade.objects.create(
    nome_cidade="Cuiabá",
    uf_cidade="MT",
    latitude_cidade=-15.6014,
    longitude_cidade=-56.0979
)

# Criar bairro
bairro = Bairro.objects.create(
    nome_bairro="Centro",
    cidade=cidade,
    latitude_bairro=-15.6014,
    longitude_bairro=-56.0979
)
```

## 🌐 Desenvolvimento Frontend

### Estrutura de Templates
```
templates/
├── base.html              # Template base
├── home.html              # Página inicial
├── dashboard.html         # Dashboard principal
├── mapa.html              # Mapa interativo
├── sobre.html             # Página sobre
├── relatorios_base.html   # Base para relatórios
└── registration/          # Templates de autenticação
    ├── login.html
    ├── pw_reset_form.html
    ├── pw_reset_done.html
    ├── password_reset_confirm.html
    └── pw_reset_complete.html
```

### Sistema de CSS
```css
/* Variáveis CSS personalizadas */
:root {
    --card-bg: #ffffff;
    --bs-primary: #0d6efd;
    --bs-secondary: #6c757d;
    --bs-success: #198754;
    --bs-warning: #ffc107;
    --bs-danger: #dc3545;
}

/* Classes utilitárias */
.custom-nav-btn {
    background: linear-gradient(135deg, var(--bs-primary), var(--bs-secondary));
    border-radius: 15px;
    padding: 20px;
    text-decoration: none;
    color: white;
    transition: all 0.3s ease;
}
```

### JavaScript e Interatividade
```javascript
// Chart.js para gráficos
const ctx = document.getElementById('chartCanvas').getContext('2d');
const chart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: chartLabels,
        datasets: [{
            label: 'Colaboradores por Cidade',
            data: chartData,
            backgroundColor: 'rgba(13, 110, 253, 0.8)'
        }]
    }
});

// Leaflet.js para mapas
const map = L.map('map').setView([-15.6014, -56.0979], 10);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
```

## 💬 Sistema de Chat

### WebSockets com Django Channels
```python
# consumers.py
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )
```

### Routing de WebSockets
```python
# routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
```

## 🗺️ Sistema de Mapas

### Integração com OpenStreetMap
```html
<!-- Template do mapa -->
<div id="map" style="height: 600px;"></div>

<script>
// Configuração do mapa
const map = L.map('map').setView([-15.6014, -56.0979], 8);

// Camada de tiles do OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Dados de calor
const heatData = {{ heat_data|safe }};
const heatmapLayer = L.heatLayer(heatData, {
    radius: 25,
    blur: 15,
    maxZoom: 10
}).addTo(map);
</script>
```

### Dados Geográficos
```python
# views.py - Dados para o mapa
def mapa_apoiadores(request):
    # Coordenadas dos colaboradores
    coords_colaboradores = Colaborador.objects.filter(
        cidade__latitude_cidade__isnull=False
    ).values_list(
        'cidade__latitude_cidade', 
        'cidade__longitude_cidade'
    )
    
    # Coordenadas dos convidados
    coords_convidados = Convidado.objects.filter(
        cidade__latitude_cidade__isnull=False
    ).values_list(
        'cidade__latitude_cidade', 
        'cidade__longitude_cidade'
    )
    
    # Combina coordenadas para mapa de calor
    heat_data = [
        [float(lat), float(lon)]
        for lat, lon in list(coords_colaboradores) + list(coords_convidados)
    ]
    
    context = {'heat_data': json.dumps(heat_data)}
    return render(request, 'mapa.html', context)
```

## 📊 Dashboard e Relatórios

### KPIs e Métricas
```python
# views.py - Cálculo de KPIs
def dashboard(request):
    # Total de colaboradores
    total_colaboradores = Colaborador.objects.count()
    
    # Total de convidados
    total_convidados = Convidado.objects.count()
    
    # Colaboradores com contagem de convidados
    colaboradores_com_contagem = Colaborador.objects.annotate(
        num_convidados=Count('convidados')
    )
    
    # Top 15 colaboradores
    top_15_colaboradores = colaboradores_com_contagem.order_by(
        '-num_convidados'
    )[:15]
    
    # Eficiência média
    eficiencia_media = 0
    colaboradores_ativos = colaboradores_com_contagem.filter(
        num_convidados__gt=0
    ).count()
    
    if colaboradores_ativos > 0:
        eficiencia_media = total_convidados / colaboradores_ativos
```

### Gráficos com Chart.js
```javascript
// Gráfico de barras para cidades
const ctxCidades = document.getElementById('chartCidades').getContext('2d');
new Chart(ctxCidades, {
    type: 'bar',
    data: {
        labels: {{ labels_cidades_colab|safe }},
        datasets: [{
            label: 'Colaboradores por Cidade',
            data: {{ data_cidades_colab|safe }},
            backgroundColor: 'rgba(13, 110, 253, 0.8)',
            borderColor: 'rgba(13, 110, 253, 1)',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
```

## 🔒 Segurança e Autenticação

### Proteção de Rotas
```python
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Proteção com decorator
@login_required
def dashboard(request):
    # View protegida
    pass

# Proteção com mixin
class ColaboradorListView(LoginRequiredMixin, ListView):
    model = Colaborador
    template_name = 'colaboradores/lista.html'
    login_url = '/login/'
```

### Validação de Formulários
```python
# forms.py
class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ['nome', 'telefone', 'cidade', 'bairro']
    
    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            # Remove caracteres não numéricos
            telefone = re.sub(r'[^\d]', '', telefone)
            if len(telefone) < 10:
                raise forms.ValidationError('Telefone deve ter pelo menos 10 dígitos')
        return telefone
```

### Content Security Policy
```python
# settings.py
CSP_DEFAULT_SRC = ("'self'", "https://unpkg.com", "https://*.tile.openstreetmap.org")
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://unpkg.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://unpkg.com")
CSP_IMG_SRC = ("'self'", "data:", "https://*.tile.openstreetmap.org")
CSP_FONT_SRC = ("'self'", "https://cdn.jsdelivr.net")
CSP_CONNECT_SRC = ("'self'",)
```

## 🧪 Testes

### Configuração de Testes
```python
# tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from colaboradores.models import Colaborador
from geografia.models import Cidade

class ColaboradorTestCase(TestCase):
    def setUp(self):
        # Cria dados de teste
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.cidade = Cidade.objects.create(
            nome_cidade='Cuiabá',
            uf_cidade='MT'
        )
        self.colaborador = Colaborador.objects.create(
            nome='João Silva',
            telefone='65999999999',
            cidade=self.cidade,
            cadastrado_por=self.user
        )
    
    def test_colaborador_creation(self):
        self.assertEqual(self.colaborador.nome, 'João Silva')
        self.assertEqual(self.colaborador.cidade.nome_cidade, 'Cuiabá')
    
    def test_colaborador_str_representation(self):
        self.assertEqual(str(self.colaborador), 'João Silva')
```

### Execução de Testes
```bash
# Executar todos os testes
python manage.py test

# Executar testes de uma app específica
python manage.py test colaboradores

# Executar testes com cobertura
coverage run --source='.' manage.py test
coverage report
coverage html

# Executar testes específicos
python manage.py test colaboradores.tests.ColaboradorTestCase.test_colaborador_creation
```

## 🔧 Ferramentas de Desenvolvimento

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

### Ruff e Black
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ["py312"]
exclude = '''
/(
  \.venv
  | migrations
  | static
  | media
)/
'''

[tool.ruff]
target-version = "py312"
line-length = 88
fix = true
extend-exclude = ["migrations", ".venv", "static", "media"]

[tool.ruff.lint]
select = ["E","F","W","I","UP","B","C4","RET","SIM","N","RUF"]
ignore = [
  "E203",  # compatibilidade com Black
]
```

### VS Code Configuration
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

## 🚀 Deploy e Produção

### Scripts de Deploy
```bash
#!/bin/bash
# daphne_start.sh
cd /srv/sisvot
source .venv/bin/activate
export DJANGO_SETTINGS_MODULE=sistema_fidelizacao.settings

# Verificar Django
python manage.py check --deploy || exit 1

# Iniciar Daphne
exec daphne -b 0.0.0.0 -p 8000 sistema_fidelizacao.asgi:application
```

### Configuração de Produção
```python
# settings_prod.py
DEBUG = False
ALLOWED_HOSTS = ['fidelizamax.app.br', 'www.fidelizamax.app.br']

# Banco de dados de produção
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sisvot_prod',
        'USER': 'sisuserdb',
        'PASSWORD': 'senha_producao',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# Configurações de segurança
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Nginx Configuration
```nginx
# /etc/nginx/sites-available/sisvot
server {
    listen 80;
    server_name fidelizamax.app.br;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name fidelizamax.app.br;
    
    ssl_certificate /etc/letsencrypt/live/fidelizamax.app.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/fidelizamax.app.br/privkey.pem;
    
    location / {
        proxy_pass http://unix:/srv/sisvot/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /srv/sisvot/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## 📚 Recursos e Referências

### Documentação Django
- [Django 5.2 Documentation](https://docs.djangoproject.com/en/5.2/)
- [Django Channels Documentation](https://channels.readthedocs.io/)
- [Django Security](https://docs.djangoproject.com/en/5.2/topics/security/)

### Bibliotecas Frontend
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.0/)
- [Chart.js Documentation](https://www.chartjs.org/docs/)
- [Leaflet.js Documentation](https://leafletjs.com/reference.html)

### Ferramentas de Qualidade
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Black Documentation](https://black.readthedocs.io/)
- [Pre-commit Documentation](https://pre-commit.com/)

### Tutoriais e Exemplos
- [Django Channels Tutorial](https://channels.readthedocs.io/en/stable/tutorial/)
- [Django Testing Tutorial](https://docs.djangoproject.com/en/5.2/topics/testing/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)

---

**Última Atualização**: Dezembro 2024  
**Versão do Guia**: 1.0.0

