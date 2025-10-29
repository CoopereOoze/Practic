# -*- coding: utf-8 -*-

import telebot
from telebot import types
import matplotlib.pyplot as plt
import io
import random

bot = telebot.TeleBot("8417675565:AAH_yO1evfTocEh-2Cx9V7vkDj6hM9cbLHk")

USER_DATA = {}
CATEGORIES = {
    'income': ['Зарплата', 'Фриланс', 'Инвестиции', 'Подарки', 'Прочее'],
    'expense': ['Еда', 'Транспорт', 'Жилье', 'Развлечения', 'Здоровье', 'Одежда', 'Техника', 'Образование', 'Прочее']
}

TEMP_DATA = {}

FINANCIAL_TIPS = [
    "Откладывайте 10-20% от каждого дохода на сбережения",
    "Используйте кэшбэк и cashback-сервисы при покупках",
    "Готовьте дома - это экономичнее ресторанов",
    "Ведите учет всех расходов для анализа трат",
    "Составляйте список покупок и не покупайте импульсивно",
    "Рассмотрите альтернативный транспорт для экономии",
    "Погашайте кредиты с высокими процентами в первую очередь",
    "Создайте финансовую подушку на 3-6 месяцев расходов",
    "Ставьте конкретные финансовые цели на месяц и год",
    "Планируйте крупные покупки заранее, избегая спонтанных"
]

def get_user_data(uid):
    if uid not in USER_DATA:
        USER_DATA[uid] = {
            'transactions': [],
            'budgets': {}
        }
    return USER_DATA[uid]

def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Добавить доход', 'Добавить расход')
    keyboard.row('Статистика', 'Бюджет')
    keyboard.row('Напоминания', 'Советы')
    keyboard.row('Сброс данных')
    return keyboard

def add_transaction_with_category(user_id, category, transaction_type):
    amount = TEMP_DATA[user_id]['amount']

    user_data = get_user_data(user_id)
    transaction = {
        'id': len(user_data['transactions']) + 1,
        'amount': amount,
        'category': category,
        'type': transaction_type
    }
    user_data['transactions'].append(transaction)

    del TEMP_DATA[user_id]
    bot.send_message(user_id, f"Транзакция добавлена!\nСумма: {amount:.2f} ₽\nКатегория: {category}", reply_markup=main_keyboard())

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = "Финансовый помощник\n\nДоходы/расходы, бюджеты, статистика"
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == 'Добавить доход')
def add_income(message):
    TEMP_DATA[message.from_user.id] = {'mode': 'income_amount'}
    msg = bot.send_message(message.chat.id, "Введите сумму дохода:")
    bot.register_next_step_handler(msg, process_income_amount)

def process_income_amount(message):
    user_id = message.from_user.id
    try:
        amount = float(message.text)
        if amount <= 0:
            bot.send_message(message.chat.id, "Сумма дохода должна быть положительной:")
            bot.register_next_step_handler(message, process_income_amount)
            return

        TEMP_DATA[user_id] = {'mode': 'income_category', 'amount': amount}

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for category in CATEGORIES['income']:
            keyboard.row(category)
        keyboard.row('Отмена')

        bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=keyboard)

    except ValueError:
        bot.send_message(message.chat.id, "Введите корректную сумму:")
        bot.register_next_step_handler(message, process_income_amount)

@bot.message_handler(func=lambda message: message.text == 'Добавить расход')
def add_expense(message):
    TEMP_DATA[message.from_user.id] = {'mode': 'expense_amount'}
    msg = bot.send_message(message.chat.id, "Введите сумму расхода:")
    bot.register_next_step_handler(msg, process_expense_amount)

def process_expense_amount(message):
    user_id = message.from_user.id
    try:
        amount = float(message.text)
        if amount <= 0:
            bot.send_message(message.chat.id, "Сумма расхода должна быть положительной:")
            bot.register_next_step_handler(message, process_expense_amount)
            return

        TEMP_DATA[user_id] = {'mode': 'expense_category', 'amount': amount}

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for category in CATEGORIES['expense']:
            keyboard.row(category)
        keyboard.row('Отмена')

        bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=keyboard)

    except ValueError:
        bot.send_message(message.chat.id, "Введите корректную сумму:")
        bot.register_next_step_handler(message, process_expense_amount)

