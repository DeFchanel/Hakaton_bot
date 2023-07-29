import telebot
import os
from telebot import types
from dotenv import load_dotenv
import random
import json
from pprint import pprint

load_dotenv()
token = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(token)
incorrect_answers = {
    'question': [],
    'your_answer': [],
    'correct_answer': []
}
with open("data.json", "rb") as read_file:
    questions = json.load(read_file)


def randomize_questions(num_of_questions):
    test_questions = random.sample(list(questions.keys()), num_of_questions)
    return test_questions


def main_test(test_questions, num, points, chat_id):
    if num == len(test_questions):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        menu_button = types.KeyboardButton('Меню выбора режима')
        markup.add(menu_button)
        pprint(incorrect_answers)
        if incorrect_answers['question']:
            bot.send_message(chat_id, 'Неверные вопросы:')
            for i in range(len(incorrect_answers['question'])):
                question_text = incorrect_answers['question'][i]
                your_answer = incorrect_answers['your_answer'][i]
                correct_answer = incorrect_answers['correct_answer'][i]
                bot.send_message(chat_id, f'•{question_text} \n •Ваш ответ: {your_answer}      •Верный ответ: {correct_answer}')
        bot.send_message(chat_id, f'Ваши очки: {points}', reply_markup=markup)
    else:
        question = test_questions[num]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for option in questions[question].keys():
            markup.add(types.KeyboardButton(option))
            markup.row()
        markup.add(types.KeyboardButton('Выход'))
        msg = bot.send_message(chat_id, question, reply_markup=markup)
        bot.register_next_step_handler(msg, check_answer, question, num, points, test_questions)


@bot.message_handler(func=lambda message: message.text in ['/start', 'Меню выбора режима', 'Выход'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("5 вопросов")
    button2 = types.KeyboardButton("15 вопросов")
    button3 = types.KeyboardButton("30 вопросов")
    markup.add(button1, button2, button3)
    bot.send_message(message.chat.id, 'Добро пожаловать в тест по Python! Выберите режим.', reply_markup=markup)

    
@bot.message_handler(content_types=['text'])
def select_mode(message):
    chat_id = message.chat.id
    if message.text == '5 вопросов':
        test_questions = randomize_questions(5)
        main_test(test_questions, 0, 0, chat_id)
    elif message.text == '15 вопросов':
        test_questions = randomize_questions(15)
        main_test(test_questions, 0, 0, chat_id)
    elif message.text == '30 вопросов':
        test_questions = randomize_questions(30)
        main_test(test_questions, 0, 0, chat_id)
    

def check_answer(message, question, num, points, test_questions):
    chat_id = message.chat.id
    answer = message.text
    if answer == 'Выход':
        send_welcome(message)
        return
    try:
        if questions[question][answer]:
            points += 1
            num += 1
            main_test(test_questions, num, points, chat_id)
        else:
            incorrect_answers['question'].append(question)
            incorrect_answers['your_answer'].append(answer)
            for option in questions[question]:
                if questions[question][option]:
                    correct_answer = option
            incorrect_answers['correct_answer'].append(correct_answer)
            num += 1
            main_test(test_questions, num, points, chat_id)
    except KeyError:
        bot.send_message(message.chat.id, 'Вы ввели недопустимый ответ. Попробуйте еще раз')
        main_test(test_questions, num, points, chat_id)
    

bot.infinity_polling()