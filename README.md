![бейджик об удачно завершенном workflow](https://github.com/belyashnikovatn/foodgram/actions/workflows/main.yml/badge.svg)

# Проект 
Цель проекта — закрепить теорию курса по модулям: 
закрепить теорию по управлению проектами на удалённом сервере, усвоить навык по развёртыванию и настройке процесса CI/CD: создание образов с помощью технологии Docker, создание контейнеров, управление группой контейнеров (оркестрация), описание worfklow для автоматизации беспрерывных интеграции и сопровождения.  
Объект: kittygram — приложение, где авторизованные пользователи могут добавить фотки котов с описанием их достижений (а другие авторизованные пользователи — полюбоваться ими).

## Содержание
- [Технологии](#технологии)
- [Запуск проекта](#запуск-проекта)
- [Выполненные мною задачи](#задачи)
- [Авторство](#авторство)

## Технологии:
Python + Django REST Framework + TokenAuthentication + JS + Docker + GitHub Actions
Подключение БД зависит от флага DEBUG:
- True (тестовый режим) — SQLite
- False (продакшн) — PostgreSQL


## Запуск проекта 
<details>
<summary>Локально</summary>
- $ git clone https://github.com/belyashnikovatn/foodgram.git 
- $ cd frontend
- $ npm i
- $ npm run start
В другом терминале:
- $ cd backend
- $ python -m venv venv
- $ source venv/Scripts/activate
- $ python -m pip install --upgrade pip
- $ pip install -r requirements.txt
- $ python manage.py migrate
- $ python manage.py runserver
</details>

<details>
<summary>Через docker руками</summary>
- $ cd infra
- docker compose up -d --build
</details>

Переменные окружения заложены в .env, используется библиотека load_dotenv. 
<details>
<summary>Список переменных:</summary>
Для подключения к СУБД postgres:  
POSTGRES_DB=exmaple  
POSTGRES_USER=exmaple  
POSTGRES_PASSWORD=exmaple  
DB_HOST=exmaple  
DB_PORT=exmaple  

Для настроек проекта:
SECRET_KEY=exmaple  
DEBUG=TrueOrAny  
ALLOWED_HOSTS=domain,xxx.xxx.xxx.xxx  

Для создания админа (функция initadmin):  
username=username  
email=username@gmail.com  
first_name=first_name  
last_name=last_name  
password=password  
</details>

Для примера есть файл .env.example

## Задачи:

<details>
<summary> План </summary> 
| Задача	| Статус | Результат |
|:-------------|:-------------|:-------------|
|Модель данных ERD|Выполнено|---|
|Определить приложения|Выполнено| 3 приложения: users, recepies, api |
|Определить модель для пользователя|Выполнено| Поля пользователя не стандартные (+фото) -> заменяем модель User |
|Создать проект и приложения|Выполнено| 3 приложения: users, recepies, api (именно в таком порядке зависимости) |
|Настроить аутентификацию/авторизацию|Выполнено| --- |
|Создать модели данных|Выполнено| ---|
|Определить список функций для проектирования вьюсетов|Выполнено | Файл-таблица. Список вью: Users, Ingredi Tag Recipe |
|Настроить админку стандарт|Выполнено| --- |
|Настроить админку расширено |В работе| --- |
|Локализация всего проекта |Выполнено| --- |
|Создать сериализаторы|Выполнено| --- |
|Создать вьюшки|Выполнено| ---- |
|Создать пермишены|Выполнено| --- |
|Подготовить тестовые данные для загрузки|Выполнено| --- |
|Доработать compose |Выполнено| --- |
|Создать прод compose|Выполнено| --- |
|Настроить CI/CD|Выполнено| --- |
|Вшить загрузку данных в CI/CD|Выполнено| --- |
|Вшить создание админа в CI/CD|Выполнено| --- |
</details>


### Проектирование и реализация 
Для определения моделей и связей между ними была создана диаграмма "сущность-связь"
<details>
<summary>Диаграмма</summary>
![foodgram_erd](https://github.com/belyashnikovatn/foodgram/blob/main/ERD_API_FOODGRAM.png)
</details>  
Для меня это всегда самая важная часть, потому что это основа структуры данных и взаимодействия.  

После этого 




Этапы проекта:  
0. Проектирование, моделирование, рисование, планирование  
1. Сделать всё очень просто (с повторами кода, без оптимизации), но главное, чтобы проходили тесты postman  
2. Оптимизация: вынести общий код, удалить повторения и лишние переменные итд  
3. Описать классы и функции, сложные места  
4. Сделать develop docker compose, собрать образы, запушить на хаб  
5. Сделать product docker compose, развернуть проект на сервере, настроить nginx  
6. Прописать git workflow для CI/CD  
7. Протестировать релиз, доделать баги, чтобы убедиться, что workflow рабочий  
8. Документация  

entrypoint 
loaddata (дополнительно загружаются теги)
initadmin
collectstatic

### Настройка контейнеризации
- Создан Dockerfile для backend, gateway, db 
- Изменены настройки nginx для контейнера foodgram-proxy
- Изменён settings: media + env + database settings
- Созданы  docker-compose.yml и docker-compose.production.yml

|Имя образа	|Название контейнера|Название volume|
|:-------------:|:-------------:|:-------------:|
|postgres:13|foodgram-db|pg_data|
|foodgram_backend|foodgram-back|static, media| 
|foodgram_frontend|foodgram-front|static|
|foodgram_gateway|foodgram-proxy|static, media| 

### Настройка CI/CD
- Прописан workflow в main.yml:
    - проверка кода по PEP8 (push в любую ветку)
    - сбор образов и push на докерхаб (push в main ветку)
    - обновление образов на сервере и перезапуск приложения (push в main ветку)
    - уведомление по Telegram 
- Изменены настройки nginx на удалённом сервере

## Итоги
Самым ценным в этом проекте для меня стало:
- понимание, как проектировать сложные вьюсеты, так как до этого я использовала ModelViewSet или ReadOnlyModelViewSet без всяких дополнительных action 
- понимание разделения зон ответственности и задач слоёв views и serializer  
- понимание, что любую задачу можно решить каким-либо путём.  На некоторые задачи у меня уходило по 2-3 дня, казалось неразрешимым, но я читала, спрашивала, читала опять и находила решение.  


## Авторство
[Беляшникова Таня](https://github.com/belyashnikovatn)
