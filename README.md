# SeriesBot 🎬

SeriesBot — це Telegram-бот для рекомендації серіалів на основі жанру, рейтингу або пошуку за назвою.

## Основні можливості:
- Пошук серіалів
- Рекомендації за жанрами
- Додавання у список "переглянуто" або "хочу подивитись"
- Підписка на серіали

## Покрокова інструкція для розробника

### 1. Необхідне програмне забезпечення

- **Python 3.10+** — Інтерпретатор мови Python
- **Git** — Система керування версіями
- **PostgreSQL 14+** — СУБД для зберігання даних
- **Poetry** — Менеджер залежностей Python
- **PyCharm** — Середовище для розробки Python
- **DataGrip** — GUI-клієнт для роботи з PostgreSQL
- **Telegram Desktop / Web** — Тестування Telegram-бота

Автор використовує PyCharm для розробки, DataGrip для роботи з базою даних та Telegram Desktop або Web для тестування бота. За потреби можна використовувати будь-які зручні аналоги, такі як VS Code, DBeaver, Telegram у браузері тощо.

Poetry можна швидко встановити, виконавши в терміналі таку команду:  
`curl -sSL https://install.python-poetry.org | python3 -`
### 2. Клонування репозиторію

Відкрийте термінал або вбудований термінал у PyCharm (вкладка *Terminal*) і виконайте наступні команди:
```
git clone https://github.com/OleksiyVereshchagin/TelegramBot.git
cd TelegramBot
```
### 3. Налаштування проєкту в PyCharm

1. Відкрийте клонований проєкт у PyCharm.
2. Якщо з'явиться повідомлення про `pyproject.toml`, натисніть "Configure Python interpreter".
3. Оберіть **Poetry Environment** → натисніть "OK".
4. У разі потреби вручну встановіть залежності:

```bash
poetry install
```
### 4. Налаштування змінних середовища

1. Створіть файл `.env` у корені проєкту з таким вмістом:
```
BOT_TOKEN=токен_вашого_бота
DATABASE_URL=postgresql://postgres:пароль@localhost:5432/seriesbot
DEEPL_API_KEY=ваш_ключ
```
2. У PyCharm:

- Відкрийте: **Run** → **Edit Configurations**.
- Створіть нову конфігурацію → **Python**.
- В полі **Script path** вкажіть `main.py`.
- В полі **Environment variables** оберіть `.env` або вручну вкажіть змінні.

### 5. Створення бази даних у DataGrip

1. Відкрийте **DataGrip**.
2. Створіть нове підключення: **+** → **Data Source** → **PostgreSQL**.
3. Вкажіть наступні параметри:
   - **Host**: localhost
   - **Port**: 5432
   - **User**: postgres
   - **Password**: ваш пароль
4. Натисніть **Test Connection** → збережіть.
5. Клік правою кнопкою по серверу → **New** → **Database** → Назва: `seriesbot`.
6. База даних створена. Таблиці створяться автоматично при запуску бота.

### 6. Запуск бота у режимі розробки

1. У **PyCharm**:
   - Відкрийте `main.py`.
   - Натисніть **Run**.

2. Або в терміналі:

```bash
poetry run python main.py
```
### 7. Основні команди для розробки

- **poetry install** — Встановлення залежностей.
- **poetry run python main.py** — Запуск бота.
- **poetry shell** — Вхід у віртуальне середовище.
- **pytest** — Запуск тестів.
- **git pull / git push** — Оновлення/відправка змін до репозиторію.
  

##  Документування коду

Для підтримки чистого та зрозумілого коду, ми використовуємо стандарти документування, сумісні з [PEP 257](https://peps.python.org/pep-0257/).

### Основні правила

- Усі **функції**, **методи** та **класи** повинні містити `docstring` одразу після їх оголошення.
- `Docstring` має чітко та коротко пояснювати призначення функції чи класу.
- Документація має бути написана **у формі описового речення**.
- Для асинхронних функцій також обов’язково вказуйте, що вона робить та які параметри приймає (якщо є).

### Формат `docstring`

```python
def some_function(param1: str, param2: int) -> bool:
    """
    Короткий опис того, що робить функція.

    Args:
        param1 (str): опис першого параметра.
        param2 (int): опис другого параметра.

    Returns:
        bool: опис того, що повертає функція.
    """
```  

## Автор
Олексій Верещагін
