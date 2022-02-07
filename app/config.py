from pydantic import BaseSettings

class Settings(BaseSettings):
    db_host: str
    db_port: str
    db_pass: str
    db_name: str
    db_user: str
    secret_key: str
    algorithm: str
    access_token_ttl: int

    class Config:
        env_file = ".env"

settings = Settings()