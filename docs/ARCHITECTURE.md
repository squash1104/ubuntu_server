# Arquitetura Técnica - SisAps

## 🏗️ Visão Geral da Arquitetura

O SisAps é um sistema web baseado em arquitetura de camadas, seguindo o padrão MVC (Model-View-Controller) do Django. O sistema é projetado para ser escalável, manutenível e seguro, com separação clara de responsabilidades entre as diferentes camadas.

## 🎯 Princípios de Design

### 1. Separação de Responsabilidades
- **Models**: Lógica de negócio e acesso a dados
- **Views**: Controle de fluxo e apresentação
- **Templates**: Interface do usuário
- **Forms**: Validação e processamento de entrada
- **URLs**: Roteamento de requisições

### 2. DRY (Don't Repeat Yourself)
- Reutilização de código através de mixins e herança
- Templates base com extensão
- Utilitários compartilhados entre apps

### 3. SOLID Principles
- **Single Responsibility**: Cada classe tem uma responsabilidade
- **Open/Closed**: Extensível sem modificação
- **Liskov Substitution**: Substituição de implementações
- **Interface Segregation**: Interfaces específicas
- **Dependency Inversion**: Dependências abstratas

## 🏛️ Arquitetura de Camadas

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                          │
├─────────────────────────────────────────────────────────────┤
│  HTML5 | CSS3 | JavaScript | Bootstrap 5 | Chart.js       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Presentation Layer                       │
├─────────────────────────────────────────────────────────────┤
│  Django Templates | Forms | Static Files                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                    │
├─────────────────────────────────────────────────────────────┤
│  Django Views | Custom Logic | Business Rules              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Access Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Django Models | ORM | Database Queries                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                     │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL | Redis | File System | External APIs          │
└─────────────────────────────────────────────────────────────┘
```

## 🗄️ Modelo de Dados

### Diagrama ER (Entidade-Relacionamento)
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    User     │    │ Colaborador │    │  Convidado  │
├─────────────┤    ├─────────────┤    ├─────────────┤
│ id (PK)     │◄───┤ id (PK)     │    │ id (PK)     │
│ username    │    │ nome        │    │ nome        │
│ email       │    │ telefone    │    │ telefone    │
│ password    │    │ cidade_id   │───►│ cidade_id   │───►┌─────────────┐
│ first_name  │    │ bairro_id   │───►│ bairro_id   │───►│   Cidade    │
│ last_name   │    │ data_cad    │    │ data_cad    │    ├─────────────┤
│ is_active   │    │ user_id     │    │ colab_id    │    │ id (PK)     │
└─────────────┘    └─────────────┘    └─────────────┘    │ nome_cidade │
                                                        │ uf_cidade   │
                                                        │ latitude    │
                                                        │ longitude   │
                                                        └─────────────┘
                                                               ▲
                                                               │
                                                        ┌─────────────┐
                                                        │   Bairro    │
                                                        ├─────────────┤
                                                        │ id (PK)     │
                                                        │ nome_bairro │
                                                        │ cidade_id   │
                                                        │ latitude    │
                                                        │ longitude   │
                                                        └─────────────┘
```

### Relacionamentos
- **User ↔ Colaborador**: One-to-One (cadastrado_por)
- **Colaborador ↔ Convidado**: One-to-Many (colaborador)
- **Cidade ↔ Bairro**: One-to-Many (cidade)
- **Cidade ↔ Colaborador**: One-to-Many (cidade)
- **Cidade ↔ Convidado**: One-to-Many (cidade)
- **Bairro ↔ Colaborador**: One-to-Many (bairro)
- **Bairro ↔ Convidado**: One-to-Many (bairro)

## 🌐 Arquitetura de Comunicação

### Padrão Request-Response
```
┌─────────────┐    HTTP Request     ┌─────────────┐
│   Client    │ ──────────────────► │   Django    │
│ (Browser)   │                     │   Server    │
└─────────────┘                     └─────────────┘
        ▲                                  │
        │                                  ▼
        │                           ┌─────────────┐
        │                           │   Views     │
        │                           │  (Logic)    │
        │                           └─────────────┘
        │                                  │
        │                                  ▼
        │                           ┌─────────────┐
        │                           │  Models     │
        │                           │ (Database)  │
        │                           └─────────────┘
        │                                  │
        │                                  ▼
        │                           ┌─────────────┐
        │                           │ Templates   │
        │                           │   (HTML)    │
        │                           └─────────────┘
        │                                  │
        │                                  ▼
        │                           ┌─────────────┐
        │                           │   Response  │
        │                           │   (HTML)    │
        │                           └─────────────┘
        │                                  │
        │                                  ▼
        │                           ┌─────────────┐
        │                           │   Client    │
        │                           │ (Browser)   │
        └───────────────────────────┘             ┘
```

