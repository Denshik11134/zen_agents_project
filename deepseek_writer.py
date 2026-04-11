"""
deepseek_writer.py — Генерация статей через DeepSeek API.

Использует модель deepseek-chat через OpenAI-совместимый клиент.
API-ключ берётся из переменной окружения DEEPSEEK_API_KEY.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Загружаем переменные из .env
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH)

# Инициализируем клиент DeepSeek
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# Системный промпт — задаёт стиль и структуру
SYSTEM_PROMPT = """\
Ты — опытный автор статей для Яндекс.Дзена. Пиши живым, увлекательным русским языком.

ПРАВИЛА СТИЛЯ:
- Пиши на чистом русском языке, БЕЗ англицизмов и кальки с английского.
- Используй риторические вопросы, живые примеры, обращения к читателю («вы», «представьте»).
- Избегай канцелярита, штампов и воды.
- Длина статьи: 800–1000 слов.

СТРУКТУРА СТАТЬИ:
1. Заголовок (яркий, цепляющий, без «Как…»)
2. Введение (2-3 абзаца: проблема, почему это важно, интрига)
3. 3-4 подзаголовка с развернутыми разделами (примеры, факты, объяснения)
4. Заключение (выводы, призыв к размышлению)
5. Резюме (3-5 ключевых мыслей в виде маркированного списка)

ФОРМАТ ОТВЕТА:
Ответь ТОЛЬКО текстом статьи, БЕЗ пояснений, БЕЗ комментариев.
Не добавляй markdown-обёртку типа ``` или мета-текст вроде «Вот статья».
"""


def generate_article(topic: str, context: str = "") -> str | None:
    """
    Сгенерировать статью по заданной теме через DeepSeek API.

    Args:
        topic: Тема статьи (например, «Почему мы боимся перемен»).
        context: Дополнительный контекст (необязательно).

    Returns:
        Текст статьи или None при ошибке.
    """
    user_prompt = f"Тема статьи: {topic}"
    if context:
        user_prompt += f"\n\nДополнительный контекст: {context}"

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.8,
            max_tokens=4000,
        )
        article = response.choices[0].message.content
        if article:
            return article.strip()
        return None

    except Exception as e:
        print(f"[deepseek_writer] Ошибка генерации: {e}")
        return None


if __name__ == "__main__":
    # Быстрый тест
    test_topic = "Почему привычка полезнее мотивации"
    print(f"Генерация статьи по теме: {test_topic}\n")
    result = generate_article(test_topic)
    if result:
        print(result)
    else:
        print("Не удалось сгенерировать статью. Проверьте DEEPSEEK_API_KEY.")
