import os
import requests
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
import asyncio
from dotenv import load_dotenv

load_dotenv()


async def get_expenses(api_key, date_str):
    url = "https://advert-api.wb.ru/adv/v1/upd"
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    params = {
        'from': date_str,
        'to': date_str,
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            expenses = sum(item['updSum'] for item in data)
            return expenses
        else:
            return 0
    else:
        return 0


async def get_wildberries_expenses(api_key, date_str):
    expenses = await get_expenses(api_key, date_str)
    return expenses, f"NaturCo - {expenses} ₽"


async def get_company3_expenses(api_key, date_str):
    expenses = await get_expenses(api_key, date_str)
    return expenses, f"PixShop - {expenses} ₽"


async def send_message(api_keys, bot_token, chat_id):
    # Фиксируем дату вчера и позавчера
    yesterday = datetime.now() - timedelta(days=1)
    day_before_yesterday = datetime.now() - timedelta(days=2)
    date_yesterday_str = yesterday.strftime('%Y-%m-%d')
    date_day_before_yesterday_str = day_before_yesterday.strftime('%Y-%m-%d')

    # Получаем данные за вчера
    wildberries_expenses_yesterday, wildberries_message_yesterday = await get_wildberries_expenses(api_keys['NaturCo'], date_yesterday_str)
    company3_expenses_yesterday, company3_message_yesterday = await get_company3_expenses(api_keys['PixShop'], date_yesterday_str)

    # Получаем данные за позавчера
    wildberries_expenses_day_before_yesterday = await get_expenses(api_keys['NaturCo'], date_day_before_yesterday_str)
    company3_expenses_day_before_yesterday = await get_expenses(api_keys['PixShop'], date_day_before_yesterday_str)

    total_expenses_yesterday = wildberries_expenses_yesterday + company3_expenses_yesterday
    total_expenses_day_before_yesterday = wildberries_expenses_day_before_yesterday + company3_expenses_day_before_yesterday
    difference = total_expenses_yesterday - total_expenses_day_before_yesterday

    date_str = yesterday.strftime('%d.%m.%Y')
    message = (
        f"Ежедневный расход за РК‼️\n\n"
        f"🗓 {date_str}\n\n"
        f"▶️ {wildberries_message_yesterday}\n"
        f"▶️ {company3_message_yesterday}\n\n"
        f"Итого: {total_expenses_yesterday} ₽‼️\n\n"
        f"расходы {'больше' if difference > 0 else 'меньше'} на {abs(difference):.2f} ₽"
    )

    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')


async def main():
    api_keys = {
        'NaturCo': os.getenv('NATURCO_API_KEY'),
        'PixShop': os.getenv('PIXSHOP_API_KEY')
    }
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_message, 'cron', hour=11, minute=20, args=[api_keys, bot_token, chat_id])
    scheduler.start()

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
