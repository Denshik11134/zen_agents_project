"""
create_article.py — создание статьи по введённой теме.

Поиск через DuckDuckGo → генерация через OpenRouter/Gemini.
"""

import json
import os

from agents.researcher.search_agent import search_duckduckgo
# Ollama версия закомментирована — используется OpenRouter
# from agents.writer.test_writer import write_article
from openrouter_writer import generate_article


def main():
    topic = input("Тема статьи: ")
    print(f"\n🔍 Ищу информацию по теме: {topic}...")

    # Шаг 1: поиск информации
    results = search_duckduckgo(topic, max_results=5)

    # Сохраняем результаты в JSON (опционально)
    os.makedirs("data", exist_ok=True)
    safe_topic = topic.replace(" ", "_")
    json_path = f"data/search_{safe_topic}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ Результаты сохранены в {json_path}")

    # Формируем контекст из результатов поиска
    context = "\n".join(
        [f"- {r['title']}: {r['snippet']}" for r in results]
    )

    # Шаг 2: генерация статьи через OpenRouter (Gemini Flash)
    print("✍️ Генерирую статью через OpenRouter...")
    article = generate_article(topic, context)

    if article:
        os.makedirs("articles", exist_ok=True)
        article_path = f"articles/{safe_topic}.md"
        with open(article_path, "w", encoding="utf-8") as f:
            f.write(article)
        print(f"✅ Статья сохранена в {article_path}")

        print("\n--- СТАТЬЯ ---\n")
        print(article)
    else:
        print("❌ Не удалось сгенерировать статью. Проверьте OPENROUTER_API_KEY в .env.")


if __name__ == "__main__":
    main()
