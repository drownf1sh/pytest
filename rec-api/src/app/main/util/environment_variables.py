import os

VAULT_ENGINE = os.environ.get("VAULT_ENGINE") or ""
VAULT_ADDR = os.environ.get("VAULT_ADDR") or ""
VAULT_TOKEN = os.environ.get("VAULT_TOKEN") or ""

APP_PROJ = os.environ.get("APP_PROJ") or ""
APP_ENV = os.environ.get("APP_ENV") or ""
APP_NAME = os.environ.get("APP_NAME") or ""
APP_VERSION = os.environ.get("APP_VERSION") or ""
