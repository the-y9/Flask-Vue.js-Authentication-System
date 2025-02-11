class Config(object):
    DEBUG = False
    TESTING = False
    

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///g.db'
    SECRET_KEY = "forty2"
    SECURITY_PASSWORD_SALT = "42salty"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'