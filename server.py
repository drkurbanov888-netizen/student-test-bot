import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters
)

TOKEN = "9247629027:AAHVWlwGdEq2man8hx9GHwI764PjXzWXY9E"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Список из 10 вопросов для теста
QUESTIONS = [
    "1. Какой орган отвечает за фильтрацию крови в организме человека?",
    "2. Какой отдел кишечника является самым длинным?",
    "3. Какой витамин синтезируется в коже под действием солнечных лучей?",
    "4. Какая железа вырабатывает инсулин?",
    "5. Как называется основной фермент желудочного сока, расщепляющий белки?",
    "6. Какой газ преобладает во вдыхаемом воздухе?",
    "7. Нормальная температура здорового человека (в градусах Цельсия)?",
    "8. Сколько камер у сердца человека?",
    "9. Какая группа крови является универсальной для переливания?",
    "10. Какой орган человека обладает способностью к наибольшей регенерации?"
]

# Функция старта теста
async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['answers'] = []
    context.user_data['current_q'] = 0
    
    await update.message.reply_text(
        "📝 Добро пожаловать на тестирование!\n"
        "Вам предстоит ответить на 10 вопросов.\n\n"
        f"<b>Вопрос 1 из 10:</b>\n{QUESTIONS[0]}",
        parse_mode="HTML"
    )
    return 0

# Функция обработки ответов на вопросы
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_q_index = context.user_data.get('current_q', 0)
    user_answer = update.message.text
    
    # Сохраняем ответ
    answers = context.user_data.setdefault('answers', [])
    answers.append({
        "question": QUESTIONS[current_q_index],
        "answer": user_answer
    })
    
    # Переходим к следующему вопросу
    current_q_index += 1
    context.user_data['current_q'] = current_q_index
    
    if current_q_index < len(QUESTIONS):
        # Задаем следующий вопрос
        await update.message.reply_text(
            f"Ответ принят! ✅\n\n<b>Вопрос {current_q_index + 1} из 10:</b>\n{QUESTIONS[current_q_index]}",
            parse_mode="HTML"
        )
        return current_q_index
    else:
        # Тест завершен
        result_text = "🎉 <b>Тест успешно завершен! Спасибо!</b>\n\nВаши ответы:\n"
        for i, item in enumerate(answers, 1):
            result_text += f"\n{i}. {item['question']}\nОтвет: <i>{item['answer']}</i>\n"
        
        await update.message.reply_text(result_text, parse_mode="HTML")
        
        # Вывод в терминал преподавателя
        print(f"Студент {update.effective_user.full_name} завершил тест!")
        for item in answers:
            print(f" - {item['question']}: {item['answer']}")
            
        return ConversationHandler.END

async def cancel_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Тестирование отменено.")
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Динамически создаем состояния для всех 10 вопросов
    states_dict = {}
    for i in range(len(QUESTIONS)):
        states_dict[i] = [MessageHandler(filters.TEXT & (~filters.COMMAND), handle_answer)]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("test", start_test)],
        states=states_dict,
        fallbacks=[CommandHandler("cancel", cancel_test)],
    )

    application.add_handler(conv_handler)
    
    print("Бот с тестом на 10 вопросов успешно запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()