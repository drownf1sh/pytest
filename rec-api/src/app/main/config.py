from .configuration.vault_vars_config import *

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    MONGODB_SETTINGS = [
        {
            "alias": "default",
            "host": REC_DB_URI,
            "connect": False,
        },
        {
            "alias": "crm_db",
            "host": CRM_DB_URI,
            "connect": False,
        },
        {
            "alias": "sch_db",
            "host": SCH_DB_URI,
            "connect": False,
        },
    ]
    DEBUG = False


class LocalConfig(Config):
    DEBUG = True


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    DEBUG = True
    TESTING = True


class UnittestConfig(Config):
    DEBUG = True
    TESTING = True


class StagingConfig(Config):
    DEBUG = False


class ProductionConfig(Config):
    DEBUG = False


config_by_name = dict(
    local=LocalConfig,
    test=UnittestConfig,
    dev00=DevelopmentConfig,
    tst00=TestingConfig,
    tst01=StagingConfig,
    tst02=TestingConfig,
    stg=StagingConfig,
    prd=ProductionConfig,
)
