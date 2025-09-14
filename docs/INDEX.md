# 📚 Índice da Documentação - SisAps

## 🚀 Documentação Principal

### [README.md](./README.md)
**Visão geral completa do sistema**
- Descrição do projeto
- Funcionalidades principais
- Instalação e configuração
- Modelos de dados
- URLs e rotas
- Configurações de produção
- Suporte e contato

### [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)
**Guia técnico para desenvolvedores**
- Ambiente de desenvolvimento
- Python e Django
- Banco de dados
- Frontend
- Sistema de chat
- Mapas e geolocalização
- Dashboard e relatórios
- Segurança e autenticação
- Testes
- Ferramentas de desenvolvimento
- Deploy e produção

### [ARCHITECTURE.md](./ARCHITECTURE.md)
**Arquitetura técnica detalhada**
- Visão geral da arquitetura
- Princípios de design
- Arquitetura de camadas
- Modelo de dados
- Padrões de design
- Performance e escalabilidade
- Segurança
- Monitoramento
- Manutenibilidade

## 📋 Seções Rápidas

### 🏗️ **Arquitetura**
- [Visão Geral](./ARCHITECTURE.md#-visão-geral-da-arquitetura)
- [Modelo de Dados](./ARCHITECTURE.md#-modelo-de-dados)
- [Padrões de Design](./ARCHITECTURE.md#-padrões-de-design-implementados)

### 🚀 **Desenvolvimento**
- [Configuração Inicial](./DEVELOPER_GUIDE.md#-configuração-inicial)
- [Estrutura do Projeto](./DEVELOPER_GUIDE.md#-estrutura-de-desenvolvimento)
- [Banco de Dados](./DEVELOPER_GUIDE.md#-banco-de-dados)
- [Frontend](./DEVELOPER_GUIDE.md#-desenvolvimento-frontend)

### 🔧 **Configuração**
- [Instalação](./README.md#-instalação-e-configuração)
- [Ambiente de Desenvolvimento](./DEVELOPER_GUIDE.md#-configurações-de-desenvolvimento)
- [Configurações de Produção](./README.md#-configurações-de-produção)
- [Deploy](./DEVELOPER_GUIDE.md#-deploy-e-produção)

### 📊 **Funcionalidades**
- [Dashboard](./README.md#-funcionalidades-do-dashboard)
- [Sistema de Chat](./README.md#-sistema-de-chat)
- [Mapas Interativos](./README.md#-sistema-de-mapas)
- [Relatórios](./README.md#-relatórios-e-exportação)

## 🔍 Busca Rápida por Tópico

### **Django e Python**
- [Configurações](./DEVELOPER_GUIDE.md#-configurações-de-desenvolvimento)
- [Modelos](./DEVELOPER_GUIDE.md#-modelos-e-relacionamentos)
- [Views](./DEVELOPER_GUIDE.md#-dashboard-e-relatórios)
- [URLs](./README.md#-urls-e-rotas)

### **Banco de Dados**
- [PostgreSQL](./README.md#-configurações-de-banco-de-dados)
- [Migrações](./DEVELOPER_GUIDE.md#-migrações)
- [Queries Otimizadas](./ARCHITECTURE.md#-database-optimization)
- [Modelos](./README.md#-modelos-de-dados)

### **Frontend**
- [Bootstrap 5](./DEVELOPER_GUIDE.md#-sistema-de-css)
- [Chart.js](./DEVELOPER_GUIDE.md#-gráficos-com-chartjs)
- [Leaflet.js](./DEVELOPER_GUIDE.md#-integração-com-openstreetmap)
- [JavaScript](./DEVELOPER_GUIDE.md#-javascript-e-interatividade)

### **WebSockets e Chat**
- [Django Channels](./DEVELOPER_GUIDE.md#-websockets-com-django-channels)
- [Consumers](./DEVELOPER_GUIDE.md#-websockets-com-django-channels)
- [Routing](./DEVELOPER_GUIDE.md#-routing-de-websockets)
- [Implementação](./README.md#-sistema-de-chat)

### **Segurança**
- [Autenticação](./DEVELOPER_GUIDE.md#-proteção-de-rotas)
- [CSP](./DEVELOPER_GUIDE.md#-content-security-policy)
- [Validação](./DEVELOPER_GUIDE.md#-validação-de-formulários)
- [Proteção](./ARCHITECTURE.md#-authentication--authorization)

### **Deploy e Produção**
- [Scripts](./README.md#-scripts-de-deploy)
- [Nginx](./DEVELOPER_GUIDE.md#-nginx-configuration)
- [Gunicorn](./README.md#-configurações-de-servidor)
- [Daphne](./README.md#-configurações-de-servidor)

## 🛠️ Comandos Úteis

### **Desenvolvimento**
```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar servidor
python manage.py runserver

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Shell do Django
python manage.py shell

# Testes
python manage.py test
```

### **Produção**
```bash
# Coletar arquivos estáticos
python manage.py collectstatic

# Verificar configurações
python manage.py check --deploy

# Iniciar Daphne (WebSockets)
./daphne_start.sh

# Iniciar Gunicorn
./gunicorn_start.sh
```

### **Qualidade de Código**
```bash
# Formatação com Black
black .

# Linting com Ruff
ruff check --fix

# Pre-commit hooks
pre-commit run --all-files
```

## 📁 Estrutura de Arquivos

```
docs/
├── INDEX.md              # Este arquivo - Índice da documentação
├── README.md             # Documentação principal do sistema
├── DEVELOPER_GUIDE.md    # Guia técnico para desenvolvedores
└── ARCHITECTURE.md       # Arquitetura técnica detalhada
```

## 🔗 Links Externos

### **Documentação Oficial**
- [Django 5.2](https://docs.djangoproject.com/en/5.2/)
- [Django Channels](https://channels.readthedocs.io/)
- [PostgreSQL](https://www.postgresql.org/docs/)

### **Ferramentas Frontend**
- [Bootstrap 5](https://getbootstrap.com/docs/5.0/)
- [Chart.js](https://www.chartjs.org/docs/)
- [Leaflet.js](https://leafletjs.com/reference.html)

### **Ferramentas de Desenvolvimento**
- [Ruff](https://docs.astral.sh/ruff/)
- [Black](https://black.readthedocs.io/)
- [Pre-commit](https://pre-commit.com/)

## 📞 Suporte

### **Equipe de Desenvolvimento**
- **Desenvolvedor Principal**: Luciano
- **Email**: lucianolrv@gmail.com
- **Suporte**: suporte@fidelizamax.app.br

### **Canais de Suporte**
- Sistema de tickets interno
- Chat em tempo real
- Email de suporte
- Documentação técnica

## 📈 Status do Projeto

- **Versão**: 1.0.0
- **Status**: Em Produção
- **Última Atualização**: Dezembro 2024
- **Ambiente**: sistema.fidelizamax.app.br

---

## 🎯 Como Usar Esta Documentação

### **Para Novos Desenvolvedores**
1. Comece pelo [README.md](./README.md) para entender o sistema
2. Leia o [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md) para configuração
3. Consulte o [ARCHITECTURE.md](./ARCHITECTURE.md) para entender a estrutura

### **Para Desenvolvedores Experientes**
1. Use o [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md) como referência rápida
2. Consulte o [ARCHITECTURE.md](./ARCHITECTURE.md) para padrões e decisões
3. Use o [README.md](./README.md) para configurações de produção

### **Para DevOps/Infraestrutura**
1. Foque no [README.md](./README.md) para configurações de produção
2. Use o [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md) para scripts de deploy
3. Consulte o [ARCHITECTURE.md](./ARCHITECTURE.md) para monitoramento

---

**📚 Documentação criada para facilitar o desenvolvimento e manutenção do SisAps**  
**🔄 Mantenha esta documentação atualizada conforme o sistema evolui**

