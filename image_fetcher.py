"""
image_fetcher.py — поиск релевантных изображений для статей.

Источники (по порядку):
1. DuckDuckGo Images (через duckduckgo-search) — с английским запросом.
2. Wikimedia Commons API (без ключа, релевантные фото/иллюстрации).
3. Lorem Picsum (picsum.photos) — fallback, случайные фото.
"""

import re
import requests
from duckduckgo_search import DDGS

# Минимальная ширина картинки (px)
MIN_WIDTH = 400

# Fallback
PICSUM_URL = "https://picsum.photos/800/500"

# Wikimedia Commons API endpoint
WIKIMEDIA_URL = "https://commons.wikimedia.org/w/api.php"

# Простой словарь русских тем → английские эквиваленты для поиска картинок
RU_TO_EN = {
    "тревог": "anxiety",
    "паник": "panic",
    "самооценк": "self-esteem",
    "выгоран": "burnout",
    "прокрастинац": "procrastination",
    "бессонниц": "insomnia",
    "мотивац": "motivation",
    "одиночеств": "loneliness",
    "обида": "resentment",
    "гнев": "anger",
    "уверенност": "confidence",
    "апати": "apathy",
    "кризис": "crisis",
    "ревност": "jealousy",
    "память": "memory",
    "внимани": "attention",
    "зависимост": "addiction",
    "отношен": "relationships",
    "партнёр": "partner",
    "психолог": "psychology",
    "стресс": "stress",
    "депресс": "depression",
    "соцсет": "social media",
    "самокритик": "self-criticism",
    "перфекционизм": "perfectionism",
    "границы": "boundaries",
    "спокой": "calm",
    "медитац": "meditation",
    "расслабл": "relaxation",
    "сон": "sleep",
    "страх": "fear",
    "эмоци": "emotions",
    "техник": "techniques",
    "упражнен": "exercises",
    "совет": "tips",
    "как справиться": "how to cope",
    "как побороть": "how to overcome",
    "как пережить": "how to survive",
}


def _translate_query(query: str) -> str:
    """Преобразовать русский запрос в английский для поиска картинок."""
    result = query.lower()
    found_any = False
    for ru_word, en_word in sorted(RU_TO_EN.items(), key=lambda x: -len(x[0])):
        if ru_word in result:
            result = result.replace(ru_word, en_word)
            found_any = True
    # Оставляем только английские буквы и пробелы
    result = re.sub(r"[^a-z\s]", " ", result)
    result = re.sub(r"\s+", " ", result).strip()
    # Если нашли хотя бы одно слово — добавляем контекст psychology
    if found_any:
        result = f"{result} psychology mental health"
    return result if len(result) > 1 else "psychology calm mind"


def _search_ddg(query: str, max_results: int = 10) -> str | None:
    """Поиск через DuckDuckGo Images."""
    # DDG лучше работает с английскими запросами
    en_query = _translate_query(query)
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(en_query, max_results=max_results))
        for r in results:
            img_url = r.get("image", "")
            width = r.get("width", 0)
            if img_url and width >= MIN_WIDTH:
                return img_url
        if results:
            return results[0].get("image")
    except Exception:
        pass
    return None


def _search_wikimedia(query: str) -> str | None:
    """Поиск через Wikimedia Commons API (без ключа)."""
    headers = {
        "User-Agent": "ZenAgentsProject/1.0 (article illustration generator)"
    }
    # Wikimedia тоже лучше ищет на английском
    en_query = _translate_query(query)
    params = {
        "action": "query",
        "generator": "search",
        "gsrnamespace": "6",  # File namespace
        "gsrsearch": f"{en_query}",
        "gsrlimit": "10",
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 800,
        "format": "json",
        "utf8": 1,
    }
    try:
        resp = requests.get(WIKIMEDIA_URL, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            imageinfo = page.get("imageinfo", [])
            if imageinfo:
                img_url = imageinfo[0].get("thumburl") or imageinfo[0].get("url")
                if img_url:
                    return img_url
    except Exception:
        pass
    return None


def fetch_image(query: str) -> str | None:
    """Найти релевантную картинку для заданного запроса.

    Возвращает URL изображения или None.
    """
    # 1. DuckDuckGo
    url = _search_ddg(query)
    if url:
        return url

    # 2. Wikimedia Commons
    url = _search_wikimedia(query)
    if url:
        return url

    # 3. Fallback — Picsum
    print("  → DuckDuckGo и Wikimedia не нашли, использую случайное фото (Picsum)")
    return PICSUM_URL


def build_markdown_image(url: str, alt: str = "Иллюстрация") -> str:
    """Создать markdown-строку для вставки изображения."""
    return f"![{alt}]({url})"


if __name__ == "__main__":
    topic = input("Тема для поиска картинки: ")
    url = fetch_image(topic)
    if url:
        print(f"\n✅ Найдена: {url}")
        print(build_markdown_image(url, topic))
    else:
        print("\n❌ Картинка не найдена")
