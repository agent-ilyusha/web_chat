# VITS - Видео-чат приложение

## Основные возможности
- Видео-звонки в реальном времени
- Система обмена сообщениями
- Управление пользовательскими профилями
- Безопасная аутентификация и авторизация
- Поддержка WebRTC для видеосвязи

## Технический стек
- Django 5.1.7
- Django REST Framework
- Channels для WebSocket
- WebRTC (aiortc)
- PostgreSQL
- OpenCV для обработки видео

## Требования
- Python 3.8+
- PostgreSQL
- Виртуальное окружение Python

## Установка и настройка

1. Клонируйте репозиторий:
```bash
git clone [URL репозитория]
cd vits
```

2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate  # для Linux/Mac
.venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirmets.txt
```

4. Создайте файл .env в корневой директории и настройте переменные окружения:
```
POSTGRES_NAME
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
DJANGO_SECRET_KEY
```

5. Примените миграции:
```bash
python manage.py migrate
```

6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

7. Запустите сервер разработки:
```bash
python manage.py runserver
```

## Структура проекта
- `vits/` - основное приложение
- `video_message/` - модуль видеосвязи
- `users_profile/` - управление профилями пользователей
- `chat/` - система обмена сообщениями
- `templates/` - HTML шаблоны
- `static/` - статические файлы (CSS, JavaScript, изображения)

## Разработка
Для запуска в режиме разработки используйте:
```bash
daphne vits.asgi:application
```