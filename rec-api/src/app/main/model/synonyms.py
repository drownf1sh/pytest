from app.main.database.mongodb import db


class SynonymsWords(db.Document):
    """
    Define data object for synonyms words
    """

    # Meta variables
    meta = {"collection": "recSynonymsDictionary"}

    # Document variables
    search_word = db.StringField(required=True)
    synonyms_dict = db.DictField()
