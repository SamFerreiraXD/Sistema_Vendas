"""
Módulo de configurações da aplicação.

Usa Pydantic Settings para ler variáveis de ambiente de forma tipada e segura.
Todas as outras partes do sistema devem importar o objeto `settings` deste
arquivo em vez de usar os.environ diretamente — isso garante validação
e centraliza a configuração em um único lugar.

Nota sobre extra='ignore':
- A configuração `extra='ignore'` faz com que Pydantic ignore variáveis de 
  ambiente que não estão definidas na classe Settings. Isso é necessário para
  permitir variáveis específicas do Docker (como DB_ROOT_PASSWORD) que não são
  usadas pela aplicação FastAPI, mas são necessárias para configurar os
  containers.
"""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Aplicação
    APP_NAME: str = "ERP PDV"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Banco de dados
    DB_HOST: str
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DATABASE_URL: str

    # Segurança / JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS — string separada por vírgulas no .env
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignora variáveis de ambiente não mapeadas (ex: DB_ROOT_PASSWORD para Docker)
    )

    @property
    def cors_origins(self) -> List[str]:
        """Transforma a string ALLOWED_ORIGINS em uma lista de origens."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


# Instância única (singleton) usada em toda a aplicação
settings = Settings()
