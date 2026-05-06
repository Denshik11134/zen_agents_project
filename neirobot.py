import asyncio
import logging
import os
import sys
import traceback
from datetime import datetime, timedelta
from aiohttp import web

import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ============ ЛОГИРОВАНИЕ ============
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("neirobot")

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

# ============ HTTP-КЛИЕНТ (создаётся в main) ============
http_client: httpx.AsyncClient | None = None


# ============ ОПРЕДЕЛЕНИЕ ЯЗЫКА ============
def detect_language(text: str) -> str:
    if not text:
        return "ru"
    if any("а" <= c <= "я" or "А" <= c <= "Я" for c in text):
        return "ru"
    return "en"


# ============ УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ============
def init_user(user_id: int):
    if user_id not in users:
        users[user_id] = {
            "free": 3,
            "plan": "free",
            "trial_until": None,
            "trial_used": False,
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


# ============ ГЕНЕРАЦИЯ (через OpenRouter — стабильнее) ============
async def _call_openrouter(model: str, system_text: str, prompt: str,
                           temperature: float, max_tokens: int) -> str:
    """Единая точка вызова OpenRouter API."""
    if not OPENROUTER_KEY:
        return "⚠️ OPENROUTER_KEY не настроен."
    if http_client is None:
        return "⚠️ HTTP-клиент не инициализирован."

    try:
        response = await http_client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "X-Title": "NeirostatBot",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_text},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )
        data = response.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        log.error("OpenRouter unexpected response: %s", data)
        return f"⚠️ Сервис вернул неожиданный ответ: {str(data)[:200]}"
    except httpx.TimeoutException:
        log.exception("OpenRouter timeout")
        return "⚠️ Таймаут запроса к AI. Попробуйте позже."
    except Exception as e:
        log.exception("OpenRouter error")
        return f"⚠️ Ошибка AI: {str(e)[:200]}"


async def generate_text(prompt: str, lang: str = "ru") -> str:
    system_text = (
        "Ты — полезный ассистент. Отвечай подробно, с примерами, на русском языке."
        if lang == "ru"
        else "You are a helpful assistant. Answer in detail with examples, in English."
    )
    return await _call_openrouter(
        "deepseek/deepseek-chat", system_text, prompt, 0.7, 2000
    )


async def generate_premium(prompt: str, lang: str = "ru") -> str:
    system_text = (
        "Ты — профессиональный копирайтер с 10-летним опытом. Пиши структурированно: "
        "заголовок H1, подзаголовки H2, списки, примеры. На русском языке."
        if lang == "ru"
        else "You are a professional copywriter. Write structured: H1, H2, bullet points. In English."
    )
    return await _call_openrouter(
        "deepseek/deepseek-chat", system_text, prompt, 0.8, 2500
    )


async def generate_code(task: str, lang: str = "ru") -> str:
    system_text = (
        "Ты — Senior Developer. Пиши чистый, работающий код с комментариями на русском. Выводи только код."
        if lang == "ru"
        else "You are a Senior Developer. Write clean code. Output only code."
    )
    return await _call_openrouter(
        "deepseek/deepseek-chat", system_text, task, 0.2, 3000
    )


# ============ ТЕКСТЫ ============
def t(key: str, lang: str = "ru") -> str:
    texts = {
        "limit": {
            "ru": f"❌ Лимит исчерпан!\n🎁 /trial — 3 дня (мест: {MAX_TRIALS - trial_count})\n💳 /buy — 200₽/мес",
            "en": f"❌ Limit reached!\n🎁 /trial — 3 days ({MAX_TRIALS - trial_count} spots)\n💳 /buy — $2/month",
        },
        "trial_ok": {
            "ru": "🎁 3 дня премиум!\n✅ Безлимит текста\n✅ Генерация кода\n📝 /write тема\n💻 /code задача",
            "en": "🎁 3 days premium!\n✅ Unlimited text\n✅ Code gen\n📝 /write topic\n💻 /code task",
        },
        "trial_used": {
            "ru": "❌ Триал использован.\n💳 /buy — 200₽/мес",
            "en": "❌ Trial used.\n💳 /buy — $2/month",
        },
        "no_trials": {
            "ru": "❌ Мест нет.\n💳 /buy — 200₽/мес",
            "en": "❌ No spots.\n💳 /buy — $2/month",
        },
        "code_no": {
            "ru": "💻 Только премиум.\n🎁 /trial — 3 дня",
            "en": "💻 Premium only.\n🎁 /trial — 3 days",
        },
        "buy": {
            "ru": "💳 Премиум — 200₽/мес\n💻 Код — 100₽/раз\n📩 @neirostat_bot",
            "en": "💳 Premium — $2/month\n💻 Code — $1/gen\n📩 @neirostat_bot",
        },
    }
    return texts.get(key, {}).get(lang, "")


# ============ КОМАНДЫ ============
async def cmd_ping(message: types.Message):
    """Тестовая команда — без вызова API."""
    log.info("CMD /ping from user_id=%s", message.from_user.id)
    await message.answer("Pong! 🏓")


