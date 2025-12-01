from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/pdv_db")

# Criar engine do SQLAlchemy
engine = create_engine(DATABASE_URL)

# Criar SessionLocal para gerenciar sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

# Dependência para obter sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
