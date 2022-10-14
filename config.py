import os

class Config:
    DEBUG = False
    DEVELOPMENT = False
    CRUX_API_KEY = os.getenv("CRUX_API_KEY", "default")

class ProductionConfig(Config):
    pass

class StagingConfig(Config):
    DEBUG = True

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True