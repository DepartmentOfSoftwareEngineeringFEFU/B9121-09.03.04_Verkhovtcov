from CogSolver.models import Rule
from django.contrib import admin
from django.urls import path

from .views import rules_report  # Импорт view


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'condition_type', 'priority', 'is_active',
                    'new_status')
    list_filter = ('is_active', 'condition_type')
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'priority', 'is_active',
                       'new_status')
        }),
        ('Условия', {
            'fields': ('condition_type', 'days_threshold', 'role_id',
                       'min_text_length'),
            'description': 'Параметры условия срабатывания правила'
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.condition_type == 'date_compare' and obj.days_threshold is None:
            raise ValueError("Для сравнения дат необходимо указать порог дней")
        super().save_model(request, obj, form, change)

    change_list_template = 'CogSolver/admin/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'report/',
                self.admin_site.admin_view(rules_report),
                name='rules_report'
            ),
        ]
        return custom_urls + urls
