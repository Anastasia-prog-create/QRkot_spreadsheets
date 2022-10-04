# QRkot_spreadseets
Фонд собирает пожертвования на различные целевые проекты,автоматически распределяет свободные средства из пожертвований по активным проектам. Добавлена возможность создания отчета по закрытым проектам c помощью Google Drive API и Google Sheets API.

## Технологии и пакеты
* FastAPI
* SQLAlchemy
* Google Drive API
* Google Sheets API

## Установка проекта
Склонируйте проект на Ваш компьютер
   ```sh
   git clone https://github.com/Anastasia-prog-create/cat_charity_fund.git
   ```

В корневой папке проекта активируйте виртуальное окружение
   ```sh
   python3 -m venv venv
   ```
   ```sh
   source venv/bin/activate
   ```
Обновите менеджер пакетов (pip)
   ```sh
   pip3 install --upgrade pip
   ```
Установите необходимые зависимости
   ```sh
   pip3 install -r requirements.txt
   ```
Автогенерация первой миграции
   ```sh
   alembic revision --autogenerate -m "Ваш комментарий"
   ```
Автогенерация первой миграции
   ```sh
   alembic upgrade head
   ```
Для запуска проекта выполните команду
```sh
uvicorn app.main:app --reload
```

Подробная документация будет доступна после запуска проекта по ссылке:  
http://127.0.0.1:8000/docs

## Автор проекта
Кривошеева Анастасия - студент 6 когорты Яндекс.Практикума.  
[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Anastasia-prog-create)
