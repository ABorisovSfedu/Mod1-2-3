import threading
import stanza

# Глобальный кэш пайплайна
_NLP_RU = None
_LOCK = threading.Lock()


def _init_ru_pipeline():
    """
    Инициализация RU-пайплайна Stanza с загрузкой моделей из сети.
    Процессоры: tokenize, pos, lemma (включая разбиение на предложения).
    """
    # Скачиваем модели русского один раз на запуск
    stanza.download("ru")
    # Создаём пайплайн
    return stanza.Pipeline(
        lang="ru",
        processors="tokenize,pos,lemma",
        use_gpu=False,
        tokenize_no_ssplit=False,
    )


def get_ru_pipeline():
    """Ленивая и потокобезопасная инициализация кэшированного пайплайна."""
    global _NLP_RU
    if _NLP_RU is None:
        with _LOCK:
            if _NLP_RU is None:
                _NLP_RU = _init_ru_pipeline()
    return _NLP_RU


def preload_ru():
    """Явная инициализация при старте приложения (скачает и прогреет модели)."""
    get_ru_pipeline()
