import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..main import app
from ..services import create_user
from ..schemas import UserCreate
from fastapi.testclient import TestClient

# Configuração do banco de dados de teste (SQLite em memória)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    return create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    from ..database import get_db as original_get_db
    app.dependency_overrides[original_get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()

def test_register_user(client):
    """Testa registro de usuário"""
    user_data = {
        "nome": "João Vendedor",
        "email": "joao@test.com",
        "perfil": "vendedor",
        "senha": "123456"
    }

    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["nome"] == user_data["nome"]
    assert data["perfil"] == user_data["perfil"]
    assert "id" in data

def test_login_success(client):
    """Testa login bem-sucedido"""
    # Primeiro registrar usuário
    user_data = {
        "nome": "João Vendedor",
        "email": "joao@test.com",
        "perfil": "vendedor",
        "senha": "123456"
    }
    client.post("/auth/register", json=user_data)

    login_data = {
        "email": "joao@test.com",
        "senha": "123456"
    }

    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data

def test_login_invalid_credentials(client):
    """Testa login com credenciais inválidas"""
    # Registrar usuário
    user_data = {
        "nome": "João Vendedor",
        "email": "joao@test.com",
        "perfil": "vendedor",
        "senha": "123456"
    }
    client.post("/auth/register", json=user_data)

    login_data = {
        "email": "joao@test.com",
        "senha": "wrongpassword"
    }

    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Email ou senha incorretos" in response.json()["detail"]

def test_register_duplicate_email(client):
    """Testa registro com email duplicado"""
    # Registrar primeiro usuário
    user_data1 = {
        "nome": "João Vendedor",
        "email": "joao@test.com",
        "perfil": "vendedor",
        "senha": "123456"
    }
    client.post("/auth/register", json=user_data1)

    # Tentar registrar com mesmo email
    user_data2 = {
        "nome": "Maria Vendedora",
        "email": "joao@test.com",  # Mesmo email
        "perfil": "vendedor",
        "senha": "123456"
    }

    response = client.post("/auth/register", json=user_data2)
    assert response.status_code == 400
    assert "Email já cadastrado" in response.json()["detail"]

def test_register_invalid_profile(client):
    """Testa registro com perfil inválido"""
    user_data = {
        "nome": "Pedro Admin",
        "email": "pedro@test.com",
        "perfil": "admin",  # Perfil inválido
        "senha": "123456"
    }

    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400
    assert "Perfil deve ser" in response.json()["detail"]
