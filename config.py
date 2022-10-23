import os

class Config:
    DEBUG = False
    DEVELOPMENT = False
    CRUX_API_KEY = os.getenv("CRUX_API_KEY", "default")
    SECRET_KEY = os.getenv("SECRET_KEY", "default")

class ProductionConfig(Config):
    pass

class StagingConfig(Config):
    DEBUG = True

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True

# Set global variables
quota_reached = False
domain = None
filters = []
all_links = []
all_urls = []
urls_data = []