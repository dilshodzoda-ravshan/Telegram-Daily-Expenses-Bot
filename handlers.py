# handlers.py
import os
import requests
import logging
from datetime import datetime, timedelta
from telegram import Bot, Update
from telegram.ext import CommandHandler, ContextTypes

logger = logging.getLogger(__name__)

LOW_STOCK_THRESHOLD_50 = {
    '225851382': 'vosk500',
    '225032002': 'vosk300',
    '153803184': 'vosk1kg',
    '94179895': '9v1kaseta',
    '93069798': '8v1prowax',
    '86828177': 'prowaxnabor10v1',
    '170885775': 'shvabra10l',
    '150934104': 'profnabor',
    '160079830': '9v1prowaxM',
    '191779704': 'shvabra1233'
}

LOW_STOCK_THRESHOLD_10 = {
    '226971489': 'v',
    '229900832': 'voski500prof',
    '177239543': 'NaborOSEF',
    '226959137': 'vosk500Pix',
    '220713224': 'obuvnica5v1',
    '220718912': 'obuvnica3v1',
    '220718912': 'obuvnica3v1yarus',
    '183715519': 'obuvnica6v1',
    '222701901': 'korobkiblack10pcs',
    '221283028': 'Korobkisale10pcs',
    '231540276': 'korobki10mix',
    '217692099': 'voskoplavblack5v1',
    '217011756': 'premiumblack1v1',
    '220752088': 'Yashik9pcs'
}


async def get_expenses(api_key, date_str):
    url = "https://advert-api.wb.ru/adv/v1/upd"
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    params = {
        'from': date_str,
        'to': date_str,
    }

    logger.info(f"Fetching expenses for {date_str} with API key {api_key[:5]}...")
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            expenses = sum(item['updSum'] for item in data)
            logger.info(f"Expenses for {date_str}: {expenses} ₽")
            return expenses
        else:
            logger.warning(f"No data found for {date_str}")
            return 0
    else:
        logger.error(f"Failed to fetch expenses: {response.status_code} {response.text}")
        return 0


async def get_expenses_for_period(api_key, date_from_str, date_to_str):
    url = "https://advert-api.wb.ru/adv/v1/upd"
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    params = {
        'from': date_from_str,
        'to': date_to_str,
    }

    logger.info(f"Fetching expenses from {date_from_str} to {date_to_str} with API key {api_key[:5]}...")
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            expenses = sum(item['updSum'] for item in data)
            logger.info(f"Expenses from {date_from_str} to {date_to_str}: {expenses} ₽")
            return expenses
        else:
            logger.warning(f"No data found from {date_from_str} to {date_to_str}")
            return 0
    else:
        logger.error(f"Failed to fetch expenses: {response.status_code} {response.text}")
        return 0


async def get_wildberries_expenses(api_key, date_str):
    return await get_expenses(api_key, date_str)


async def get_company3_expenses(api_key, date_str):
    return await get_expenses(api_key, date_str)


def fetch_product_data(nms):
    url = f'https://card.wb.ru/cards/detail?nm={nms}&locale=ru&dest=-1216601,-115136,-421732,123585595'
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()


def extract_stock_quantities(json_data):
    products = json_data['data']['products']
    stock_quantities = {
        'FBO': 0,
        'FBS': 0
    }

    for product in products:
        sizes = product.get('sizes', [])
        for size in sizes:
            stocks = size.get('stocks', [])
            for stock in stocks:
                qty = stock.get('qty', 0)
                dtype = stock.get('dtype')

                # Assuming dtype 4 is FBO and dtype 1 is FBS
                if dtype == 4:
                    stock_quantities['FBO'] += qty
                elif dtype == 1:
                    stock_quantities['FBS'] += qty

    return stock_quantities


async def send_message(api_keys, bot_token, chat_id):
    logger.info("Preparing to send message...")
    yesterday = datetime.now() - timedelta(days=1)
    day_before_yesterday = datetime.now() - timedelta(days=2)
    date_yesterday_str = yesterday.strftime('%Y-%m-%d')
    date_day_before_yesterday_str = day_before_yesterday.strftime('%Y-%m-%d')

    wildberries_expenses_yesterday = await get_wildberries_expenses(api_keys['NaturCo'], date_yesterday_str)
    company3_expenses_yesterday = await get_company3_expenses(api_keys['PixShop'], date_yesterday_str)

    wildberries_expenses_day_before_yesterday = await get_expenses(api_keys['NaturCo'], date_day_before_yesterday_str)
    company3_expenses_day_before_yesterday = await get_expenses(api_keys['PixShop'], date_day_before_yesterday_str)

    wildberries_difference = wildberries_expenses_yesterday - wildberries_expenses_day_before_yesterday
    company3_difference = company3_expenses_yesterday - company3_expenses_day_before_yesterday

    total_expenses_yesterday = wildberries_expenses_yesterday + company3_expenses_yesterday
    total_expenses_day_before_yesterday = wildberries_expenses_day_before_yesterday + company3_expenses_day_before_yesterday
    total_difference = total_expenses_yesterday - total_expenses_day_before_yesterday

    # Fetch product data and stock quantities
    product_codes = ['225851382']  # Replace with your actual product codes
    stock_quantities = {'FBO': 0, 'FBS': 0}
    for code in product_codes:
        json_data = fetch_product_data(code)
        stock_data = extract_stock_quantities(json_data)
        stock_quantities['FBO'] += stock_data['FBO']
        stock_quantities['FBS'] += stock_data['FBS']

    date_str = yesterday.strftime('%d.%m.%Y')
    wildberries_icon = '🔺' if wildberries_difference > 0 else '🔽'
    company3_icon = '🔺' if company3_difference > 0 else '🔽'
    total_icon = '🔺' if total_difference > 0 else '🔽'

    message = (
        f"Ежедневный расход за РК‼️\n\n"
        f"🗓 {date_str}\n\n"
        f"▶️ NaturCo - {wildberries_expenses_yesterday} ₽ {wildberries_icon}\n"
        f"▶️ PixShop - {company3_expenses_yesterday} ₽ {company3_icon}\n\n"
        f"Итого: {total_expenses_yesterday} ₽ {total_icon}\n\n"
        f"Расходы {'больше' if total_difference > 0 else 'меньше'} на {abs(total_difference):.2f} ₽\n\n"
    )

    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
    logger.info("Message sent successfully.")


