import os

import hvac

from ..util.decryption import PRIVATE_KEY_PATH
from ..util.decryption import RsaUtil
from ..util.environment_variables import APP_ENV
from ..util.environment_variables import APP_PROJ
from ..util.environment_variables import APP_VERSION
from ..util.environment_variables import APP_NAME
from ..util.environment_variables import VAULT_ADDR
from ..util.environment_variables import VAULT_ENGINE
from ..util.environment_variables import VAULT_TOKEN

TWO = 2
TWO_HUNDRED = 200
TWENTY_THOUSAND = 20000
FIVE_THOUSAND = 5000


if not APP_ENV:
    REDIS_MODE = os.getenv("REDIS_MODE")
    REC_DB_URI = os.getenv("REC_DB_URI")
    PROFANITY_SCREEN_API = os.getenv("PROFANITY_SCREEN_API")
    STORE_NAME_DUP_CHECK_API = os.getenv("STORE_NAME_DUP_CHECK_API")
    GLB_DB_URI = os.getenv("GLB_DB_URI")
    CRM_DB_URI = os.getenv("CRM_DB_URI")
    SCH_DB_URI = os.getenv("SCH_DB_URI")
    REDIS_HOST_STR = os.getenv("REDIS_HOST_STR")
    REDIS_PORT = os.getenv("REDIS_PORT")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    REDIS_DATABASE = os.getenv("REDIS_DATABASE")
    REDIS_MASTER = os.getenv("REDIS_MASTER")
    # RECENTLY_VIEW_DB = os.getenv("RECENTLY_VIEW_DB")
    PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC")
    # BIGQUERY_CREDENTIAL = os.getenv("BIGQUERY_CREDENTIAL")
    # SPANNER_CREDENTIAL = os.getenv("SPANNER_CREDENTIAL")
    PUBSUB_CREDENTIAL = os.getenv("PUBSUB_CREDENTIAL")
    # SPANNER_DATABASE_ID = os.getenv("SPANNER_DATABASE_ID")
    # SPANNER_INSTANCE_ID = os.getenv("SPANNER_INSTANCE_ID")

    # MongoDB Connection config in local, refer to pymongo mongo_client.py for detail
    MAX_POOL_SIZE = TWO_HUNDRED
    MIN_POOL_SIZE = TWO
    MAX_IDLE_TIME_MS = TWENTY_THOUSAND
    SOCKET_TIMEOUT_MS = TWENTY_THOUSAND
    CONNECT_TIMEOUT_MS = TWENTY_THOUSAND
    SERVER_SELECTION_TIMEOUT_MS = FIVE_THOUSAND

