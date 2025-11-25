from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Interior Space Optimization"
    API_V1_STR: str = "/api/v1"
    
    # Firebase Credential Path (to be filled later)
    FIREBASE_CREDENTIALS_PATH: str = "serviceAccountKey.json"

    class Config:
        case_sensitive = True

settings = Settings()
