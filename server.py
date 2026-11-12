import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Токен вашего бота
TOKEN = "9247629027:AAHVWlwGdEq2man8hx9GHwI764PjXzWXY9E"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Состояния разговора
GET_NAME, GET_GROUP, TESTING = range(3)

QUESTIONS = [
    {
        "question": "1. Что такое гастрит?",
        "options": ["А) Воспаление слизистой оболочки желудка", "Б) Заболевание печени", "В) Инфекция почек"],
        "correct": "А"
    },
    {
        "question": "2. Основная функция тонкого кишечника?",
        "options": ["А) Всасывание питательных веществ", "Б) Выработка желчи", "В) Фильтрация крови"],
        "correct": "А"
    }
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Для прохождения теста введите ваши **ФИО** (Фамилия Имя Отчество):",
        parse_mode="Markdown",
        protect_content=True
    )
    return GET_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student_name'] = update.message.text
    await update.message.reply_text(
        "Отлично. Теперь введите номер вашей **группы** (например, ИС-21):",
        parse_mode="Markdown",
        protect_content=True
    )
    return GET_GROUP

async def get_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student_group'] = update.message.text
    context.user_data['score'] = 0
    context.user_data['current_q'] = 0
    
    name = context.user_data['student_name']
    group = context.user_data['student_group']
    
    await update.message.reply_text(
        f"Спасибо, {name} (группа {group}). Начинаем тест! Вопросы защищены от копирования.",
        protect_content=True
    )
    return await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q_index = context.user_data['current_q']
    
    if q_index < len(QUESTIONS):
        q_data = QUESTIONS[q_index]
        text = f"*{q_data['question']}*\n\n" + "\n".join(q_data['options']) + "\n\n_(Напишите в ответ только букву правильного варианта: А, Б или В)_"
        
        await update.message.reply_text(text, parse_mode="Markdown", protect_content=True)
        return TESTING
    else:
        score = context.user_data['score']
        name = context.user_data['student_name']
        group = context.user_data['student_group']
        total = len(QUESTIONS)
        
        await update.message.reply_text(
            f"🎉 **Тест завершен!**\n\n"
            f"👤 Студент: {name}\n"
            f"🏫 Группа: {group}\n"
            f"📊 Результат: **{score} из {total}** правильных ответов.",
            parse_mode="Markdown",
            protect_content=True
        )
        return ConversationHandler.END

async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text.strip().upper()
    q_index = context.user_data['current_q']
    q_data = QUESTIONS[q_index]
    
    if user_answer.startswith(q_data['correct']):
        context.user_data['score'] += 1
        
    context.user_data['current_q'] += 1
    return await send_question(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Тест отменен.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Простой HTTP-сервер для того, чтобы Render считал веб-сервис живым
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

def main():
    # Запускаем HTTP-сервер в отдельном потоке для Render Web Service
    t = threading.Thread(target=run_http_server, daemon=True)
    t.start()

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("test", start)],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_group)],
            TESTING: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
