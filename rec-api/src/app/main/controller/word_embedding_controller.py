from flask_restplus import Namespace
from app.main.controller.controller import WordEmbeddingController
from app.main.service.word_embedding_service import (
    get_vectors_for_word_lists,
    get_vectors_for_ngram_word_lists,
    get_sentences_average_vectors,
    get_sentences_average_vectors_ngram,
    get_phrase_for_sentence,
)
import app.main.util.externalized_messages as messages
import app.main.util.controller_args as controller_args

api = Namespace("word_embedding", description="Word Embedding API")


@api.route("/word_vectors", methods=["Get"])
@api.param(name="words", description=messages.descriptions["words"], type=str)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.word_embedding_args["error_message"],
        example_value=messages.example_format["word_embedding_value"],
        success_str="return_word_vector_json",
    )
)
class WordEmbedding(WordEmbeddingController):
    def __init__(
        self,
        api,
        args_dict=controller_args.word_embedding_args,
        service=get_vectors_for_word_lists,
    ):
        WordEmbeddingController.__init__(self, args_dict, service)


@api.route("/ngram_word_vectors", methods=["Get"])
@api.param(name="words", description=messages.descriptions["words_ngram"], type=str)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.word_embedding_args["error_message"],
        example_value=messages.example_format["ngram_word_embedding_value"],
        success_str="return_word_vector_json",
    )
)
class NgramWordEmbedding(WordEmbeddingController):
    def __init__(
        self,
        api,
        args_dict=controller_args.word_embedding_args,
        service=get_vectors_for_ngram_word_lists,
    ):
        WordEmbeddingController.__init__(self, args_dict, service)


@api.route("/sentence_vector", methods=["Get"])
@api.param(name="sentence", description=messages.descriptions["sentence"], type=str)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.sentence_embedding_args["error_message"],
        example_value=messages.example_format["sentence_embedding_value"],
        success_str="return_sentence_vector",
    )
)
class SentenceVector(WordEmbeddingController):
    def __init__(
        self,
        api,
        args_dict=controller_args.sentence_embedding_args,
        service=get_sentences_average_vectors,
    ):
        WordEmbeddingController.__init__(self, args_dict, service)


@api.route("/ngram_sentence_vector", methods=["Get"])
@api.param(
    name="sentence", description=messages.descriptions["sentence_ngram"], type=str
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.sentence_embedding_args["error_message"],
        example_value=messages.example_format["sentence_embedding_value_ngram"],
        success_str="return_sentence_vector",
    )
)
class SentenceVectorNgram(WordEmbeddingController):
    def __init__(
        self,
        api,
        args_dict=controller_args.sentence_embedding_args,
        service=get_sentences_average_vectors_ngram,
    ):
        WordEmbeddingController.__init__(self, args_dict, service)


@api.route("/phrase", methods=["Get"])
@api.param(
    name="sentence", description=messages.descriptions["sentence_for_phrase"], type=str
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.sentence_embedding_args["error_message"],
        example_value=messages.example_format["phrase_value"],
        success_str="return_phrase_list",
    )
)
class Phrase(WordEmbeddingController):
    def __init__(
        self,
        api,
        args_dict=controller_args.sentence_embedding_args,
        service=get_phrase_for_sentence,
    ):
        WordEmbeddingController.__init__(self, args_dict, service)
