from app.main.database.mongodb import db


class WordVector(db.Document):
    """
    Define data object for word embedding
    """

    # Meta variables
    meta = {"collection": "recWordEmbedding"}

    # Document variables
    word = db.StringField(required=True)
    vector = db.ListField()


class NgramWordVector(db.Document):
    """
    Define data object for ngram word embedding
    """

    # Meta variables
    meta = {"collection": "recWordEmbeddingNgram"}

    # Document variables
    word = db.StringField(required=True)
    vector = db.ListField()


class PhraseDict(db.Document):
    """
    Define data object for phrasing dictionary
    """

    # Meta variables
    meta = {"collection": "recPhraseDictionary"}

    # Document variables
    ngram = db.StringField(required=True)