async def cmd_start(message: types.Message):
    log.info("CMD /start from user_id=%s text=%r", message.from_user.id, message.text)
    user_id = message.from_user.id
    init_user(user_id)
    access = check_access(user_id)
    user = users[user_id]

    welcome = "🤖 AI Content Generator\n\n📝 /write тема\n💻 /code задача\n👑 /premium тема\n🏓 /ping — проверка\n\n"
    if access == "free":
        welcome += f"🆓 {user['free']} бесплатно\n🎁 /trial — 3 дня (мест: {MAX_TRIALS - trial_count})!\n💳 /buy"
    elif access == "trial":
        remaining = user["trial_until"] - datetime.now()
        welcome += f"🎁 Триал: ~{int(remaining.total_seconds() // 3600)} ч\n👑 Всё открыто!"
    elif access == "premium":
        welcome += "👑 Премиум активен!"
    await message.answer(welcome)


async def cmd_trial(message: types.Message):
    log.info("CMD /trial from user_id=%s", message.from_user.id)
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
    log.info("CMD /write from user_id=%s", message.from_user.id)
    user_id = message.from_user.id
    init_user(user_id)
    prompt = (message.text or "").replace("/write", "", 1).strip()
    lang = detect_language(prompt)

    if not prompt:
        return await message.answer("📝 /write Как выбрать ноутбук")
    if not can_generate_text(user_id):
        return await message.answer(t("limit", lang))

    msg = await message.answer("✍️ Генерирую...")
    try:
        access = check_access(user_id)
        result = await (
            generate_premium(prompt, lang)
            if access in ["trial", "premium"]
            else generate_text(prompt, lang)
        )
        if access == "free":
            users[user_id]["free"] -= 1
        if len(result) > 4000:
            await msg.edit_text(result[:3900] + "...")
            await message.answer(result[3900:])
        else:
            await msg.edit_text(result)
    except Exception as e:
        log.exception("cmd_write failed")
        await msg.edit_text(f"❌ Ошибка: {str(e)[:100]}")


async def cmd_code(message: types.Message):
    log.info("CMD /code from user_id=%s", message.from_user.id)
    user_id = message.from_user.id
    init_user(user_id)
    prompt = (message.text or "").replace("/code", "", 1).strip()
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
        log.exception("cmd_code failed")
        await msg.edit_text(f"❌ Ошибка: {str(e)[:100]}")


async def cmd_premium(message: types.Message):
    log.info("CMD /premium from user_id=%s", message.from_user.id)
    user_id = message.from_user.id
    init_user(user_id)
    prompt = (message.text or "").replace("/premium", "", 1).strip()
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
        log.exception("cmd_premium failed")
        await msg.edit_text(f"❌ Ошибка: {str(e)[:100]}")


async def cmd_status(message: types.Message):
    log.info("CMD /status from user_id=%s", message.from_user.id)
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
    log.info("CMD /buy from user_id=%s", message.from_user.id)
    await message.answer(t("buy", "ru"))


# ============ MIDDLEWARE: лог всех входящих сообщений ============
async def log_all_messages(message: types.Message):
    """Catch-all хендлер — логирует ВСЕ входящие сообщения."""
    log.info(
        "MSG from user_id=%s username=@%s text=%r",
        message.from_user.id,
        message.from_user.username,
        message.text,
    )


# ============ WEBHOOK & HEALTH CHECK ============
router = web.RouteTableDef()


@router.get("/health")
async def health_check(request):
    return web.Response(text="OK")


@router.post("/webhook")
async def telegram_webhook(request):
    bot = request.app["bot"]
    dp = request.app["dp"]

    try:
        update = await request.json()
        await dp.feed_update(bot, types.Update(**update))
    except Exception as e:
        logging.exception("Webhook error: %s", e)

    return web.Response(text="OK")


async def on_startup(app):
    bot = app["bot"]
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        await bot.set_webhook(f"{webhook_url}/webhook")
        logging.info("Webhook set to: %s/webhook", webhook_url)


async def on_shutdown(app):
    bot = app["bot"]
    await bot.delete_webhook()
    logging.info("Webhook deleted")


# ============ ЗАПУСК ============
async def main():
    global http_client

    port = int(os.getenv("PORT", 8080))

    http_client = httpx.AsyncClient(timeout=60.0)
    log.info("HTTP client initialized")

    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()

    # Регистрация команд
    dp.message.register(cmd_ping, Command("ping"))
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_trial, Command("trial"))
    dp.message.register(cmd_write, Command("write"))
    dp.message.register(cmd_code, Command("code"))
    dp.message.register(cmd_premium, Command("premium"))
    dp.message.register(cmd_status, Command("status"))
    dp.message.register(cmd_buy, Command("buy"))
    dp.message.register(log_all_messages)

    # Проверка коннекта к Telegram
    try:
        me = await bot.get_me()
        log.info("Bot connected: @%s (id=%s)", me.username, me.id)
    except Exception as e:
        log.error("FAILED to connect to Telegram: %s", e)
        log.error(traceback.format_exc())
        log.error(
            "WinError 121 / connection timeout обычно означает блокировку "
            "Telegram провайдером. Используйте VPN или прокси."
        )
        await http_client.aclose()
        return

    # Создаём aiohttp приложение
    app = web.Application()
    app["bot"] = bot
    app["dp"] = dp
    app.router.add_routes(router)

    # Startup/shutdown хуки
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_shutdown)

    log.info("Starting webhook server on port %s...", port)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    log.info("Bot started! Webhook ready at /webhook, health at /health")

    # Keep running
    try:
        await asyncio.Event().wait()
    finally:
        await http_client.aclose()
        await bot.session.close()
        await runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Bot stopped by user")
    except Exception:
        log.exception("Fatal error")
