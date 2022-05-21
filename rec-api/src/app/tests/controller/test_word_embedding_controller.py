import json
import operator

import pytest
from unittest.mock import patch
from app.main import create_app
from app.main.model.word_embedding import WordVector, NgramWordVector, PhraseDict

client = create_app(config_name="test").test_client()


class TestWordEmbeddingController:
    def test_get_word_vector(self):
        word_vector = WordVector(word="orange", vector=[0.01, 0.01, 0.01])
        word_vector.save()
        expect = {"orange": [0.01, 0.01, 0.01]}
        response = client.get("/api/rec/word_embedding/word_vectors?words=orange")
        word_vector.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_get_word_vector_404(self):
        word_vector = WordVector(word="oranges", vector=[0.01, 0.01, 0.01])
        word_vector.save()
        expect = {"orange": []}
        response = client.get("/api/rec/word_embedding/word_vectors?words=orange")
        word_vector.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_get_ngram_word_vector(self):
        word_vector = NgramWordVector(word="orange_pie", vector=[0.01, 0.01, 0.01])
        word_vector.save()
        expect = {"orange_pie": [0.01, 0.01, 0.01]}
        response = client.get(
            "/api/rec/word_embedding/ngram_word_vectors?words=orange_pie"
        )
        word_vector.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_get_ngram_word_vector_404(self):
        word_vector = NgramWordVector(word="orange_pie", vector=[0.01, 0.01, 0.01])
        word_vector.save()
        expect = {"apple_pie": []}
        response = client.get(
            "/api/rec/word_embedding/ngram_word_vectors?words=apple_pie"
        )
        word_vector.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_get_phrase_for_sentence(self):
        ngram = PhraseDict(ngram="apple_pie")
        ngram.save()
        expect = ["this", "apple_pie"]
        response = client.get(
            "/api/rec/word_embedding/phrase?sentence=this%20apple%20pie"
        )
        ngram.delete()
        assert operator.eq(expect, json.loads(response.data))

    def test_get_phrase_for_sentence_not_found(self):
        ngram = PhraseDict(ngram="apple_pie")
        ngram.save()
        expect = ["this", "orange", "pie"]
        response = client.get(
            "/api/rec/word_embedding/phrase?sentence=this%20orange%20pie"
        )
        ngram.delete()
        assert operator.eq(expect, json.loads(response.data))

    @patch("app.main.service.word_embedding_service.word_vector_length", 3)
    def test_get_sentence_vector(self):
        word_vector = WordVector(word="orange", vector=[0.01, 0.02, 0.03])
        word_vector1 = WordVector(word="apple", vector=[0.03, 0.02, 0.01])
        word_vector.save()
        word_vector1.save()
        expect = {"sentence": "orange apple", "vector": [0.02, 0.02, 0.02]}
        response = client.get(
            "/api/rec/word_embedding/sentence_vector?sentence=orange%20apple"
        )
        word_vector.delete()
        word_vector1.delete()
        assert operator.eq(expect, json.loads(response.data))

    @patch("app.main.service.word_embedding_service.word_vector_length", 3)
    def test_get_sentence_vector_404(self):
        word_vector = WordVector(word="orange", vector=[0.03, 0.02, 0.03])
        word_vector1 = WordVector(word="apple", vector=[0.03, 0.04, 0.03])
        word_vector.save()
        word_vector1.save()
        expect = {"sentence": "orange apple pie", "vector": [0.02, 0.02, 0.02]}
        response = client.get(
            "/api/rec/word_embedding/sentence_vector?sentence=orange%20apple%20pie"
        )
        word_vector.delete()
        word_vector1.delete()
        assert operator.eq(expect, json.loads(response.data))

    @patch("app.main.service.word_embedding_service.word_vector_length", 3)
    def test_get_sentence_vector_all_not_found(self):
        word_vector = WordVector(word="orange", vector=[0.03, 0.02, 0.03])
        word_vector1 = WordVector(word="apple", vector=[0.03, 0.04, 0.03])
        word_vector.save()
        word_vector1.save()
        expect = {"sentence": "pie pie", "vector": [0.0, 0.0, 0.0]}
        response = client.get(
            "/api/rec/word_embedding/sentence_vector?sentence=pie%20pie"
        )
        word_vector.delete()
        word_vector1.delete()
        assert operator.eq(expect, json.loads(response.data))

    @patch("app.main.service.word_embedding_service.ngram_word_vector_length", 3)
    def test_get_ngram_sentence_vector(self):
        word_vector = NgramWordVector(word="orange_pie", vector=[0.01, 0.02, 0.03])
        word_vector1 = NgramWordVector(word="apple_pie", vector=[0.03, 0.02, 0.01])
        word_vector.save()
        word_vector1.save()
        expect = {"sentence": "orange_pie apple_pie", "vector": [0.02, 0.02, 0.02]}
        response = client.get(
            "/api/rec/word_embedding/ngram_sentence_vector?sentence=orange_pie%20apple_pie"
        )
        word_vector.delete()
        word_vector1.delete()
        assert operator.eq(expect, json.loads(response.data))

    @patch("app.main.service.word_embedding_service.ngram_word_vector_length", 3)
    def test_get_ngram_sentence_vector_404(self):
        word_vector = NgramWordVector(word="orange_pie", vector=[0.03, 0.02, 0.03])
        word_vector1 = NgramWordVector(word="apple_pie", vector=[0.03, 0.04, 0.03])
        word_vector.save()
        word_vector1.save()
        expect = {
            "sentence": "orange_pie apple_pie banana_pie",
            "vector": [0.02, 0.02, 0.02],
        }
        response = client.get(
            "/api/rec/word_embedding/ngram_sentence_vector?sentence=orange_pie%20apple_pie%20banana_pie"
        )
        word_vector.delete()
        word_vector1.delete()
        assert operator.eq(expect, json.loads(response.data))

    @patch("app.main.service.word_embedding_service.ngram_word_vector_length", 3)
    def test_get_ngram_sentence_vector_all_not_found(self):
        word_vector = NgramWordVector(word="orange_pie", vector=[0.03, 0.02, 0.03])
        word_vector1 = NgramWordVector(word="apple_pie", vector=[0.03, 0.04, 0.03])
        word_vector.save()
        word_vector1.save()
        expect = {
            "sentence": "banana_pie banana_pie",
            "vector": [0.0, 0.0, 0.0],
        }
        response = client.get(
            "/api/rec/word_embedding/ngram_sentence_vector?sentence=banana_pie%20banana_pie"
        )
        word_vector.delete()
        word_vector1.delete()
        assert operator.eq(expect, json.loads(response.data))


if __name__ == "__main__":
    pytest.main()