### WebSockets para Chat
```
┌─────────────┐    WebSocket      ┌─────────────┐
│   Client    │ ◄────────────────► │   Daphne    │
│ (Browser)   │    Connection     │   Server    │
└─────────────┘                   └─────────────┘
        │                                  │
        │                                  ▼
        │                           ┌─────────────┐
        │                           │  Consumer   │
        │                           │ (Chat Logic)│
        │                           └─────────────┘
        │                                  │
        │                                  ▼
        │                           ┌─────────────┐
        │                           │ Channel     │
        │                           │  Layer      │
        │                           └─────────────┘
        │                                  │
        │                                  ▼
        │                           ┌─────────────┐
        │                           │  Database   │
        │                           │ (Messages)  │
        │                           └─────────────┘
```

## 🔧 Padrões de Design Implementados

### 1. Factory Pattern
```python
# Exemplo de criação de objetos relacionados
class ColaboradorFactory:
    @staticmethod
    def create_with_location(nome, telefone, cidade_nome, bairro_nome):
        cidade, _ = Cidade.objects.get_or_create(
            nome_cidade=cidade_nome,
            defaults={'uf_cidade': 'MT'}
        )
        bairro, _ = Bairro.objects.get_or_create(
            nome_bairro=bairro_nome,
            cidade=cidade
        )
        return Colaborador.objects.create(
            nome=nome,
            telefone=telefone,
            cidade=cidade,
            bairro=bairro
        )
```

### 2. Strategy Pattern
```python
# Diferentes estratégias de relatório
class ReportStrategy:
    def generate_report(self, data):
        raise NotImplementedError

class PDFReportStrategy(ReportStrategy):
    def generate_report(self, data):
        # Lógica para gerar PDF
        pass

class CSVReportStrategy(ReportStrategy):
    def generate_report(self, data):
        # Lógica para gerar CSV
        pass
```

### 3. Observer Pattern
```python
# Signals do Django para notificações
@receiver(post_save, sender=Colaborador)
def notify_colaborador_created(sender, instance, created, **kwargs):
    if created:
        # Notificar administradores
        send_notification(f"Novo colaborador: {instance.nome}")
```

### 4. Template Method Pattern
```python
# Base para diferentes tipos de relatório
class BaseReport:
    def generate(self):
        data = self.collect_data()
        processed_data = self.process_data(data)
        return self.format_report(processed_data)
    
    def collect_data(self):
        raise NotImplementedError
    
    def process_data(self, data):
        raise NotImplementedError
    
    def format_report(self, data):
        raise NotImplementedError
```

## 🚀 Padrões de Performance

### 1. Database Optimization
```python
# Uso de select_related para evitar N+1 queries
colaboradores = Colaborador.objects.select_related(
    'cidade', 'bairro', 'cadastrado_por'
).all()

# Uso de prefetch_related para relacionamentos many-to-many
colaboradores = Colaborador.objects.prefetch_related('convidados').all()

# Annotate para cálculos agregados
colaboradores_com_contagem = Colaborador.objects.annotate(
    num_convidados=Count('convidados')
)
```

### 2. Caching Strategy
```python
# Cache de dados frequentemente acessados
from django.core.cache import cache

def get_dashboard_data():
    cache_key = 'dashboard_data'
    data = cache.get(cache_key)
    
    if data is None:
        data = calculate_dashboard_data()
        cache.set(cache_key, data, timeout=300)  # 5 minutos
    
    return data
```

### 3. Pagination
```python
# Paginação para listas grandes
from django.core.paginator import Paginator

def colaborador_list(request):
    colaboradores_list = Colaborador.objects.all()
    paginator = Paginator(colaboradores_list, 25)  # 25 por página
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'colaboradores/lista.html', {'page_obj': page_obj})
```

## 🔒 Arquitetura de Segurança

### 1. Authentication & Authorization
```python
# Middleware de autenticação
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Proteção de rotas
@login_required
def dashboard(request):
    # Apenas usuários autenticados
    pass

# Permissões baseadas em usuário
def can_edit_colaborador(user, colaborador):
    return user.is_staff or user == colaborador.cadastrado_por
```

### 2. Content Security Policy
```python
# Políticas de segurança de conteúdo
CSP_DEFAULT_SRC = ("'self'", "https://unpkg.com")
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://unpkg.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://unpkg.com")
CSP_IMG_SRC = ("'self'", "data:", "https://*.tile.openstreetmap.org")
```

