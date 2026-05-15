import { motion } from "framer-motion";
import Head from "next/head";
import { useState, type FormEvent } from "react";

// ---------- Иконки для форматов ----------
const icons = {
  article: (
    <svg className="w-12 h-12 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  ),
  post: (
    <svg className="w-12 h-12 text-pink-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
  ),
  thread: (
    <svg className="w-12 h-12 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
    </svg>
  ),
  script: (
    <svg className="w-12 h-12 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
  ),
  ad: (
    <svg className="w-12 h-12 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
    </svg>
  ),
  content: (
    <svg className="w-12 h-12 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
    </svg>
  ),
};

// ---------- Данные ----------
const formatCards = [
  { title: "Статьи", icon: icons.article },
  { title: "Посты для соцсетей", icon: icons.post },
  { title: "Треды для X (Twitter)", icon: icons.thread },
  { title: "Сценарии видео", icon: icons.script },
  { title: "Рекламные посты", icon: icons.ad },
  { title: "Любой контент", icon: icons.content },
];

const steps = [
  {
    number: "01",
    title: "Выбери формат",
    desc: "Выбери тип контента: статья, пост, тред, сценарий или реклама.",
  },
  {
    number: "02",
    title: "Опиши тему",
    desc: "Напиши ключевые слова или краткое описание того, что нужно сгенерировать.",
  },
  {
    number: "03",
    title: "Получи результат",
    desc: "AI создаст уникальный текст за секунды. Ты можешь редактировать или сразу публиковать.",
  },
];

const plans = [
  {
    name: "Бесплатный",
    price: "0 ₽",
    features: ["3 генерации текста", "Стандартное качество", "Без приоритета"],
    cta: "Попробовать",
    highlighted: false,
  },
  {
    name: "Премиум",
    price: "200 ₽ / мес",
    features: ["Неограниченные генерации", "Высокое качество (DeepSeek)", "Приоритетная очередь", "Доступ к новым моделям"],
    cta: "Оформить",
    highlighted: true,
  },
];

const testimonials = [
  {
    name: "Мария",
    role: "SMM‑менеджер",
    text: "Neirostat экономит мне часы работы. Пишу посты в 5 раз быстрее!",
  },
  {
    name: "Алексей",
    role: "Блогер",
    text: "Треды получаются живыми и вовлекающими. Подписчики в восторге.",
  },
  {
    name: "Елена",
    role: "Копирайтер",
    text: "Пользуюсь Премиумом – качество на уровне топ‑авторов. Очень рекомендую.",
  },
];

// ---------- Компоненты анимации ----------
const fadeInUp = {
  hidden: { opacity: 0, y: 40 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.5, ease: "easeOut" },
  }),
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

// ---------- Секция Hero ----------
const Hero = () => (
  <section className="relative flex flex-col items-center justify-center min-h-screen px-6 text-center overflow-hidden">
    {/* Фоновый градиент */}
    <div className="absolute inset-0 bg-gradient-to-b from-cyan-900/20 via-slate-900 to-slate-900 pointer-events-none" />

    <motion.div
      className="relative z-10 max-w-3xl"
      initial={{ opacity: 0, y: 60 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
    >
      <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold leading-tight bg-gradient-to-r from-cyan-300 via-purple-300 to-pink-300 bg-clip-text text-transparent">
        Создавай контент с&nbsp;помощью&nbsp;AI
      </h1>
      <p className="mt-6 text-lg sm:text-xl text-gray-300 max-w-xl mx-auto">
        neirostat.ru — генератор статей, постов, тредов, сценариев и рекламы. 
        Бесплатно и без регистрации.
      </p>
      <motion.a
        href="#formats"
        className="mt-8 inline-block px-8 py-4 rounded-full bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-semibold text-lg shadow-lg hover:shadow-cyan-500/30 transition-all"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        Начать бесплатно
      </motion.a>
    </motion.div>

    {/* Декоративные круги */}
    <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
    <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl" />
  </section>
);

// ---------- Секция Форматов ----------
const Formats = () => (
  <section id="formats" className="py-20 px-6 max-w-6xl mx-auto">
    <motion.h2
      className="text-3xl sm:text-4xl font-bold text-center mb-12"
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      Форматы контента
    </motion.h2>

    <motion.div
      className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
      variants={staggerContainer}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-50px" }}
    >
      {formatCards.map((card, i) => (
        <motion.div
          key={card.title}
          className="group relative bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 hover:border-cyan-400/50 transition-colors"
          variants={fadeInUp}
          custom={i}
          whileHover={{ y: -5, boxShadow: "0 10px 40px rgba(0,0,0,0.3)" }}
        >
          <div className="mb-4">{card.icon}</div>
          <h3 className="text-xl font-semibold">{card.title}</h3>
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-cyan-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
        </motion.div>
      ))}
    </motion.div>
  </section>
);

// ---------- Секция Как это работает ----------
const HowItWorks = () => (
  <section className="py-20 px-6 bg-slate-800/50">
    <div className="max-w-5xl mx-auto">
      <motion.h2
        className="text-3xl sm:text-4xl font-bold text-center mb-12"
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
      >
        Как это работает
      </motion.h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {steps.map((step, i) => (
          <motion.div
            key={step.number}
            className="flex flex-col items-center text-center"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.2, duration: 0.5 }}
          >
            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-cyan-400 to-purple-600 flex items-center justify-center text-2xl font-bold mb-4">
              {step.number}
            </div>
            <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
            <p className="text-gray-400">{step.desc}</p>
          </motion.div>
        ))}
      </div>
    </div>
  </section>
);

