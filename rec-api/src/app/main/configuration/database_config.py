from app.main.configuration.vault_vars_config import (
    GLB_DB_URI,
    REC_DB_URI,
    CRM_DB_URI,
    SCH_DB_URI,
)

"""
Ths part is to map db name with its uri
"""
db_list = {
    "mongo_glb": GLB_DB_URI,
    "mongo_rec": REC_DB_URI,
    "mongo_crm": CRM_DB_URI,
    "mongo_sch": SCH_DB_URI,
    "test_db": "mongodb://localhost/test",
}
