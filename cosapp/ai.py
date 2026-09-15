import re

from django.conf import settings
from openai import OpenAI

CITATION = re.compile(r'\s*\(?\[[^\]]*\]\([^)]*\)\)?')

PROMPT = (
    'Косметический товар: {brand} {title}. Категория: {category}.\n'
    'Найди его и напиши 2-3 коротких пункта на русском: назначение, '
    'ключевые ингредиенты, кому подходит.\n'
    'Простым текстом, каждый пункт с новой строки. Без markdown, без ссылок.\n'
    'Если товар не найден, ответь одной строкой: нет данных.'
)


def generate_summary(product):
    response = OpenAI().responses.create(
        model=settings.OPENAI_MODEL,
        tools=[{'type': 'web_search'}],
        input=PROMPT.format(
            brand=product.brand.title,
            title=product.title,
            category=product.category.title,
        ),
    )
    return CITATION.sub('', response.output_text).replace('**', '').strip()
