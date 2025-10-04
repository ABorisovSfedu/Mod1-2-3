import pytest
from app.nlp.extract import split_sentences, lemmatize_phrase

def test_split_sentences_ru():
    text = "Привет! Это простой тест. Проверим разбиение на предложения."
    sents = split_sentences(text)
    assert sents == [
        "Привет!",
        "Это простой тест.",
        "Проверим разбиение на предложения."
    ]

def test_lemmatize_phrase_ru():
    text = "Кнопки и формы на страницах"
    lemmas = lemmatize_phrase(text)
    # Ожидаем нормальные формы
    assert lemmas == "кнопка и форма на страница"
