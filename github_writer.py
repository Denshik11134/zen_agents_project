import os
from openai import OpenAI

# On Railway, GITHUB_TOKEN is set via the dashboard environment variables.
# No need to load .env file.

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    # Defer the error — let the app start, but fail gracefully at generation time.
    # This prevents ImportError from crashing the entire app on startup.
    client = None
else:
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=GITHUB_TOKEN,
    )

def generate_article(topic, context=""):
    if client is None:
        print("ERROR: GITHUB_TOKEN is not set. Set it in Railway dashboard or .env file.")
        return None

    prompt = f"""
Ты — экспертный автор, пишущий статьи для Яндекс.Дзен в нейтральном, объективном стиле.
Напиши статью на тему: {topic}.
Контекст (информация для статьи): {context}

Требования к стилю:
- Строго запрещено писать от первого лица. Не использовать местоимения «я», «мне», «мой», «мы», «наш» и любые личные местоимения.
- Не использовать личные истории, anecdotes от автора, фразы типа «я считаю», «по моему опыту», «мне кажется».
- Стиль — экспертный, информационный, как в энциклопедии, учебнике или инструкции.
- Использовать безличные и обезличенные обороты: «следует», «необходимо», «можно сделать», «распространённая ошибка», «специалисты рекомендуют», «как показывает практика», «советы», «важно знать».
- Язык — русский, грамотный, живой, но без излишней эмоциональности и пафоса.
- Запрещены английские слова, шаблонные фразы, канцеляризмы.
- Короткие абзацы для удобства чтения.

Структура статьи:
1. Заголовок
2. Введение (раскрытие темы, обозначение проблемы)
3. 3-4 подзаголовка с подробным разбором аспектов
4. Заключение (выводы по теме)
5. Краткое резюме (ключевые мысли)

Длина: 800-1000 слов.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    topic = input("Тема статьи: ")
    print(generate_article(topic))
