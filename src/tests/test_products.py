import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from ..main import app
from ..database import Base
from ..services import create_user
from ..schemas import UserCreate

# Configuração do banco de dados de teste (SQLite em memória)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar tabelas de teste
Base.metadata.create_all(bind=engine)

# Override da dependência get_db
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Aplicar override
from ..database import get_db as original_get_db
app.dependency_overrides[original_get_db] = override_get_db

client = TestClient(app)

# Token para testes (será definido no conftest.py ou fixture)
auth_token = None

def setup_test_user():
    """Cria usuário de teste e retorna token"""
    global auth_token

    # Criar gerente para testes
    user_data = UserCreate(
        nome="Gerente Teste",
        email="gerente@test.com",
        perfil="gerente",
        senha="123456"
    )

    db = next(get_db())
    try:
        create_user(db, user_data)
    except:
        pass  # Usuário já existe

    # Fazer login
    response = client.post("/auth/login", json={
        "email": "gerente@test.com",
        "senha": "123456"
    })
    auth_token = response.json()["access_token"]

def get_auth_headers():
    """Retorna headers com token de autenticação"""
    return {"Authorization": f"Bearer {auth_token}"}

def test_create_product():
    """Testa criação de produto"""
    setup_test_user()

    product_data = {
        "nome": "Produto Teste",
        "codigo_barras": "123456789",
        "preco": 10.50,
        "estoque": 100.0
    }

    response = client.post(
        "/produtos/",
        json=product_data,
        headers=get_auth_headers()
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == product_data["nome"]
    assert data["preco"] == product_data["preco"]
    assert data["estoque"] == product_data["estoque"]

def test_list_products():
    """Testa listagem de produtos"""
    response = client.get("/produtos/", headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_product_by_id():
    """Testa busca de produto por ID"""
    # Primeiro criar um produto
    product_data = {
        "nome": "Produto Busca",
        "codigo_barras": "987654321",
        "preco": 25.00,
        "estoque": 50.0
    }

    create_response = client.post(
        "/produtos/",
        json=product_data,
        headers=get_auth_headers()
    )
    product_id = create_response.json()["id"]

    # Buscar produto
    response = client.get(f"/produtos/{product_id}", headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["nome"] == product_data["nome"]

def test_update_product():
    """Testa atualização de produto"""
    # Criar produto
    product_data = {
        "nome": "Produto Update",
        "preco": 15.00,
        "estoque": 75.0
    }

    create_response = client.post(
        "/produtos/",
        json=product_data,
        headers=get_auth_headers()
    )
    product_id = create_response.json()["id"]

    # Atualizar
    update_data = {
        "nome": "Produto Atualizado",
        "preco": 20.00
    }

    response = client.put(
        f"/produtos/{product_id}",
        json=update_data,
        headers=get_auth_headers()
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == update_data["nome"]
    assert data["preco"] == update_data["preco"]

def test_delete_product():
    """Testa exclusão de produto"""
    # Criar produto
    product_data = {
        "nome": "Produto Delete",
        "preco": 5.00,
        "estoque": 10.0
    }

    create_response = client.post(
        "/produtos/",
        json=product_data,
        headers=get_auth_headers()
    )
    product_id = create_response.json()["id"]

    # Deletar
    response = client.delete(f"/produtos/{product_id}", headers=get_auth_headers())
    assert response.status_code == 200

    # Verificar se foi desativado (não deve aparecer na listagem)
    list_response = client.get("/produtos/", headers=get_auth_headers())
    products = list_response.json()
    product_ids = [p["id"] for p in products]
    assert product_id not in product_ids

def test_add_stock():
    """Testa adição de estoque"""
    # Criar produto
    product_data = {
        "nome": "Produto Estoque",
        "preco": 12.00,
        "estoque": 20.0
    }

    create_response = client.post(
        "/produtos/",
        json=product_data,
        headers=get_auth_headers()
    )
    product_id = create_response.json()["id"]

    # Adicionar estoque
    stock_data = [{"produto_id": product_id, "quantidade": 30.0}]

    response = client.post(
        "/produtos/estoque/entrada",
        json=stock_data,
        headers=get_auth_headers()
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["estoque"] == 50.0  # 20 + 30
