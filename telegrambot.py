from typing import List, Tuple

import telebot

from extensions import CryptoCurrency
from utils import params_from_config


bot = telebot.TeleBot(params_from_config('TOKEN'))
currencies = params_from_config('BotParams')['currency']


class APIException(Exception):
    """Ошибка вызванная действиями пользователя"""


@bot.message_handler(commands=['start', 'help'])
def start_command(message: telebot.types.Message) -> None:
    """Обработка команд запуск и помощь"""
    text = (
        'Введите команду боту в следующем формате: \n '
        '<имя валюты> <в какую валюту перевести> <количество переводимой '
        'валюты>.\n Команда /values - список доступных валют')
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['values'])
def currencies_list(message: telebot.types.Message) -> None:
    """Список доступных валют"""
    currency_names = 'Доступные валюты:\n - {}'.format(
        '\n - '.join(currencies.keys())
    )
    bot.send_message(message.chat.id, currency_names)


def get_params(message: telebot.types.Message) -> Tuple[str, str, float]:
    """Проверка введенных параметров"""
    # За одно уберём лишние пустые элементы (лишние пробелы)
    params = tuple(filter(lambda x: x, message.text.split(' ')))
    if len(params) != 3:
        raise APIException(
            'Неверное количество параметров запроса конвертации\n '
            '(<имя валюты> <в какую валюту перевести> <количество '
            'переводимой валюты>)'
        )
    quote, base, amount = params
    if quote not in tuple(currencies.keys()):
        raise APIException(
            f'Указанная валюта не доступна для расчета: {quote}'
        )

    if base not in tuple(currencies.keys()):
        raise APIException(
            f'Указанная валюта не доступна для расчета: {base}'
        )

    if base == quote:
        raise APIException(
            f'Невозможно перевести одинаковые валюты: {base} - {quote}'
        )

    if not amount.isdigit() or float(amount) <= 0:
        raise APIException(
            f'Неверно указано сумма конвертации переводимой валюты: {amount}'
        )

    return currencies[quote], currencies[base], float(amount)


@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message) -> None:
    currency = CryptoCurrency()
    try:
        quote, base, amount = get_params(message)
        summ = currency.get_price(quote, base, amount)
    except APIException as err:
        # Ошибка пользователя - выводим с сообщением пользователя
        bot.reply_to(message, f'Ошибка пользователя: "{err}"')
    except Exception as err:
        # Ошибка не пользователя - выводим просто как сообщение
        bot.send_message(
            message.chat.id, f'Не удалось обработать команду: "{err}"')
    else:
        bot.send_message(
            message.chat.id,
            f'Цена {amount} {quote} в {base} - {str(summ)}')


def bot_execute() -> None:
    bot.polling()
