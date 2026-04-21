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

# ============================================================
# ПРОМПТЫ ДЛЯ РАЗНЫХ ФОРМАТОВ И СТИЛЕЙ (ДОБАВЛЕНО)
# ============================================================

prompts = {
    # 1. СТАТЬЯ (был только этот)
    "article": """Ты — экспертный автор, пишущий статьи для Яндекс.Дзен в нейтральном, объективном стиле.
Напиши статью на тему: "{topic}".

Требования к стилю:
- Строго запрещено писать от первого лица. Не использовать «я», «мне», «мой», «мы».
- Стиль — экспертный, информационный, как в энциклопедии.
- Использовать безличные обороты: «следует», «необходимо», «специалисты рекомендуют».
- Короткие абзацы.

Структура:
1. Заголовок
2. Введение
3. 3-4 подзаголовка с разбором
4. Заключение
5. Резюме

Длина: 800-1000 слов.""",

    # 2. ТРЕД ДЛЯ X
    "twitter_thread": """Напиши тред из 3-5 твитов на тему: "{topic}".

Требования:
- Каждый твит отделён пустой строкой.
- Первый твит — цепляющий заголовок или вопрос.
- Используй эмодзи умеренно.
- Не пиши номера твитов (1/5 и т.д.).
- Пример:
Как выбрать ноутбук? 🧵

Смотри на процессор: Intel i5 или AMD Ryzen 5 — золотая середина.

Оперативки должно быть от 16 ГБ, иначе тормоза.

И не бери без SSD — это боль.""",

    # 3. ПОСТ ДЛЯ СОЦСЕТЕЙ (4 стиля)
    "social_post_neutral": """Тема: "{topic}". Напиши пост для соцсетей.
Стиль: нейтральный, спокойный.
Длина: 100-150 слов. Без эмодзи. Заверши вопросом к аудитории.""",

    "social_post_expert": """Тема: "{topic}". Экспертный пост для соцсетей.
Стиль: авторитетный, с цифрами и фактами.
Длина: 120-180 слов. Добавь 2 вымышленных факта. Заверши выводом.""",

    "social_post_friendly": """Тема: "{topic}". Дружеский пост для соцсетей.
Стиль: тёплый, разговорный.
Длина: 100-150 слов. Используй эмодзи 😊, обращение на "ты". Закончи советом.""",

    "social_post_emotional": """Тема: "{topic}". Эмоциональный пост для соцсетей.
Стиль: вдохновляющий, с личной историей.
Длина: 100-150 слов. Начни с "Представь...". Используй эмодзи ❤️✨. Призыв к комментариям.""",

    # 4. ПРОДАЮЩИЙ ПОСТ (4 стиля)
    "ad_post_neutral": """Тема: "{topic}". Рекламный пост.
Стиль: нейтральный.
Длина: 120-180 слов. Начни с выгоды. Перечисли 2-3 преимущества. CTA: "Узнать подробнее".""",

    "ad_post_expert": """Тема: "{topic}". Экспертный рекламный пост.
Стиль: авторитетный.
Длина: 120-180 слов. Слова: "инновационный", "эффективный". CTA: "Заказать сейчас".""",

    "ad_post_friendly": """Тема: "{topic}". Дружеский рекламный пост.
Стиль: тёплый.
Длина: 100-150 слов. Эмодзи, обращение на "ты". CTA: "Попробуй сам".""",

    "ad_post_emotional": """Тема: "{topic}". Эмоциональный рекламный пост.
Стиль: вдохновляющий.
Длина: 100-150 слов. Начни с "Представь, что...". CTA: "Измени свою жизнь сегодня".""",

    # 5. СЦЕНАРИЙ ДЛЯ ВИДЕО (4 стиля)
    "video_script_neutral": """Тема: "{topic}". Сценарий для видео.
Стиль: нейтральный.
Длительность: 1-2 минуты. Разбей на тайминг: "00:00 - 00:15 - Хук"
Пример:
00:00 - 00:15 - Вступление
00:15 - 01:00 - Основная часть
01:00 - 01:45 - Примеры
01:45 - 02:00 - Заключение""",

    "video_script_expert": """Тема: "{topic}". Экспертный сценарий.
Тайминг 2-3 минуты. Добавь вымышленные данные исследований. Заключение: "Подпишитесь".""",

    "video_script_friendly": """Тема: "{topic}". Дружеский сценарий.
Тайминг 1-2 минуты. Обращение "друзья". Добавь эмодзи в описание.""",

    "video_script_emotional": """Тема: "{topic}". Эмоциональный сценарий.
Тайминг 2 минуты. Построй как историю: проблема - борьба - решение. Воодушевляющий призыв.""",
}

def generate_article(topic, context="", format=None, style=None):
    print(f"=== ОТЛАДКА: format={format}, style={style} ===")  # ← добавить
    
    if client is None:
        print("ERROR: GITHUB_TOKEN is not set.")
        return None

    # Выбираем промпт в зависимости от формата и стиля
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
    prompt = prompt_template.format(topic=topic)

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