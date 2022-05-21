import pytest
from unittest.mock import patch
from app.main.model.word_embedding import WordVector, NgramWordVector, PhraseDict
from app.main.service.word_embedding_service import (
    get_vectors_for_word_lists,
    get_vectors_for_ngram_word_lists,
    get_sentences_average_vectors,
    get_sentences_average_vectors_ngram,
    get_phrase_for_sentence,
)


class TestWordEmbeddingService:
    def test_get_vectors_for_word_lists(self):
        word_vector = WordVector(word="apple", vector=[0.01, 0.01, 0.01])
        word_vector.save()
        expect = {"apple": [0.01, 0.01, 0.01]}
        result = get_vectors_for_word_lists(words="apple")
        word_vector.delete()
        assert result == expect

    def test_get_vectors_for_word_lists_failed(self):
        word_vector = WordVector(word="apples", vector=[0.01, 0.01, 0.01])
        word_vector.save()
        expect = {"apple": []}
        result = get_vectors_for_word_lists(words="apple")
        word_vector.delete()
        assert result == expect

    def test_get_ngram_vectors_for_word_lists(self):
        word_vector = NgramWordVector(word="apple_pie", vector=[0.01, 0.01, 0.01])
        word_vector.save()
        expect = {"apple_pie": [0.01, 0.01, 0.01]}
        result = get_vectors_for_ngram_word_lists(words="apple_pie")
        word_vector.delete()
        assert result == expect

    def test_get_ngram_vectors_for_word_lists_failed(self):
        word_vector = NgramWordVector(word="orange_pie", vector=[0.01, 0.01, 0.01])
        word_vector.save()
        expect = {"apple_pie": []}
        result = get_vectors_for_ngram_word_lists(words="apple_pie")
        word_vector.delete()
        assert result == expect

    def test_get_phrase_for_sentence(self):
        ngram = PhraseDict(ngram="natural_cotton_sateen")
        ngram.save()
        expect = ["this", "natural_cotton_sateen"]
        result = get_phrase_for_sentence(sentence="this natural cotton sateen")
        ngram.delete()
        assert result == expect

    def test_get_phrase_for_sentence_failed(self):
        ngram = PhraseDict(ngram="natural_cotton_sateen")
        ngram.save()
        expect = []
        result = get_phrase_for_sentence(sentence=" ")
        ngram.delete()
        assert result == expect

    @patch("app.main.service.word_embedding_service.word_vector_length", 3)
    def test_get_sentence_vector(self):
        word_vector = WordVector(word="orange", vector=[0.01, 0.02, 0.03])
        word_vector1 = WordVector(word="apple", vector=[0.03, 0.02, 0.01])
        word_vector.save()
        word_vector1.save()
        expect = {"sentence": "orange apple", "vector": [0.02, 0.02, 0.02]}
        result = get_sentences_average_vectors(sentence="orange apple")
        word_vector.delete()
        word_vector1.delete()
        assert result == expect

    @patch("app.main.service.word_embedding_service.word_vector_length", 3)
    def test_get_sentence_vector_failed(self):
        word_vector = WordVector(word="orange", vector=[0.01, 0.02, 0.03])
        word_vector1 = WordVector(word="apple", vector=[0.05, 0.04, 0.03])
        word_vector.save()
        word_vector1.save()
        expect = {"sentence": "orange apple pie", "vector": [0.02, 0.02, 0.02]}
        result = get_sentences_average_vectors(sentence="orange apple pie")
        word_vector.delete()
        word_vector1.delete()
        assert result == expect

    @patch("app.main.service.word_embedding_service.word_vector_length", 3)
    def test_get_sentence_vector_all_not_found(self):
        word_vector = WordVector(word="orange", vector=[0.01, 0.02, 0.03])
        word_vector1 = WordVector(word="apple", vector=[0.05, 0.04, 0.03])
        word_vector.save()
        word_vector1.save()
        expect = {"sentence": "pie pie", "vector": [0.0, 0.0, 0.0]}
        result = get_sentences_average_vectors(sentence="pie pie")
        word_vector.delete()
        word_vector1.delete()
        assert result == expect

    @patch("app.main.service.word_embedding_service.ngram_word_vector_length", 3)
    def test_get_ngram_sentence_vector(self):
        word_vector = NgramWordVector(word="orange_pie", vector=[0.01, 0.02, 0.03])
        word_vector1 = NgramWordVector(word="apple_pie", vector=[0.03, 0.02, 0.01])
        word_vector.save()
        word_vector1.save()
        expect = {"sentence": "orange_pie apple_pie", "vector": [0.02, 0.02, 0.02]}
        result = get_sentences_average_vectors_ngram(sentence="orange_pie apple_pie")
        word_vector.delete()
        word_vector1.delete()
        assert result == expect

    @patch("app.main.service.word_embedding_service.ngram_word_vector_length", 3)
    def test_get_ngram_sentence_vector_failed(self):
        word_vector = NgramWordVector(word="orange_pie", vector=[0.01, 0.02, 0.03])
        word_vector1 = NgramWordVector(word="apple_pie", vector=[0.05, 0.04, 0.03])
        word_vector.save()
        word_vector1.save()
        expect = {
            "sentence": "orange_pie apple_pie banana_pie",
            "vector": [0.02, 0.02, 0.02],
        }
        result = get_sentences_average_vectors_ngram(
            sentence="orange_pie apple_pie banana_pie"
        )
        word_vector.delete()
        word_vector1.delete()
        assert result == expect

    @patch("app.main.service.word_embedding_service.ngram_word_vector_length", 3)
    def test_get_ngram_sentence_vector_all_not_found(self):
        word_vector = NgramWordVector(word="orange_pie", vector=[0.01, 0.02, 0.03])
        word_vector1 = NgramWordVector(word="apple_pie", vector=[0.05, 0.04, 0.03])
        word_vector.save()
        word_vector1.save()
        expect = {
            "sentence": "banana_pie banana_pie",
            "vector": [0.0, 0.0, 0.0],
        }
        result = get_sentences_average_vectors_ngram(sentence="banana_pie banana_pie")
        word_vector.delete()
        word_vector1.delete()
        assert result == expect


if __name__ == "__main__":
    pytest.main()