def expenses_command(api_keys, bot_token):
    async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        await send_message(api_keys, bot_token, chat_id)

    return CommandHandler("expenses", command)


def interval_expenses_command(api_keys, bot_token):
    async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) != 2:
            await update.message.reply_text("Please provide start and end dates in the format: dd.mm.yyyy dd.mm.yyyy")
            return

        date_from_str, date_to_str = context.args

        try:
            date_from = datetime.strptime(date_from_str, '%d.%m.%Y')
            date_to = datetime.strptime(date_to_str, '%d.%m.%Y')
        except ValueError:
            await update.message.reply_text("Invalid date format. Please use dd.mm.yyyy.")
            return

        date_from_str_api = date_from.strftime('%Y-%m-%d')
        date_to_str_api = date_to.strftime('%Y-%m-%d')

        wildberries_expenses = await get_expenses_for_period(api_keys['NaturCo'], date_from_str_api, date_to_str_api)
        company3_expenses = await get_expenses_for_period(api_keys['PixShop'], date_from_str_api, date_to_str_api)

        total_expenses = wildberries_expenses + company3_expenses

        message = (
            f"Расходы за период с {date_from_str} по {date_to_str}:\n\n"
            f"▶️ NaturCo - {wildberries_expenses} ₽\n"
            f"▶️ PixShop - {company3_expenses} ₽\n\n"
            f"Итого: {total_expenses} ₽"
        )

        bot = Bot(token=bot_token)
        await bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='HTML')
        logger.info("Interval expenses message sent successfully.")

    return CommandHandler("interval_expenses", command)


async def check_stock_levels(bot_token, group_chat_id):
    product_codes = list(LOW_STOCK_THRESHOLD_50.keys()) + list(LOW_STOCK_THRESHOLD_10.keys())
    low_stock_messages = []

    for code in product_codes:
        json_data = fetch_product_data(code)
        stock_data = extract_stock_quantities(json_data)
        total_stock = stock_data['FBO'] + stock_data['FBS']

        if code in LOW_STOCK_THRESHOLD_50 and total_stock < 500:
            designation = LOW_STOCK_THRESHOLD_50[code]
            low_stock_messages.append(f"⚠️ Артикул {code} ({designation}) имеет остаток: {total_stock} единиц (порог < 50)")
        elif code in LOW_STOCK_THRESHOLD_10 and total_stock < 10:
            designation = LOW_STOCK_THRESHOLD_10[code]
            low_stock_messages.append(f"⚠️ Артикул {code} ({designation}) имеет остаток: {total_stock} единиц (порог < 10)")

    if low_stock_messages:
        message = "\n".join(low_stock_messages)
        bot = Bot(token=bot_token)
        await bot.send_message(chat_id=group_chat_id, text=message, message_thread_id=1156)
        logger.info("Stock level warning message sent successfully.")


def remains_command(bot_token):
    async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        product_codes = list(LOW_STOCK_THRESHOLD_50.keys()) + list(LOW_STOCK_THRESHOLD_10.keys())
        low_stock_messages = []

        for code in product_codes:
            json_data = fetch_product_data(code)
            stock_data = extract_stock_quantities(json_data)
            total_stock = stock_data['FBO'] + stock_data['FBS']

            if code in LOW_STOCK_THRESHOLD_50 and total_stock < 500:
                designation = LOW_STOCK_THRESHOLD_50[code]
                low_stock_messages.append(f"⚠️ Артикул {code} ({designation}) имеет остаток: {total_stock} единиц (порог < 50)")
            elif code in LOW_STOCK_THRESHOLD_10 and total_stock < 10:
                designation = LOW_STOCK_THRESHOLD_10[code]
                low_stock_messages.append(f"⚠️ Артикул {code} ({designation}) имеет остаток: {total_stock} единиц (порог < 10)")

        message = "\n".join(
            low_stock_messages) if low_stock_messages else "Все товары в достаточном количестве на складе."

        bot = Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text=message)
        logger.info("Remains message sent successfully.")

    return CommandHandler("remains", command)
