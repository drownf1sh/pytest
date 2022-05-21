import sys

# from app.main.configuration.vault_vars_config import BIGQUERY_CREDENTIAL
# from app.main.configuration.vault_vars_config import SPANNER_CREDENTIAL
# from app.main.database.bigquery import create_bigquery_client
from app.main.database.mongodb import PymongoConnection
from app.main.database.rediscache import create_redis_connection

# from app.main.database.spanner import create_spanner_client
from app.main.util.test_connection import create_fake_redis_connection

"""
Initialize external pymongo connection
Add or get db names from db_list in global_vars.py
"""
if "pytest" in sys.modules:
    glb_db_conn = PymongoConnection("test_db", "test_col")
    rec_db_conn = glb_db_conn
    crm_db_conn = glb_db_conn
    sch_db_conn = glb_db_conn
else:
    glb_db_conn = PymongoConnection("mongo_glb")
    rec_db_conn = PymongoConnection("mongo_rec")
    crm_db_conn = PymongoConnection("mongo_crm")
    sch_db_conn = PymongoConnection("mongo_sch")

"""
Initialize external google bigquery connection
"""
# bigquery_client = create_bigquery_client(credential_path=BIGQUERY_CREDENTIAL)

"""
Initialize external google spanner connection
"""
# spanner_client = create_spanner_client(credential_path=SPANNER_CREDENTIAL)


"""
Initialize redis sentinel connection
"""
if "pytest" in sys.modules:
    redis_client = create_fake_redis_connection()
else:
    redis_client = create_redis_connection()
