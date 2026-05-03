import asyncio
import json
import httpx
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession

import os

# ============ ТОКЕНЫ (из переменных окружения) ============
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set in environment variables")

# ============ БАЗА ПОЛЬЗОВАТЕЛЕЙ ============
users = {}
trial_count = 0
MAX_TRIALS = 10

# ============ HTTP-КЛИЕНТ ============
http_client = None

async def get_http_client():
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(timeout=60.0)
    return http_client

# ============ ОПРЕДЕЛЕНИЕ ЯЗЫКА ============
def detect_language(text: str) -> str:
    if not text:
        return "ru"
    if any('а' <= c <= 'я' or 'А' <= c <= 'Я' for c in text):
        return "ru"
    return "en"

# ============ УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ============
def init_user(user_id: int):
    if user_id not in users:
        users[user_id] = {
            "free": 3,
            "plan": "free",
            "trial_until": None,
            "trial_used": False
        }

def check_access(user_id: int) -> str:
    init_user(user_id)
    user = users[user_id]
    if user.get("trial_until") and datetime.now() < user["trial_until"]:
        return "trial"
    if user.get("plan") == "premium":
        return "premium"
    return "free"

def can_generate_text(user_id: int) -> bool:
    access = check_access(user_id)
    if access in ["trial", "premium"]:
        return True
    if access == "free" and users[user_id]["free"] > 0:
        return True
    return False

def can_generate_code(user_id: int) -> bool:
    return check_access(user_id) in ["trial", "premium"]

# ============ ГЕНЕРАЦИЯ ============
async def generate_text(prompt: str, lang: str = "ru"):
    client = await get_http_client()
    system_text = "Ты — полезный ассистент. Отвечай подробно, с примерами, на русском языке." if lang == "ru" else "You are a helpful assistant. Answer in detail with examples, in English."
    
    try:
        response = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": [{"role": "system", "content": system_text}, {"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 2000}
        )
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"DeepSeek error: {e}")
        return f"⚠️ Сервис временно недоступен. Попробуйте позже.\n\n{str(e)[:100]}"

async def generate_premium(prompt: str, lang: str = "ru"):
    client = await get_http_client()
    system_text = "Ты — профессиональный копирайтер с 10-летним опытом. Пиши структурированно: заголовок H1, подзаголовки H2, списки, примеры. На русском языке." if lang == "ru" else "You are a professional copywriter. Write structured: H1, H2, bullet points. In English."
    
    try:
        response = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": [{"role": "system", "content": system_text}, {"role": "user", "content": prompt}], "temperature": 0.8, "max_tokens": 2500}
        )
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Premium error: {e}")
        return await generate_text(prompt, lang)

async def generate_code(task: str, lang: str = "ru"):
    client = await get_http_client()
    system_text = "Ты — Senior Developer. Пиши чистый, работающий код с комментариями на русском. Выводи только код." if lang == "ru" else "You are a Senior Developer. Write clean code. Output only code."
    
    response = await client.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json", "X-Title": "NeirostatBot"},
        json={"model": "minimax/MiniMax-M2.5", "messages": [{"role": "system", "content": system_text}, {"role": "user", "content": task}], "temperature": 0.2, "max_tokens": 3000}
    )
    return response.json()["choices"][0]["message"]["content"]

# ============ ТЕКСТЫ ============
def t(key: str, lang: str = "ru") -> str:
    texts = {
        "limit": {"ru": f"❌ Лимит исчерпан!\n🎁 /trial — 3 дня (мест: {MAX_TRIALS - trial_count})\n💳 /buy — 200₽/мес", "en": f"❌ Limit reached!\n🎁 /trial — 3 days ({MAX_TRIALS - trial_count} spots)\n💳 /buy — $2/month"},
        "trial_ok": {"ru": "🎁 3 дня премиум!\n✅ Безлимит текста\n✅ Генерация кода\n📝 /write тема\n💻 /code задача", "en": "🎁 3 days premium!\n✅ Unlimited text\n✅ Code gen\n📝 /write topic\n💻 /code task"},
        "trial_used": {"ru": "❌ Триал использован.\n💳 /buy — 200₽/мес", "en": "❌ Trial used.\n💳 /buy — $2/month"},
        "no_trials": {"ru": "❌ Мест нет.\n💳 /buy — 200₽/мес", "en": "❌ No spots.\n💳 /buy — $2/month"},
        "code_no": {"ru": "💻 Только премиум.\n🎁 /trial — 3 дня", "en": "💻 Premium only.\n🎁 /trial — 3 days"},
        "buy": {"ru": "💳 Премиум — 200₽/мес\n💻 Код — 100₽/раз\n📩 @neirostat_bot", "en": "💳 Premium — $2/month\n💻 Code — $1/gen\n📩 @neirostat_bot"}
    }
    return texts.get(key, {}).get(lang, "")

