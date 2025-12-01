# PDV Web - Sistema de Ponto de Venda

Sistema de ponto de venda web para pequenos lojistas, desenvolvido com FastAPI, SQLAlchemy e PostgreSQL.

## Funcionalidades

### MVP Implementado
- ✅ Autenticação (Vendedor/Gerente)
- ✅ Cadastro de produtos
- ✅ Sistema de vendas
- ✅ Controle de estoque
- ✅ Histórico de vendas
- ✅ Relatórios básicos

### Perfis de Usuário
- **Vendedor**: Pode vender, ver produtos e suas vendas
- **Gerente**: Acesso total + cadastrar produtos e ver relatórios

## Tecnologias
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Autenticação**: JWT
- **Validação**: Pydantic
- **Testes**: Pytest
- **Container**: Docker

## Instalação e Execução

### 1. Pré-requisitos
- Python 3.12
- PostgreSQL
- Poetry (gerenciador de dependências)

### 2. Clonagem e Dependências
```bash
git clone <repository>
cd pdv-limaitservices

# Instalar dependências
poetry install
```

### 3. Configuração do Banco
```bash
# Criar banco de dados PostgreSQL
createdb pdv_db

# Configurar variáveis de ambiente
cp env.example .env
# Edite o .env com suas configurações
```

### 4. Executar Migrações
```bash
# As tabelas são criadas automaticamente pelo SQLAlchemy
# Mas você pode usar Alembic futuramente para migrations
```

### 5. Executar Aplicação
```bash
# Ativar ambiente virtual
poetry shell

# Executar servidor
uvicorn src.main:app --reload
```

A API estará disponível em: http://localhost:8000

### 6. Documentação da API
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Docker

### Construir e executar com Docker
```bash
# Construir imagem
docker build -t pdv-web .

# Executar container
docker run -p 8000:8000 --env-file .env pdv-web
```

## Testes

### Executar Testes
```bash
# Executar todos os testes
poetry run pytest

# Executar testes específicos
poetry run pytest src/tests/test_auth.py

# Com cobertura
poetry run pytest --cov=src
```

## Estrutura do Projeto
```
src/
├── main.py              # Aplicação FastAPI principal
├── database.py          # Configuração do banco de dados
├── models/              # Modelos SQLAlchemy
│   ├── user.py
│   ├── product.py
│   ├── sale.py
│   └── sale_item.py
├── schemas/             # Schemas Pydantic
│   ├── user.py
│   ├── product.py
│   ├── sale.py
│   └── report.py
├── routes/              # Endpoints da API
│   ├── auth.py
│   ├── products.py
│   ├── sales.py
│   └── reports.py
├── services/            # Lógica de negócio
│   ├── auth_service.py
│   ├── product_service.py
│   ├── sale_service.py
│   └── report_service.py
└── tests/               # Testes
    ├── test_auth.py
    └── test_products.py
```

## API Endpoints

### Autenticação
- `POST /auth/login` - Login
- `POST /auth/logout` - Logout
- `POST /auth/register` - Registrar usuário (dev)

### Produtos
- `GET /produtos/` - Listar produtos
- `POST /produtos/` - Criar produto (gerente)
- `PUT /produtos/{id}` - Atualizar produto (gerente)
- `DELETE /produtos/{id}` - Desativar produto (gerente)
- `POST /produtos/estoque/entrada` - Adicionar estoque (gerente)

### Vendas
- `POST /vendas/` - Criar venda
- `GET /vendas/` - Listar vendas
- `GET /vendas/{id}` - Detalhes da venda

### Relatórios
- `GET /relatorios/vendas-dia` - Relatório do dia (gerente)
- `GET /relatorios/vendas-periodo` - Relatório por período (gerente)

## Desenvolvimento

### Criar usuário inicial
```bash
# Via API (desenvolvimento)
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Gerente Principal",
    "email": "gerente@loja.com",
    "perfil": "gerente",
    "senha": "123456"
  }'
```

### Próximas Iterações
- Cancelamento de vendas
- Controle de caixa
- Impressão de comprovantes
- Integração fiscal
- Cliente cadastrado
- Descontos e promoções

## Licença
MIT
