"""
config.py — Configuração central do aplicativo.

ESTE ARQUIVO APLICA O PRINCÍPIO SOLID 'D' (Dependency Inversion):
- As outras partes do código NÃO leem variáveis de ambiente diretamente.
- Elas dependem desta classe 'Settings' (uma abstração).
- Se amanhã quisermos ler config de outro lugar (ex: AWS Secrets Manager),
  só mudamos aqui, sem tocar no resto do código.

Pydantic valida automaticamente os tipos (str, int) e valores obrigatórios.
"""
from functools import lru_cache  # Cache: a config é lida uma única vez

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Define todas as configurações do app.
    Pydantic lê automaticamente do arquivo .env e valida os tipos.
    """

    # model_config diz ao Pydantic:
    #  - ler de um arquivo chamado ".env"
    #  - ignorar variáveis que não estão definidas aqui
    #  - fazer case-insensitive (FLASK_ENV == flask_env)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Campos obrigatórios/opcionais ---
    # Field(..., description=...) deixa a config autodocumentada
    flask_env: str = Field(default="development", description="Ambiente de execução")

    jwt_secret: str = Field(
        ...,  # os 3 pontos = obrigatório (vai dar erro se faltar no .env)
        description="Chave secreta para assinar tokens JWT",
    )
    jwt_expire_hours: int = Field(
        default=24,
        ge=1,  # ge = greater or equal (mínimo 1 hora)
        description="Tempo de expiração do token em horas",
    )

    database_url: str = Field(
        default="sqlite:///finsmart.db",
        description="URL de conexão com o banco de dados",
    )

    # Propriedade derivada: "is_production" calculada a partir de flask_env
    @property
    def is_production(self) -> bool:
        return self.flask_env == "production"


# @lru_cache() faz a função rodar SÓ UMA VEZ e guarda o resultado.
# Como Settings é imutável durante a execução, não precisa recriar toda hora.
@lru_cache()
def get_settings() -> Settings:
    """Retorna a instância única de Settings (padrão Singleton implícito)."""
    return Settings()
