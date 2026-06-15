# ERP/PDV Genérico — Backend

Sistema de vendas (ERP/PDV) genérico, construído em **Python + FastAPI + MySQL**,
projetado para ser adaptado a diferentes tipos de negócio (lojas de roupas,
mercados, papelarias, lojas de informática, etc).

## Módulos Implementados

### ✅ Módulo 0 — Configuração inicial
"Esqueleto" do projeto: configuração, conexão com banco, segurança, logging, Docker e Alembic.

### ✅ Módulo 1 — Autenticação e Usuários
- Registro e login com JWT (access_token 1h + refresh_token 7 dias)
- Sistema de roles e permissões baseado em JSON
- Recuperação de senha por email (simulado em log)
- Endpoints protegidos com autenticação

### ✅ Módulo 2 — Produtos e Categorias
- CRUD de categorias e produtos
- Estoque com histórico de movimentação (auditoria)
- Validação de SKU e código de barras únicos
- Soft delete para preservar histórico
- Busca e filtros de produtos

### ✅ Módulo 3 — Clientes e Endereços
- CRUD de clientes (Pessoa Física e Jurídica)
- Múltiplos endereços por cliente
- Endereço principal (apenas um por cliente)
- CPF/CNPJ e email únicos
- Busca por nome, CPF/CNPJ, email e telefone
- Soft delete para clientes

## Pré-requisitos

- Python 3.12+
- Docker e Docker Compose (recomendado)
- MySQL 8 (caso não use Docker)

## Como executar com Docker (recomendado)

1. Copie o arquivo de variáveis de ambiente:

   ```bash
   cp .env.example .env
   ```

2. Edite o `.env` e defina valores reais para `SECRET_KEY`, `DB_PASSWORD`,
   `DB_ROOT_PASSWORD`, etc.

3. Suba os containers:

   ```bash
   docker compose up -d --build
   ```

4. Acesse a documentação automática da API:

   - Swagger UI: http://SEU_SERVIDOR:8000/docs
   - ReDoc: http://SEU_SERVIDOR:8000/redoc
   - Health check: http://SEU_SERVIDOR:8000/health

## Como executar localmente sem Docker

1. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/Mac
   .venv\Scripts\activate       # Windows
   ```

2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Copie o `.env.example` para `.env` e ajuste os valores (use um MySQL
   já em execução).

4. Execute em modo de desenvolvimento:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Migrações de banco (Alembic)

Após clonar o repositório, gere e aplique as migrações:

```bash
alembic revision --autogenerate -m "Módulos 0, 1 e 2 - Base da aplicação"
alembic upgrade head
```

Depois, execute o seed de dados iniciais (cria roles padrão e usuário admin):

```bash
python -c "from app.initial_data import init_db; init_db()"
```

**Usuário admin padrão:**
- Email: `admin@sistema-vendas.local`
- Senha: `Admin@123`

## Estrutura de pastas

```
Sistema_Vendas/
├── app/
│   ├── main.py            # ponto de entrada FastAPI
│   ├── core/               # config, database, security, logging
│   ├── models/             # tabelas (SQLAlchemy)
│   ├── schemas/            # validação de entrada/saída (Pydantic)
│   ├── repositories/        # acesso ao banco
│   ├── services/             # regras de negócio
│   ├── routers/              # endpoints da API
│   ├── dependencies/          # autenticação, permissões
│   └── utils/
├── alembic/                  # migrações do banco
├── logs/                       # logs da aplicação (gerados em runtime)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Próximos módulos

**Módulo 4 — Pedidos e Itens de Pedido**
**Módulo 5 — Relatórios e Analytics**
**Módulo 6 — Integrações e Webhooks**
2. Produtos e categorias
3. Estoque
4. Clientes
5. Vendas (PDV)
6. Relatórios
7. Dashboard
8. Frontend
9. Deploy em VPS