### 3. SQL Injection Protection
```python
# Uso do ORM do Django (proteção automática)
# ❌ Perigoso
# query = f"SELECT * FROM colaboradores WHERE nome = '{nome}'"

# ✅ Seguro
colaboradores = Colaborador.objects.filter(nome__icontains=nome)
```

## 📊 Arquitetura de Monitoramento

### 1. Logging Strategy
```python
# Configuração de logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 2. Health Checks
```python
# Endpoint de verificação de saúde
def health_check_view(request):
    try:
        # Verificar banco de dados
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Verificar WebSockets
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        
        return HttpResponse("OK", status=200)
    except Exception as e:
        return HttpResponse(f"ERROR: {str(e)}", status=500)
```

### 3. Performance Monitoring
```python
# Middleware para monitorar performance
import time
from django.utils.deprecation import MiddlewareMixin

class PerformanceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response['X-Request-Duration'] = str(duration)
        return response
```

## 🔄 Padrões de Manutenibilidade

### 1. Configuration Management
```python
# Configurações por ambiente
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Configurações de ambiente
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    from .settings_prod import *
elif ENVIRONMENT == 'testing':
    from .settings_test import *
else:
    from .settings_dev import *
```

### 2. Error Handling
```python
# Tratamento centralizado de erros
from django.http import JsonResponse
from django.core.exceptions import ValidationError

def custom_500_handler(request, exception=None):
    return JsonResponse({
        'error': 'Internal Server Error',
        'message': 'Ocorreu um erro interno. Tente novamente mais tarde.',
        'status': 500
    }, status=500)

# Handler personalizado para validação
def handle_validation_error(validation_error):
    return {
        'error': 'Validation Error',
        'details': validation_error.message_dict,
        'status': 400
    }
```

### 3. Code Organization
```
# Estrutura de diretórios organizada
sistema_fidelizacao/
├── __init__.py
├── settings.py          # Configurações principais
├── settings_dev.py      # Configurações de desenvolvimento
├── settings_prod.py     # Configurações de produção
├── settings_test.py     # Configurações de teste
├── urls.py              # URLs principais
├── asgi.py              # Configuração ASGI
├── wsgi.py              # Configuração WSGI
└── views.py             # Views principais

apps/
├── colaboradores/
│   ├── models.py        # Modelos de dados
│   ├── views.py         # Lógica de negócio
│   ├── forms.py         # Formulários
│   ├── urls.py          # Roteamento
│   └── admin.py         # Interface administrativa
├── convidados/
├── geografia/
└── chat/
```

## 🚀 Estratégias de Escalabilidade

### 1. Horizontal Scaling
- **Load Balancer**: Distribuição de carga entre múltiplos servidores
- **Database Sharding**: Particionamento de dados por região geográfica
- **Microservices**: Separação de funcionalidades em serviços independentes

### 2. Vertical Scaling
- **Database Optimization**: Índices, queries otimizadas, connection pooling
- **Caching Layers**: Redis para sessões e dados frequentemente acessados
- **CDN**: Distribuição de arquivos estáticos

### 3. Asynchronous Processing
```python
# Uso de Celery para tarefas assíncronas
from celery import shared_task

@shared_task
def process_large_report(data):
    # Processamento em background
    result = generate_complex_report(data)
    return result

# Uso de Django Channels para WebSockets
class ChatConsumer(AsyncWebsocketConsumer):
    async def receive(self, text_data):
        # Processamento assíncrono de mensagens
        await self.process_message(text_data)
```

## 📈 Métricas e KPIs Técnicos

### 1. Performance Metrics
- **Response Time**: Tempo de resposta das requisições
- **Throughput**: Número de requisições por segundo
- **Error Rate**: Taxa de erros
- **Resource Usage**: CPU, memória, disco

### 2. Business Metrics
- **User Engagement**: Tempo de sessão, páginas visitadas
- **Conversion Rate**: Taxa de conversão de visitantes
- **System Availability**: Tempo de disponibilidade
- **Data Quality**: Precisão e completude dos dados

### 3. Monitoring Tools
- **Application Performance Monitoring**: New Relic, Datadog
- **Log Aggregation**: ELK Stack, Splunk
- **Infrastructure Monitoring**: Prometheus, Grafana
- **Error Tracking**: Sentry, Rollbar

---

**Versão da Arquitetura**: 1.0.0  
**Última Atualização**: Dezembro 2024  
**Status**: Implementado e em Produção

