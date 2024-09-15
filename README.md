Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.



![бейджик об удачно завершенном workflow](https://github.com/belyashnikovatn/kittygram_final/actions/workflows/main.yml/badge.svg)

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
### Локально:
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

### Через docker руками:
- $ cd infra
- docker compose up -d --build

Переменные окружения заложены в .env, используется библиотека load_dotenv. Список переменных:
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- DB_HOST
- DB_PORT
- SECRET_KEY
- DEBUG
- ALLOWED_HOSTS  
Для примера есть файл .env.example

## Задачи:
### Планирование 
| Задача	| Статус | Результат |
|:-------------|:-------------|:-------------|
|Модель данных ERD|Выполнено|В ходе проектирования выяснилось, что нужно 5 связей N:M Ссылка на модель |
|Определить модель для пользователя|Выполнено| Поля пользователя не стандартные (+фото) -> заменяем модель User |
|Определить приложения|Выполнено| 3 приложения: users, recepies, api |
|Создать проект и приложения|Выполнено| 3 приложения: users, recepies, api (именно в таком порядке зависимости) |
|Создать модели данных|В работе| Tag, Ingredient, Recipe (доделать 2 разных вью + авто авторство), Subscription |
|Определить список функций для проектирования вьюсетов|В работе | --- |
|Настроить админку стандарт|Очередь| --- |
|Настроить админку классы |В работе| --- |
|Создать сериализаторы|В работе| --- |
|Создать вьюшки|Очередь| В работе |
|Настроить аутентификацию/авторизацию|Очередь| есть в этом уроке как дописать свой метод, чтобы получать токен по имя + почта
Ссылка на урок: [Спринт 13/19 → Тема 1/3: Django Rest Framework → Урок 13/15: Аутентификация по токену. JWT + Djoser]( https://practicum.yandex.ru/learn/backend-developer/courses/d3fb0c30-e2d4-4df7-a4ba-a9abce9c7554/sprints/298720/topics/faf9f009-ec4f-4a01-92b3-f8fe518250c8/lessons/26416ae0-ab86-42fd-bf31-4e0a9d148d58/#0058f86f-cd21-46e8-af87-6ed4cec2320b ) |
|Создать пермишены|Очередь| --- |
|Подготовить тестовые данные для загрузки|Очередь| --- |
|Доработать compose |Очередь| --- |
|Создать прод compose|Очередь| --- |
|Настроить CI/CD|Очередь| --- |
|Вшить загрузку данных в CI/CD|Очередь| --- |
|Вшить создание админа в CI/CD|Очередь| --- |
|Фото по дефолту|Очередь| https://www.devhandbook.com/django/user-profile/ |
|Имя|Очередь| --- |

### Реализация


### Настройка контейнеризации
- Создан Dockerfile для 
- Изменены настройки nginx для контейнера gateway
- Изменён settings: env + database settings
- Дописаны  docker-compose.yml и docker-compose.production.yml

|Имя образа	|Название контейнера|Название volume|
|:-------------:|:-------------:|:-------------:|
|gateway|gateway|static, media| 
|backend|backend|static, media| 
|frontend|frontend|static|
|postgres:13|db|pg_data|

### Настройка CI/CD
- Прописан workflow в main.yml:
    - проверка кода по PEP8 (push в любую ветку)
    - запуск тестов для фронтенда и бэкенда (push в любую ветку)
    - сбор образов и push на докерхаб (push в main ветку)
    - обновление образов на сервере и перезапуск приложения (push в main ветку)
    - сбор и перенос статики, применение миграций (на сервере)  (push в main ветку)
    - уведомление по Telegram 
- Изменены настройки nginx на удалённом сервере

Итоговая схема :  
![Итоговая схема](https://github.com/belyashnikovatn/kittygram_final/blob/main/server_docker_taski_kittygram.png)  

## Авторство
[Беляшникова Таня](https://github.com/belyashnikovatn)
