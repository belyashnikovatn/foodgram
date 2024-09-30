![бейджик об удачно завершенном workflow](https://github.com/belyashnikovatn/foodgram/actions/workflows/main.yml/badge.svg)

# Проект 
Цель проекта — закрепить теорию курса по модулям: 
- API: интерфейс взаимодействия программ
- Управление проектом на удалённом сервере

Объект проекта: [«Фудграм»](https://yummyinmytommy.zapto.org/recipes) — сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Содержание
- [Технологии](#технологии)
- [Запуск проекта](#запуск-проекта)
- [Проектирование и реализация](#проектирование-и-реализация)
- [Развёртывание](#развёртывание)
- [Итоги](#итоги)
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
<summary>Через docker</summary>
 
- $ cd infra
- docker compose up -d --build
</details>

<br/>
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

## Проектирование и реализация:

<details>
<summary> План задач </summary> 

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
|Настроить админку расширено |Выполнено| --- |
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


### Уровень данных 
Для определения моделей и связей между ними была создана диаграмма "сущность-связь". Для меня это всегда самая важная часть, потому что является основой структуры данных и взаимодействия.  
<details>
<summary>Диаграмма</summary>

 ![ERD](https://github.com/belyashnikovatn/foodgram/blob/main/ERD_API_FOODGRAM.png)
 </details>  

### Уровень представления

Для этого я собрала все ручки в один файл, осортировала по имени, и получилась такая картинка:

<details>
<summary>Список функций</summary>

 ![views](https://github.com/belyashnikovatn/foodgram/blob/main/views.png)
</details>

<br>
Логика выбора типа вьюсета:
- если действий всего два (просмот списка и единицы), то выбираем ReadOnlyModelViewSet
- если все CRUD-операции, то ModelViewSet
- если действий больше, то это дополнительные action 
- если action похожи, но имеют вилку, то это mapping

Изначально я разметила вью и функции в коде, чтобы была полная картина, только после этого приступила к реализации.

<details>
<summary>Разметка вью и функций на примере рецепта</summary>

```
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """Action для избранного рецепта."""
        return Response({'message': f'That MAIN recipe action for {self}.'})

    @favorite.mapping.post
    def add_into_fav(self, request, pk):
        """Добавить рецепт в избранное."""
        return Response({'message': f'Add recipe into {pk} favs.'})

    @favorite.mapping.delete
    def del_from_fav(self, request, pk):
        """Удалить рецепт из избранного."""
        return Response({'message': f'Del recipe from {pk} favs.'})

    @action(detail=True, permission_classes=(IsAuthenticated,), url_path='get-link')
    def get_link(self, request, pk):
        """Получить короткую ссылку на рецепт."""
        return Response({'message': f'Get your link to {pk} res.'})
```
</details>


### Уровень сериализации
В ходе переделывания функции подписки по третьему разу, я выяснила и закрепила для себя следующий подход к выбору типа сериализатора: если на входе сериализатора экземпляр модели, то есть смысл брать ModelSerializer. Если же на входе связи, а не объекты (например, та же самая подписка пользователя на пользователя), то стоит взять Serializer. Например, для схожих проверок при добавлении/удалении рецепта в избранное/список покупок я использовала один сериализатор UserRecepieSerializer.




### Этапы проекта:  

1. Проектирование, моделирование, рисование, планирование  
2. Сделать всё очень просто (с повторами кода, без оптимизации), но главное, чтобы проходили тесты postman  
3. Оптимизация: вынести общий код, удалить повторения и лишние переменные итд  
4. Описать классы и функции, сложные места  
5. Сделать develop docker compose, собрать образы, запушить на хаб  
6. Сделать product docker compose, развернуть проект на сервере, настроить nginx  
7. Прописать git workflow для CI/CD  
8. Протестировать релиз, доделать баги, чтобы убедиться, что workflow рабочий  
9. Документация  

## Развёртывание
### Настройка контейнеризации
- Создан Dockerfile для backend, gateway, db 
- Создан entrypoint, куда заложено: 
    - миграции данных
    - создание админа
    - загрузка данных (инргедиенты и теги)
    - сбор и копирование статики для бэкенда
    - запуск приложения
- Изменены настройки nginx для контейнера foodgram-proxy
- Изменён settings: media + env + database settings
- Созданы  docker-compose.yml и docker-compose.production.yml

|Имя образа	|Название контейнера|Название volume|
|:-------------:|:-------------:|:-------------:|
|postgres:13|foodgram-db|pg|
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
- понимание разделения зон ответственности и задач между слоями views и serializers  
- я ещё раз откатала схему работы в git: у меня есть ветка main, develop и остальные создавались под каждую задачу. Все изменения в develop только через pull request, уже потом в main (когда пройдены тесты Postman в и PEP8)
- понимание, что любую задачу можно решить каким-либо путём.  На некоторые задачи у меня уходило по 2-3 дня, казалось неразрешимым, но я читала, спрашивала, читала опять и находила решение.  


## Авторство
[Беляшникова Таня](https://github.com/belyashnikovatn)
