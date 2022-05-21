from app.main.database.mongodb import db


class PersonalizedScores(db.Document):
    """
    Define data object for crm personalized_scores collection
    """

    # Meta variables.
    meta = {"db_alias": "crm_db", "collection": "personalized_scores"}

    # Document variables.
    customer_email = db.StringField()
    ACM_FLG = db.StringField()
    BULK_FLAG = db.StringField()
    CAN_VALID = db.StringField()
    CA_REDUCED_FREQ_FLG = db.StringField()
    CLASSROOM_FLAG = db.StringField()
    COUPON_EXP = db.StringField()
    COUPON_TYPE = db.StringField()
    CRM_INGEST_DATE = db.StringField()
    CUSTOMER_FIELD1 = db.StringField()
    CUSTOMER_FIELD10 = db.StringField()
    CUSTOMER_FIELD2 = db.StringField()
    CUSTOMER_FIELD3 = db.StringField()
    CUSTOMER_FIELD5 = db.StringField()
    CUSTOMER_FIELD6 = db.StringField()
    CUSTOMER_FIELD7 = db.StringField()
    CUSTOMER_FIELD8 = db.StringField()
    CUSTOMER_FIELD9 = db.StringField()
    CUSTOMER_ZIP = db.IntField()
    CUSTOM_FRAME_PURCH = db.StringField()
    ECOM_PURCH_DATE = db.StringField()
    EDUCATION_FLAG = db.StringField()
    LOYALTY_ID = db.StringField()
    MIKPRO_FLAG = db.StringField()
    MILITARY_FLG = db.StringField()
    OFFER_DURATION = db.IntField()
    OFFER_ID = db.StringField()
    PREFERRED_STORE = db.IntField()
    PRODUCT_SEGMENT = db.StringField()
    PROP_SCORE_1 = db.StringField()
    PROP_SCORE_2 = db.StringField()
    PROP_SCORE_3 = db.StringField()
    PROP_SCORE_4 = db.StringField()
    PROP_SCORE_5 = db.StringField()
    QUE_VALID = db.StringField()
    RFM_SEGMENT = db.StringField()
    SENIOR_FLG = db.StringField()
    STORE_PURCH_DATE = db.StringField()
    TAX_EXEMPT_FLAG = db.StringField()
    TEACHER_FLG = db.StringField()
    US_REDUCED_FREQ_FLG = db.StringField()
    US_VALID = db.StringField()
