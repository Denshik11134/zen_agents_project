def _generate_article_job(job_id: str, user_topic: str | None, user_format: str = "article", user_style: str = "neutral") -> None:
    """Фоновая задача генерации статьи."""
    try:
        # 1. Определяем тему
        if user_topic and user_topic.strip():
            topic = user_topic.strip()
            _log(job_id, f"Используем указанную тему: {topic}")
        else:
            _log(job_id, "Ошибка: тема не указана. Пожалуйста, введите тему статьи.")
            _generation_status[job_id] = "error"
            return

        # 2. Логируем полученные формат и стиль
        _log(job_id, f"Формат: {user_format}, Стиль: {user_style}")

        # 3. Генерируем статью через GitHub Models (GPT-4o-mini)
        _log(job_id, "Генерация статьи через GitHub Models (GPT-4o-mini)...")
        article_text = generate_article(topic, "", user_format, user_style)

        if article_text is None:
            _log(job_id, "ERROR: Ошибка генерации статьи. Проверьте GITHUB_TOKEN в файле .env.")
            _generation_status[job_id] = "error"
            return

        _log(job_id, "Статья сгенерирована.")

        # 4. Формируем финальный текст (без картинок)
        final_text = f"# {topic}\n\n{article_text}"

        # 5. Сохраняем
        articles_dir = PROJECT_DIR / "articles"
        articles_dir.mkdir(exist_ok=True)
        safe_name = topic.replace(" ", "_").replace("/", "_").replace("\\", "_")
        # Ограничиваем длину имени файла
        if len(safe_name) > 80:
            safe_name = safe_name[:80]
        filename = f"{safe_name}.md"
        filepath = articles_dir / filename

        # Если файл уже существует — добавляем суффикс
        counter = 1
        while filepath.exists():
            filename = f"{safe_name}_{counter}.md"
            filepath = articles_dir / filename
            counter += 1

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(final_text)

          _log(job_id, f"Статья сохранена: articles/{filename}")

        _generation_status[job_id] = "done"
        _generation_results[job_id] = {
            "topic": topic,
            "article": final_text,
            "filename": filename,
            "filepath": str(filepath),
        }

    except Exception as e:
        _log(job_id, f"ERROR: Неожиданная ошибка: {e}")
        _generation_status[job_id] = "error"


# ─── Маршруты ───


@app.route("/")
def index():
    """Главная страница с формой."""
    return render_template("index.html")


@app.route("/privacy")
def privacy():
    """Политика конфиденциальности."""
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    """Условия использования."""
    return render_template("terms.html")


@app.route("/about")
def about():
    """О проекте."""
    return render_template("about.html")


@app.route("/contacts")
def contacts():
    """Контакты."""
    return render_template("contacts.html")


@app.route("/generate", methods=["POST"])
def generate():
    """Запустить генерацию статьи."""
    data = request.get_json(force=True)
    topic = data.get("topic", "").strip()
    format = data.get("format", "article")   # 👈 ДОБАВИТЬ
    style = data.get("style", "neutral")     # 👈 ДОБАВИТЬ

    job_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    _generation_logs[job_id] = []
    _generation_status[job_id] = "running"

    thread = threading.Thread(
        target=_generate_article_job, 
        args=(job_id, topic or None, format, style),  # 👈 ИЗМЕНИТЬ
        daemon=True
    )
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/status/<job_id>")
def status(job_id: str):
    """Получить статус задачи и логи."""
    logs = _generation_logs.get(job_id, [])
    status = _generation_status.get(job_id, "unknown")
    result = _generation_results.get(job_id)

    return jsonify({
        "job_id": job_id,
        "status": status,
        "logs": logs,
        "result": result,
    })


@app.route("/stream/<job_id>")
def stream(job_id: str):
    """Server-Sent Events для вывода логов в реальном времени."""
    def event_stream():
        last_index = 0
        while True:
            logs = _generation_logs.get(job_id, [])
            new_logs = logs[last_index:]
            for log_line in new_logs:
                yield f"data: {log_line}\n\n"
            last_index = len(logs)

            current_status = _generation_status.get(job_id, "unknown")
            if current_status in ("done", "error"):
                yield f"data: __STATUS__:{current_status}\n\n"
                break
            time.sleep(0.5)

    return Response(event_stream(), mimetype="text/event-stream")


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Внутренняя ошибка сервера"}), 500


if __name__ == "__main__":
    print("=" * 50)
    print("  Генератор статей — Яндекс.Дзен")
    print("=" * 50)
    print()
    print("  Откройте в браузере: http://0.0.0.0:5000")
    print()
    print("  Нажмите Ctrl+C для остановки.")
    print("=" * 50)
    print()
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
