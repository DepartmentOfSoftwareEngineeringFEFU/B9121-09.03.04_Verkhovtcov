from CogSolver.models import Rule, RuleEngine
from django.shortcuts import render


def rules_report(request):
    raw_results = RuleEngine.batch_apply_rules()
    changed_count = sum(1 for r in raw_results if r['status_changed'])

    # Группировка по правилам
    rules = []
    for rule in Rule.objects.filter(is_active=True):
        changed_apps = [
            r for r in raw_results
            if r['new_status'] == rule.new_status and r['status_changed']
        ]
        rules.append({
            'name': rule.name,
            'description': rule.description,
            'new_status': rule.new_status,
            'changed_applications': changed_apps,
            'changed_count': len(changed_apps)
        })

    context = {
        'results': raw_results,
        'changed_count': changed_count,
        'rules': rules,
        'columns': [
            {'name': 'ID', 'key': 'application.id'},
            {'name': 'Название', 'key': 'application.e_title'},
            {'name': 'Дата подачи', 'key': 'application.subm_date'},
            {'name': 'Дата начала', 'key': 'application.e_start_time'},
            {'name': 'Текущий статус', 'key': 'current_status'},
            {'name': 'Новый статус', 'key': 'new_status'},
            {'name': 'Изменен?', 'key': 'status_changed'},
        ],
        'columns_changed': [
            {'name': 'ID', 'key': 'application.id'},
            {'name': 'Название', 'key': 'application.e_title'},
            {'name': 'Дата подачи', 'key': 'application.subm_date'},
            {'name': 'Дата начала', 'key': 'application.e_start_time'},
            {'name': 'Текущий статус', 'key': 'current_status'},
            {'name': 'Новый статус', 'key': 'new_status'},
        ]
    }
    return render(request, 'CogSolver/index.html', context)
