# Інструкція з розгортання SeriesBot у production-середовищі

## Вимоги до апаратного забезпечення

- **Архітектура**: x86_64
- **CPU**: мінімум 2 ядра (рекомендовано 4)
- **Оперативна пам'ять (RAM)**: від 2 ГБ 
- **Диск**: мінімум 1 ГБ вільного місця (SSD бажано для швидкодії)

## Необхідне програмне забезпечення

- **Операційна система**: Windows 10 або новіше
- **Python**: 3.10 або новіше
- **PostgreSQL**: версія 13 або новіше
- **Git**: для клонування репозиторію
- **pip**: менеджер Python-пакетів


## Налаштування мережі

- Відкрити порт для вхідного зв’язку з Telegram API 
- Доступ до зовнішніх API:
- - api.tvmaze.com
- - api-free.deepl.com або api.deepl.com
- У разі використання PostgreSQL на окремому сервері: порт 5432

## Конфігурація серверів
    
Усі команди нижче потрібно вводити в PowerShell або терміналі вашої IDE, відкритому в каталозі з проєктом.
1. Створи теку проєкту та перейдіть у неї:
```
git clone https://github.com/your-username/SeriesBot.git
cd SeriesBot
``` 
2. Створи та активуй віртуальне середовище:
```
python -m venv venv
.\venv\Scripts\activate
```
3. Встанови залежності:
```
pip install -r requirements.txt
```
## Налаштування СУБД (PostgreSQL)
Використай pgAdmin, термінал або DataGrip, щоб створити нову базу:
- Ім’я бази: seriesbot_db
- Користувач: bot_user
- Пароль: securepassword123
Через термінал (PowerShell):
```
psql -U postgres
```
Далі ввести команди:
```
CREATE USER bot_user WITH PASSWORD 'securepassword123';
CREATE DATABASE seriesbot_db OWNER bot_user;
GRANT ALL PRIVILEGES ON DATABASE seriesbot_db TO bot_user;
```

Налаштування .env файлу
У корені проєкту створи або відкрий файл .env
Додай рядок:
```
DATABASE_URL=postgresql://bot_user:securepassword123@localhost:5432/seriesbot_db
```
Налаштування DataGrip
1. Відкрий DataGrip 
2. Натисни + → Data Source → PostgreSQL 
3. Заповни поля:
Поле   Значення
Host: localhost
Port: 5432
User: bot_user
Password: securepassword123
Database: seriesbot_db
4. Натисни Test Connection 
5. Якщо все добре — натисни OK

##  Розгортання коду
1. Увімкни віртуальне середовище:
```
.\venv\Scripts\activate
```
2. Запусти бота:
```
python bot.py
```
## Перевірка працездатності
1. У Telegram знайди свого бота та надішли команду /start.
2. Якщо отримуєш відповідь — бот працює.
3. У випадку помилок перевір:
   - Наявність активного інтернет-з’єднання
   - Лог-файл або консоль на наявність помилок
   - Параметри підключення до БД
   - Правильність .env файлу