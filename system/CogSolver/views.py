from CogSolver.models import RuleEngine
from django.shortcuts import render


def index(request):
    results = RuleEngine.batch_apply_rules()
    context = {
        'results': results,
        'columns': [
            {'name': 'ID', 'key': 'application.id'},
            {'name': 'Название', 'key': 'application.e_title'},
            {'name': 'Текущий статус', 'key': 'current_status'},
            {'name': 'Новый статус', 'key': 'new_status'},
            {'name': 'Изменен?', 'key': 'status_changed'},
        ]
    }
    return render(request, 'CogSolver/index.html', context)

