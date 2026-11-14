\# Лабораторная работа 4



Консольное приложение «Онлайн-бронирование столиков». Данные хранятся в PostgreSQL, схема создаётся миграциями Alembic.



\## База данных



```

docker run --name marusya-postgres -e POSTGRES\_USER=marusya -e POSTGRES\_PASSWORD=marusya -e POSTGRES\_DB=marusya -p 5432:5432 -v marusya\_pgdata:/var/lib/postgresql/data -d postgres:16

```



После перезагрузки компьютера: `docker start marusya-postgres`.



Строка подключения берётся из переменной `DATABASE\_URL`, по умолчанию:

`postgresql+psycopg://marusya:marusya@localhost:5432/marusya`



\## Миграции



```

uv sync

uv run alembic upgrade head

uv run python -m marusya.seed\_db

```



Последняя команда один раз добавляет столики и администратора.



\## Запуск



```

uv run python -m marusya.main

```



Вход администратора: логин `admin`, пароль `admin123`.

