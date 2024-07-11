# Telegram Bot for Expense Tracking and Stock Level Monitoring

## Описание

Этот проект представляет собой Telegram-бота, который отслеживает расходы и уровень запасов на складе, отправляя уведомления в указанные топики в Telegram-группе. Бот использует API Wildberries и различные команды для взаимодействия с пользователями.

## Установка

### Требования

- Python 3.8+
- pip (Python package installer)
- Telegram Bot API Token
- Environment Variables

### Шаги установки

1. Клонируйте репозиторий:

    ```sh
    git clone https://github.com/yourusername/telegram-bot.git
    cd telegram-bot
    ```

2. Установите зависимости:

    ```sh
    pip install -r requirements.txt
    ```

3. Создайте файл `.env` в корневой папке проекта и добавьте необходимые переменные окружения:

    ```env
    BOT_TOKEN=your_telegram_bot_token
    COMPANY1_API_KEY=your_api_key1
    COMPANY2_API_KEY=your_api_key2
    CHAT_ID=your_chat_id
    GROUP_CHAT_ID=your_group_chat_id
    ```

4. Запустите бота:

    ```sh
    python main.py
    ```

## Использование

### Доступные команды

- `/expenses` - Отправляет ежедневный отчет о расходах.
- `/interval_expenses <start_date> <end_date>` - Отправляет отчет о расходах за указанный период. Формат даты: `dd.mm.yyyy`.
- `/remains` - Отправляет отчет об остатках на складе.

### Пример использования

Для получения отчета о расходах за определенный период, используйте команду:

```sh
/interval_expenses 01.01.2023 07.01.2023
```

## Архитектура проекта

- **main.py**: Главный файл для запуска бота и настройки планировщика задач.
- **handlers.py**: Содержит функции для обработки команд и отправки сообщений.

## Функции

- `send_message`: Отправляет ежедневный отчет о расходах в указанный чат.
- `check_stock_levels`: Проверяет уровни запасов на складе и отправляет предупреждения в указанный топик.
- `expenses_command`: Команда для отправки отчета о расходах.
- `interval_expenses_command`: Команда для отправки отчета о расходах за указанный период.
- `remains_command`: Команда для отправки отчета об остатках на складе.

## Лицензия

Этот проект лицензирован под [MIT License](LICENSE).
