import os

# Get the absolute path of the current directory
current_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration (common settings)"""
    SECRET_KEY = "24F2003755"   # for session management
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class LocalDevelopmentConfig(Config):
    """Configuration for local development"""
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(current_dir, "database_project.sqlite3")
    DEBUG = True
