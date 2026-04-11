"""
Trend Finder — генератор жизненных тем по психологии через DuckDuckGo.

Каждый раз выбираются 2-3 случайные фразы из списка жизненных проблем,
соединяются с модификаторами, ищутся в DuckDuckGo.
Результаты фильтруются, исключаются академические/скучные темы,
использованные темы записываются в used_topics.txt.
"""

import os
import random
from duckduckgo_search import DDGS

# ─── Жизненные фразы (конкретные проблемы обычных людей) ───
LIFE_PHRASES = [
    "как справиться с тревогой",
    "что делать при панической атаке",
    "как повысить самооценку",
    "как перестать прокрастинировать",
    "как справиться с выгоранием",
    "как полюбить себя",
    "как наладить отношения с партнёром",
    "как справиться с бессонницей",
    "как найти мотивацию",
    "как перестать себя критиковать",
    "как справиться с одиночеством",
    "как выстроить личные границы",
    "как справиться с гневом",
    "как отпустить обиду",
    "как обрести уверенность в себе",
    "как справиться с апатией",
    "как пережить кризис среднего возраста",
    "как справиться с ревностью",
    "как улучшить память и внимание",
    "как справиться с зависимостью от соцсетей",
]

# ─── Модификаторы для составления запросов ───
MODIFIERS = [
    "простые советы",
    "пошаговое руководство",
    "практические упражнения",
    "история из жизни",
]

# ─── Ключевые слова для фильтрации (должно быть хотя бы одно ПСИХОЛОГИЧЕСКОЕ) ───
INCLUDE_KEYWORDS = [
    "тревог", "паник", "самооценк", "выгоран", "прокрастинац",
    "бессонниц", "мотивац", "одиночеств", "обида", "гнев",
    "уверенност", "апати", "кризис", "ревност", "память", "внимани",
    "зависимост", "отношен", "партнёр", "психолог", "совет психолог",
    "полюбить себя", "личные границы", "стресс", "депресс",
    "соцсет", "социальн", "самокритик", "перфекционизм",
    "пережить", "наладить отношения", "полюбить", "границы",
]

# ─── Стоп-слова — исключаем академические и скучные темы ───
EXCLUDE_WORDS = [
    "тренды", "2025", "2026", "прогнозы", "будущее",
    "вкр", "диплом", "научн", "исследование", "анализ", "перспективы",
]

USED_TOPICS_FILE = os.path.join(os.path.dirname(__file__), "used_topics.txt")


def _load_used_topics() -> set[str]:
    """Загрузить список использованных тем из файла."""
    if os.path.exists(USED_TOPICS_FILE):
        with open(USED_TOPICS_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def _save_used_topics(topics: set[str]) -> None:
    """Добавить новые темы в файл использованных."""
    existing = _load_used_topics()
    existing.update(topics)
    with open(USED_TOPICS_FILE, "w", encoding="utf-8") as f:
        for t in sorted(existing):
            f.write(t + "\n")


def _reset_used_topics() -> None:
    """Очистить файл использованных тем."""
    if os.path.exists(USED_TOPICS_FILE):
        os.remove(USED_TOPICS_FILE)


def _build_queries(count: int = 10) -> list[str]:
    """Случайным образом составить поисковые запросы из фраз и модификаторов."""
    queries = []
    for _ in range(count):
        # Берём 2-3 случайные фразы
        n_phrases = random.randint(2, 3)
        phrases = random.sample(LIFE_PHRASES, n_phrases)
        # Добавляем случайный модификатор
        modifier = random.choice(MODIFIERS)
        # Соединяем
        query = " + ".join(phrases) + " " + modifier
        queries.append(query)
    return queries


def search(query: str, max_results: int = 10) -> list[str]:
    """Вернуть заголовки из DuckDuckGo для запроса."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return [r["title"] for r in results if r.get("title")]
    except Exception as e:
        print(f"[!] Search error ({query[:60]}...): {e}")
        return []


def _has_keyword(title: str) -> bool:
    """Проверить, что заголовок содержит хотя бы одно ключевое слово."""
    lower = title.lower()
    return any(kw in lower for kw in INCLUDE_KEYWORDS)


def _has_excluded_word(title: str) -> bool:
    """Проверить, что заголовок содержит стоп-слово."""
    lower = title.lower()
    return any(w in lower for w in EXCLUDE_WORDS)


def filter_titles(titles: list[str]) -> list[str]:
    """Отфильтровать: включить по ключевым словам, исключить по стоп-словам."""
    return [
        t for t in titles
        if _has_keyword(t) and not _has_excluded_word(t)
    ]


def dedupe(items: list[str]) -> list[str]:
    """Удалить дубликаты с сохранением порядка."""
    return list(dict.fromkeys(items))


def get_random_psychology_topics(count: int = 5, use_ai_ranking: bool = False) -> list[str]:
    """Вернуть *count* разных жизненных тем, которых ещё не было.

    Если все найденные темы уже использовались — сбрасывает used_topics.txt.
    """
    used = _load_used_topics()

    # Составляем запросы
    queries = _build_queries(count=12)
    all_titles: list[str] = []

    for q in queries:
        print(f"Поиск: {q[:70]}...")
        results = search(q, max_results=8)
        filtered = filter_titles(results)
        all_titles.extend(filtered)

    unique = dedupe(all_titles)

    # Убираем уже использованные
    fresh = [t for t in unique if t not in used]

    # Если ничего свежего нет — сбрасываем историю
    if not fresh and unique:
        print("\n🔄 Все темы использованы — сбрасываю историю.")
        _reset_used_topics()
        used = set()
        fresh = unique

    if not fresh:
        return []

    # Берём случайную выборку
    selected = random.sample(fresh, min(count, len(fresh)))

    # Сохраняем как использованные
    _save_used_topics(set(selected))

    return selected


def main() -> None:
    print("🔍 Поиск жизненных тем...\n")
    topics = get_random_psychology_topics(5)
    if not topics:
        print("❌ Темы не найдены.")
        return

    print("\n🔥 Темы для статей:\n")
    for i, title in enumerate(topics, 1):
        print(f"{i}. {title}")


if __name__ == "__main__":
    main()
