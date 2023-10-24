import telebot
import requests
import json


TOKEN = "6770249873:AAEu6DQhYy_11wMcipcDsRHLSZ3u16sbI4U"


bot = telebot.TeleBot(TOKEN)


class CurrencyConverter:
    @staticmethod
    def get_supported_currencies():

        return ["USD", "EUR", "RUB"]

    @staticmethod
    def get_price(base, quote, amount):
        if base == quote:
            return amount

        try:
            url = f"https://min-api.cryptocompare.com/data/price?fsym={base}&tsyms={quote}"
            response = requests.get(url)
            data = response.json()

            if "Response" in data and data["Response"] == "Error":
                raise APIException("Ошибка при получении курса валюты")

            exchange_rate = data[quote]
            result = exchange_rate * amount
            return result
        except requests.exceptions.RequestException:
            raise APIException("Ошибка при отправке запроса к API")


class APIException(Exception):
    pass


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    instructions = "Для получения цены на валюту, введите сообщение в формате:\n\n"
    instructions += "<имя валюты, цену которой вы хотите узнать> <имя валюты, в которой надо узнать цену первой валюты> <количество первой валюты>\n"
    instructions += "Например: USD EUR 100"
    bot.reply_to(message, instructions)


@bot.message_handler(commands=['values'])
def handle_values(message):

    currencies = CurrencyConverter.get_supported_currencies()
    bot.reply_to(message, "Доступные валюты:\n" + ", ".join(currencies))


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        text = message.text
        base_currency, quote_currency, amount = text.split()
        price = CurrencyConverter.get_price(
            base_currency, quote_currency, float(amount))
        response = f"{amount} {base_currency} = {price} {quote_currency}"
        bot.reply_to(message, response)
    except APIException as e:
        bot.reply_to(message, f"Ошибка: {e}")
    except (ValueError, TypeError):
        bot.reply_to(
            message, "Неправильный формат. Используйте команду /help для получения инструкций.")


if __name__ == "__main__":
    bot.polling()
