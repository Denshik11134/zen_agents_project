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
Ты — опытный блогер, пишущий для Яндекс.Дзен.
Напиши статью на тему: {topic}.
Контекст (информация для статьи): {context}
Статья должна быть живой, с примерами из жизни, вопросами к читателю, длиной 800-1000 слов.
Запрещены английские слова, шаблонные фразы, канцеляризмы.
Пиши от первого лица, короткими абзацами.
Структура: заголовок, введение, 3-4 подзаголовка, заключение, краткое резюме.
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
