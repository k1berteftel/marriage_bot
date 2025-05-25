from utils.translator.Lexicon import ru, en, tr
# Другие импорты словарей языков


def get_languages() -> list[dict]:
    return [ru.texts, en.texts]
