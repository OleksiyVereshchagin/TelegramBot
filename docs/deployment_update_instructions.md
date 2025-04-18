# Інструкції для оновлення проєкту

Цей документ містить покрокові рекомендації для процесу оновлення проєкту.

## Підготовка до оновлення
1. Ознайомтеся з поточними змінами в репозиторії.
2. Перевірте журнал змін (changelog), щоб зрозуміти, що саме буде оновлюватися.
3. Переконайтеся, що всі нові функціональні можливості чи виправлення помилок були перевірені і протестовані в тестовому середовищі.

## Створення резервних копій
Перед будь-яким оновленням створіть резервні копії:
- Бази даних.
- Конфігураційних файлів.
- Важливих даних, що зберігаються в системі.

Збережіть резервні копії в безпечному місці для можливого відкату.

## Перевірка сумісності
1. Перевірте, чи є сумісність між поточним кодом та новими залежностями.
2. Перевірте сумісність нових версій програмного забезпечення, яке буде використовуватися (наприклад, Python, PostgreSQL, інші бібліотеки).

## Планування часу простою
Якщо оновлення потребує зупинки деяких служб, попередьте команду та користувачів про можливий час простою.

## Процес оновлення

### 1. Зупинка потрібних служб
- Зупиніть необхідні служби або додатки, які можуть бути перервані під час оновлення (наприклад, сервери веб-додатків, бази даних).
  
  Приклад для Windows:
  ```powershell
  Stop-Service -Name "ServiceName"
  ```
### 2. Розгортання нового коду
Виконайте оновлення коду на сервері:
    - Перейдіть до кореневої директорії проєкту:
    ```
    cd D:\university\4\tg_bot\pthn_bot
    ```
    - Отримайте останні зміни з репозиторію:
    ```
    git pull origin main
    
    ```
### 3. Міграція даних (якщо потрібно)
- Якщо в оновленні є зміни в базі даних, виконайте міграцію.
- У разі використання Alembic для міграцій у Python:
  ```
  alembic upgrade head
  ```
###  4. Оновлення конфігурацій
-Перевірте та оновіть конфігураційні файли (наприклад, файли .env, налаштування серверів).
-Переконайтеся, що всі нові параметри конфігурації, які були додані в процесі оновлення, коректно відображені.

## Перевірка після оновлення
Тести правильності роботи
Запустіть всі тести на тестовому сервері або локально, щоб переконатися, що після оновлення нічого не зламалося.

###  Тести правильності роботи
Запустіть всі тести на тестовому сервері або локально, щоб переконатися, що після оновлення нічого не зламалося.
```
pytest tests/
```

## Моніторинг продуктивності
- Перевірте продуктивність додатку після оновлення. Виміряйте час відгуку та завантаження серверу.
- Використовуйте моніторингові інструменти (наприклад, Prometheus, Grafana) для збору статистики.

## Можливі проблеми та їх вирішення
Якщо після оновлення виникають помилки, зверніться до логів:
   - Перевірте логи додатків.
   - Перевірте логи системи для помилок у конфігурації чи запусках сервісів.

##  Процедура відкату (rollback)
Якщо оновлення виявилося некоректним, виконайте відкат:
1. Відновіть резервні копії бази даних.
2. Відкатіть зміни в коді:
```
git reset --hard HEAD~1
```
3. Перезапустіть служби, якщо вони були зупинені. 
4. Повторно перевірте правильність роботи додатку.