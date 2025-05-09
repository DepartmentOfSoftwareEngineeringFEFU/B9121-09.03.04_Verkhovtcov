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