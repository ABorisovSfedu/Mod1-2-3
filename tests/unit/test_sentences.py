from app.services.chunker import split_sentences

def test_split_sentences_basic():
    text = "Здравствуйте. Это тест. Т.е. проверка. Спасибо! Погнали?"
    sents = split_sentences(text)
    assert any("Здравствуйте." in s for s in sents)
    assert any("Это тест." in s for s in sents)
    assert any("Спасибо!" in s for s in sents)
    assert any("Погнали?" in s for s in sents)