from app.nlp.extract import split_sentences, lemmatize_phrase, extract_np_candidates

def test_split_sentences_ru():
    text = "Привет! Это простой тест. Проверим разбиение на предложения."
    assert split_sentences(text) == [
        "Привет!",
        "Это простой тест.",
        "Проверим разбиение на предложения.",
    ]

def test_lemmatize_phrase_ru():
    text = "Кнопки и формы на страницах"
    lemmas = lemmatize_phrase(text)
    assert lemmas == "кнопка и форма на страница"

def test_np_candidates_ru():
    text = "Нужна форма обратной связи и каталог услуг"
    nps = extract_np_candidates(text)
    # Должны встретиться ключевые сочетания
    assert "обратный связь" in nps or "форма обратный связь" in nps
    assert "каталог услуга" in nps
