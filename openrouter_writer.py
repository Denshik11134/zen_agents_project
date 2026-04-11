"""
openrouter_writer.py — генерация статей через OpenRouter API.

Модель: google/gemini-2.0-flash-exp:free (бесплатная, быстрая — 2-5 секунд).
API-ключ берётся из переменной окружения OPENROUTER_API_KEY.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

# Загружаем .env
load_dotenv()

MODEL_NAME = "google/gemini-2.0-flash-exp:free"

# OpenRouter API через OpenAI-совместимый клиент
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _get_client() -> OpenAI:
    """Создать клиент для OpenRouter API."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Переменная OPENROUTER_API_KEY не найдена в .env файле.\n"
            "Создайте ключ на https://openrouter.ai/keys и добавьте в .env:\n"
            "OPENROUTER_API_KEY=sk-or-v1-..."
        )
    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "https://localhost:5000",
            "X-Title": "Zen Article Generator",
        },
    )


def _check_openrouter() -> bool:
    """Проверить, что API-ключ задан."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print(
            "\n[!] OPENROUTER_API_KEY не найден в .env.\n"
            "    Создайте ключ на https://openrouter.ai/keys\n"
            "    и добавьте в файл .env:\n"
            "    OPENROUTER_API_KEY=sk-or-v1-...\n"
        )
        return False
    return True


def generate_article(topic: str, context: str = "") -> str | None:
    """Сгенерировать статью на заданную тему через OpenRouter (Gemini Flash).

    Живой русский стиль: вопросы к читателю, примеры из жизни,
    длина 800-1000 слов, структура: заголовок, введение, 3-4 подзаголовка,
    заключение, краткое резюме.
    """
    if not _check_openrouter():
        return None

    prompt = f"""
Ты — русскоязычный психолог и блогер на Яндекс.Дзен. Пишешь статью на тему: "{topic}".

ПРАВИЛА СТИЛЯ:
1. Только русский текст. Никаких английских слов, транслита и латиницы.
2. Никаких эмодзи.
3. Забудь шаблонные фразы: "в современном мире", "бешеный ритм жизни", "актуально как никогда", "давайте разберёмся".
4. Пиши от первого лица: "я столкнулся", "мне помогло", "я думаю".
5. Задавай вопросы читателю: "Знакомо?", "А у вас бывало?", "Чувствовали что-то похожее?".
6. Добавляй живые истории с именами, местами, небольшими диалогами.
7. Разговорный стиль: "представьте", "кстати", "знаете что", "на самом деле".
8. Объём: 800-1000 слов. Пиши развёрнуто, не поверхностно.

СТРУКТУРА СТАТЬИ:
# {topic}

Введение (3-4 абзаца): начни с живой ситуации — как будто человек рассказал тебе свою историю. Используй фразы "многие через это проходят", "я тоже", "вот что мне помогло".

### Подзаголовок 1
2-3 абзаца. История с деталями (имя, место, диалог) + объяснение, почему так происходит.

### Подзаголовок 2
2-3 абзаца. Практический совет или техника. Объясни простым языком.

### Подзаголовок 3
2-3 абзаца. Упражнение или пошаговая инструкция для читателя.

### Подзаголовок 4
2-3 абзаца. Поддержка читателя, типичные ошибки и как их избежать.

Заключение (2-3 абзаца): подведи итог, поддержи читателя, мягко пригласи подписаться.

Краткое резюме:
- пункт 1
- пункт 2
- пункт 3
- пункт 4

Каждый пункт резюме — конкретный вывод или действие.

Тема: {topic}
Дополнительный контекст: {context}
"""

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4096,
        )
        article = response.choices[0].message.content
        if article:
            return article.strip()
        print("[!] OpenRouter вернул пустой ответ.")
        return None

    except EnvironmentError as e:
        print(f"\n[!] {e}")
        return None
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg.lower() or "unauthorized" in error_msg.lower():
            print(
                f"\n[!] Ошибка авторизации OpenRouter: неверный API-ключ.\n"
                f"    Проверьте OPENROUTER_API_KEY в файле .env.\n"
            )
        elif "rate limit" in error_msg.lower():
            print(
                f"\n[!] Превышен лимит запросов OpenRouter. Подождите немного.\n"
            )
        else:
            print(f"\n[!] Ошибка генерации статьи через OpenRouter: {e}\n")
        return None


if __name__ == "__main__":
    topic_input = input("Тема статьи: ")
    result = generate_article(topic_input)
    if result:
        print("\n--- СТАТЬЯ ---\n")
        print(result)
    else:
        print("\n❌ Не удалось сгенерировать статью.")
