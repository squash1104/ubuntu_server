# SisAps - Sistema de Fidelização de Apoiadores

## 📋 Visão Geral

O **SisAps** é um sistema web desenvolvido em Django para gerenciar e acompanhar a fidelização de apoiadores políticos. O sistema permite o cadastro e monitoramento de colaboradores e convidados, com funcionalidades de geolocalização, relatórios e comunicação em tempo real.

## 🏗️ Arquitetura do Sistema

### Tecnologias Principais
- **Backend**: Django 5.2.4 (Python 3.12)
- **Banco de Dados**: PostgreSQL
- **Servidor ASGI**: Daphne (para WebSockets)
- **Servidor WSGI**: Gunicorn (para produção)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **WebSockets**: Django Channels 4.2.2
- **Mapas**: OpenStreetMap com Leaflet.js
- **Gráficos**: Chart.js

### Estrutura do Projeto
```
sisvot/
├── sistema_fidelizacao/     # Projeto principal Django
├── colaboradores/           # App para gerenciar colaboradores
├── convidados/             # App para gerenciar convidados
├── geografia/              # App para dados geográficos
├── chat/                   # App para comunicação em tempo real
├── templates/              # Templates HTML
├── static/                 # Arquivos estáticos (CSS, JS, imagens)
├── staticfiles/            # Arquivos estáticos coletados
├── docs/                   # Documentação
└── requirements.txt        # Dependências Python
```

## 🚀 Funcionalidades Principais

### 1. Gestão de Colaboradores
- Cadastro de colaboradores com dados pessoais
- Associação com localização geográfica (cidade/bairro)
- Controle de metas e performance
- Histórico de atividades

### 2. Gestão de Convidados
- Cadastro de convidados/eleitores
- Vinculação com colaboradores responsáveis
- Geolocalização para análise territorial
- Controle de status e acompanhamento

### 3. Dashboard Analítico
- KPIs de performance por colaborador
- Gráficos de distribuição geográfica
- Análise por mesorregiões (Norte, Nordeste, Sudeste, Sudoeste, Centro-Sul)
- Mapa de calor com concentração de apoiadores

### 4. Sistema de Chat
- Comunicação em tempo real entre usuários
- WebSockets para atualizações instantâneas
- Histórico de mensagens
- Indicadores de status online/offline

### 5. Relatórios e Exportação
- Relatórios personalizáveis por período
- Exportação em PDF
- Filtros avançados por localização e status
- Análises comparativas

### 6. Mapa Interativo
- Visualização geográfica de apoiadores
- Mapa de calor por concentração
- Navegação por cidades e bairros
- Integração com OpenStreetMap

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.12+
- PostgreSQL 12+
- Node.js (para compilação de assets)
- Git

### 1. Clone do Repositório
```bash
git clone <repository-url>
cd sisvot
```

### 2. Configuração do Ambiente Virtual
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows
```

### 3. Instalação de Dependências
```bash
pip install -r requirements.txt
```

### 4. Configuração do Banco de Dados
```bash
# Crie o banco PostgreSQL
createdb sisvot_db

# Execute as migrações
python manage.py migrate

# Crie um superusuário
python manage.py createsuperuser
```

### 5. Configuração de Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=postgresql://usuario:senha@localhost:5432/sisvot_db
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
```

### 6. Coleta de Arquivos Estáticos
```bash
python manage.py collectstatic
```

### 7. Execução do Sistema
```bash
# Desenvolvimento
python manage.py runserver

# Produção (com Daphne para WebSockets)
./daphne_start.sh

# Produção (com Gunicorn)
./gunicorn_start.sh
```

## 🗄️ Modelos de Dados

### Colaborador
- **nome**: Nome completo do colaborador
- **telefone**: Número de contato
- **cidade**: Referência à cidade (ForeignKey)
- **bairro**: Referência ao bairro (ForeignKey)
- **data_cadastro**: Data/hora de cadastro
- **cadastrado_por**: Usuário que fez o cadastro

### Convidado
- **nome**: Nome completo do convidado
- **telefone**: Número de contato
- **cidade**: Referência à cidade (ForeignKey)
- **bairro**: Referência ao bairro (ForeignKey)
- **colaborador**: Colaborador responsável (ForeignKey)
- **data_cadastro**: Data/hora de cadastro

