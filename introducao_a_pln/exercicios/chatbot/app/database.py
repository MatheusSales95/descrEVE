import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Carrega as variáveis do .env (que está na pasta pai)
load_dotenv()

# 2. Monta a URL de conexão do PostgreSQL
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# 3. Cria a "Engrenagem" do banco
engine = create_engine(DB_URL)

# 4. Cria a fábrica de sessões (cada request do usuário ganha uma sessão)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. A classe base para criar os modelos
Base = declarative_base()

# Função para pegar o banco de dados (Dependency Injection)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