@bot.message_handler(func=lambda message: message.from_user.id in TEMP_DATA and
                    TEMP_DATA[message.from_user.id].get('mode') == 'budget_category' and
                    message.text in CATEGORIES['expense'])
def process_budget_category(message):
    user_id = message.from_user.id
    category = message.text
    TEMP_DATA[user_id] = {'mode': 'budget_amount', 'category': category}
    bot.send_message(message.chat.id, f"Категория: {category}\nВведите лимит бюджета:")

@bot.message_handler(func=lambda message: message.text in CATEGORIES['income'] + CATEGORIES['expense'] and
                    message.from_user.id in TEMP_DATA)
def process_category_selection(message):
    user_id = message.from_user.id
    category = message.text
    mode = TEMP_DATA[user_id].get('mode')

    if mode == 'income_category' and category in CATEGORIES['income']:
        add_transaction_with_category(user_id, category, 'income')
    elif mode == 'expense_category' and category in CATEGORIES['expense']:
        add_transaction_with_category(user_id, category, 'expense')

@bot.message_handler(func=lambda message: message.text == 'Бюджет')
def budget_menu(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Установить бюджет', 'Просмотреть бюджеты')
    keyboard.row('Назад')
    bot.send_message(message.chat.id, "Управление бюджетами:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == 'Установить бюджет')
def set_budget(message):
    TEMP_DATA[message.from_user.id] = {'mode': 'budget_category'}
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for category in CATEGORIES['expense']:
        keyboard.row(category)
    keyboard.row('Назад')
    bot.send_message(message.chat.id, "Выберите категорию для бюджета:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.from_user.id in TEMP_DATA and
                    TEMP_DATA[message.from_user.id].get('mode') == 'budget_amount')
def process_budget_amount(message):
    user_id = message.from_user.id
    try:
        budget = float(message.text)
        if budget <= 0:
            bot.send_message(message.chat.id, "Бюджет должен быть положительным:")
            return

        category = TEMP_DATA[user_id]['category']
        user_data = get_user_data(user_id)
        user_data['budgets'][category] = budget

        del TEMP_DATA[user_id]
        bot.send_message(message.chat.id, f"Бюджет установлен: {category} - {budget:.2f} ₽", reply_markup=main_keyboard())

    except ValueError:
        bot.send_message(message.chat.id, "Введите корректную сумму:")

@bot.message_handler(func=lambda message: message.text == 'Просмотреть бюджеты')
def show_budgets(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

    if not user_data.get('budgets'):
        bot.send_message(message.chat.id, "Бюджеты не установлены")
        return

    category_expenses = {}
    for i in user_data['transactions']:
        if i['type'] == 'expense':
            category_expenses[i['category']] = category_expenses.get(i['category'], 0) + i['amount']

    text = "Ваши бюджеты:\n\n"
    for category, limit in user_data['budgets'].items():
        spent = category_expenses.get(category, 0)
        percentage = (spent / limit * 100) if limit > 0 else 0
        text += f"{category}: {spent:.2f} / {limit:.2f} ₽ ({percentage:.1f}%)\n"

    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: message.text == 'Напоминания')
def reminders_menu(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Действующие напоминания', 'Добавить напоминание')
    keyboard.row('Удалить напоминание', 'Назад')
    bot.send_message(message.chat.id, "Управление напоминаниями:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == 'Действующие напоминания')
def show_reminders(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    reminders = user_data.get('reminders', [])

    if not reminders:
        bot.send_message(message.chat.id, "Напоминаний нет")
    else:
        text = "Ваши напоминания:\n\n" + "\n".join(f"{i['id']}. {i['text']}" for i in reminders)
        bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: message.text == 'Добавить напоминание')
def add_reminder(message):
    TEMP_DATA[message.from_user.id] = {'mode': 'add_reminder'}
    bot.send_message(message.chat.id, "Введите текст напоминания:")

@bot.message_handler(func=lambda message: message.from_user.id in TEMP_DATA and
                    TEMP_DATA[message.from_user.id].get('mode') == 'add_reminder')
def process_reminder_text(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text:
        user_data = get_user_data(user_id)
        if 'reminders' not in user_data:
            user_data['reminders'] = []

        reminder_id = len(user_data['reminders']) + 1
        user_data['reminders'].append({'id': reminder_id, 'text': text})
        del TEMP_DATA[user_id]
        bot.send_message(message.chat.id, f"Напоминание #{reminder_id} добавлено!", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == 'Удалить напоминание')
def delete_reminder_menu(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    reminders = user_data.get('reminders', [])

    if not reminders:
        bot.send_message(message.chat.id, "Напоминаний для удаления нет")
    else:
        text = "Введите номер напоминания для удаления:\n\n" + "\n".join(f"{r['id']}. {r['text']}" for r in reminders)
        TEMP_DATA[user_id] = {'mode': 'delete_reminder'}
        bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: message.from_user.id in TEMP_DATA and
                    TEMP_DATA[message.from_user.id].get('mode') == 'delete_reminder')
def process_delete_reminder(message):
    user_id = message.from_user.id
    try:
        reminder_id = int(message.text)
        user_data = get_user_data(user_id)
        reminders = user_data.get('reminders', [])

        for i, reminder in enumerate(reminders):
            if reminder['id'] == reminder_id:
                del reminders[i]
                del TEMP_DATA[user_id]
                bot.send_message(message.chat.id, f"Напоминание #{reminder_id} удалено!", reply_markup=main_keyboard())
                return

        bot.send_message(message.chat.id, "Напоминание не найдено")
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректный номер")

@bot.message_handler(func=lambda message: message.text == 'Сброс данных')
def reset_data(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Да, сбросить все', 'Нет, отменить')
    bot.send_message(message.chat.id, "Сбросить все данные?", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == 'Да, сбросить все')
def confirm_reset(message):
    user_id = message.from_user.id
    USER_DATA[user_id] = {'transactions': [], 'budgets': {}}
    if user_id in TEMP_DATA:
        del TEMP_DATA[user_id]
    bot.send_message(message.chat.id, "Все данные сброшены!", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == 'Статистика')
def show_statistics(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

    income = sum(i['amount'] for i in user_data['transactions'] if i['type'] == 'income')
    expenses = sum(i['amount'] for i in user_data['transactions'] if i['type'] == 'expense')

    category_expenses = {}
    for i in user_data['transactions']:
        if i['type'] == 'expense':
            category_expenses[i['category']] = category_expenses.get(i['category'], 0) + i['amount']

    text = f"Общая статистика\n\nДоходы: {income:.2f} ₽\nРасходы: {expenses:.2f} ₽\nБаланс: {income - expenses:.2f} ₽\n\nРасходы по категориям:\n"

    for category, amount in category_expenses.items():
        text += f"* {category}: {amount:.2f} ₽\n"

    if category_expenses:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        categories = list(category_expenses.keys())
        amounts = list(category_expenses.values())

        ax1.pie(amounts, labels=categories, autopct='%1.1f%%')
        ax1.set_title('Расходы по категориям')

        types = ['Доходы', 'Расходы', 'Баланс']
        values = [income, expenses, income - expenses]
        colors = ['green', 'red', 'blue']

        bars = ax2.bar(types, values, color=colors)
        ax2.set_title('Финансовая картина')
        ax2.set_ylabel('Сумма')

        for bar, value in zip(bars, values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    f'{value:.2f}', ha='center', va='bottom')

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        bot.send_photo(message.chat.id, buf, caption=text)
    else:
        bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: message.text == 'Советы')
def show_tips(message):
    tips = random.sample(FINANCIAL_TIPS, 3)
    tips_text = "Советы:\n\n" + "\n".join(f"• {tip}" for tip in tips)
    bot.send_message(message.chat.id, tips_text)

@bot.message_handler(func=lambda message: message.text in ['Нет, отменить', 'Назад', 'Отмена'])
def cancel_or_back(message):
    user_id = message.from_user.id
    if user_id in TEMP_DATA:
        del TEMP_DATA[user_id]
    bot.send_message(message.chat.id, "Главное меню", reply_markup=main_keyboard())

if __name__ == "__main__":
    bot.polling(none_stop=True)