### Cidade
- **nome_cidade**: Nome da cidade
- **uf_cidade**: Sigla do estado
- **latitude_cidade**: Coordenada de latitude
- **longitude_cidade**: Coordenada de longitude

### Bairro
- **nome_bairro**: Nome do bairro
- **cidade**: Referência à cidade (ForeignKey)
- **latitude_bairro**: Coordenada de latitude
- **longitude_bairro**: Coordenada de longitude

### Message (Chat)
- **sender**: Usuário remetente
- **recipient**: Usuário destinatário
- **content**: Conteúdo da mensagem
- **timestamp**: Data/hora de envio
- **read**: Status de leitura
- **read_at**: Data/hora de leitura

## 🌐 URLs e Rotas

### URLs Principais
- `/` - Página inicial
- `/home/` - Home do sistema
- `/dashboard/` - Dashboard principal
- `/login/` - Autenticação
- `/logout/` - Logout
- `/sobre/` - Informações sobre o sistema

### URLs das Aplicações
- `/colaboradores/` - Gestão de colaboradores
- `/convidados/` - Gestão de convidados
- `/geografia/` - Dados geográficos
- `/chat/` - Sistema de chat
- `/mapa-apoiadores/` - Mapa interativo

### URLs de Autenticação
- `/password_reset/` - Reset de senha
- `/password_reset/done/` - Confirmação de reset
- `/reset/<uidb64>/<token>/` - Confirmação de nova senha
- `/reset/done/` - Senha alterada com sucesso

## 🔧 Configurações de Produção

### Configurações de Segurança
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['sistema.fidelizamax.app.br', 'www.sistema.fidelizamax.app.br']
CSRF_TRUSTED_ORIGINS = ['https://sistema.fidelizamax.app.br']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### Configurações de Banco de Dados
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sisvot_db',
        'USER': 'sisuserdb',
        'PASSWORD': 'senha-segura',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```

### Configurações de Email
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-de-app'
DEFAULT_FROM_EMAIL = 'suporte@fidelizamax.app.br'
```

