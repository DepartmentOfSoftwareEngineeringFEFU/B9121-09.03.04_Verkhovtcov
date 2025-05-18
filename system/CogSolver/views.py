from CogEditor.models import Application
from CogSolver.forms import ApplicationForm
from CogSolver.models import Rule, RuleEngine
from django.shortcuts import render
from django.views.generic.edit import CreateView


def rules_report(request):
    # FIXME - обновить логику после коммита d41f374
    raw_results = RuleEngine.batch_apply_rules()
    changed_count = sum(1 for r in raw_results if r["status_changed"])

    # Группировка по правилам
    rules = []
    for rule in Rule.objects.filter(is_active=True):
        changed_apps = [
            r
            for r in raw_results
            if r["new_status"] == rule.new_status and r["status_changed"]
        ]
        rules.append(
            {
                "name": rule.name,
                "description": rule.description,
                "new_status": rule.new_status,
                "changed_applications": changed_apps,
                "changed_count": len(changed_apps),
            }
        )

    context = {
        "results": raw_results,
        "changed_count": changed_count,
        "rules": rules,
        "columns": [
            {"name": "ID", "key": "application.id"},
            {"name": "Название", "key": "application.e_title"},
            {"name": "Дата подачи", "key": "application.subm_date"},
            {"name": "Статус в БД", "key": "current_status"},
            {"name": "Статус классификатора", "key": "new_status"},
            {"name": "Изменен?", "key": "status_changed"},
        ],
        "columns_changed": [
            {"name": "ID", "key": "application.id"},
            {"name": "Название", "key": "application.e_title"},
            {"name": "Дата подачи", "key": "application.subm_date"},
            {"name": "Статус в БД", "key": "current_status"},
            {"name": "Статус классификатора", "key": "new_status"},
        ],
    }
    return render(request, "CogSolver/rules_report.html", context)


class ApplicationCreateView(CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'CogSolver/application_classifier.html'
    success_url = '/editor/'  # Прямой путь

    def form_valid(self, form):
        # Вызываем save() формы (в котором ваша логика)
        self.object = form.save()

        print("Получена заявка:", self.object)

        return super().form_valid(form)
