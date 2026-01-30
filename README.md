# Django Hexagonal Architecture Template

Template Django production-grade com arquitetura hexagonal, autenticação via cookies HttpOnly JWT, e integração com Celery.

## Arquitetura

```
src/
├── domain/          # Entidades puras, sem dependências externas
├── application/     # Casos de uso, DTOs, ports
├── infrastructure/  # Django, Celery, adapters
└── interface/       # API controllers, CLI
```

### Princípios

1. **Domain Layer**: Zero dependências externas (só Python stdlib)
2. **Application Layer**: Orquestra casos de uso, define ports
3. **Infrastructure Layer**: Django vive aqui como adaptador
4. **Interface Layer**: Entry points (API, CLI)

## Quick Start

### Pré-requisitos

- Python 3.11+
- PDM
- PostgreSQL (ou SQLite para dev)
- Redis (para Celery)

# Clone o repositório
git clone https://github.com/jonatasperaza/DjangoTemplate.git
cd DjangoTemplate

# Instale dependências
pdm install

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações

# Execute migrações
pdm run migrate

# Inicie o servidor
pdm run dev
```

### Comandos Disponíveis

```bash
pdm run dev           # Servidor de desenvolvimento
pdm run migrate       # Aplicar migrações
pdm run makemigrations # Criar migrações
pdm run shell         # Django shell
pdm run test          # Rodar testes
pdm run test-cov      # Testes com coverage
pdm run lint          # Verificar código
pdm run lint-fix      # Corrigir problemas de lint
pdm run typecheck     # Verificar tipos
pdm run celery        # Iniciar worker Celery
```

## Autenticação

Este template usa **HttpOnly Cookies com JWT** para autenticação:

- `access_token`: Cookie HttpOnly, expira em 15 minutos
- `refresh_token`: Cookie HttpOnly, expira em 7 dias

### Endpoints

```
POST /api/auth/login     # Login com email/senha
POST /api/auth/logout    # Logout (revoga tokens)
POST /api/auth/refresh   # Renova access token
```

## Estrutura de Diretórios

```
backend/
├── src/
│   ├── domain/                    # Zero dependências externas
│   │   ├── entities/              # Entidades de domínio
│   │   ├── repositories/          # Interfaces (Ports)
│   │   ├── services/              # Domain services
│   │   └── exceptions.py          # Exceções de domínio
│   │
│   ├── application/               # Casos de uso
│   │   ├── ports/                 # Interfaces de infraestrutura
│   │   ├── services/              # Application services
│   │   ├── dto/                   # Data Transfer Objects
│   │   └── events/                # Domain events
│   │
│   ├── infrastructure/            # Implementações
│   │   ├── django/                # Django config e models
│   │   ├── persistence/           # Repository implementations
│   │   ├── security/              # Auth adapters
│   │   ├── messaging/             # Celery
│   │   └── web/                   # Middleware, serializers
│   │
│   └── interface/                 # Entry points
│       ├── api/                   # REST API views
│       └── cli/                   # Management commands
│
├── tests/
│   ├── unit/                      # Testes unitários (70%)
│   ├── integration/               # Testes de integração (20%)
│   └── e2e/                       # Testes end-to-end (10%)
│
├── pyproject.toml                 # PDM config
├── manage.py
└── README.md
```

## Testes

### Pirâmide de Testes

- **Unit (70%)**: Testes de domínio, rápidos, sem DB
- **Integration (20%)**: Testes de repositories com DB
- **E2E (10%)**: Testes de API completos

```bash
# Todos os testes
pdm run test

# Com coverage
pdm run test-cov

# Apenas domínio
pdm run pytest tests/unit/domain -v
```

## Configuração

### Variáveis de Ambiente

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://user:pass@localhost:5432/dbname

# Redis/Celery
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_ACCESS_TOKEN_LIFETIME=900      # 15 minutos
JWT_REFRESH_TOKEN_LIFETIME=604800  # 7 dias
```

## Licença

MIT
