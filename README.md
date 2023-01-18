# praktikum_new_diplom

CI/CD foodgram: ![status](https://github.com/FanisGi/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# Проект Foodgram, «Продуктовый помощник»

## Описание

Сервис позволяет пользователям публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Ключевые технологии

* Python 3.7
* Django 3.2
* Djagorestframework 3.14 
* djoser 2.1
* docker 20.10
* docker-compose 1.25
* nginx 1.18
* gunicorn 20.0
* psycopg2-binary 2.8

## Установка
### на локальной машине

1. Cклонируйте репозитарий:

`git clone git@github.com:FanisGi/api_yamdb.git`

2. Cоздайте и активируйте виртуальное окружение:

```
# Для MacOS и Linux
python3 -m venv venv && . venv/bin/activate

# Для Windows
python -m venv venv && . venv/Scripts/activate
```

3. Установите все зависимости из файла requirements.txt:

`pip install -r requirements.txt`

4. Выполните миграции и загрузите статику:

`python manage.py migrate`

`python manage.py collectstatic --no-input`

5. Запустите веб сервер:

`python manage.py runserver`

### на удаленном сервере
Установите на сервере docker и docker-compose

Скопируйте на сервер docker-compose.yaml и nginx/default.conf

Создайте копию проекта в своём профиле github.

В репозитории проекта создайте в Secrets GitHub переменные окружения для работы:

DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<имя базы данных postgres>
DB_USER=<пользователь бд>
DB_PASSWORD=<пароль>
DB_HOST=<db>
DB_PORT=<5432>

DOCKER_PASSWORD=<пароль от DockerHub>
DOCKER_USERNAME=<имя пользователя>

SECRET_KEY=<секретный ключ проекта django>

HOST_IP=<username для подключения к серверу>
USER_HOST=<IP сервера>
PASSPHRASE_FOR_HOST=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ (для получения команда c терминала **cat ~/.ssh/id_rsa**)>

TELEGRAM_TO=<ID чата, в который придет сообщение>
TELEGRAM_TOKEN=<токен вашего бота>
При команде git push в ветку master начнётся выполнения файла workflows. Дождитесь завершения всех задач.
Регистрация
Алгоритм регистрации пользователей:

Пользователь отправляет POST-запрос на добавление нового пользователя с параметрами email и username на эндпоинт /api/v1/auth/signup/.
YaMDB отправляет письмо с кодом подтверждения (confirmation_code) на адрес email.
Пользователь отправляет POST-запрос с параметрами username и confirmation_code на эндпоинт /api/v1/auth/token/, в ответе на запрос ему приходит token (JWT-токен).
При желании пользователь отправляет PATCH-запрос на эндпоинт /api/v1/users/me/ и заполняет поля в своём профайле (описание полей — в документации).
Пользовательские роли
Аноним — может просматривать описания произведений, читать отзывы и комментарии.
Аутентифицированный пользователь (user) — может, как и Аноним, читать всё, дополнительно он может публиковать отзывы и ставить оценку произведениям (фильмам/книгам/песенкам), может комментировать чужие отзывы; может редактировать и удалять свои отзывы и комментарии. Эта роль присваивается по умолчанию каждому новому пользователю.
Модератор (moderator) — те же права, что и у Аутентифицированного пользователя плюс право удалять любые отзывы и комментарии.
Администратор (admin) — полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям.
Суперюзер Django — обладет правами администратора (admin)
Примеры API запросов
GET /categories/

Response sample [ { "count": 0, "next": "string", "previous": "string", "results": [ { "name": "string", "slug": "string" } ] } ]

POST /categories/

Request samples { "name": "string", "slug": "string" }

Response samples { "name": "string", "slug": "string" }

Полное описание доступно по эндпоинту /redoc/ - http://84.201.165.117/redoc/

Автор
Gilazov Fanis