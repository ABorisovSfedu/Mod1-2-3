from typing import List, Tuple, Dict
from app.nlp.pipeline import get_ru_pipeline
from app.models.schemas import Keyphrase

# Небольшой набор русских стоп-слов для MVP
_STOP = {
    "и", "или", "а", "но", "как", "что", "же", "то", "бы", "уже",
    "в", "во", "на", "над", "под", "по", "из", "за", "к", "ко", "от", "до", "с", "со", "у", "о", "об", "при",
    "это", "этот", "эта", "эти", "тот", "та", "те", "который", "которые", "его", "ее", "их",
    "есть", "быть", "будет", "можно", "нужно"
}


def split_sentences(text: str) -> List[str]:
    nlp = get_ru_pipeline()
    doc = nlp(text)
    return [s.text for s in doc.sentences]


def lemmatize_phrase(text: str) -> str:
    nlp = get_ru_pipeline()
    doc = nlp(text)
    lemmas: List[str] = []
    for s in doc.sentences:
        for w in s.words:
            if w.upos == "PUNCT":
                continue
            lemmas.append((w.lemma or w.text).lower())
    return " ".join(lemmas)


def _extract_candidates_with_types(text: str) -> List[Tuple[str, str]]:
    """
    Возвращает список (lemma_phrase, pattern_type),
    где pattern_type ∈ {"single", "adj_noun", "noun_noun"}.
    """
    nlp = get_ru_pipeline()
    doc = nlp(text)

    cands: List[Tuple[str, str]] = []
    for s in doc.sentences:
        words = [w for w in s.words if w.upos != "PUNCT"]
        n = len(words)
        for i, w in enumerate(words):
            # одиночный NOUN
            if w.upos == "NOUN":
                cand1 = (w.lemma or w.text).lower()
                cands.append((cand1, "single"))

            # ADJ + NOUN
            if w.upos == "ADJ" and i + 1 < n and words[i + 1].upos == "NOUN":
                adj = (w.lemma or w.text).lower()
                nn = (words[i + 1].lemma or words[i + 1].text).lower()
                cands.append((f"{adj} {nn}", "adj_noun"))

            # NOUN + NOUN
            if w.upos == "NOUN" and i + 1 < n and words[i + 1].upos == "NOUN":
                n1 = (w.lemma or w.text).lower()
                n2 = (words[i + 1].lemma or words[i + 1].text).lower()
                cands.append((f"{n1} {n2}", "noun_noun"))
    return cands


def _normalize_text_phrase(lemma_phrase: str) -> str:
    # для MVP возвращаем text как ту же фразу, что и lemma, в нижнем регистре
    return lemma_phrase


def _filter_and_merge(cands: List[Tuple[str, str]]) -> List[Tuple[str, float]]:
    """
    Фильтрация по стоп-словам и слияние дублей (по лемме).
    Возвращает список (lemma_phrase, confidence).
    Предпочитаем более «сильные» паттерны (adj_noun/noun_noun = 0.8) перед single (=0.6).
    Если есть длинная фраза, удаляем вложенные одиночные существительные.
    """
    # 1) выставляем confidence
    scored: List[Tuple[str, float]] = []
    for lemma_phrase, kind in cands:
        toks = [t for t in lemma_phrase.split() if t not in _STOP]
        if not toks:
            continue
        if kind in ("adj_noun", "noun_noun"):
            conf = 0.8
        else:
            conf = 0.6
        scored.append((" ".join(toks), conf))

    if not scored:
        return []

    # 2) дедуп по лемме с выбором большего confidence/длины
    best: Dict[str, Tuple[str, float]] = {}
    for lemma, conf in scored:
        prev = best.get(lemma)
        if prev is None or (conf > prev[1]) or (conf == prev[1] and len(lemma) > len(prev[0])):
            best[lemma] = (lemma, conf)

    # 3) если есть длинные фразы, убираем одиночные леммы, которые входят в них как токены
    phrases = list(best.values())
    multi = [p for p in phrases if " " in p[0]]
    singles = [p for p in phrases if " " not in p[0]]
    singles_to_keep = []
    multi_tokens = set()
    for m, _ in multi:
        multi_tokens.update(m.split())
    for s, conf in singles:
        if s not in multi_tokens:
            singles_to_keep.append((s, conf))

    merged = multi + singles_to_keep
    # Сохраняем порядок появления приблизительно: многословные раньше, затем одиночные
    return merged


def extract_keyphrases(text: str) -> List[Keyphrase]:
    """
    Основная функция: извлекает ключевые фразы и возвращает список Keyphrase.
    """
    cands = _extract_candidates_with_types(text)
    merged = _filter_and_merge(cands)

    keyphrases: List[Keyphrase] = []
    for lemma, conf in merged:
        text_norm = _normalize_text_phrase(lemma)
        keyphrases.append(Keyphrase(text=text_norm, lemma=lemma, confidence=conf))
    return keyphrases


def extract_np_candidates(text: str) -> List[str]:
    """
    Старый вспомогательный интерфейс (оставлен для обратной совместимости).
    Возвращает только леммы NP-кандидатов.
    """
    cands = _extract_candidates_with_types(text)
    return [lemma for lemma, _ in _filter_and_merge(cands)]