### Configurações de WebSockets
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
        # Para produção, considere usar Redis:
        # 'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'CONFIG': {
        #     'hosts': [('localhost', 6379)],
        # },
    },
}
```

## 📊 Funcionalidades do Dashboard

### KPIs Principais
- Total de colaboradores
- Total de convidados
- Eficiência média (convidados por colaborador ativo)
- Distribuição por metas (abaixo, na meta, superada)

### Gráficos e Visualizações
- Distribuição de colaboradores por cidade
- Distribuição de convidados por cidade
- Análise por mesorregiões
- Mapa de calor geográfico

### Filtros e Relatórios
- Filtros por período
- Filtros por localização
- Filtros por status
- Exportação em PDF

## 🗺️ Sistema de Mapas

### Tecnologias Utilizadas
- **OpenStreetMap**: Base de mapas
- **Leaflet.js**: Biblioteca JavaScript para mapas interativos
- **Heatmap.js**: Plugin para mapas de calor

### Funcionalidades
- Visualização de coordenadas geográficas
- Mapa de calor por concentração de apoiadores
- Navegação por cidades e bairros
- Zoom e pan interativos

## 💬 Sistema de Chat

### Características
- Comunicação em tempo real
- WebSockets para atualizações instantâneas
- Histórico de mensagens
- Indicadores de status online/offline
- Notificações de novas mensagens

### Implementação
- **Consumers**: Gerenciam conexões WebSocket
- **Routing**: Define padrões de URL para WebSockets
- **Models**: Armazenam mensagens e perfis de usuário
- **Signals**: Atualizam perfis automaticamente

## 🔒 Segurança e Autenticação

### Sistema de Autenticação
- Login/logout padrão do Django
- Reset de senha por email
- Proteção de rotas com `@login_required`
- Validação de formulários

### Content Security Policy (CSP)
```python
CSP_DEFAULT_SRC = ("'self'", "https://unpkg.com", "https://*.tile.openstreetmap.org")
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://unpkg.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://unpkg.com")
CSP_IMG_SRC = ("'self'", "data:", "https://*.tile.openstreetmap.org")
```

## 📱 Responsividade e UX

### Design System
- Bootstrap 5 para layout responsivo
- Ícones Bootstrap Icons
- Tema personalizado com variáveis CSS
- Componentes reutilizáveis

### Funcionalidades Mobile
- Layout responsivo para todos os dispositivos
- Navegação otimizada para touch
- Gráficos adaptáveis
- Mapas com controles touch-friendly

## 🧪 Testes e Qualidade

### Ferramentas de Qualidade
- **Ruff**: Linter e formatação de código
- **Black**: Formatação automática
- **Pre-commit**: Hooks para qualidade de código
- **Pytest**: Framework de testes

### Configuração de Testes
```toml
[tool.pytest.ini_options]
addopts = "-q"
DJANGO_SETTINGS_MODULE = "core.settings"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
asyncio_mode = "auto"
```

## 🚀 Deploy e Produção

### Scripts de Deploy
- `daphne_start.sh`: Inicia servidor ASGI para WebSockets
- `gunicorn_start.sh`: Inicia servidor WSGI para produção

### Configurações de Servidor
- **Daphne**: Porta 8000 para desenvolvimento
- **Gunicorn**: Socket Unix para produção
- **Nginx**: Proxy reverso (configuração necessária)
- **Systemd**: Gerenciamento de serviços

### Variáveis de Ambiente de Produção
```bash
export DJANGO_SETTINGS_MODULE=sistema_fidelizacao.settings
export DJANGO_WSGI_MODULE=sistema_fidelizacao.wsgi
```

## 📈 Monitoramento e Logs

### Logs do Sistema
- Logs do Django
- Logs do Gunicorn
- Logs do Daphne
- Logs de erro e acesso

### Health Checks
- Endpoint `/health/` para monitoramento
- Verificação de conectividade com banco
- Status dos serviços WebSocket

## 🔄 Manutenção e Atualizações

### Comandos de Manutenção
```bash
# Backup do banco
pg_dump sisvot_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Atualização de dependências
pip install -r requirements.txt --upgrade

# Aplicação de migrações
python manage.py migrate

# Coleta de arquivos estáticos
python manage.py collectstatic --noinput

# Verificação de segurança
python manage.py check --deploy
```

### Backup e Recuperação
- Backup automático do banco PostgreSQL
- Versionamento de código com Git
- Documentação de mudanças
- Procedimentos de rollback

## 🤝 Contribuição e Desenvolvimento

### Padrões de Código
- PEP 8 para estilo Python
- Docstrings para documentação
- Type hints para tipagem
- Commits semânticos

### Workflow de Desenvolvimento
1. Criação de branch para feature
2. Desenvolvimento com testes
3. Pull request com revisão
4. Merge após aprovação
5. Deploy em ambiente de teste
6. Deploy em produção

## 📚 Recursos Adicionais

### Documentação Django
- [Django Documentation](https://docs.djangoproject.com/)
- [Django Channels](https://channels.readthedocs.io/)
- [Django REST Framework](https://www.django-rest-framework.org/)

### Recursos de Frontend
- [Bootstrap 5](https://getbootstrap.com/docs/5.0/)
- [Chart.js](https://www.chartjs.org/)
- [Leaflet.js](https://leafletjs.com/)
- [OpenStreetMap](https://www.openstreetmap.org/)

### Ferramentas de Desenvolvimento
- [Ruff](https://github.com/astral-sh/ruff)
- [Black](https://black.readthedocs.io/)
- [Pre-commit](https://pre-commit.com/)

## 📞 Suporte e Contato

### Equipe de Desenvolvimento
- **Desenvolvedor Principal**: Luciano
- **Email**: lucianolrv@gmail.com
- **Suporte**: suporte@fidelizamax.app.br

### Canais de Suporte
- Sistema de tickets interno
- Chat em tempo real
- Email de suporte
- Documentação técnica

---

**Versão**: 1.0.0  
**Última Atualização**: Dezembro 2024  
**Status**: Em Produção

