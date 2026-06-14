"""
Configuração da conexão com o banco de dados MySQL via SQLAlchemy.

- `engine`: objeto que gerencia o pool de conexões com o banco.
- `SessionLocal`: fábrica de sessões. Cada requisição da API deve usar
  uma sessão própria, aberta e fechada via dependência `get_db`.
- `Base`: classe base da qual todos os models (tabelas) herdam.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# pool_pre_ping evita erros de "MySQL server has gone away" em conexões
# ociosas; pool_recycle reconecta periodicamente para evitar timeouts do MySQL.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """
    Dependência do FastAPI que fornece uma sessão de banco de dados
    por requisição e garante que ela seja sempre encerrada,
    mesmo em caso de erro.

    Uso em um router:

        @router.get("/exemplo")
        def exemplo(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
