from CogSolver.models import RuleEngine
from django.shortcuts import render


def rules_report(request):
    raw_results = RuleEngine.batch_apply_rules()

    context = {
        'results': raw_results,
        'columns': [
            {'name': 'ID', 'key': 'application.id'},
            {'name': 'Название', 'key': 'application.e_title'},
            {'name': 'Дата подачи заявки', 'key': 'application.subm_date'},
            {'name': 'Дата проведения мероприятия',
             'key': 'application.e_start_time'},
            {'name': 'Текущий статус', 'key': 'current_status'},
            {'name': 'Новый статус', 'key': 'new_status'},
            {'name': 'Изменен?', 'key': 'status_changed'},
        ]
    }
    return render(request, 'CogSolver/index.html', context)
