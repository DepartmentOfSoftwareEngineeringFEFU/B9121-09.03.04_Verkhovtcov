# methods-of-software-intellectualization

Репозиторий для хранения курсовой работы по дисциплине Методы и технологии интеллектуализации программных систем

## Ссылки на полезные материалы

1. Django:
   - https://django.fun/docs/django/5.2/intro/tutorial02/
2. Дополнительно:
   - https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

## Функционал:

    1. Главная
        localhost/
    2. Получение перечня заявок за месяц:
        localhost/application/archive/<int:year>/<int:month>
    3. Получение перечня заявок за год
        localhost/application/archive/<int:year>
    4. Получение перечня заявок за все время
        localhost/application/archive/
    5. Получение заявки по id
        localhost/application/<int:id>
    6. Получение перечня организованных мероприятий по id сотрудника
        localhost/organizer/<int:id>/events/

## Запуск

```bash
python manage.py runserver 192.168.1.37:8050 --insecure
```

Запуск на localhost с возможностью допуска с ПК локальной сети:
```bash
python manage.py runserver 0.0.0.0:8050 --insecure
```

Локальный IP-адресс можно узнать через команду ipconfig


### Дамп и загрузка данных

В папке с manage.py выполнить команду для создания дампа в файл dump.json

```bash
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > dump.json
```

В папке с manage.py выполнить команду для загрузки дампа из файла dump.json

```bash
python manage.py loaddata dump.json
```