# ============ КОМАНДЫ ============
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id)
    access = check_access(user_id)
    lang = detect_language(message.text or "")
    user = users[user_id]

    welcome = "🤖 AI Content Generator\n\n📝 /write тема\n💻 /code задача\n👑 /premium тема\n\n"
    if access == "free":
        welcome += f"🆓 {user['free']} бесплатно\n🎁 /trial — 3 дня (мест: {MAX_TRIALS - trial_count})!\n💳 /buy"
    elif access == "trial":
        remaining = user["trial_until"] - datetime.now()
        welcome += f"🎁 Триал: ~{int(remaining.total_seconds() // 3600)} ч\n👑 Всё открыто!"
    elif access == "premium":
        welcome += "👑 Премиум активен!"
    await message.answer(welcome)

async def cmd_trial(message: types.Message):
    global trial_count
    user_id = message.from_user.id
    init_user(user_id)
    user = users[user_id]
    lang = detect_language(message.text or "")

    if user.get("trial_used"):
        return await message.answer(t("trial_used", lang))
    if user.get("trial_until") and datetime.now() < user["trial_until"]:
        remaining = int((user["trial_until"] - datetime.now()).total_seconds() // 3600)
        return await message.answer(f"🎁 Триал активен! ~{remaining} ч")
    if trial_count >= MAX_TRIALS:
        return await message.answer(t("no_trials", lang))

    trial_count += 1
    user["trial_until"] = datetime.now() + timedelta(days=3)
    user["trial_used"] = True
    await message.answer(t("trial_ok", lang))

async def cmd_write(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id)
    prompt = message.text.replace("/write", "").strip()
    lang = detect_language(prompt)

    if not prompt:
        return await message.answer("📝 /write Как выбрать ноутбук")
    if not can_generate_text(user_id):
        return await message.answer(t("limit", lang))

    msg = await message.answer("✍️ Генерирую...")
    try:
        access = check_access(user_id)
        result = await (generate_premium(prompt, lang) if access in ["trial", "premium"] else generate_text(prompt, lang))
        if access == "free":
            users[user_id]["free"] -= 1
        if len(result) > 4000:
            await msg.edit_text(result[:3900] + "...")
            await message.answer(result[3900:])
        else:
            await msg.edit_text(result)
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {str(e)[:100]}")

async def cmd_code(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id)
    prompt = message.text.replace("/code", "").strip()
    lang = detect_language(prompt)

    if not prompt:
        return await message.answer("💻 /code Python парсер CSV")
    if not can_generate_code(user_id):
        return await message.answer(t("code_no", lang))

    msg = await message.answer("⚡ Генерирую код...")
    try:
        code = await generate_code(prompt, lang)
        filename = "code.py" if "python" in prompt.lower() else "code.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        await msg.delete()
        await message.answer_document(types.FSInputFile(filename), caption="💻 Код готов!")
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {str(e)[:100]}")

async def cmd_premium(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id)
    prompt = message.text.replace("/premium", "").strip()
    lang = detect_language(prompt)
    access = check_access(user_id)

    if access not in ["trial", "premium"]:
        return await message.answer("👑 Только премиум.\n🎁 /trial — 3 дня")
    if not prompt:
        return await message.answer("👑 /premium Стратегия продвижения")

    msg = await message.answer("👑 Премиум...")
    try:
        result = await generate_premium(prompt, lang)
        if len(result) > 4000:
            await msg.edit_text(result[:3900] + "...")
            await message.answer(result[3900:])
        else:
            await msg.edit_text(result)
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {str(e)[:100]}")

async def cmd_status(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id)
    access = check_access(user_id)
    user = users[user_id]

    if access == "free":
        text = f"🆓 Бесплатный\n📝 Осталось: {user['free']}\n🎁 Триал: {'доступен' if not user.get('trial_used') else 'использован'}"
    elif access == "trial":
        remaining = int((user["trial_until"] - datetime.now()).total_seconds() // 3600)
        text = f"🎁 Триал\n⏰ Осталось: ~{remaining} ч"
    elif access == "premium":
        text = "👑 Премиум"
    else:
        text = "Неизвестно"
    await message.answer(f"📊 {text}")

async def cmd_buy(message: types.Message):
    await message.answer(t("buy", "ru"))

# ============ ЗАПУСК ============
async def main():
    global http_client
    http_client = httpx.AsyncClient(timeout=60.0)

    session = AiohttpSession()
    bot = Bot(token=TELEGRAM_TOKEN, session=session)
    dp = Dispatcher()

    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_trial, Command("trial"))
    dp.message.register(cmd_write, Command("write"))
    dp.message.register(cmd_code, Command("code"))
    dp.message.register(cmd_premium, Command("premium"))
    dp.message.register(cmd_status, Command("status"))
    dp.message.register(cmd_buy, Command("buy"))

    print("Bot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())