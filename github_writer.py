import os
from openai import OpenAI

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    client = None
else:
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=GITHUB_TOKEN,
    )

prompts = {
    "article": """Ты — экспертный автор. Напиши статью на тему: "{topic}".

Требования:
- Длина: 800-1000 слов.
- Структура: введение, 3-4 подзаголовка, заключение.
- Стиль: нейтральный, экспертный, без эмодзи.

{details_section}""",

    "twitter_thread": """Напиши тред из 3-5 твитов на тему: "{topic}".

Требования:
- Каждый твит отделён пустой строкой.
- Первый твит — цепляющий.
- Без нумерации.

{details_section}""",

    "social_post_neutral": """Тема: "{topic}". Напиши пост для соцсетей.
Стиль: нейтральный.
Длина: 100-150 слов.
{details_section}""",

    "social_post_expert": """Тема: "{topic}". Экспертный пост.
Длина: 120-180 слов. С цифрами и фактами.
{details_section}""",

    "social_post_friendly": """Тема: "{topic}". Дружеский пост.
Длина: 100-150 слов. С эмодзи, обращение на "ты".
{details_section}""",

    "social_post_emotional": """Тема: "{topic}". Эмоциональный пост.
Длина: 100-150 слов. Вдохновляющий, с историей.
{details_section}""",

    "ad_post_neutral": """Напиши продающий пост для: "{topic}".

{details_section}

Требования:
- Длина: 150-200 слов.
- Подчеркни преимущества.
- Добавь призыв к действию.
- Стиль: нейтральный.""",

    "ad_post_expert": """Напиши экспертный продающий пост для: "{topic}".

{details_section}

Требования:
- Длина: 150-200 слов.
- Профессиональные термины.
- CTA: "Заказать сейчас".""",

    "ad_post_friendly": """Напиши дружеский продающий пост для: "{topic}".

{details_section}

Требования:
- Длина: 150-200 слов.
- Тёплый тон, эмодзи, "ты".
- CTA: "Попробуй сам".""",

    "ad_post_emotional": """Напиши эмоциональный продающий пост для: "{topic}".

{details_section}

Требования:
- Длина: 150-200 слов.
- Яркий, вдохновляющий.
- CTA: "Измени свою жизнь".""",

    "video_script_neutral": """Сценарий для видео: "{topic}".
Длительность: 1-2 минуты. С таймингом.
{details_section}""",

    "video_script_expert": """Экспертный сценарий: "{topic}".
Тайминг 2-3 минуты.
{details_section}""",

    "video_script_friendly": """Дружеский сценарий: "{topic}".
Тайминг 1-2 минуты.
{details_section}""",

    "video_script_emotional": """Эмоциональный сценарий: "{topic}".
Тайминг 2 минуты.
{details_section}""",
}

def generate_article(topic, context="", format=None, style=None, details=""):
    print(f"=== ОТЛАДКА: format={format}, style={style}, details={details[:100] if details else 'нет'}... ===")
    
    if client is None:
        print("ERROR: GITHUB_TOKEN is not set.")
        return None

    # Формируем секцию с деталями
    details_section = ""
    if details and details.strip():
        details_section = f"""
=== ИНФОРМАЦИЯ ОТ ПОЛЬЗОВАТЕЛЯ ===
{details}
================================

Учти эту информацию обязательно! Если указаны характеристики — включи их в текст."""

    # Выбираем промпт
    if format == "article" or format is None:
        prompt_key = "article"
    elif format == "twitter_thread":
        prompt_key = "twitter_thread"
    elif format == "social_post":
        if style in ["neutral", "expert", "friendly", "emotional"]:
            prompt_key = f"social_post_{style}"
        else:
            prompt_key = "social_post_neutral"
    elif format == "ad_post":
        if style in ["neutral", "expert", "friendly", "emotional"]:
            prompt_key = f"ad_post_{style}"
        else:
            prompt_key = "ad_post_neutral"
    elif format == "video_script":
        if style in ["neutral", "expert", "friendly", "emotional"]:
            prompt_key = f"video_script_{style}"
        else:
            prompt_key = "video_script_neutral"
    else:
        prompt_key = "article"

    prompt_template = prompts.get(prompt_key, prompts["article"])
    prompt = prompt_template.format(topic=topic, details_section=details_section)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    topic = input("Тема: ")
    print(generate_article(topic))