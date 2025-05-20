from CogEditor.models import (
    AgreedStatus,
    Application,
    Employee,
    EmployeePosition,
    EventFormat,
    Order,
    ParticipatoryRole,
    Schedule,
    Sources,
    StructuralUnit,
)
from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

admin.site.register(AgreedStatus)
admin.site.register(Employee)
admin.site.register(EmployeePosition)
admin.site.register(EventFormat)
admin.site.register(Order)
admin.site.register(ParticipatoryRole)
admin.site.register(Schedule)
admin.site.register(Sources)
admin.site.register(StructuralUnit)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['e_title', 'subm_date', 'status', 'organizer']
    actions = ['reset_approval_status']

    @admin.action(
        description=_("Сбросить статус согласования")
    )  # `_` для перевода
    def reset_approval_status(self, request, queryset):
        """
        Сбрасывает статус согласования у выбранных заявок
        на статус по умолчанию.
        """
        try:
            default_status = AgreedStatus.objects.get(n_stage=3)
            updated_count = queryset.update(status=default_status)

            self.message_user(
                request,
                _(f"Статус согласования сброшен для {updated_count} заявок."),
                messages.SUCCESS,  # Сообщение об успехе (зелёное)
            )
        except AgreedStatus.DoesNotExist:
            self.message_user(
                request,
                _("Ошибка: статус по умолчанию не найден!"),
                messages.ERROR,  # Сообщение об ошибке (красное)
            )
