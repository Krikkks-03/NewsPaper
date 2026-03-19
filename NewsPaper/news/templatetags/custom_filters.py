import re
from django import template

register = template.Library()

# Список слов для цензуры (в нижнем регистре)
CENSORED_WORDS = {'блать', 'дурак', 'ебать', 'сигареты', 'чурка'}

@register.filter(name='censor')
def censor(value):
    """
    Заменяет нецензурные слова на первую букву + звёздочки.
    Если передана не строка — выбрасывает TypeError.
    """
    if not isinstance(value, str):
        raise TypeError(f"Фильтр censor можно применять только к строкам, получен {type(value).__name__}")

    def replace_word(match):
        word = match.group(0)
        if word.lower() in CENSORED_WORDS:
            # Первая буква остаётся, остальные заменяются *
            return word[0] + '*' * (len(word) - 1)
        return word

    # Ищем слова, состоящие из русских букв
    pattern = re.compile(r'\b[а-яА-ЯёЁ]+\b')
    return pattern.sub(replace_word, value)