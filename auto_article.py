"""
auto_article.py — автоматическое создание статьи: поиск тем → генерация → сохранение.

Весь стек: DuckDuckGo (поиск) + OpenRouter/Gemini (генерация) + DuckDuckGo Images (картинки).
"""

import os
import random
import re

from trend_finder import get_random_psychology_topics
# Ollama версия закомментирована — используется OpenRouter
# from agents.writer.test_writer import write_article
from openrouter_writer import generate_article
from image_fetcher import fetch_image, build_markdown_image


def sanitize_filename(name: str, max_len: int = 100) -> str:
    """Remove illegal filename characters and trim length."""
    name = re.sub(r'[\\/:*?"<>|]', "", name)
    name = name.replace(" ", "_")
    return name[:max_len] if len(name) > max_len else name


def main() -> None:
    try:
        print("🔍 Поиск психологических тем...")
        topics = get_random_psychology_topics(count=5)
        if not topics:
            print("❌ Темы не найдены")
            return

        topic = random.choice(topics)
        print(f"✅ Выбрана тема: {topic}")

        print("✍️ Генерация статьи через OpenRouter (Gemini Flash)...")
        article = generate_article(topic)
        if not article:
            print("❌ Ошибка генерации. Проверьте OPENROUTER_API_KEY в файле .env.")
            return

        # 🖼️ Поиск картинки
        print("🔎 Поиск иллюстрации...")
        img_url = fetch_image(topic)
        if img_url:
            article = build_markdown_image(img_url, topic) + "\n\n" + article
            print(f"✅ Картинка добавлена: {img_url}")
        else:
            print("⚠️ Картинка не найдена, продолжаю без неё")

        filename = sanitize_filename(topic) + ".md"
        os.makedirs("articles", exist_ok=True)
        filepath = os.path.join("articles", filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(article)

        print(f"✅ Статья сохранена: {filepath}")

    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()
