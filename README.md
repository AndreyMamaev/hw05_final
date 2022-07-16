# Социальная сеть YATUBE
### Описание
Социальная сеть для блогеров.
### Технологии
Python 3.9.6
Django 2.2.19
### Запуск проекта в dev-режиме
Клонировать репозиторий и перейти в него в командной строке:

```git clone git@github.com:AndreyMamaev/hw05_final.git```

```cd hw05_final```

Cоздать и активировать виртуальное окружение:

```python -m venv venv```

```. venv/scripts/activate```

```python -m pip install --upgrade pip```

Установить зависимости из файла requirements.txt:

```pip install -r requirements.txt```

Выполнить миграции:

```python manage.py migrate```

Запустить проект:

```python manage.py runserver```

