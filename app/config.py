import os


class Config(object):
    SECRET_KEY = 'fbb59d4ed85248ed8eba0cf085a62633'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
                              os.path.abspath(
                                  os.path.join(os.path.dirname(__file__), 'models', 'main.db')
                              )
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True


class DevelopConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_dict = {
    "dev": DevelopConfig,
    "pro": ProductionConfig
}