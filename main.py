
''''''
# main.py
import os
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import ApplicationBuilder
import asyncio
from dotenv import load_dotenv
from handlers import expenses_command, interval_expenses_command, send_message, remains_command, check_stock_levels

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()


async def main():
    api_keys = {
        'NaturCo': os.getenv('NATURCO_API_KEY'),
        'PixShop': os.getenv('PIXSHOP_API_KEY')
    }
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    group_chat_id = os.getenv('GROUP_CHAT_ID')
    # Initialize the bot
    application = ApplicationBuilder().token(bot_token).build()

    # Remove any existing webhook
    await application.bot.delete_webhook()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_message, 'cron', hour=9, minute=30, args=[api_keys, bot_token, chat_id])

    scheduler.add_job(check_stock_levels, 'interval', seconds=20, args=[bot_token, group_chat_id])

    scheduler.start()

    logger.info("Scheduler started.")

    application.add_handler(expenses_command(api_keys, bot_token))
    application.add_handler(interval_expenses_command(api_keys, bot_token))
    application.add_handler(remains_command(bot_token))  # Add the remains command

    # Initialize the application
    await application.initialize()

    # Start the application
    await application.start()
    await application.updater.start_polling()

    # Keep the application running
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
