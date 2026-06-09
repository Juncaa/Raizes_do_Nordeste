import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Banco escolhido: SQLite por ser mais prático e não precisa instalar adicionais.

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./raizes.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def pegar_banco():
    banco = SessionLocal()
    try:
        yield banco
    finally:
        banco.close()