// ---------- Секция Тарифы ----------
const Pricing = () => (
  <section id="pricing" className="py-20 px-6 max-w-5xl mx-auto">
    <motion.h2
      className="text-3xl sm:text-4xl font-bold text-center mb-12"
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      Тарифы
    </motion.h2>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
      {plans.map((plan) => (
        <motion.div
          key={plan.name}
          className={`relative rounded-3xl p-8 border ${
            plan.highlighted
              ? "border-cyan-400 bg-gradient-to-b from-cyan-900/30 to-purple-900/30 shadow-2xl shadow-cyan-500/20"
              : "border-white/10 bg-white/5"
          }`}
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          whileHover={{ scale: 1.02 }}
        >
          {plan.highlighted && (
            <div className="absolute -top-3 right-6 bg-gradient-to-r from-yellow-300 to-orange-400 text-black text-xs font-bold px-3 py-1 rounded-full">
              ХИТ
            </div>
          )}
          <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
          <p className="text-3xl font-extrabold mb-6">{plan.price}</p>
          <ul className="space-y-3 mb-8">
            {plan.features.map((f) => (
              <li key={f} className="flex items-start gap-2">
                <svg className="w-5 h-5 mt-0.5 text-cyan-400 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-300">{f}</span>
              </li>
            ))}
          </ul>
          <motion.a
            href={plan.highlighted ? "/premium" : "/generate"}
            className={`block text-center py-3 rounded-xl font-semibold ${
              plan.highlighted
                ? "bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-400 hover:to-purple-500 text-white"
                : "bg-white/10 hover:bg-white/20 text-white"
            } transition-all`}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
          >
            {plan.cta}
          </motion.a>
        </motion.div>
      ))}
    </div>
  </section>
);

// ---------- Секция Отзывы ----------
const Testimonials = () => (
  <section className="py-20 px-6 bg-slate-800/30">
    <div className="max-w-5xl mx-auto">
      <motion.h2
        className="text-3xl sm:text-4xl font-bold text-center mb-12"
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
      >
        Отзывы
      </motion.h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {testimonials.map((t, i) => (
          <motion.div
            key={t.name}
            className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.15, duration: 0.5 }}
          >
            <p className="text-gray-300 italic mb-4">“{t.text}”</p>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-400 to-purple-600 flex items-center justify-center text-sm font-bold">
                {t.name[0]}
              </div>
              <div>
                <p className="font-semibold">{t.name}</p>
                <p className="text-sm text-gray-500">{t.role}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  </section>
);

// ---------- Форма обратной связи ----------
const ContactForm = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    // Здесь можно реализовать отправку (пока заглушка)
    alert("Спасибо! Мы свяжемся с вами.");
    setName("");
    setEmail("");
    setMessage("");
  };

  return (
    <section id="contact" className="py-20 px-6 max-w-xl mx-auto">
      <motion.h2
        className="text-3xl sm:text-4xl font-bold text-center mb-8"
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
      >
        Обратная связь
      </motion.h2>

      <motion.form
        onSubmit={handleSubmit}
        className="space-y-5"
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <input
          type="text"
          placeholder="Ваше имя"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400 transition-colors"
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400 transition-colors"
        />
        <textarea
          placeholder="Ваше сообщение"
          rows={4}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          required
          className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400 transition-colors resize-none"
        />
        <motion.button
          type="submit"
          className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-600 font-semibold text-white hover:shadow-lg hover:shadow-cyan-500/20 transition-all"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Отправить
        </motion.button>
      </motion.form>
    </section>
  );
};

// ---------- Футер ----------
const Footer = () => (
  <footer className="border-t border-white/10 py-8 px-6">
    <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-gray-500">
      <p>&copy; {new Date().getFullYear()} neirostat.ru — AI генератор контента</p>
      <nav className="flex gap-6">
        <a href="/privacy" className="hover:text-cyan-400 transition-colors">Конфиденциальность</a>
        <a href="/terms" className="hover:text-cyan-400 transition-colors">Условия</a>
        <a href="/contacts" className="hover:text-cyan-400 transition-colors">Контакты</a>
      </nav>
    </div>
  </footer>
);

// ---------- Главная страница ----------
export default function Home() {
  return (
    <>
      <Head>
        <title>neirostat.ru — AI генератор контента</title>
        <meta name="description" content="Генератор статей, постов, тредов, сценариев и рекламы на основе искусственного интеллекта. Бесплатно." />
      </Head>

      <main className="min-h-screen bg-slate-950 text-white">
        <Hero />
        <Formats />
        <HowItWorks />
        <Pricing />
        <Testimonials />
        <ContactForm />
        <Footer />
      </main>
    </>
  );
}