else:
    # Initialize Vault client to read secret from vault
    client = hvac.Client(
        url="https://" + VAULT_ADDR + ":8200", token=VAULT_TOKEN, verify=False
    )

    # Read secrets from vault
    read_secret_result = client.secrets.kv.v1.read_secret(
        path="general",
        mount_point=VAULT_ENGINE,
    )

    secret_data = read_secret_result["data"]
    rsaUtil = None
    for key, value in secret_data.items():
        if type(value) == str and value.startswith("enc(") and value.endswith(")"):
            if rsaUtil is None and PRIVATE_KEY_PATH:
                rsaUtil = RsaUtil(PRIVATE_KEY_PATH)
            secret_data[key] = rsaUtil.decrypt_by_private_key(value)

    PROFANITY_SCREEN_API = secret_data["profanity_screen_api"]
    STORE_NAME_DUP_CHECK_API = secret_data["store_name_dup_check"]

    REC_DB_SECRET = {
        "rec_uri": secret_data["rec.mongodb.uri"],
        "glb_uri": secret_data["glb.mongodb.uri"],
        "crm_uri": secret_data["crm.mongodb.uri"],
        "sch_uri": secret_data["sch.mongodb.uri"],
        "username": secret_data["rec.mongodb.username"],
        "password": secret_data["rec.mongodb.password"],
        # Mongo shard username, if not present using rec.mongodb.username
        "shard_username": secret_data["rec.mongodb.shard.username"]
        if "rec.mongodb.shard.username" in secret_data
        else secret_data["rec.mongodb.username"],
        # Mongo shard password, if not present using rec.mongodb.password
        "shard_password": secret_data["rec.mongodb.shard.password"]
        if "rec.mongodb.shard.password" in secret_data
        else secret_data["rec.mongodb.password"],
    }

    REC_DB_URI = (
        "mongodb://"
        + REC_DB_SECRET["shard_username"]
        + ":"
        + REC_DB_SECRET["shard_password"]
        + "@"
        + REC_DB_SECRET["rec_uri"]
    )

    GLB_DB_URI = (
        "mongodb://"
        + REC_DB_SECRET["username"]
        + ":"
        + REC_DB_SECRET["password"]
        + "@"
        + REC_DB_SECRET["glb_uri"]
    )

    CRM_DB_URI = (
        "mongodb://"
        + REC_DB_SECRET["username"]
        + ":"
        + REC_DB_SECRET["password"]
        + "@"
        + REC_DB_SECRET["crm_uri"]
    )

    SCH_DB_URI = (
        "mongodb://"
        + REC_DB_SECRET["username"]
        + ":"
        + REC_DB_SECRET["password"]
        + "@"
        + REC_DB_SECRET["sch_uri"]
    )

    REDIS_SECRET = {
        "mode": secret_data["redis.mode"],
        "host": secret_data["redis.host.str"],
        "port": secret_data["redis.port"],
        "password": secret_data["redis.password"],
        "database": secret_data["redis.database"],
        "master": secret_data["redis.master-name"],
    }
    REDIS_MODE = REDIS_SECRET["mode"]

    REDIS_HOST_STR = REDIS_SECRET["host"]
    REDIS_PORT = REDIS_SECRET["port"]
    REDIS_PASSWORD = REDIS_SECRET["password"]
    REDIS_DATABASE = REDIS_SECRET["database"]
    REDIS_MASTER = REDIS_SECRET["master"]

    # RECENTLY_VIEW_DB = secret_data["recently_view_db"]

    PUBSUB_TOPIC = secret_data["pubsub_topic"]

    PUBSUB_CREDENTIAL = secret_data["pubsub_credential_path"]

    # BIGQUERY_CREDENTIAL = secret_data["bigquery_credential_path"]
    # SPANNER_CREDENTIAL = secret_data["spanner_credential_path"]
    # SPANNER_DATABASE_ID = secret_data["spanner_database_id"]
    # SPANNER_INSTANCE_ID = secret_data["spanner_instance_id"]

    # MongoDB Connection config in VAULT, refer to pymongo mongo_client.py for detail
    # one-liner ternary operator: some_expression if condition else other_expression
    # If the secret key exist then fetch Vault value, otherwise use the default value
    MAX_POOL_SIZE = (
        secret_data["rec.mongodb.maxPoolSize"]
        if "rec.mongodb.maxPoolSize" in secret_data
        else TWO_HUNDRED
    )
    MIN_POOL_SIZE = (
        secret_data["rec.mongodb.minPoolSize"]
        if "rec.mongodb.minPoolSize" in secret_data
        else TWO
    )
    MAX_IDLE_TIME_MS = (
        secret_data["rec.mongodb.maxIdleTimeMS"]
        if "rec.mongodb.maxIdleTimeMS" in secret_data
        else TWENTY_THOUSAND
    )
    SOCKET_TIMEOUT_MS = (
        secret_data["rec.mongodb.socketTimeoutMS"]
        if "rec.mongodb.socketTimeoutMS" in secret_data
        else TWENTY_THOUSAND
    )
    CONNECT_TIMEOUT_MS = (
        secret_data["rec.mongodb.connectTimeoutMS"]
        if "rec.mongodb.connectTimeoutMS" in secret_data
        else TWENTY_THOUSAND
    )
    SERVER_SELECTION_TIMEOUT_MS = (
        secret_data["rec.mongodb.serverSelectionTimeoutMS"]
        if "rec.mongodb.serverSelectionTimeoutMS" in secret_data
        else FIVE_THOUSAND
    )
